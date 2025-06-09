#!/usr/bin/env bash

# optional nvidia gpu support
# nvidia-smi
# sudo microk8s enable gpu

echo
echo "enable ingress:"
microk8s enable ingress
microk8s kubectl apply -f ingress-extern.yaml

echo
echo "Create pv and optional microk8s-hostpath storageClass:"
# microk8s kubectl edit storageclass microk8s-hostpath
# set reclaimPolicy: Retain
microk8s enable hostpath-storage
microk8s kubectl apply -f pv-logs.yaml

