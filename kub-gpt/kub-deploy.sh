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
echo "creating namespace gpt"
microk8s kubectl create namespace gpt

echo
echo "installing gpt-umbrella helm chart"
microk8s helm3 install gpt . --namespace gpt \
  --set secrets.SECRET_KEY="$SECRET_KEY" \
  --set secrets.MONGO_INITDB_ROOT_PASSWORD="$MONGO_INITDB_ROOT_PASSWORD" \
  --set secrets.KONG_PG_PASSWORD="$KONG_PG_PASSWORD" \
  --set secrets.POSTGRES_PASSWORD="$POSTGRES_PASSWORD"
