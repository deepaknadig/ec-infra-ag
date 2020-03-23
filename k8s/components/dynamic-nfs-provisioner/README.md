# Dynamic NFS Provisioner for Kubernetes

## Install

To install the dynamic NFS provisioner:

First, update the namespace in `nfs-namespace.yaml`, `rbac.yaml` and `deployment.yaml` (or `deployment-arm.yaml`) files.
Change the namespace to the desired name, e.g., `name: nfs-provisioner`. Update the settings in the `deployment.yaml` file to point to the correct server and NFS mount path. Install the configs using:

```bash
kubectl apply -f nfs-namespace.yaml
kubectl apply -f rbac.yaml
kubectl apply -f class.yaml
```

For AMD64 Architecture:

```bash
kubectl apply -f deployment.yaml
```

For ARM64 Architecture:
```bash
kubectl apply -f deployment-arm.yaml
```

## Test

Test using the files in the `test` directory:

```bash
kubectl apply -f test-claim.yaml -f test-pod.yaml
```

This should create the persistent volume and associated claims automatically, and creates a `SUCCESS` file in the NFS store mount path.

Delete the test:

```bash
kubectl delete -f test-claim.yaml -f test-pod.yaml
```
