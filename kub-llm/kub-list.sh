#!/usr/bin/env bash

echo "kubectl get all -n llm:"
microk8s kubectl get all -n llm

echo "kubectl get all -n ingress:"
microk8s kubectl get all -n ingress

# Get the status of the deployment
echo
echo "kubectl get volumes:"
microk8s kubectl get pv
microk8s kubectl get pvc -n llm

# if pvc is pending, kubectl edit pv downloads-pv and delete the 'claimRef' section
echo
echo "kubectl get deployments:"
microk8s kubectl get deployments -n llm

echo
echo "kubectl get services:"
microk8s kubectl get services -n llm
microk8s kubectl get ingress -n llm

echo
echo "kubectl get replicasets:"
microk8s kubectl get rs -n llm

echo
echo "kubectl get pods:"
microk8s kubectl get pods -n llm
# microk8s kubectl logs <pod-name> -n llm

echo
echo "kubectl get secrets:"
microk8s kubectl get secrets -n llm

