#!/usr/bin/env bash

microk8s kubectl get namespaces

microk8s helm3 uninstall llm-umbrella --namespace llm
microk8s kubectl delete namespace llm

