# KubeVirt

k0rdent can deploy child clusters using KubeVirt. Follow these steps to configure and
deploy KubeVirt clusters:

1. Install k0rdent

    Follow the instructions in [Install k0rdent](../install-k0rdent.md) to create a
    management cluster with k0rdent running.

1. Prepare the KubeVirt Infrastructure Cluster

    Follow the instructions in [KubeVirt Infrastructure Cluster Preparation](../../../appendix/kubevirt-infra.md) to
    prepare your KubeVirt Infrastructure Cluster.

1. `virtctl` CLI (optional)

    If you plan to access KubeVirt VMs directly, [install the `virtctl` CLI](https://kubevirt.io/quickstart_cloud/)
    (see the `Virtctl` section).

1. Create the `Secret` with the base64-encoded KubeVirt Infrastructure Cluster kubeconfig under the `data.kubeconfig`
    key

    Replace `$KUBEVIRT_INFRA_CLUSTER_KUBECONFIG_B64` with the base64-encoded kubeconfig of your KubeVirt Infrastructure
    Cluster.

    ```bash
    cat > kubevirt-kubeconfig-secret.yaml << EOF
    apiVersion: v1
    data:
      kubeconfig: $KUBEVIRT_INFRA_CLUSTER_KUBECONFIG_B64
    kind: Secret
    metadata:
      name: kubevirt-kubeconfig
      namespace: kcm-system
      labels:
        k0rdent.mirantis.com/component: "kcm"
    type: Opaque
    EOF
    ```
    Apply the YAML to your cluster:

    ```bash
    kubectl apply -f kubevirt-kubeconfig-secret.yaml
    ```

1. Create the k0rdent `Credential` object

    Define a `Credential` that references the `Secret` from the previous step.
    Save this as `kubevirt-cred.yaml`.

    Note that `.spec.identityRef.name` must match `.metadata.name` of the `Secret` object created in the previous step.

    ```bash
    cat > kubevirt-cred.yaml << EOF
    apiVersion: k0rdent.mirantis.com/v1beta1
    kind: Credential
    metadata:
      name: kubevirt-cred
      namespace: kcm-system
    spec:
      identityRef:
        apiVersion: v1
        kind: Secret
        name: kubevirt-kubeconfig
        namespace: kcm-system
    EOF
    ```

    Apply the YAML to your cluster:

    ```bash
    kubectl apply -f kubevirt-cred.yaml
    ```

1. Create the `ClusterIdentity` resource template `ConfigMap`

    Create the k0rdent `ClusterIdentity` resource template `ConfigMap`. As in prior steps,
    create a YAML file called `kubevirt-kubeconfig-resource-template.yaml`:

    > NOTE:
    > The `ConfigMap` name must be exactly `$SECRET_NAME-resource-template` (in this case, `kubevirt-kubeconfig-resource-template`). See
    > [naming the template configmap](../../../appendix/appendix-providers.md#naming-the-template-configmap) for details.

    ```bash
    cat > kubevirt-kubeconfig-resource-template.yaml << EOF
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: kubevirt-kubeconfig-resource-template
      namespace: kcm-system
      labels:
        k0rdent.mirantis.com/component: "kcm"
      annotations:
        projectsveltos.io/template: "true"
    EOF
    ```
    The `ConfigMap` only contains metadata and no data fields. This is expected, because we do not need to template
    any objects inside child clusters. You can use this object in the future if the need arises.

    Apply this YAML to your management cluster:

    ```bash
    kubectl apply -f kubevirt-kubeconfig-resource-template.yaml -n kcm-system
    ```

1. Create your first child cluster

    To test the configuration, create a YAML file with the specification of your `ClusterDeployment` and save it as
    `my-kubevirt-cluster-deployment.yaml`.

    You can list the available templates with:

    ```bash
    kubectl get clustertemplate -n kcm-system
    ```
    ```console { .no-copy }
    NAMESPACE    NAME                            VALID
    kcm-system   kubevirt-hosted-cp-1-8-0        true
    kcm-system   kubevirt-standalone-cp-1-8-0    true
    ...
    kcm-system   openstack-hosted-cp-1-8-0       true
    kcm-system   remote-cluster-1-8-0            true
    kcm-system   vsphere-standalone-cp-1-8-0     true
    ```

    A `ClusterDeployment` definition might look like this:

    ```yaml
    apiVersion: k0rdent.mirantis.com/v1beta1
    kind: ClusterDeployment
    metadata:
      name: my-kubevirt-cluster-deployment
      namespace: kcm-system
    spec:
      template: kubevirt-standalone-cp-1-8-0 # name of the clustertemplate
      credential: $CREDENTIAL_NAME
      propagateCredentials: false
      config:
        clusterLabels: {}
        clusterAnnotations: {}
        controlPlaneNumber: 1
        workersNumber: 1
        cluster:
          controlPlaneServiceTemplate:
            spec:
              type: LoadBalancer
        controlPlane:
          dnsConfig:
            nameservers:
            - 8.8.8.8
          cpu:
            model: host-passthrough
        worker:
          dnsConfig:
            nameservers:
            - 8.8.8.8
          cpu:
            model: host-passthrough
    ```

    Apply the YAML to your management cluster:

    ```bash
    kubectl apply -f my-kubevirt-cluster-deployment.yaml
    ```

    This starts the provisioning process, where k0rdent creates Cluster API KubeVirt
    objects in the management cluster and virtual machines in the infrastructure cluster. You can follow the
    provisioning process with:

    ```bash
    kubectl -n kcm-system get clusterdeployment.k0rdent.mirantis.com my-kubevirt-cluster-deployment --watch
    ```

    After the cluster is `Ready`, you can access it via its kubeconfig, just like any other Kubernetes cluster:

    ```bash
    kubectl -n kcm-system get secret my-kubevirt-cluster-deployment-kubeconfig -o jsonpath='{.data.value}' | base64 -d > my-kubevirt-cluster-deployment.kubeconfig
    KUBECONFIG="my-kubevirt-cluster-deployment.kubeconfig" kubectl get pods -A
    ```

1. Cleanup

    To clean up KubeVirt resources, delete the managed cluster by deleting the `ClusterDeployment`:

    ```bash
    kubectl get clusterdeployments -A
    ```
    ```console { .no-copy }
    NAMESPACE    NAME                            READY   STATUS
    kcm-system   my-kubevirt-cluster-deployment   True    Object is ready
    ```
    ```bash
    kubectl delete clusterdeployments my-kubevirt-cluster-deployment -n kcm-system
    ```
    ```console { .no-copy }
    clusterdeployment.k0rdent.mirantis.com "my-kubevirt-cluster-deployment" deleted
    ```
