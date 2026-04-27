# Upgrading k0rdent

> IMPORTANT: In some circumstances, upgrades involve additional manual steps. Be sure to check the additional instructions for upgrading to k0rdent [`0.2.0`](upgrade-to-0-2-0.md), [`0.3.0`](upgrade-to-0-3-0.md), [`1.0.0`](upgrade-to-1-0-0.md), [`1.1.1`](upgrade-to-1-1-1.md), or [`1.7.0`](upgrade-to-1-7-0.md).

> NOTE:
> If upgrading from versions of k0rdent
> prior to v1.0.0, upgrade to v1.0.0 first to facilitate the change
> from `alpha` to `beta` APIs.

Upgrading k0rdent involves making upgrades to the `Management` object. To do that, you must have the `Global Admin` role. (For detailed information about k0rdent RBAC roles and permissions, refer to the [RBAC documentation](../access/rbac/index.md).) Follow these steps to upgrade k0rdent:

1. Create a new `Release` object

    Start by creating a `Release` object in the management cluster that points to the desired version. You can see
    available versions at [https://github.com/k0rdent/kcm/releases](https://github.com/k0rdent/kcm/releases).  The actual
    `Release` object includes information on the templates and resources that are available, as well as the version of the
    Kubernetes Cluster API.  For example, the v1.8.0 `Release` object looks like this:

    ```yaml
    apiVersion: k0rdent.mirantis.com/v1beta1
    kind: Release
    metadata:
      name: kcm-1-8-0
      annotations:
        helm.sh/resource-policy: keep
    spec:
      version: 1.8.0
      kcm:
        template: kcm-1-8-0
      capi:
        template: cluster-api-1-8-0
      providers:
        - name: cluster-api-provider-k0sproject-k0smotron
          template: cluster-api-provider-k0sproject-k0smotron-1-8-0
        - name: cluster-api-provider-azure
          template: cluster-api-provider-azure-1-8-0
        - name: cluster-api-provider-vsphere
          template: cluster-api-provider-vsphere-1-8-0
        - name: cluster-api-provider-aws
          template: cluster-api-provider-aws-1-8-0
        - name: cluster-api-provider-openstack
          template: cluster-api-provider-openstack-1-8-0
        - name: cluster-api-provider-docker
          template: cluster-api-provider-docker-1-8-0
        - name: cluster-api-provider-gcp
          template: cluster-api-provider-gcp-1-8-0
        - name: cluster-api-provider-ipam
          template: cluster-api-provider-ipam-1-8-0
        - name: cluster-api-provider-infoblox
          template: cluster-api-provider-infoblox-1-8-0                    
        - name: projectsveltos
          template: projectsveltos-1-8-0
    ```

    Thankfully, you don't have to build these YAML files yourself. Once you've chosen a release, you can go ahead and create the release object by referencing the YAML file online, as in:

    ```bash
    VERSION=v1.8.0
    kubectl create -f https://github.com/k0rdent/kcm/releases/download/${VERSION}/release.yaml
    ```
    ```console { .no-copy }
    release.k0rdent.mirantis.com/kcm-1-8-0 created
    ```

2. List Available `Releases`

    Once you've created the new `Release` you need to update the `Management` object to use it. Start by viewing all available `Release`s:

    ```bash
    kubectl get releases
    ```

    ```console { .no-copy }
    NAME        AGE
    kcm-0-2-0   6d9h
    kcm-1-8-0   12m
    ```

3. Patch the `Management` object with the new `Release`

    Update the `spec.release` field in the `Management` object to point to the new release. Replace `<release-name>` with the name of your desired release:

    ```bash
    RELEASE_NAME=kcm-1-8-0
    kubectl patch managements.k0rdent.mirantis.com kcm --patch "{\"spec\":{\"release\":\"${RELEASE_NAME}\"}}" --type=merge
    ```

4. Verify the Upgrade

    Although the change will be made immediately, it will take some time for k0rdent to update the components it should be
    using. Monitor the readiness of the `Management` object to ensure the upgrade was successful. For example:

    ```bash
    kubectl get managements.k0rdent.mirantis.com kcm
    ```
    ```console { .no-copy }
    NAME   READY   RELEASE     AGE
    kcm    True    kcm-1-8-0   4m34s
    ```
