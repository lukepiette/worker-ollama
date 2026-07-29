#!/bin/bash
set -e

echo "Starting Runpod Ollama worker..."

# Cache models on the network volume when one is attached, so warm workers
# and restarts skip the pull entirely.
if [ -d "/runpod-volume" ]; then
    export OLLAMA_MODELS="/runpod-volume/ollama/models"
    mkdir -p "$OLLAMA_MODELS"
    echo "Network volume detected — caching models at $OLLAMA_MODELS"
fi

ollama serve &

echo "Waiting for Ollama server to be ready..."
until curl -sf http://127.0.0.1:11434/api/version > /dev/null; do
    sleep 0.5
done
echo "Ollama server is ready"

if [ -n "$OLLAMA_MODEL" ]; then
    echo "Pulling model: $OLLAMA_MODEL"
    ollama pull "$OLLAMA_MODEL"
    echo "Model pulled: $OLLAMA_MODEL"
fi

exec python3 -u /handler.py
