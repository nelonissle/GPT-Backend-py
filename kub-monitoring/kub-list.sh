#!/usr/bin/env bash

echo "kubectl get all -n adminwebserver:"
microk8s kubectl get all -n adminwebserver

echo "kubectl get all -n ingress:"
microk8s kubectl get all -n ingress

# Get the status of the deployment
echo
echo "kubectl get volumes:"
microk8s kubectl get pv
microk8s kubectl get pvc -n adminwebserver

# if pvc is pending, kubectl edit pv downloads-pv and delete the 'claimRef' section
echo
echo "kubectl get deployments:"
microk8s kubectl get deployments -n adminwebserver

echo
echo "kubectl get services:"
microk8s kubectl get services -n adminwebserver

echo
echo "kubectl get replicasets:"
microk8s kubectl get rs -n adminwebserver

echo
echo "kubectl get pods:"
microk8s kubectl get pods -n adminwebserver
# microk8s kubectl logs <pod-name> -n adminwebserver

echo
echo "kubectl get secrets:"
microk8s kubectl get secrets -n adminwebserver

