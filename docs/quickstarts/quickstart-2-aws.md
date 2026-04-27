# QuickStart 2 - AWS target environment

In this QuickStart guide, we'll be gathering information and performing preparatory steps to enable k0rdent (running on your management node) to manage clusters on Amazon Web Services (AWS), and we'll deploy our first child cluster.

As noted in the [Guide to QuickStarts](./index.md), you'll need administrative access to an AWS account to complete this step. If you haven't yet created a management node and installed k0rdent, go back to [QuickStart 1 - Management node and cluster](./quickstart-1-mgmt-node-and-cluster.md).

Note that if you have already done one of the other quickstarts, such as our Azure QuickStart ([QuickStart 2 - Azure target environment](./quickstart-2-azure.md)), you can  use the same management cluster, continuing here with steps to add the ability to manage clusters on AWS. The k0rdent management cluster can accommodate multiple provider and credential setups, enabling management of multiple infrastructures. And even if your management node is external to AWS (for example, it could be on an Azure virtual machine), as long as you permit outbound traffic to all IP addresses from the management node, this should work fine. A big benefit of k0rdent is that it provides a single point of control and visibility across multiple clusters on multiple clouds and infrastructures.

> NOTE:
> **CLOUD SECURITY 101**: k0rdent requires _some_ but not _all_ permissions
> to manage AWS via the CAPA (ClusterAPI for AWS) provider.

Because k0rdent doesn't require all permissions, a best practice for using k0rdent with AWS (this pattern is repeated
with other clouds and infrastructures) is to create a new user on your account with the particular permissions it and CAPA require. In this section, we'll create and configure IAM for that user, and perform other steps to make that k0rdent user's credentials accessible to it in the management node.

> NOTE:
> If you're working on a shared AWS account, please ensure that the k0rdent user is not already set up before creating a new one.

Creating a k0rdent user with minimal required permissions is one of several principle-of-least-privilege mechanisms used to help ensure security as organizations work with Kubernetes at progressively greater scales. For more on k0rdent security best practices, please see the [Administrator Guide](../admin/index.md).

## Install the AWS CLI

We'll use the AWS CLI to create and set IAM permissions for the k0rdent user, so we'll install it on our management node:

```bash
sudo apt install unzip
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" 
unzip awscliv2.zip 
sudo ./aws/install
```

## Install clusterawsadm

