#!/usr/bin/env bash

# ask if user wants to forward the ports
echo "Forwarding ports for ollama and kong services..."
# ask if user wants to redirect port 8000 to 30800
echo "Do you want to forward ports with kubectl? (y/n)"
read answer
if [[ "$answer" == "y" ]]; then
  echo "kubectl forward port to localhost:"
  microk8s kubectl port-forward svc/llm-ollama-tinyllama 11434:11434 -n llm
  microk8s kubectl port-forward svc/kong-gateway 8000:8000 8001:8001 -n gpt
fi

echo
echo "Do you want to forward ports? (y/n)"
read answer
if [[ "$answer" == "y" ]]; then
  echo "forward ports to localhost using ingress:"
  sudo iptables -t nat -A PREROUTING -p tcp --dport 8000 -j REDIRECT --to-port 30800
  sudo iptables -t nat -A PREROUTING -p tcp --dport 8001 -j REDIRECT --to-port 30801
  sudo iptables -t nat -A PREROUTING -p tcp --dport 11434 -j REDIRECT --to-port 31434
fi

echo
echo "ollama check status:"
curl http://localhost:11434

echo
echo "kong check status:"
curl http://localhost:8000/

echo
echo "kong check admin status:"
curl http://localhost:8001/
