---
intent: create-clusterdeployment-from-template
audience: platform-engineers
prereqs: available-credential-and-valid-clustertemplate-in-management-cluster
inputs: credential-reference-template-name-and-clusterdeployment-config-values
outputs: submitted-clusterdeployment-resource-and-provisioning-observability-path
related_docs: docs/reference/template/index.md, docs/reference/crds/index.md, docs/quickstarts/index.md, docs/admin/clusters/deploy-cluster.md
last_verified_version: 1.8.0
---

# Deploying a Cluster

k0rdent simplifies the process of deploying and managing Kubernetes clusters across various cloud platforms through the use of `ClusterDeployment` objects, which include all of the information k0rdent needs to know in order to create the cluster you want. This `ClusterDeployment` system relies on predefined templates and credentials.

A cluster deployment typically involves:

1. Credentials for the infrastructure provider (such as AWS, vSphere, and so on).
2. A template that defines the desired cluster configuration (for example, number of nodes or instance types).
3. Submitting the configuration for deployment and monitoring the process.

Follow these steps to deploy a standalone Kubernetes cluster:

1. Obtain the `Credential` object

    k0rdent needs credentials to communicate with the infrastructure provider (for example, AWS, Azure, or vSphere). These credentials enable k0rdent to provision resources such as virtual machines, networking components, and storage.

    `Credential` objects are generally created ahead of time and made available to users. You can see all of the existing `Credential` objects by querying the management cluster:

    ```bash
    kubectl get credentials -n accounting
    ```

    When you find a `Credential` that looks appropriate, you can get more information by `describe`-ing it, as in:

    ```bash
    kubectl describe credential accounting-cluster-credential -n accounting
    ```

    You'll see the YAML for the `Credential` object, as in:

    ```yaml
    apiVersion: k0rdent.mirantis.com/v1beta1
    kind: Credential
    metadata:
      name: accounting-cluster-credential
      namespace: accounting
    spec:
      description: "Credentials for Accounting AWS account"
      identityRef:
        apiVersion: infrastructure.cluster.x-k8s.io/v1beta2
        kind: AWSClusterStaticIdentity
        name: accountingd-cluster-identity
    ```

    As you can see, the `.spec.description` field gives more information about the `Credential`.

    If the `Credential` you need doesn't yet exist, you can ask your cloud administrator to create it, or you can
    follow the instructions in the [Credential System](../admin/access/credentials/index.md), as well as the specific instructions for your [target infrastructure](../admin/installation/prepare-mgmt-cluster/index.md), to create it yourself.

    > TIP:
    > Double-check to make sure that your credentials have sufficient permissions to create resources on the target infrastructure.

2. Select a Template

    Templates in k0rdent are predefined configurations that describe how to set up the cluster. Templates include details such as:

    * The number and type of control plane and worker nodes.
    * Networking settings.
    * Regional deployment preferences.

    Templates act as a blueprint for creating a cluster. To see the list of available templates, use the following command:

    ```bash
    kubectl get clustertemplate -n kcm-system
    ```

    ```console { .no-copy }
    NAMESPACE    NAME                            VALID
    kcm-system   aws-standalone-cp-1-8-0         true
    kcm-system   azure-standalone-cp-1-8-0       true
    kcm-system   gcp-standalone-cp-1-8-0         true
    ...
    kcm-system   remote-cluster-1-8-0            true
    kcm-system   vsphere-standalone-cp-1-8-0     true
    ```

    You can then get information on the actual template by describing it, as in:

    ```bash
    kubectl describe clustertemplate aws-standalone-cp-1-8-0 -n kcm-system
    ```

3. [Optional] Create `ClusterAuthentication` object to configure authentication for the kubernetes cluster.
   For details about the IAM configuration, see [Cluster Identity and Authorization Management](../admin/clusters/cluster-iam-setup.md).

