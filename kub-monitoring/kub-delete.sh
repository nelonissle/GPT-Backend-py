#!/usr/bin/env bash

echo "delete all resources in namespace monitoring:"
#microk8s kubectl delete -f webserver/
microk8s kubectl delete secret nginx-tls -n adminwebserver
microk8s kubectl delete pv downloads-pv
microk8s kubectl delete namespace adminwebserver

