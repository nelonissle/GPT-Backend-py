#!/usr/bin/env bash

echo
echo "installing llm-umbrella helm chart"
microk8s helm3 upgrade llm . --namespace llm -f values.yaml 
