#!/usr/bin/env bash

microk8s kubectl get namespaces

microk8s helm3 uninstall gpt --namespace gpt
microk8s kubectl delete namespace gpt

# ask with a prompt if i shall delete the claim in my pv
echo "Do you want to delete claim logs? (y/n)"
read answer
if [[ "$answer" == "y" ]]; then
  microk8s kubectl patch pv logs-pv -p '{"spec":{"claimRef": null}}'
fi
