# Ollama Serverless Worker

[![Runpod](https://api.runpod.io/badge/lukepiette/worker-ollama)](https://console.runpod.io/hub/lukepiette/worker-ollama)

Run any [Ollama](https://ollama.com) model — including HuggingFace GGUF repos — on Runpod Serverless. Supports chat and completion requests, streaming, tool calling, and automatic model caching on network volumes.

## Quickstart

1. Deploy this template from the Runpod Hub
2. Set the `OLLAMA_MODEL` environment variable to the model you want (see [Choosing a model](#choosing-a-model))
3. Send a request:

```bash
curl -X POST "https://api.runpod.ai/v2/<ENDPOINT_ID>/runsync" \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "messages": [{"role": "user", "content": "Why is the sky blue?"}]
    }
  }'
```

## Choosing a model

`OLLAMA_MODEL` accepts anything `ollama pull` accepts:

| Source | Example |
|---|---|
| Ollama library | `llama3.2:3b`, `qwen2.5-coder:7b` |
| HuggingFace GGUF repo | `hf.co/prism-ml/Bonsai-27B-gguf:Q1_0` |

For HuggingFace GGUF repos that contain multiple quantization files, specify the quant as a tag (`:Q4_K_M`, `:Q1_0`, `:F16`, ...). Without a tag, Ollama defaults to `Q4_K_M` and fails if the repo doesn't include one.

**Sizing tip:** the VRAM needed for weights is roughly the size of the GGUF file plus ~15% overhead for KV cache and activations. Pick a GPU with headroom above that.

## API

### Input

| Field | Type | Required | Description |
|---|---|---|---|
| `messages` | array | one of `messages`/`prompt` | Chat messages, OpenAI format |
| `prompt` | string | one of `messages`/`prompt` | Raw completion prompt |
| `model` | string | no | Overrides `OLLAMA_MODEL`; pulled on demand if missing |
| `stream` | bool | no | Stream response chunks (default `false`) |
| `options` | object | no | Ollama options (`temperature`, `num_ctx`, `top_p`, ...) |
| `tools` | array | no | Tool definitions for models that support tool calling |
| `format` | string/object | no | `"json"` or a JSON schema for structured output |
| `system` | string | no | System prompt (completion mode) |
| `keep_alive` | string/int | no | How long to keep the model loaded (default: forever) |

### Chat request

```json
{
  "input": {
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Write a haiku about GPUs."}
    ],
    "options": {"temperature": 0.7}
  }
}
```

### Completion request

```json
{
  "input": {
    "prompt": "The capital of France is",
    "options": {"num_predict": 10}
  }
}
```

### Streaming

Set `"stream": true` and use `/run` + `/stream/<JOB_ID>`, or `/runsync` to receive the aggregated stream. Each chunk is a JSON line in Ollama's [streaming format](https://github.com/ollama/ollama/blob/main/docs/api.md).

### Output

Non-streaming responses return Ollama's native response object:

```json
{
  "model": "llama3.2:3b",
  "message": {"role": "assistant", "content": "..."},
  "done": true,
  "eval_count": 42,
  "eval_duration": 1234567890
}
```

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_MODEL` | — | Model pulled at worker startup |
| `OLLAMA_KEEP_ALIVE` | `-1` (forever) | How long models stay loaded in VRAM |

## Model caching

Attach a network volume to the endpoint and models are stored at `/runpod-volume/ollama/models` — new workers skip the download and cold starts drop to seconds. Without a volume, each fresh worker pulls the model on first boot.

## Local development

```bash
docker build -t ollama-worker .
docker run --gpus all -e OLLAMA_MODEL=llama3.2:1b ollama-worker
```

Without a GPU, Ollama falls back to CPU inference — slow, but enough to smoke-test the handler with a small model. You can also test the handler directly against `test_input.json`:

```bash
python3 handler.py --rp_serve_api  # requires a local ollama serve
```
