#!/usr/bin/env bash

echo "kubectl get all -n gpt:"
microk8s kubectl get all -n gpt

echo "kubectl get all -n ingress:"
microk8s kubectl get all -n ingress

# Get the status of the deployment
echo
echo "kubectl get volumes:"
microk8s kubectl get pv
microk8s kubectl get pvc -n gpt

# if pvc is pending, kubectl edit pv downloads-pv and delete the 'claimRef' section
echo
echo "kubectl get deployments:"
microk8s kubectl get deployments -n gpt

echo
echo "kubectl get services:"
microk8s kubectl get services -n gpt
microk8s kubectl get ingress -n gpt

echo
echo "kubectl get replicasets:"
microk8s kubectl get rs -n gpt

echo
echo "kubectl get pods:"
microk8s kubectl get pods -n gpt
# microk8s kubectl logs <pod-name> -n gpt

echo
echo "kubectl get secrets:"
microk8s kubectl get secrets -n gpt

