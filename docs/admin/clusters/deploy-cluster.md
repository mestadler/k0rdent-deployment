# Deploying a Cluster

k0rdent is designed to simplify the process of deploying and managing Kubernetes clusters across various cloud platforms. It does this through the use of `ClusterDeployment` objects, which include all of the information k0rdent needs to know in order to create the cluster you're looking for. This `ClusterDeployment` system relies on predefined templates and credentials.

A cluster deployment typically involves:

1. Setting up credentials for the infrastructure provider (for example, AWS, vSphere).
2. Choosing a template that defines the desired cluster configuration (for example, number of nodes, instance types).
3. Cluster Authentication setup (optional).
4. Submitting the configuration for deployment and monitoring the process.

Follow these steps to deploy a standalone Kubernetes cluster tailored to your specific needs:

1. Create the `Credential` object

    Credentials are essential for k0rdent to communicate with the infrastructure provider (for example, AWS, Azure, vSphere). These credentials enable k0rdent to provision resources such as virtual machines, networking components, and storage.

    `Credential` objects are generally created ahead of time and made available to users, so before you look into creating a
    new one be sure what you're looking for doesn't already exist. You can see all of the existing `Credential` objects by
    querying the management cluster:

    ```bash
    kubectl get credentials --all-namespaces
    ```

    If the `Credential` you need doesn't yet exist, go ahead and create it.

    Start by creating a `Credential` object that includes all required authentication details for your chosen infrastructure provider. Follow the instructions in the [chapter about credential management](../access/credentials/index.md), as well as the specific instructions for your [target infrastructure](../installation/prepare-mgmt-cluster/index.md).

    > NOTE:
    > A `Credential` may optionally specify the `spec.region` field. When set, all `ClusterDeployment` objects that reference
    > this `Credential` will be deployed to the corresponding regional cluster.
    > Learn more in [Creating a Credential in a Region](../regional-clusters/creating-credential-in-region.md).

    > TIP: 
    > Double-check to make sure that your credentials have sufficient permissions to create resources on the target infrastructure.

2. Select a Template

    Templates in k0rdent are predefined configurations that describe how to set up the cluster. Templates include details such as:

    * The number and type of control plane and worker nodes
    * Networking settings
    * Regional deployment preferences

    Templates act as a blueprint for creating a cluster. To see the list of available templates, use the following command:

    ```bash
    kubectl get clustertemplate -n kcm-system
    ```

    ```console { .no-copy }
    NAME                            VALID
    adopted-cluster-1-8-0           true
    aws-eks-1-8-0                   true
    aws-hosted-cp-1-8-0             true
    aws-standalone-cp-1-8-0         true
    azure-aks-1-8-0                 true
    azure-hosted-cp-1-8-0           true
    azure-standalone-cp-1-8-0       true
    docker-hosted-cp-1-8-0          true
    gcp-gke-1-8-0                   true
    gcp-hosted-cp-1-8-0             true
    gcp-standalone-cp-1-8-0         true
    openstack-standalone-cp-1-8-0   true
    remote-cluster-1-8-0            true
    vsphere-hosted-cp-1-8-0         true
    vsphere-standalone-cp-1-8-0     true
    ```

    You can then get information on the actual template by describing it, as in:

    ```bash
    kubectl describe clustertemplate aws-standalone-cp-1-8-0 -n kcm-system
    ```

3. [Optional] Create `ClusterAuthentication` object to configure authentication for the kubernetes cluster.
   For details about the IAM configuration, see [Cluster Identity and Authorization Management](cluster-iam-setup.md).

5. Create a ClusterDeployment YAML Configuration

    The `ClusterDeployment` object is the main configuration file that defines your cluster's specifications. It includes:

    * The template to use
    * The credentials for the infrastructure provider
    * The name of the ClusterAuthentication object with cluster authentication configuration (optional)
    * Optional customizations such as instance types, regions, and networking

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

    You will of course want to replace the placeholders with actual values. (For more information about `dryRun` see [Understanding the Dry Run](../../appendix/appendix-dryrun.md).) For example, this is a simple AWS infrastructure provider `ClusterDeployment`:

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
      dryRun: false
      config:
        clusterLabels: {}
        region: us-west-2
        controlPlane:
          instanceType: t3.small
          rootVolumeSize: 32
        worker:
          instanceType: t3.small
          rootVolumeSize: 32
    ```

    > NOTE
    > * The `.spec.credential` value should match the `.metadata.name` value of a created `Credential` object.
    > * The `.spec.clusterAuth` value should match the `.metadata.name` value of the `ClusterAuthentication` object.
    > For more information about authentication configuration in k0rdent follow
    > [Cluster Identity and Authorization Management](cluster-iam-setup.md).

    > TIP:
    > If automatic cleanup of potentially orphaned *LoadBalancer Services* and *Storage devices* during deletion of
    > the `ClusterDeployment` object is required, set `.spec.cleanupOnDeletion` to `true`.
    > This is a best-effort cleanup: if there is no possibility to acquire a managed cluster's kubeconfig,
    > the cleanup will **not** happen.

6. Apply the Configuration

    Once the `ClusterDeployment` configuration is ready, apply it to the k0rdent management cluster:

    ```bash
    kubectl apply -f clusterdeployment.yaml
    ```

    This step submits your deployment request to k0rdent. If you've set `dryRun` to `true` you can observe what would happen. Otherwise, k0rdent will go ahead and begin provisioning the necessary infrastructure.

7. Verify Deployment Status

    After submitting the configuration, verify that the `ClusterDeployment` object has been created successfully:

    ```bash
    kubectl -n <namespace> get clusterdeployment.kcm <cluster-name> -o=yaml
    ```

    The output shows the current status and any errors.

8. Monitor Provisioning

    k0rdent will now start provisioning resources (for example, VMs and networks) and setting up the cluster. To monitor this process, run:

    ```bash
    kubectl -n <namespace> get cluster <cluster-name> -o=yaml
    ```

    > TIP:  
    > For a detailed view of the provisioning process, use the `clusterctl describe` command (note that this requires the [`clusterctl`](https://github.com/kubernetes-sigs/cluster-api/releases) CLI):

    ```bash
    clusterctl describe cluster <cluster-name> -n <namespace> --show-conditions all
    ```

9. Retrieve the Kubernetes Configuration

    When provisioning is complete, retrieve the kubeconfig file for the new cluster. This file enables you to interact with the cluster using `kubectl`:

    ```bash
    kubectl get secret -n <namespace> <cluster-name>-kubeconfig -o=jsonpath={.data.value} | base64 -d > kubeconfig
    ```

    You can then use this file to access the cluster, as in:

    ```bash
    export KUBECONFIG=kubeconfig
    kubectl get pods -A
    ```

    Store the kubeconfig file securely, as it contains authentication details for accessing the cluster.

