import os

import requests
import runpod

OLLAMA_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "")

session = requests.Session()


def get_local_models():
    response = session.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
    response.raise_for_status()
    return [m["name"] for m in response.json().get("models", [])]


def ensure_model(model):
    local = get_local_models()
    if model in local or f"{model}:latest" in local:
        return
    response = session.post(
        f"{OLLAMA_BASE_URL}/api/pull",
        json={"model": model, "stream": False},
        timeout=3600,
    )
    response.raise_for_status()


def handler(job):
    job_input = job.get("input") or {}

    model = job_input.get("model") or DEFAULT_MODEL
    if not model:
        yield {
            "error": (
                "No model specified. Set the OLLAMA_MODEL environment variable "
                "on the endpoint or pass 'model' in the request input, e.g. "
                "'hf.co/prism-ml/Bonsai-27B-gguf:Q1_0' or 'llama3.2:3b'."
            )
        }
        return

    messages = job_input.get("messages")
    prompt = job_input.get("prompt")
    if not messages and not prompt:
        yield {"error": "Provide either 'messages' (chat) or 'prompt' (completion) in input."}
        return

    try:
        ensure_model(model)
    except requests.RequestException as err:
        yield {"error": f"Failed to pull model '{model}': {err}"}
        return

    if messages:
        endpoint = f"{OLLAMA_BASE_URL}/api/chat"
        payload = {"model": model, "messages": messages}
    else:
        endpoint = f"{OLLAMA_BASE_URL}/api/generate"
        payload = {"model": model, "prompt": prompt}

    for key in ("options", "format", "keep_alive", "tools", "system", "template"):
        if key in job_input:
            payload[key] = job_input[key]

    stream = bool(job_input.get("stream", False))
    payload["stream"] = stream

    try:
        if stream:
            with session.post(endpoint, json=payload, stream=True, timeout=3600) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line:
                        continue
                    yield line.decode("utf-8")
        else:
            response = session.post(endpoint, json=payload, timeout=3600)
            response.raise_for_status()
            yield response.json()
    except requests.RequestException as err:
        yield {"error": f"Ollama request failed: {err}"}


runpod.serverless.start(
    {
        "handler": handler,
        "return_aggregate_stream": True,
    }
)
