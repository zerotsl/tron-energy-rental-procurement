from __future__ import annotations

import json
import os
import time
from typing import Any
from urllib import request, error


def _estimate_tokens_and_energy(payload: dict[str, Any]) -> tuple[int, float]:
    usage = payload.get("usage") or {}
    prompt_tokens = int(usage.get("prompt_tokens") or 0)
    completion_tokens = int(usage.get("completion_tokens") or 0)
    total_tokens = prompt_tokens + completion_tokens
    energy_kwh = round((total_tokens / 1000.0) * 0.0002, 6)
    return total_tokens, energy_kwh


def _demo_response(model: str, prompt: str, session_id: str) -> dict[str, Any]:
    from app.services.audit_store import append_record

    response_text = (
        "{\"status\": \"approved\", \"reason\": \"Within policy envelope and no limit violation detected.\", \"approved\": true}"
        if "budget" not in prompt.lower() and "supplier" not in prompt.lower() and "delivery" not in prompt.lower()
        else "{\"status\": \"stopped\", \"reason\": \"Policy guardrail triggered: a spend boundary was detected.\", \"approved\": false}"
    )
    parsed = json.loads(response_text)
    total_tokens = 770
    energy_kwh = round((total_tokens / 1000.0) * 0.0002, 6)
    result = {
        "model": model,
        "status": parsed["status"],
        "reason": parsed["reason"],
        "approved": bool(parsed.get("approved", False)),
        "usage": {"prompt_tokens": 420, "completion_tokens": 350, "total_tokens": total_tokens},
        "energy_kwh": energy_kwh,
        "session_id": session_id,
        "provider": "kiln-demo-fallback",
    }
    append_record({
        "kind": "kiln_call",
        "status": result["status"],
        "session_id": session_id,
        "model": model,
        "usage": result["usage"],
        "energy_kwh": result["energy_kwh"],
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    })
    return result


def call_kiln_model(system_prompt: str, user_prompt: str, session_id: str, model: str | None = None) -> dict[str, Any]:
    selected_model = model or os.getenv("KILN_MODEL", "gpt-oss-120b")
    endpoint = os.getenv("KILN_API_URL")
    api_key = os.getenv("KILN_API_KEY")

    if not endpoint or not api_key:
        return _demo_response(selected_model, user_prompt, session_id)

    payload = {
        "model": selected_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 256,
    }

    request_body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        endpoint,
        data=request_body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "tron-energy-procurement-agent/0.1",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception:
        return _demo_response(selected_model, user_prompt, session_id)

    choice = (data.get("choices") or [{}])[0]
    message = choice.get("message") or {}
    content = message.get("content") or ""
    usage = data.get("usage") or {}

    try:
        parsed = json.loads(content)
    except Exception:
        parsed = {"status": "stopped", "reason": content or "Kiln call did not return JSON.", "approved": False}

    total_tokens, energy_kwh = _estimate_tokens_and_energy({"usage": usage})
    return {
        "model": selected_model,
        "status": parsed.get("status", "stopped"),
        "reason": parsed.get("reason", "Policy check failed."),
        "approved": bool(parsed.get("approved", False)),
        "usage": {
            "prompt_tokens": int(usage.get("prompt_tokens") or 0),
            "completion_tokens": int(usage.get("completion_tokens") or 0),
            "total_tokens": total_tokens,
        },
        "energy_kwh": energy_kwh,
        "session_id": session_id,
        "provider": "kiln",
    }
