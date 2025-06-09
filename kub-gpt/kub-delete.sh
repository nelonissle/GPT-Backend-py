#!/usr/bin/env bash

microk8s kubectl get namespaces

microk8s helm3 uninstall gpt --namespace gpt
microk8s kubectl delete namespace gpt

echo "The following PVs will be deleted:"
microk8s kubectl get pv | awk '$5=="Available"{print $1}'
read -p "Proceed? (y/n): " answer
if [[ "$answer" == "y" ]]; then
  for pv in $(microk8s kubectl get pv --no-headers | awk '$5=="Available"{print $1}'); do
    microk8s kubectl delete pv $pv
  done
fi

# ask with a prompt if i shall delete pv
ls /var/snap/microk8s/common/default-storage
echo "Do you want to delete pv data? (y/n)"
read answer
if [[ "$answer" == "y" ]]; then
  sudo rm -rf /var/snap/microk8s/common/default-storage/gpt-*
fi

# ask with a prompt if i shall delete the claim in my pv
#echo "Do you want to delete claim logs? (y/n)"
#read answer
#if [[ "$answer" == "y" ]]; then
#  microk8s kubectl patch pv logs-pv -p '{"spec":{"claimRef": null}}'
#fi
