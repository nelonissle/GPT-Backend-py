#!/usr/bin/env bash

echo "kubectl forward port to localhsot:"
#microk8s kubectl port-forward service/ollama-ollama 11434:11434 &

echo "kubectl get all -n ingress:"
curl http://localhost:11434

curl http://localhost:11434/api/tags

curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "tinyllama", "prompt": "Hello, world!"}'