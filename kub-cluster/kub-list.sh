#!/usr/bin/env bash

echo "kubectl get all -n ingress:"
microk8s kubectl get all -n ingress

# Get the status of the deployment
echo
echo "kubectl get volumes:"
microk8s kubectl get pv

