import builtins
import hmac
import json
import os
import selectors
import shutil
import signal
import subprocess
import sys
import time

from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# Configuration
RUNTIME_ROOT = Path("/opt/pulse-worker")
PYTHON = str(Path(sys.executable).resolve())

PYTHON_VERSION = (
    f"python{sys.version_info.major}.{sys.version_info.minor}"
)

SITE_PACKAGES = Path("/opt/pulse-worker/python-packages")

HOST = "127.0.0.1"
PORT = 8765

MAX_SOURCE_SIZE = 64 * 1024
MAX_OUTPUT_SIZE = 256 * 1024
MAX_PROCESS_OUTPUT = 4 * 1024 * 1024

EXECUTION_TIMEOUT = 10
MAX_FILE_SIZE = 16 * 1024 * 1024

class ExecutionTimeout(Exception):
    pass

class OutputLimitExceeded(Exception):
    pass

class LimitedWriter:
    MARKER = "\n[Output truncated: size limit reached]"
    
    def __init__(self, limit):
        self.limit = limit
        self.buffer = bytearray()
        self.truncated = False
    
    def write(self, value):
        value = str(value)
        
        if self.truncated:
            return len(value)
        
        encoded = value.encode("utf-8")
        remaining = self.limit - len(self.buffer)
        
        if len(encoded) <= remaining:
            self.buffer.extend(encoded)
        else:
            marker = self.MARKER.encode("utf-8")
            budget = max(0, remaining - len(marker))
            
            self.buffer.extend(encoded[:budget])
            self.buffer.extend(marker[:remaining - budget])
            self.truncated = True
        
        return len(value)
    
    def flush(self):
        pass
    
    def getvalue(self):
        return self.buffer.decode("utf-8", errors="ignore")

# Runs inside Bubblewrap
RUNNER_SOURCE = r'''
import builtins
import io
import json
import sys

from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

sys.path.insert(0, "/opt/pulse-worker")

from pulse import run
from src.error import PulseError
from src.runtime import PulseRuntimeException

MAX_SOURCE_SIZE = 64 * 1024
MAX_OUTPUT_SIZE = 256 * 1024

class InputNotSupported(Exception):
    pass

class LimitedWriter:
    MARKER = "\n[Output truncated: size limit reached]"
    
    def __init__(self, limit):
        self.limit = limit
        self.buffer = bytearray()
        self.truncated = False
    
    def write(self, value):
        value = str(value)
        
        if self.truncated:
            return len(value)
        
        encoded = value.encode("utf-8")
        remaining = self.limit - len(self.buffer)
        
        if len(encoded) <= remaining:
            self.buffer.extend(encoded)
        else:
            marker = self.MARKER.encode("utf-8")
            budget = max(0, remaining - len(marker))
            
            self.buffer.extend(encoded[:budget])
            self.buffer.extend(marker[:remaining - budget])
            self.truncated = True
        
        return len(value)
    
    def flush(self):
        pass
    
    def getvalue(self):
        return self.buffer.decode("utf-8", errors="ignore")

original_stdout = sys.stdout

def respond(stdout="", stderr="", exit_code=0):
    result = {
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": exit_code,
    }
    
    json.dump(result, original_stdout, ensure_ascii=False)
    original_stdout.write("\n")
    original_stdout.flush()

def reject_input(*args, **kwargs):
    raise InputNotSupported(
        "Interactive input is not supported in online execution."
    )

def main():
    try:
        payload = sys.stdin.read(128 * 1024)
        data = json.loads(payload)
        
        if not isinstance(data, dict):
            respond(stderr="Invalid request.", exit_code=1)
            return
        
        code = data.get("code", "")
        
        if not isinstance(code, str):
            respond(stderr="Code must be a string.", exit_code=1)
            return
        
        if not code.strip():
            respond(stderr="No Pulse code provided.", exit_code=1)
            return
        
        if len(code.encode("utf-8")) > MAX_SOURCE_SIZE:
            respond(
                stderr="Program exceeds the 64 KB source limit.",
                exit_code=1,
            )
            return
    
    except (json.JSONDecodeError, UnicodeError):
        respond(stderr="Invalid JSON request.", exit_code=1)
        return
    
    output = LimitedWriter(MAX_OUTPUT_SIZE)
    errors = LimitedWriter(MAX_OUTPUT_SIZE)
    
    original_input = builtins.input
    builtins.input = reject_input
    
    try:
        with redirect_stdout(output), redirect_stderr(errors):
            run(
                code,
                output=lambda text, end="\n": (
                    output.write(str(text)),
                    output.write(str(end)),
                ),
            )
        
        respond(
            stdout=output.getvalue(),
            stderr=errors.getvalue(),
            exit_code=0,
        )
    
    except InputNotSupported as exc:
        respond(
            stdout=output.getvalue(),
            stderr=str(exc),
            exit_code=1,
        )
    
    except PulseRuntimeException as exc:
        respond(
            stdout=output.getvalue(),
            stderr=exc.error.plain_message,
            exit_code=1,
        )
    
    except PulseError as exc:
        respond(
            stdout=output.getvalue(),
            stderr=exc.plain_message,
            exit_code=1,
        )
    
    except Exception:
        respond(
            stdout=output.getvalue(),
            stderr="Internal execution error.",
            exit_code=1,
        )
    
    finally:
        builtins.input = original_input

if __name__ == "__main__":
    main()
'''

