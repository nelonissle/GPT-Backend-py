#!/usr/bin/env bash

echo
echo "enable ingress:"
microk8s enable ingress

echo
echo "Create pv:"
microk8s kubectl apply -f pv-db.yaml
microk8s kubectl apply -f pv-logs.yaml