4. Create a ClusterDeployment YAML Configuration

    Once you have the `Credential` and the `ClusterTemplate` you can create the `ClusterDeployment` object configuration.
    It includes:

    * The template to use.
    * The credentials for the infrastructure provider.
    * Optional customizations such as instance types, regions, and networking.

    Create a `ClusterDeployment` configuration in a YAML file, following this structure:

    ```yaml
    apiVersion: k0rdent.mirantis.com/v1beta1
    kind: ClusterDeployment
    metadata:
      name: <cluster-name>
      namespace: <kcm-system-namespace>
    spec:
      template: <template-name>
      credential: <infrastructure-provider-credential-name>
      clusterAuth: <cluster-authentication-name>
      dryRun: <"true" or "false" (default: "false")>
      cleanupOnDeletion: <"true" or "false" (default: "false")>
      config:
        <cluster-configuration>
    ```

    You will of course want to replace the placeholders with actual values. (For more information about `dryRun` see [Understanding the Dry Run](../appendix/appendix-dryrun.md)) For example, this is a simple AWS infrastructure provider `ClusterDeployment`:

    ```yaml
    apiVersion: k0rdent.mirantis.com/v1beta1
    kind: ClusterDeployment
    metadata:
      name: my-cluster-deployment
      namespace: kcm-system
    spec:
      template: aws-standalone-cp-1-8-0
      credential: aws-credential
      clusterAuth: auth-config-dex
      config:
        clusterLabels: {}
        region: us-west-2
        controlPlane:
          instanceType: t3.small
        worker:
          instanceType: t3.small
    ```

    > NOTE
    > * The `.spec.credential` value should match the `.metadata.name` value of a created `Credential` object.
    > * The `.spec.clusterAuth` value should match the `.metadata.name` value of the `ClusterAuthentication` object.
    > For more information about authentication configuration in k0rdent follow
    > [Cluster Identity and Authorization Management](../admin/clusters/cluster-iam-setup.md).

    > TIP:
    > If automatic cleanup of potentially orphaned *LoadBalancer Services* and *Storage devices* during deletion of
    > the `ClusterDeployment` object is required, set `.spec.cleanupOnDeletion` to `true`.
    > This is a best-effort cleanup: if there is no possibility to acquire a managed cluster's kubeconfig,
    > the cleanup will **not** happen.

5. Apply the Configuration

    Once the `ClusterDeployment` configuration is ready, apply it to the k0rdent management cluster:

    ```bash
    kubectl apply -f clusterdeployment.yaml
    ```

    This step submits your deployment request to k0rdent.

6. Verify Deployment Status

    After submitting the configuration, verify that the `ClusterDeployment` object has been created successfully:

    ```bash
    kubectl -n <namespace> get clusterdeployment.kcm <cluster-name> -o=yaml
    ```

    The output shows the current status and any errors.

7. Monitor Provisioning

    k0rdent will now start provisioning resources (for example, VMs or networks) and setting up the cluster. To monitor this process, run:

    ```bash
    kubectl -n <namespace> get cluster <cluster-name> -o=yaml
    ```

8. Retrieve the Kubernetes Configuration

    When provisioning is complete, you can retrieve the kubeconfig file for the new cluster so you can interact with the cluster using `kubectl`:

    ```bash
    kubectl get secret -n <namespace> <cluster-name>-kubeconfig -o=jsonpath={.data.value} | base64 -d > kubeconfig
    ```

    You can then use this file to access the cluster, as in:

    ```bash
    export KUBECONFIG=kubeconfig
    kubectl get pods -A
    ```

    Store the kubeconfig file securely, as it contains authentication details for accessing the cluster.

## Cleanup

When you're finished you'll want to remove the cluster. Because the cluster is represented by the `ClusterDeployment` object,
deleting the cluster is a simple matter of deleting that object. For example:

```bash
kubectl delete clusterdeployment <cluster-name> -n kcm-system
```

Note that even though the Kubernetes object is deleted immediately, it will take a few minutes for the actual resources to be removed.
