#!/bin/bash

NFS_STORE=/srv/nfs/kube/mongo
LINE='$NFS_STORE	*(rw,sync,no_subtree_check,no_root_squash,no_all_squash)'
FILE='/etc/exports'

sudo apt install nfs-kernel-server
sudo mkdir -p $NFS_STORE

grep -qF -- "$LINE" "$FILE" || sudo echo "$LINE" >> "$FILE"

sudo chown nobody:nogroup $NFS_STORE
sudo exportfs -rav
sudo exportfs -v

sudo systemctl daemon-reload
sudo systemctl start nfs-server.service
sudo systemctl restart nfs-server.service
