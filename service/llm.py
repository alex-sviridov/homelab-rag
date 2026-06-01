#!/usr/bin/env python3

import os
from pathlib import Path
from urllib import response
import requests
import logging

log = logging.getLogger(__name__)

class InferenceError(Exception):
    """Error occurred during LLM inference."""
class InferenceTimeoutError(InferenceError):
    """Inference request timed out."""

def check_model_ready() -> bool:
    try:
        response = requests.get(
            f"{os.getenv('INFERENCE_URL')}/ps",
            timeout=int(os.getenv("REQUEST_TIMEOUT_SEC")),
        )
        response.raise_for_status()
        models = response.json().get("models", [])
        return any(m.get("model") == os.getenv("MODEL") for m in models)
    except (requests.RequestException, ValueError):
        return False


def query(prompt: str, system_prompt: str = "") -> str:
    log.debug(
        "llm_query_started",
        extra={
            "prompt_length": len(prompt),
            "system_prompt_length": len(system_prompt),
            "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
        },
    )
    try:
        response = requests.post(
            f"{os.getenv('INFERENCE_URL')}/chat",
            json={
                "model": os.getenv("MODEL"),
                "messages": [
                    {"role": "user", "content": prompt},
                    {"role": "system", "content": system_prompt},
                ],
                "think": False,
                "stream": False,
            },
            timeout=int(os.getenv("REQUEST_TIMEOUT_SEC")),
        )

        response.raise_for_status()
        response = response.json()

    except requests.Timeout as e:
        log.error("llm_query_timeout", extra={"error": str(e)})
        raise InferenceTimeoutError("inference timed out") from e
    except requests.RequestException as e:
        log.error("llm_query_failed", extra={"error": str(e)})
        raise InferenceError(str(e)) from e
    
    log.debug(
        "llm_query_handled",
        extra={
            "total_duration_ms": response.get("total_duration", 0)/1000000,
            "load_duration_ms": response.get("load_duration", 0)/1000000,
            "prompt_eval_count": response.get("prompt_eval_count", 0),
            "prompt_eval_duration_ms": response.get("prompt_eval_duration", 0)/1000000,
            "eval_count": response.get("eval_count", 0),
            "eval_duration_ms": response.get("eval_duration", 0)/1000000,
        },
    )
    try:
        return response["message"]["content"]
    except (KeyError, TypeError) as e:
        log.error("llm_bad_response", extra={"error": str(e)})
        raise InferenceError("unexpected response shape") from e
