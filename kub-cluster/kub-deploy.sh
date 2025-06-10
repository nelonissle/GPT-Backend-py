#!/usr/bin/env bash

# optional nvidia gpu support
# nvidia-smi
# sudo microk8s enable gpu

#echo
#echo "enable ingress:"
#microk8s enable ingress
#microk8s kubectl apply -f ingress-extern.yaml

echo
echo "enable metallb"
microk8s enable metallb
# set the ip range to 192.168.n.180-192.168.n.190

echo
echo "Checking MetalLB status..."
microk8s kubectl get pods -n metallb-system

echo
echo "Checking LoadBalancer services..."
microk8s kubectl get svc --all-namespaces | grep LoadBalancer

echo
echo "MetalLB configuration:"
microk8s kubectl get configmap -n metallb-system -o yaml

echo
echo "To access your services, use the EXTERNAL-IP shown above"
echo "Example: curl http://<EXTERNAL-IP>:8000/"


echo
echo "Create pv and optional microk8s-hostpath storageClass:"
# microk8s kubectl edit storageclass microk8s-hostpath
# set reclaimPolicy: Retain
microk8s enable hostpath-storage
microk8s kubectl apply -f pv-logs.yaml

