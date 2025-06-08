#!/usr/bin/env bash

microk8s kubectl get pods -n gpt

# read the pod name form command line to be used in next kubectl exec command
read -p "Enter the pod name: " ser_name

microk8s kubectl describe pod $ser_name -n gpt
