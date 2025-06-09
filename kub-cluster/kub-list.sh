#!/usr/bin/env bash

echo "kubectl get all -n ingress:"
microk8s kubectl get all -n ingress

sudo iptables -t nat -L -n -v --line-numbers

# Get the status of the deployment
echo
echo "kubectl get volumes:"
microk8s kubectl get pv
ls /var/snap/microk8s/common/default-storage
ls /data/logs

