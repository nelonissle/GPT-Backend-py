#!/usr/bin/env bash

echo
echo "installing gpt-umbrella helm chart"
microk8s helm3 upgrade gpt . --namespace gpt
