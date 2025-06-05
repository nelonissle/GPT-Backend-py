#!/usr/bin/env bash

# Create the namespace
microk8s kubectl apply -f webserver/namespace.yaml

# Create TLS cert
# sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
#openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
#  -keyout tls.key -out tls.crt \
#  -subj "/CN=private.nissle.ch" \
#  -addext "subjectAltName=DNS:private.nissle.ch"

microk8s kubectl create secret tls nginx-tls \
  --cert=tls.crt \
  --key=tls.key \
  -n adminwebserver


# microk8s kubectl create secret docker-registry ghcr --docker-server=ghcr.io \
#  --docker-username=YOUR_GITHUB_USERNAME --docker-password=YOUR_GITHUB_PAT --docker-email=YOUR_EMAIL \
#  -n adminwebserver
echo "my GitHub PAT is: $GITHUB_REGTOKEN"
microk8s kubectl create secret docker-registry ghcr --docker-server=ghcr.io \
  --docker-username=webernissle --docker-password=$GITHUB_REGTOKEN --docker-email=webernissle@gmail.com \
  -n adminwebserver

microk8s kubectl apply -f webserver/ -n adminwebserver

# Deploy the Nginx application
#microk8s kubectl apply -f webserver/deployment.yaml
# Expose the Nginx application
#microk8s kubectl apply -f webserver/service.yaml

echo
echo "enable ingress:"
microk8s enable ingress

