#!/usr/bin/env bash

export LLMHOST=192.168.9.181

echo "kubectl forward port to localhsot:"
# microk8s kubectl port-forward svc/llm-ollama-tinyllama 11434:11434 -n llm &

microk8s kubectl get svc -n llm
# read ip adress of the service on command line to variable LLMHOST
echo
echo "Enter the IP address of the LLM service (e.g., 192.168.9.181):"
read LLMHOST

echo
echo "ollama check status on host $LLMHOST:"
curl http://$LLMHOST:11434

echo
echo "ollama install model:"
curl -X POST http://$LLMHOST:11434/api/pull \
     -H "Content-Type: application/json" \
     -d '{"name":"llama3"}'

echo
echo "ollama check status after installing model:"     
curl -X POST http://$LLMHOST:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3", "prompt": "Hello, world!"}'

echo
echo "ollama list models:"
# read tags from curl and convert output to json and print models[0].name and supress other output
curl -sS http://$LLMHOST:11434/api/tags | jq '.models[] | .name'

echo
echo "done."
