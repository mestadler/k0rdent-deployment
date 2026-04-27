---
intent: deploy-remote-cluster-quickstart
audience: platform-engineers
prereqs: management-cluster-with-k0rdent-and-ssh-accessible-linux-hosts
inputs: remote-host-connectivity-ssh-secret-and-clustertemplate-selection
outputs: remote-clusterdeployment-applied-and-cluster-provisioning-started
related_docs: docs/quickstarts/index.md, docs/quickstarts/quickstart-1-mgmt-node-and-cluster.md, docs/reference/template/template-remote.md, docs/user/user-create-cluster.md
last_verified_version: 1.8.0
---

# QuickStart 2 - Existing infrastructure

In many cases, you will want k0rdent (running on your management node) to deploy a k0s child cluster on existing infrastructure. The remote servers will serve as worker nodes in the cluster, while the control plane components will reside within the management cluster and be managed by k0smotron. By doing this, you maximize your existing hardware and simplify administration costs by decreasing the number of servers required to run your infrastructure.

The remote machines that will be part of the cluster must meet the following prerequisites:

1.	Linux-based operating system; the remote hosts should meet the [k0s system requirements](https://docs.k0sproject.io/stable/system-requirements/)
2.	SSH access enabled for the root user
3.	Internet access
4.	Connectivity between the management cluster and the remote hosts' networks

If you haven't yet created a management node and installed k0rdent, go back to [QuickStart 1 - Management node and cluster](quickstart-1-mgmt-node-and-cluster.md).

Note that if you have already done one of the other quickstarts, such as our AWS QuickStart ([QuickStart 2 - AWS target environment](quickstart-2-aws.md)) or ([QuickStart 2 - Azure target environment](quickstart-2-azure.md)), you can use the same management cluster, continuing here with steps to add the ability to manage remote clusters. The k0rdent management cluster can accommodate multiple provider and credential setups, enabling management of multiple infrastructures. A big benefit of k0rdent is that it provides a single point of control and visibility across multiple clusters on multiple clouds and infrastructures.

Before proceeding, make sure your management cluster meets the following requirements:

1. A [default storage class](https://kubernetes.io/docs/tasks/administer-cluster/change-default-storage-class/) is configured on the management cluster to support Persistent Volumes.
2. If the API server will be exposed as a `LoadBalancer`, ensure the appropriate cloud provider is installed on the management cluster.

## Create a Secret object containing the private SSH key to access remote machines

Create a `Secret` object to securely store the private SSH key, under the key `value`, for accessing all remote machines that will be part of the cluster. Start by setting the following environment variables, for example by adding them to an `.env` file and sourcing it. (Make sure to either update the `KEY_PATH` to point to the keyfile or enter the directly under `PRIVATE_SSH-KEY_B64`.)

```bash
# Setup Environment
KEY_PATH=~/.ssh/id_ed25519
PRIVATE_SSH_KEY_B64=$(cat $KEY_PATH | base64 -w 0)
SECRET_NAME=remote-ssh-key
KCM_SYSTEM_NS=kcm-system
CREDENTIAL_NAME=remote-cred
RESOURCE_TEMPLATE_NAME=remote-ssh-key-resource-template
CLUSTER_DEPLOYMENT_NAME=my-remote-clusterdeployment1
MACHINE_0_ADDRESS=127.0.0.1
MACHINE_1_ADDRESS=127.0.0.2
```

Now create the `remote-ssh-key-secret.yaml` file:

```bash
cat > remote-ssh-key-secret.yaml << EOF
apiVersion: v1
data:
  value: $PRIVATE_SSH_KEY_B64
kind: Secret
metadata:
  name: $SECRET_NAME
  namespace: $KCM_SYSTEM_NS
  labels:
    k0rdent.mirantis.com/component: "kcm"
type: Opaque
EOF
```

Apply the YAML to the k0rdent management cluster:
```bash
kubectl apply -f remote-ssh-key-secret.yaml
```
```console { .no-copy }
secret/remote-ssh-key created
```

## Create the KCM Credential Object

Create a YAML file with the specification of our credential and save it as `remote-cred.yaml`.

Note that `.spec.name` must match `.metadata.name` of the `Secret` object created in the previous step.

```bash
cat > remote-cred.yaml << EOF
apiVersion: k0rdent.mirantis.com/v1beta1
kind: Credential
metadata:
  name: $CREDENTIAL_NAME
  namespace: kcm-system
spec:
  identityRef:
    apiVersion: v1
    kind: Secret
    name: $SECRET_NAME
    namespace: $KCM_SYSTEM_NS
EOF
```

Apply the YAML to your cluster:
```bash
kubectl apply -f remote-cred.yaml
```
```console { .no-copy }
credential.k0rdent.mirantis.com/remote-cred created
```

## Create the Cluster Identity resource template ConfigMap

Now we create the k0rdent `ClusterIdentity` resource template `ConfigMap`. As in prior steps, create a YAML file called `remote-ssh-key-resource-template.yaml`:

> NOTE:
> The `ConfigMap` name, in this case, needs to be exactly `remote-ssh-key-resource-template`. See [naming the template configmap](../appendix/appendix-providers.md#naming-the-template-configmap) for details.

```bash
cat > remote-ssh-key-resource-template.yaml << EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: $RESOURCE_TEMPLATE_NAME
  namespace: $KCM_SYSTEM_NS
  labels:
    k0rdent.mirantis.com/component: "kcm"
  annotations:
    projectsveltos.io/template: "true"
EOF
```
Note that the `ConfigMap` doesn't have any values, only metadata. This is expected, as we don't need to template any object inside child clusters, but we can use that object in the future if the need arises.

Now apply this YAML to your management cluster:

```bash
kubectl apply -f remote-ssh-key-resource-template.yaml -n kcm-system
```

## List available cluster templates

To create a remote cluster, begin by listing the available `ClusterTemplate` objects provided with k0rdent:

```bash
kubectl get clustertemplate -n kcm-system
```

You'll see output resembling the following. Make note of the name of the Remote Cluster template in its present version (in the example below, that's `remote-cluster-1-8-0`):

```console { .no-copy }
NAMESPACE    NAME                            VALID
kcm-system   remote-cluster-1-8-0            true
kcm-system   adopted-cluster-1-8-0           true
...
kcm-system   openstack-standalone-cp-1-8-0   true
kcm-system   vsphere-standalone-cp-1-8-0     true
```

## Create your ClusterDeployment

To deploy a cluster, create a YAML file called `my-remote-clusterdeployment1.yaml`. We'll use this to create a `ClusterDeployment` object representing the deployed cluster. The `ClusterDeployment` identifies for k0rdent the `ClusterTemplate` you want to use for cluster creation, the identity credential object you want to create it under, plus the machines' IP addresses (represented by the placeholder `MACHINE_0_ADDRESS` and `MACHINE_1_ADDRESS` below), the SSH port of the remote machines and the user to use when connecting to remote machines (`root`):

> NOTE:
> The user must have root permissions. 
> Also, the service type should be correctly configured. If using the `LoadBalancer` service type, ensure the appropriate cloud provider is installed on the management cluster.
> For other service types (such as `ClusterIP` or `NodePort`), verify that the management cluster network is accessible from the host machines to allow virtual machines to connect to the API server.

```bash
cat > my-remote-clusterdeployment1.yaml << EOF
apiVersion: k0rdent.mirantis.com/v1beta1
kind: ClusterDeployment
metadata:
  name: $CLUSTER_DEPLOYMENT_NAME
  namespace: $KCM_SYSTEM_NS
spec:
  template: remote-cluster-1-8-0 # name of the clustertemplate
  credential: remote-cred
  propagateCredentials: false
  config:
    k0smotron:
      service:
        type: LoadBalancer
    machines:
    - address: $MACHINE_0_ADDRESS
      user: root # The user must have root permissions 
      port: 22
    - address: $MACHINE_1_ADDRESS
      user: root # The user must have root permissions 
      port: 22
EOF
```

## Apply the ClusterDeployment to deploy the management cluster

Finally, we'll apply the `ClusterDeployment` YAML (`my-remote-clusterdeployment1.yaml`) to instruct k0rdent to deploy the cluster:

```bash
kubectl apply -f my-remote-clusterdeployment1.yaml
```

Kubernetes should confirm the creation:

```console { .no-copy }
clusterdeployment.k0rdent.mirantis.com/my-remote-clusterdeployment1 created
```

There will be a delay as the cluster finishes provisioning. Follow the provisioning process with the following command:

```bash
kubectl -n kcm-system get clusters.cluster.x-k8s.io my-remote-clusterdeployment1 --watch
```

To verify that the remote machines were successfuly provisioned, run:

```bash
kubectl -n kcm-system get remotemachines.infrastructure.cluster.x-k8s.io -l helm.toolkit.fluxcd.io/name=my-remote-clusterdeployment1 -o=jsonpath={.items[*].status}
```

If the machines were provisioned, the output of this command will be similar to:

```console { .no-copy }
{"ready":true}{"ready":true}
```

If there is any error, the output will contain an error message.

## Obtain the cluster's kubeconfig

Now you can retrieve the cluster's kubeconfig:

```bash
kubectl -n kcm-system get secret my-remote-clusterdeployment1-kubeconfig -o jsonpath='{.data.value}' | base64 -d > my-remote-clusterdeployment1-kubeconfig.kubeconfig
```

And you can use the kubeconfig to see what's running on the cluster:

```bash
KUBECONFIG="my-remote-clusterdeployment1-kubeconfig.kubeconfig" kubectl get pods -A
```

## List child clusters

To verify the presence of the child cluster, list the available `ClusterDeployment` objects on the management cluster:

```bash
kubectl get ClusterDeployments -A
```
```console { .no-copy }
NAMESPACE    NAME                          READY   STATUS
kcm-system   my-remote-clusterdeployment1   True    ClusterDeployment is ready
```

## Tear down the child cluster

To tear down the child cluster, delete the `ClusterDeployment` from the management cluster:

```bash
kubectl delete ClusterDeployment my-remote-clusterdeployment1 -n kcm-system
```
```console { .no-copy }
clusterdeployment.k0rdent.mirantis.com "my-remote-clusterdeployment1" deleted
```

## Next Steps

Now that you've finished the QuickStart, we have some suggestions for what to do next:

Check out the [Administrator Guide](../admin/index.md) ...

* For a more detailed view of k0rdent setup for production
* For details about setting up k0rdent to manage clusters on VMware and OpenStack
* For details about using k0rdent with cloud Kubernetes distros such as AWS EKS and Azure AKS
