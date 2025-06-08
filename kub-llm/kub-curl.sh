#!/usr/bin/env bash

echo "kubectl forward port to localhsot:"
# microk8s kubectl port-forward svc/llm-ollama-tinyllama 11434:11434 -n llm &

echo
echo "ollama check status:"
curl http://localhost:11434

echo
echo "ollama install model:"
curl -X POST http://localhost:11434/api/pull \
     -H "Content-Type: application/json" \
     -d '{"name":"llama3"}'
     

curl http://localhost:11434/api/tags

curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3", "prompt": "Hello, world!"}'