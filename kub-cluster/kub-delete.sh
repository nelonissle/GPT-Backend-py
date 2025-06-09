#!/usr/bin/env bash

echo "delete all pv:"
microk8s kubectl delete pv logs-pv


echo "The following PVs will be deleted:"
microk8s kubectl get pv | awk '$5=="Available"{print $1}'
read -p "Proceed? (y/n): " answer
if [[ "$answer" == "y" ]]; then
  for pv in $(microk8s kubectl get pv --no-headers | awk '$5=="Available"{print $1}'); do
    microk8s kubectl delete pv $pv
  done
fi

echo "The following PVs will be deleted:"
microk8s kubectl get pv | awk '$5=="Released"{print $1}'
read -p "Proceed? (y/n): " answer
if [[ "$answer" == "y" ]]; then
  for pv in $(microk8s kubectl get pv --no-headers | awk '$5=="Released"{print $1}'); do
    microk8s kubectl delete pv $pv
  done
fi

# ask with a prompt if i shall delete pv
ls /var/snap/microk8s/common/default-storage
echo "Do you want to delete pv data? (y/n)"
read answer
if [[ "$answer" == "y" ]]; then
  sudo rm -rf /var/snap/microk8s/common/default-storage/*
fi

echo
echo "delete nat rules:"
sudo iptables -t nat -D PREROUTING 2
sudo iptables -t nat -D PREROUTING 3
sudo iptables -t nat -D PREROUTING 4