import json
import os
import urllib.request
import urllib.error

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

WORKER_URL = "http://127.0.0.1:8765/execute"
WORKER_TOKEN = os.environ.get("PULSE_WORKER_TOKEN")

@csrf_exempt
@require_POST
def execute(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid JSON request."}, status=400)

    if not isinstance(data, dict):
        return JsonResponse({"error": "Invalid JSON request."}, status=400)
    code = data.get("code", "")

    if not isinstance(code, str):
        return JsonResponse({"error": "Code must be a string."}, status=400)

    if not code.strip():
        return JsonResponse({"error": "No Pulse code provided."}, status=400)

    if not WORKER_TOKEN:
        return JsonResponse({"error": "Execution service unavailable."}, status=503)

    payload = json.dumps({"code": code}).encode("utf-8")

    worker_request = urllib.request.Request(
        WORKER_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {WORKER_TOKEN}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            worker_request,
            timeout=15,
        ) as response:
            result = json.loads(response.read())

        return JsonResponse(result)

    except urllib.error.HTTPError:
        return JsonResponse({"error": "Execution service failed."}, status=502)

    except (urllib.error.URLError, TimeoutError):
        return JsonResponse({"error": "Execution service unavailable."}, status=503)

    except Exception:
        return JsonResponse({"error": "Execution service failed."}, status=502)
