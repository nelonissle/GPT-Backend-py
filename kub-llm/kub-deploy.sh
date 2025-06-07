#!/usr/bin/env bash

microk8s kubectl get namespaces

microk8s kubectl create namespace llm

# Create the namespace
microk8s helm3 install llm . --namespace llm
