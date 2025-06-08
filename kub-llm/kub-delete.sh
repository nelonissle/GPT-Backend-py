#!/usr/bin/env bash

microk8s kubectl get namespaces

microk8s helm3 uninstall llm --namespace llm
microk8s kubectl delete namespace llm

# ask with a prompt if i shall delete the claim in my pv
echo "Do you want to delete the persistent volume claim (PVC) and patch the persistent volume (PV)? (y/n)"
read answer
if [[ "$answer" == "y" ]]; then
  microk8s kubectl patch pv db-pv -p '{"spec":{"claimRef": null}}'
fi
