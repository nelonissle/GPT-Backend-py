#!/usr/bin/env bash

echo "make sure the pv and ingress is available in the cluster"
microk8s kubectl get all -n ingress
microk8s kubectl get pv

echo
echo "get all helm charts"
microk8s helm3 list

echo
echo "all namespaces:"
microk8s kubectl get namespaces

echo
echo "creating namespace llm"
microk8s kubectl create namespace llm

echo
echo "installing llm-umbrella helm chart"
microk8s helm3 install llm . --namespace llm
