#!/usr/bin/env bash

echo "kubectl forward port to localhsot:"
# microk8s kubectl port-forward svc/llm-ollama-tinyllama 11434:11434 -n llm &

echo
echo "kong check status:"
curl http://localhost:8000

echo
echo "curl to generate text with:"
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser2", "password": "VeryStrongPassword123!@", "role": "developer"}'