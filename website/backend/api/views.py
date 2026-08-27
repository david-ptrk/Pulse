import sys
from pathlib import Path
import io
from contextlib import redirect_stdout

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

PULSE_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PULSE_ROOT))

from pulse import run
from src.error import PulseError, report_error
from src.runtime import PulseRuntimeException

@csrf_exempt
@require_POST
def execute(request):
    try:
        import json
        
        data = json.loads(request.body)
        code = data.get("code", "")
        
        if not isinstance(code, str):
            return JsonResponse(
                {
                    "error": "Code must be a string."
                },
                status=400,
            )
        
        if not code.strip():
            return JsonResponse(
                {
                    "error": "No Pulse code provided."
                },
                status=400,
            )
        
        output = io.StringIO()
        
        def capture(text, end="\n"):
            output.write(str(text))
            output.write(str(end))
        
        with redirect_stdout(output):
            run(code, output=capture)
        
        return JsonResponse(
            {
                "stdout": output.getvalue(),
                "stderr": "",
                "exit_code": 0,
            }
        )
    
    except PulseRuntimeException as e:
        return JsonResponse(
            {
                "stdout": output.getvalue() if "output" in locals() else "",
                "stderr": str(e),
                "exit_code": 1,
            }
        )
    
    except PulseError as e:
        return JsonResponse(
            {
                "stdout": output.getvalue() if "output" in locals() else "",
                "stderr": str(e),
                "exit_code": 1,
            }
        )
    
    except json.JSONDecodeError:
        return JsonResponse(
            {
                "error": "Invalid JSON request."
            },
            status=400,
        )
    
    except Exception as e:
        return JsonResponse(
            {
                "stdout": output.getvalue() if "output" in locals() else "",
                "stderr": f"Internal error: {e}",
                "exit_code": 1,
            },
            status=500,
        )

