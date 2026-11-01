import builtins
import io
import json
import sys
import traceback
from contextlib import redirect_stderr, redirect_stdout

from pathlib import Path

PULSE_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PULSE_ROOT))

from pulse import run
from src.error import PulseError
from src.runtime import PulseRuntimeException


MAX_SOURCE_SIZE = 64 * 1024
MAX_OUTPUT_SIZE = 256 * 1024

original_stdout = sys.stdout
original_stderr = sys.stderr


class InputNotSupported(Exception):
    pass


class LimitedWriter:
    MARKER = "\n[Output truncated: size limit reached]"

    def __init__(self, limit):
        self.limit = limit
        self.buffer = io.StringIO()
        self.size = 0
        self.truncated = False

    def write(self, text):
        text = str(text)

        if self.truncated:
            return len(text)

        encoded = text.encode("utf-8")
        remaining = self.limit - self.size

        if len(encoded) <= remaining:
            self.buffer.write(text)
            self.size += len(encoded)
        else:
            marker = self.MARKER.encode("utf-8")

            if len(marker) > self.limit:
                marker = marker[:self.limit]

            content_budget = self.limit - len(marker)
            existing = self.buffer.getvalue().encode("utf-8")
            combined = existing + encoded

            accepted = combined[:content_budget].decode(
                "utf-8", errors="ignore"
            )

            self.buffer = io.StringIO(accepted)
            self.buffer.write(marker.decode("utf-8", errors="ignore"))

            self.size = len(self.buffer.getvalue().encode("utf-8"))
            self.truncated = True

        return len(text)

    def flush(self):
        pass

    def getvalue(self):
        return self.buffer.getvalue()


def reject_input(*args, **kwargs):
    raise InputNotSupported(
        "Interactive input is not supported in online execution."
    )


def respond(stdout="", stderr="", exit_code=0, error=None):
    result = {
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": exit_code,
    }

    if error is not None:
        result["error"] = error

    json.dump(result, original_stdout)
    original_stdout.write("\n")
    original_stdout.flush()


def main():
    try:
        payload = sys.stdin.read(1024 * 1024)
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
        traceback.print_exc(file=original_stderr)
        respond(
            stdout=output.getvalue(),
            stderr="Internal execution error.",
            exit_code=1,
        )

    finally:
        builtins.input = original_input


if __name__ == "__main__":
    main()
