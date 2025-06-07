#!/usr/bin/env bash

echo "delete all pv:"
microk8s kubectl delete pv logs-pv
microk8s kubectl delete pv db-pv