def set_resource_limits():
    import resource
    
    resource.setrlimit(resource.RLIMIT_CPU, (10, 11))
    resource.setrlimit(
        resource.RLIMIT_FSIZE,
        (MAX_FILE_SIZE, MAX_FILE_SIZE),
    )
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

def sandbox_command():
    return [
        "bwrap",
        "--die-with-parent",
        "--new-session",
        "--unshare-all",
        
        "--ro-bind", "/usr", "/usr",
        "--ro-bind", "/lib", "/lib",
        "--ro-bind", "/lib64", "/lib64",
        "--ro-bind", "/etc", "/etc",
        
        "--dir", "/opt",
        "--ro-bind", str(RUNTIME_ROOT), "/opt/pulse-worker",
        "--ro-bind", str(SITE_PACKAGES), "/opt/python-packages",
        
        "--proc", "/proc",
        "--dev", "/dev",
        "--tmpfs", "/tmp",
        "--tmpfs", "/workspace",
        
        "--chdir", "/workspace",
        "--clearenv",
        
        "--setenv", "HOME", "/workspace",
        "--setenv", "TMPDIR", "/tmp",
        "--setenv", "PATH", "/usr/bin:/bin",
        "--setenv", "PYTHONPATH", "/opt/python-packages",
        "--setenv", "PYTHONDONTWRITEBYTECODE", "1",
        
        "--setenv", "OMP_NUM_THREADS", "1",
        "--setenv", "MKL_NUM_THREADS", "1",
        "--setenv", "OPENBLAS_NUM_THREADS", "1",
        
        PYTHON,
        "-c",
        RUNNER_SOURCE,
    ]

def kill_process(process):
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        pass

def run_sandbox(code):
    payload = json.dumps(
        {"code": code},
        ensure_ascii=False,
    ).encode("utf-8")
    
    process = subprocess.Popen(
        sandbox_command(),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=0,
        start_new_session=True,
        preexec_fn=set_resource_limits,
    )
    
    selector = selectors.DefaultSelector()
    
    streams = {
        "stdout": bytearray(),
        "stderr": bytearray(),
    }
    
    total_output = 0
    sent = 0
    deadline = time.monotonic() + EXECUTION_TIMEOUT
    
    try:
        for stream, name in (
            (process.stdout, "stdout"),
            (process.stderr, "stderr"),
        ):
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ, name)
        
        stdin_fd = process.stdin.fileno()
        os.set_blocking(stdin_fd, False)
        selector.register(
            stdin_fd,
            selectors.EVENT_WRITE,
            "stdin",
        )
        
        while selector.get_map():
            if time.monotonic() >= deadline:
                raise ExecutionTimeout
            
            if process.poll() is not None:
                try:
                    selector.unregister(stdin_fd)
                except KeyError:
                    pass
                
                if not process.stdin.closed:
                    process.stdin.close()
            
            events = selector.select(0.05)
            
            for key, _ in events:
                if key.data == "stdin":
                    try:
                        written = os.write(
                            stdin_fd,
                            payload[sent:sent + 16384],
                        )
                        sent += written
                    except BrokenPipeError:
                        sent = len(payload)
                    
                    if sent >= len(payload):
                        selector.unregister(stdin_fd)
                        process.stdin.close()
                
                else:
                    name = key.data
                    
                    chunk = os.read(
                        key.fileobj.fileno(),
                        65536,
                    )
                    
                    if not chunk:
                        selector.unregister(key.fileobj)
                        key.fileobj.close()
                        continue
                    
                    streams[name].extend(chunk)
                    total_output += len(chunk)
                    
                    if total_output > MAX_PROCESS_OUTPUT:
                        raise OutputLimitExceeded
        
        process.wait(timeout=1)
        
        if process.returncode != 0:
            raise RuntimeError("Sandbox process failed.")
        
        if streams["stderr"]:
            raise RuntimeError("Unexpected sandbox error output.")
        
        try:
            result = json.loads(
                streams["stdout"].decode("utf-8")
            )
        except (json.JSONDecodeError, UnicodeError):
            raise RuntimeError("Invalid executor response.")
        
        if not isinstance(result, dict):
            raise RuntimeError("Invalid executor response.")
        
        if (
            not isinstance(result.get("stdout"), str)
            or not isinstance(result.get("stderr"), str)
            or type(result.get("exit_code")) is not int
        ):
            raise RuntimeError("Invalid executor response.")
        
        if (
            len(result["stdout"].encode("utf-8")) > MAX_OUTPUT_SIZE
            or len(result["stderr"].encode("utf-8")) > MAX_OUTPUT_SIZE
        ):
            raise RuntimeError("Executor output exceeded its limit.")
        
        return result
    
    finally:
        selector.close()
        
        if process.poll() is None:
            kill_process(process)
        
        for stream in (
            process.stdin,
            process.stdout,
            process.stderr,
        ):
            if not stream.closed:
                stream.close()

