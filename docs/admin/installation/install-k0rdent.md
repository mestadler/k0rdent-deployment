---
intent: install-k0rdent-on-management-cluster
audience: platform-engineers
prereqs: reachable-kubernetes-cluster-and-helm
inputs: cluster-context-namespace-and-target-version
outputs: deployed-kcm-release-in-kcm-system
related_docs: ../index.md, verify-install.md, ../../release-notes/index.md
last_verified_version: 1.8.0
---

# Install k0rdent

This section assumes that you already have a kubernetes cluster installed. If you need to setup a cluster you can follow the [Create and prepare a Kubernetes cluster with k0s](./create-mgmt-clusters/mgmt-create-k0s-single.md) to create a test cluster, or [Create and prepare a production grade Kubernetes cluster with EKS](./create-mgmt-clusters/mgmt-create-eks-multi.md) to create something more substantial. 

The actual management cluster is a Kubernetes cluster with the k0rdent application installed. The simplest way to install k0rdent is through its Helm chart. You can find current versions in the [release notes](../../release-notes/index.md), and from there you can deploy the Helm chart, as in:

```bash
helm install kcm oci://ghcr.io/k0rdent/kcm/charts/kcm --version 1.8.0 -n kcm-system --create-namespace
```
```console { .no-copy }
Pulled: ghcr.io/k0rdent/kcm/charts/kcm:1.8.0
Digest: sha256:129ac55104c4dc34b44e1f6a8440312f49e3012fef4c63c03384e8954bcf4bcd
NAME: kcm
LAST DEPLOYED: 2026-04-17T00:00:00Z
NAMESPACE: kcm-system
STATUS: deployed
REVISION: 1
TEST SUITE: None
```

> NOTE:
> Make sure to specify the correct release version number.

The helm chart deploys the KCM operator and prepares the environment, and KCM then proceeds to deploy the various subcomponents, including CAPI. The entire process takes a few minutes.

## Cleanup: Uninstall k0rdent

And of course when you need to clean up, you can use helm as well. Follow these steps:

1. Remove any `ClusterDeployment` objects in the cluster.

2. Delete the `Management` object:

    ```bash
    kubectl delete management.k0rdent kcm
    ```

3. Remove the kcm Helm release:

    ```bash
    helm uninstall kcm -n kcm-system
    ```

4. Finally, remove the kcm-system namespace:

    ```bash
    kubectl delete ns kcm-system
    ```
