#!/usr/bin/env bash

# Load environment variables from ../.env
set -o allexport
if [ -f ../.env ]; then
  source ../.env
fi
set +o allexport

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
  --set admin-service.secrets.SECRET_KEY="$SECRET_KEY" \
  --set admin-service.secrets.MONGO_INITDB_ROOT_PASSWORD="$MONGO_INITDB_ROOT_PASSWORD" \
  --set auth-service.secrets.SECRET_KEY="$SECRET_KEY" \
  --set chat-service.secrets.SECRET_KEY="$SECRET_KEY" \
  --set chat-service.secrets.MONGO_INITDB_ROOT_PASSWORD="$MONGO_INITDB_ROOT_PASSWORD" \
  --set chat-service.secrets.OLLAMA_API_URL="$OLLAMA_API_URL" \
  --set kong.secrets.KONG_PG_PASSWORD="$KONG_PG_PASSWORD" \
  --set mongo.secrets.MONGO_INITDB_ROOT_PASSWORD="$MONGO_INITDB_ROOT_PASSWORD" \
  --set postgres.secrets.POSTGRES_PASSWORD="$POSTGRES_PASSWORD"