def execute(code):
    if not isinstance(code, str):
        raise ValueError("Code must be a string.")
    
    if not code.strip():
        raise ValueError("No Pulse code provided.")
    
    if len(code.encode("utf-8")) > MAX_SOURCE_SIZE:
        raise ValueError("Program exceeds the 64 KB source limit.")
    
    try:
        return run_sandbox(code)
    except ExecutionTimeout:
        return {
            "stdout": "",
            "stderr": "Execution timed out.",
            "exit_code": 124,
        }
    except OutputLimitExceeded:
        return {
            "stdout": "",
            "stderr": "Executor output exceeded its limit.",
            "exit_code": 1,
        }

class WorkerHandler(BaseHTTPRequestHandler):
    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)
    
    def do_POST(self):
        if self.path != "/execute":
            self.send_json({"error": "Not found."}, 404)
            return
        
        token = os.environ.get("PULSE_WORKER_TOKEN", "")
        
        supplied = self.headers.get("Authorization", "")
        expected = f"Bearer {token}"
        
        if not token or not hmac.compare_digest(supplied, expected):
            self.send_json({"error": "Unauthorized."}, 401)
            return
        
        try:
            length = int(self.headers.get("Content-Length", "0"))
            
            if length <= 0 or length > 128 * 1024:
                self.send_json(
                    {"error": "Invalid request size."},
                    413,
                )
                return
            
            payload = self.rfile.read(length)
            data = json.loads(payload)
            
            if not isinstance(data, dict):
                raise ValueError("Invalid request.")
            
            result = execute(data.get("code", ""))
            self.send_json(result)
        except (json.JSONDecodeError, UnicodeError):
            self.send_json({"error": "Invalid JSON request."}, 400)
        except ValueError as exc:
            self.send_json({"error": str(exc)}, 400)
        except Exception:
            self.send_json(
                {"error": "Execution service failed."},
                500,
            )
    
    def log_message(self, format, *args):
        pass

def main():
    if shutil.which("bwrap") is None:
        raise SystemExit("Bubblewrap is not installed.")
    
    if not (
        RUNTIME_ROOT.is_dir()
        and (RUNTIME_ROOT / "pulse.py").is_file()
        and (RUNTIME_ROOT / "pulse_info.py").is_file()
        and (RUNTIME_ROOT / "src").is_dir()
        and (RUNTIME_ROOT / "bin").is_dir()
    ):
        raise SystemExit("Pulse runtime is incomplete.")
    
    if not SITE_PACKAGES.is_dir():
        raise SystemExit("Python virtual environment was not found.")
    
    if not Path("/lib64").exists():
        raise SystemExit("/lib64 is missing.")
    
    token = os.environ.get("PULSE_WORKER_TOKEN", "")
    
    if len(token) < 32:
        raise SystemExit(
            "PULSE_WORKER_TOKEN must contain at least 32 characters."
        )
    
    server = HTTPServer((HOST, PORT), WorkerHandler)
    server.timeout = 1
    
    print(f"Pulse worker listening on {HOST}:{PORT}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()