---
intent: reference-clustertemplate-predefined-management
audience: platform-engineers
prereqs: k0rdent-management-cluster-with-template-crds
inputs: list-of-installed-predefined-templates-and-template-lifecycle-operation
outputs: controlled-predefined-template-set-in-management-cluster
related_docs: docs/reference/template/index.md, docs/reference/crds/index.md, docs/admin/installation/verify-install.md, docs/user/user-create-cluster.md
last_verified_version: 1.8.0
---

## Remove Templates shipped with k0rdent

If you need to limit the templates that exist in your k0rdent installation, follow the instructions below:

1. Get the list of `ProviderTemplate`, `ClusterTemplate` or `ServiceTemplate` objects shipped with k0rdent. For example,
for `ClusterTemplate` objects, run:

    ```bash
    kubectl get clustertemplates -n kcm-system -l helm.toolkit.fluxcd.io/name=kcm-templates
    ```

    ```console { .no-copy }
    NAMESPACE    NAME                            VALID
    kcm-system   aws-standalone-cp-1-8-0         true
    kcm-system   azure-standalone-cp-1-8-0       true
    ...
    kcm-system   openstack-standalone-cp-1-8-0   true
    kcm-system   vsphere-standalone-cp-1-8-0     true
    ```

2. Remove the template from the list using `kubectl delete`, as in:

    ```bash
    kubectl delete clustertemplate -n kcm-system <template-name>
    ```
