#!/bin/bash

NFS_STORE="/srv/nfs/kube"
LINE="$NFS_STORE	*(rw,sync,no_subtree_check,no_root_squash,no_all_squash)"
FILE="/etc/exports"

sudo apt install nfs-kernel-server


if [ ! -d $NFS_STORE ]; then
    printf '%s\n' --------------------
    printf "Creating directories...\n"
    printf '%s\n' --------------------
    sudo mkdir -p $NFS_STORE
    ls -R /srv
    printf '%s\n' --------------------
    printf "Directories created.\n"
    printf '%s\n' --------------------
fi

printf '%s\n' --------------------
printf "Configuring NFS service...\n"
printf '%s\n' --------------------
grep -qF -- "$LINE" "$FILE" || echo $LINE | sudo tee -a $FILE
sudo chown nobody:nogroup $NFS_STORE
sudo exportfs -rav
sudo exportfs -v
printf '%s\n' --------------------
printf "Done.\n"
printf '%s\n' --------------------

printf '%s\n' --------------------
printf "Starting NFS service...\n"
printf '%s\n' --------------------
sudo systemctl daemon-reload
sudo systemctl enable rpcbind.service
sudo systemctl enable nfs-kernel-server
sudo systemctl restart nfs-kernel-server.service
sudo systemctl status nfs-kernel-server.service
printf '%s\n' --------------------
printf "Done.\n"
printf '%s\n' --------------------