k0rdent uses Cluster API (CAPI) to marshal clouds and infrastructures. For AWS, this means using the components from the Cluster API Provider AWS (CAPA) project. This QuickStart leverages [`clusterawsadm`](https://cluster-api-aws.sigs.k8s.io/), a CLI tool created by the CAPA project that helps with AWS-specific tasks like IAM role, policy, and credential configuration.

To install `clusterawsadm` on Ubuntu on x86 hardware:

```bash
curl -LO https://github.com/kubernetes-sigs/cluster-api-provider-aws/releases/download/v2.7.1/clusterawsadm-linux-amd64
sudo install -o root -g root -m 0755 clusterawsadm-linux-amd64 /usr/local/bin/clusterawsadm
```

## Export your administrative credentials

You should have these already, preserved somewhere safe. If not, you can visit the AWS webUI (Access Management > Users) and generate new credentials (Access Key ID, Secret Access Key, and Session Token (if using multi-factor authentication)).

Export the credentials to the management node environment:

```bash
export AWS_REGION=EXAMPLE_AWS_REGION
export AWS_ACCESS_KEY_ID=EXAMPLE_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=EXAMPLE_SECRET_ACCESS_KEY
export AWS_SESSION_TOKEN=EXAMPLE_SESSION_TOKEN # Optional. If you are using Multi-Factor or Single Sign On Auth.
```

These credentials will be used both by the AWS CLI (to create your k0rdent user) and by `clusterawsadm` (to create a CloudFormation template used by CAPA within k0rdent).

## Create the k0rdent AWS user

Now we can use the AWS CLI to create a new k0rdent user:

```bash
 aws iam create-user --user-name k0rdentQuickstart
```
```console
{
    "User": {
        "Path": "/",
        "UserName": "k0rdentQuickstart",
        "UserId": "EXAMPLE_USER_ID",
        "Arn": "arn:aws:iam::FAKE_ARN_123:user/k0rdentQuickstart",
        "CreateDate": "2025-01-18T08:15:27+00:00"
    }
}
```

If you don't have permissions to create the user, ask your administrator for assistance. Once the user is created, you won't have to do it again. You can also show them this page to make sure you won't run into any other issues.

## Check for available IPs

Because k0rdent has 3 availablilty zone NAT gateways, each cluster needs 3 public IPs. Unfortunately, the default
`EC2-VPC Elastic IPs` quota per region is 5, so while you likely won't have issues with a first cluster, if you try to deplay a 
second to the same region, you are likely to run into issues.  

You can determine how many elastic IPs are available from the command line:

```bash
LIMIT=$(aws ec2 describe-account-attributes --attribute-names vpc-max-elastic-ips --query 'AccountAttributes[0].AttributeValues[0].AttributeValue' --output text)
USED=$(aws ec2 describe-addresses --query 'Addresses[*].PublicIp' --output text | wc -w)
AVAILABLE=$((LIMIT - USED))
echo "Available Public IPs: $AVAILABLE"
```
```console { .no-copy }
Available Public IPs: 5
```

If you have less than 3 available public IPs, you can request an increase in your quota:

```bash
aws service-quotas request-service-quota-increase \
    --service-code ec2 \
    --quota-code L-0263D0A3 \
    --desired-value 20
```

You can check on the status of your request:

```bash
aws service-quotas list-requested-service-quota-change-history \
    --service-code ec2
```
```console { .no-copy }
{
    "RequestedQuotas": [
        {
            "Id": "EXAMPLE_ACCESS_KEY_ID",
            "ServiceCode": "ec2",
            "ServiceName": "Amazon Elastic Compute Cloud (Amazon EC2)",
            "QuotaCode": "L-0263D0A3",
            "QuotaName": "EC2-VPC Elastic IPs",
            "DesiredValue": 20.0,
            "Status": "PENDING",
            "Created": "2025-02-09T02:27:01.573000-05:00",
            "LastUpdated": "2025-02-09T02:27:01.956000-05:00",
            "Requester": "{\"accountId\":\"EXAMPLE_ACCESS_KEY_ID\",\"callerArn\":\"arn:aws:iam::EXAMPLE_ACCESS_KEY_ID:user/nchase\"}",
            "QuotaArn": "arn:aws:servicequotas:EXAMPLE_AWS_REGION:EXAMPLE_ACCESS_KEY_ID:ec2/L-0263D0A3",
            "GlobalQuota": false,
            "Unit": "None",
            "QuotaRequestedAtLevel": "ACCOUNT"
        }
    ]
}
```

## Configure AWS IAM for k0rdent

Before k0rdent CAPI can manage resources on AWS, you need to use `clusterawsadm` to create a bootstrap CloudFormation stack with additional IAM policies and a service account. You do this under the administrative account credentials you earlier exported to the management node environment:

```bash
clusterawsadm bootstrap iam create-cloudformation-stack
```

## Attach IAM policies to the k0rdent user

Next, we'll attach appropriate policies to the k0rdent user. These are:

* `control-plane.cluster-api-provider-aws.sigs.k8s.io`
* `controllers.cluster-api-provider-aws.sigs.k8s.io`
* `nodes.cluster-api-provider-aws.sigs.k8s.io`
* `controllers-eks.cluster-api-provider-aws.sigs.k8s.io`

We use the AWS CLI to attach them. To do this, you will need to extract the Amazon Resource Name (ARN) for the newly-created user:

```bash
AWS_ARN_ID=$(aws iam get-user --user-name k0rdentQuickstart --query 'User.Arn' --output text | sed -E 's/.*::([0-9]+):.*/\1/')
echo $AWS_ARN_ID
```

 Assemble and execute the following commands to implement the required policies:

```bash
aws iam attach-user-policy --user-name k0rdentQuickstart --policy-arn arn:aws:iam::$AWS_ARN_ID:policy/controllers.cluster-api-provider-aws.sigs.k8s.io
aws iam attach-user-policy --user-name k0rdentQuickstart --policy-arn arn:aws:iam::$AWS_ARN_ID:policy/control-plane.cluster-api-provider-aws.sigs.k8s.io
aws iam attach-user-policy --user-name k0rdentQuickstart --policy-arn arn:aws:iam::$AWS_ARN_ID:policy/nodes.cluster-api-provider-aws.sigs.k8s.io
aws iam attach-user-policy --user-name k0rdentQuickstart --policy-arn arn:aws:iam::$AWS_ARN_ID:policy/controllers-eks.cluster-api-provider-aws.sigs.k8s.io
```

We can check to see that policies were attached to the new user:

```bash
aws iam list-attached-user-policies --user-name k0rdentQuickstart

```
And you'll see output that looks like this (this is non-valid example text):

```console { .no-copy }
{
    "AttachedPolicies": [
        {
            "PolicyName": "controllers-eks.cluster-api-provider-aws.sigs.k8s.io",
            "PolicyArn": "arn:aws:iam::AWS_ARN_ID:policy/controllers-eks.cluster-api-provider-aws.sigs.k8s.io"
        },
        {
            "PolicyName": "controllers.cluster-api-provider-aws.sigs.k8s.io",
            "PolicyArn": "arn:aws:iam::AWS_ARN_ID:policy/controllers.cluster-api-provider-aws.sigs.k8s.io"
        },
        {
            "PolicyName": "control-plane.cluster-api-provider-aws.sigs.k8s.io",
            "PolicyArn": "arn:aws:iam::AWS_ARN_ID:policy/control-plane.cluster-api-provider-aws.sigs.k8s.io"
        },
        {
            "PolicyName": "nodes.cluster-api-provider-aws.sigs.k8s.io",
            "PolicyArn": "arn:aws:iam::AWS_ARN_ID:policy/nodes.cluster-api-provider-aws.sigs.k8s.io"
        }
    ]
}
```

## Create AWS credentials for the k0rdent user

In the AWS IAM Console, you can now create the Access Key ID and Secret Access Key for the k0rdent user and download them. You can also do this via the AWS CLI:

```bash
aws iam create-access-key --user-name k0rdentQuickstart
```

You should see something like this. It's important to save these credentials securely somewhere other than the management node, since the management node may end up being ephemeral. Again, this is non-valid example text:

```console { .no-copy }
{
    "AccessKey": {
        "UserName": "k0rdentQuickstart",
        "AccessKeyId": "EXAMPLE_ACCESS_KEY_ID",
        "Status": "Active",
        "SecretAccessKey": "EXAMPLE_SECRET_ACCESS_KEY",
        "CreateDate": "2025-01-18T08:33:35+00:00"
    }
}
```

<!--
> WARNING:
> You may encounter an issue where EKS machines are not created due to the `ControlPlaneIsStable` preflight check
> failure during EKS cluster deployment. Please follow the
> [instruction](known-issues-eks.md#eks-machines-are-not-created-controlplaneisstable-preflight-check-failed)
> to apply the workaround.
-->

## Create IAM credentials secret on the management cluster

Next, we create a `Secret` containing credentials for the k0rdent user and apply this to the management cluster running k0rdent, in the `kcm-system` namespace. Important: if you use another namespace, k0rdent will be unable to read the credentials. To do this, create the following YAML in a file called `aws-cluster-identity-secret.yaml`:

> NOTE:
> The `Secret` name, in this case, needs to be exactly `aws-cluster-identity-secret`. See [credential secret](../appendix/appendix-providers.md#credential-secret) for  details.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: aws-cluster-identity-secret
  namespace: kcm-system
  labels:
    k0rdent.mirantis.com/component: "kcm"
type: Opaque
stringData:
  AccessKeyID: "EXAMPLE_ACCESS_KEY_ID"
  SecretAccessKey: "EXAMPLE_SECRET_ACCESS_KEY"
```

Remember: the Access Key ID and Secret Access Key are the ones you generated for the k0rdent user, `k0rdentQuickStart`.

Apply this YAML to the management cluster as follows:

```bash
kubectl apply -f aws-cluster-identity-secret.yaml -n kcm-system
```

## Create the AWSClusterStaticIdentity object

Next, we need to create an `AWSClusterStaticIdentity` object that uses the secret.

To do this, create a YAML file named `aws-cluster-identity.yaml` as follows:

```yaml
apiVersion: infrastructure.cluster.x-k8s.io/v1beta2
kind: AWSClusterStaticIdentity
metadata:
  name: aws-cluster-identity
  labels:
    k0rdent.mirantis.com/component: "kcm"
spec:
  secretRef: aws-cluster-identity-secret
  allowedNamespaces: {}
```

Note that the `spec.secretRef` is the same as the `metadata.name` of the secret we just created.

Create the object as follows:

```bash
kubectl apply -f aws-cluster-identity.yaml  -n kcm-system
```

## Create the k0rdent Cluster Manager credential object

Now we create the k0rdent Cluster Manager credential object. As in prior steps, create a YAML file called `aws-cluster-identity-cred.yaml`:

```yaml
apiVersion: k0rdent.mirantis.com/v1beta1
kind: Credential
metadata:
  name: aws-cluster-identity-cred
  namespace: kcm-system
spec:
  description: "Credential Example"
  identityRef:
    apiVersion: infrastructure.cluster.x-k8s.io/v1beta2
    kind: AWSClusterStaticIdentity
    name: aws-cluster-identity
```

Note that `.spec.identityRef.kind` must be `AWSClusterStaticIdentity` and `.spec.identityRef.name` must match the `.metadata.name` of the `AWSClusterStaticIdentity` object.

Now apply this YAML to your management cluster:

```bash
kubectl apply -f aws-cluster-identity-cred.yaml -n kcm-system
```

## Create the k0rdent Cluster Identity resource template ConfigMap

Now we create the k0rdent Cluster Identity resource template `ConfigMap`. As in prior steps, create a YAML file called `aws-cluster-identity-resource-template.yaml`:

> NOTE:
> The `ConfigMap` name, in this case, needs to be exactly `aws-cluster-identity-resource-template`. See [naming the template configmap](../appendix/appendix-providers.md#naming-the-template-configmap) for details.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-cluster-identity-resource-template
  namespace: kcm-system
  labels:
    k0rdent.mirantis.com/component: "kcm"
  annotations:
    projectsveltos.io/template: "true"
```

Note that `ConfigMap` is empty. This is expected, we don't need to template any object inside child cluster(s), but we can use that object in the future if need arises.

Now apply this YAML to your management cluster:

```bash
kubectl apply -f aws-cluster-identity-resource-template.yaml -n kcm-system
```

## List available cluster templates

k0rdent is now fully configured to manage AWS. To create a cluster, begin by listing the available `ClusterTemplate` objects provided with k0rdent:

```bash
kubectl get clustertemplate -n kcm-system
```

You'll see output resembling what's below. Grab the name of the AWS standalone cluster template in its present version (in the below example, that's `aws-standalone-cp-1-8-0`):

```console { .no-copy }
NAMESPACE    NAME                            VALID
kcm-system   aws-standalone-cp-1-8-0         true
kcm-system   aws-hosted-cp-1-8-0             true
kcm-system   aws-eks-1-8-0                   true
...
kcm-system   gcp-standalone-cp-1-8-0         true
kcm-system   openstack-standalone-cp-1-8-0   true
```

## Create your ClusterDeployment

Now, to deploy a cluster, create a YAML file called `my-aws-clusterdeployment1.yaml`. We'll use this to create a `ClusterDeployment` object in k0rdent, representing the deployed cluster. The `ClusterDeployment` identifies for k0rdent the `ClusterTemplate` you want to use for cluster creation, the identity credential object you want to create it under (that of your k0rdent user), plus the region and instance types you want to use to host control plane and worker nodes:

```yaml
apiVersion: k0rdent.mirantis.com/v1beta1
kind: ClusterDeployment
metadata:
  name: my-aws-clusterdeployment1
  namespace: kcm-system
spec:
  template: aws-standalone-cp-1-8-0
  credential: aws-cluster-identity-cred
  config:
    clusterLabels: {}
    region: us-east-2
    controlPlane:
      instanceType: t3.small
      rootVolumeSize: 32
    worker:
      instanceType: t3.small
      rootVolumeSize: 32
```

## Apply the `ClusterDeployment` to deploy the cluster

Finally, we'll apply the `ClusterDeployment` YAML (`my-aws-clusterdeployment1.yaml`) to instruct k0rdent to deploy the cluster:

```bash
kubectl apply -f my-aws-clusterdeployment1.yaml
```

Kubernetes should confirm this:

```console { .no-copy }
clusterdeployment.k0rdent.mirantis.com/my-aws-clusterdeployment1 created
```

There will be a delay as the cluster finishes provisioning. You can watch the provisioning process with the following command:

```bash
kubectl -n kcm-system get clusterdeployment.k0rdent.mirantis.com my-aws-clusterdeployment1 --watch
```

In a short while, you'll see output such as:

```console { .no-copy }
NAME                        READY   STATUS
my-aws-clusterdeployment1   True    ClusterDeployment is ready
```

## Obtain the cluster's kubeconfig

Now you can retrieve the cluster's `kubeconfig`:

```bash
kubectl -n kcm-system get secret my-aws-clusterdeployment1-kubeconfig -o jsonpath='{.data.value}' | base64 -d > my-aws-clusterdeployment1.kubeconfig
```

And you can use the `kubeconfig` to see what's running on the cluster:

```bash
KUBECONFIG="my-aws-clusterdeployment1.kubeconfig" kubectl get pods -A
```

## List child clusters

To verify the presence of the child cluster, list the available `ClusterDeployment` objects:

```bash
kubectl get ClusterDeployments -A
```

You'll see output something like this:

```console { .no-copy }
NAMESPACE    NAME                        READY   STATUS
kcm-system   my-aws-clusterdeployment1   True    ClusterDeployment is ready
```

## Tear down the child cluster

To tear down the child cluster, delete the `ClusterDeployment`:

```bash
kubectl delete ClusterDeployment my-aws-clusterdeployment1 -n kcm-system
```

You'll see confirmation like this:

```console { .no-copy }
clusterdeployment.k0rdent.mirantis.com "my-aws-clusterdeployment1" deleted
```

## Next Steps

Now that you've finished the k0rdent QuickStart, we have some suggestions for what to do next:

Check out the [Administrator Guide](../admin/index.md) ...

* For a more detailed view of k0rdent setup for production
* For details about setting up k0rdent to manage clusters on VMware and OpenStack
* For details about using k0rdent with cloud Kubernetes distros: AWS EKS and Azure AKS

<!--
Or check out the [Demos Repository](https://github.com/k0rdent/demos) for fast, makefile-driven demos of k0rdent's key features.
-->
