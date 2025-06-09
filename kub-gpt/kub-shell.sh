#!/usr/bin/env bash

microk8s kubectl get pods -n gpt

# read the pod name form command line to be used in next kubectl exec command
read -p "Enter the pod name: " pod_name

microk8s kubectl exec -it $pod_name -n gpt -- /bin/sh

#microk8s kubectl logs deployment.apps/bookingservice -n gpt
