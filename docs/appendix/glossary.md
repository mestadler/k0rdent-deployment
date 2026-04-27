# k0rdent Glossary

This glossary is a collection of terms related to k0rdent. It clarifies some of the unique terms and concepts we use or explains more common ones that may need a little clarity in the way we use them.

## Beach-head Services

We use the term to refer to those Kubernetes services that need to be installed on a Kubernetes cluster to make it actually useful, for example: an ingress controller, CNI, and/or CSI. While from the perspective of how they are deployed they are no different from other Kubernetes services, we define them as distinct from the apps and services deployed as part of the applications.

## AccessManagement (CRD)
A Custom Resource Definition (CRD) in k0rdent used to define and manage access controls. 
It typically includes specifications for `AccessRule` and `TargetNamespace` objects to control the 
distribution of resources such as `ClusterTemplate`, `ServiceTemplate`, and `Credential` objects to 
specific namespaces within managed clusters.

## AccessRules
A component within the `AccessManagement` CRD that specifies which k0rdent 
resources (such as `ClusterTemplateChain`, `Credential`, and `ServiceTemplateChain` objects) are to be 
distributed to a defined set of `TargetNamespaces`.

## Cluster API (CAPI)
CAPI is a Kubernetes project that provides a declarative way to manage the lifecycle of 
Kubernetes clusters. It abstracts the underlying infrastructure, allowing users to 
create, scale, upgrade, and delete clusters using a consistent API. CAPI is extensible 
via providers that offer infrastructure-specific functionality, such as AWS, Azure, and 
vSphere.

## CAPI provider (see also [Infrastructure provider](#infrastructure-provider-see-also-capi-provider))
A CAPI provider is a Kubernetes CAPI extension that allows k0rdent to manage and drive 
the creation of clusters on a specific infrastructure via API calls.

## CAPA
CAPA stands for Cluster API Provider for AWS.

## CAPG
CAPG stands for Cluster API Provider for Google Cloud.

## CAPO
CAPO stands for Cluster API Provider for OpenStack.

## CAPV
CAPV stands for Cluster API Provider for vSphere.

## CAPZ
CAPZ stands for Cluster API Provider for Azure.

## Cloud Controller Manager
Cloud Controller Manager (CCM) is a Kubernetes component that embeds logic to manage a 
specific infrastructure provider.

## Cluster Deployment
A Kubernetes cluster created and managed by k0rdent.

## ClusterDeployment (CRD)
A Custom Resource Definition (CRD) in k0rdent that represents 
the desired state and configuration of a Kubernetes cluster to be created and managed by 
k0rdent. It typically includes details about the infrastructure 
provider, cluster topology, version, and references to other configurations such as 
`ClusterTemplate` or `ServiceTemplate` objects.

## ClusterIdentity
ClusterIdentity is a Kubernetes object that references a Secret object containing 
credentials for a specific infrastructure provider.

## ClusterIPAM (CRD)
A Custom Resource Definition (CRD) in k0rdent responsible 
for defining and managing IP address pools at a broad, cluster-aware level. It serves as 
the central authority or source from which IP address ranges (CIDRs) or specific blocks 
can be allocated for use by various Kubernetes clusters or their internal networks.

## ClusterIPAMClaim (CRD)
A Custom Resource Definition (CRD) in k0rdent that enables 
users or automated processes to request or "claim" specific IP address resources (such as
subnets or blocks of IPs) from a `ClusterIPAM` instance. This mechanism ensures orderly 
allocation of IP addresses to individual Kubernetes clusters or other network-dependent 
components.

## ClusterTemplate (CRD)
A Custom Resource Definition (CRD) in k0rdent that provides 
a reusable blueprint for defining the configuration, components, and characteristics of a 
Kubernetes cluster. `ClusterTemplate` objects are used by k0rdent
to ensure consistency when provisioning or managing multiple clusters.

## ClusterTemplateChain (CRD)
A Custom Resource Definition (CRD) in k0rdent that defines an
ordered sequence or a collection of `ClusterTemplate` objects. This allows for the 
application of multiple layers of cluster configurations in a structured and repeatable 
manner, often used to build up complex cluster environments.

## Credential
A `Credential` is a custom resource (CR) in kcm that supplies k0rdent with the necessary 
credentials to manage a specific infrastructure. The credential object references other 
CRs with infrastructure-specific credentials such as access keys, passwords, 
certificates, etc. This means that a credential is specific to the CAPI provider that 
uses it.

## Declarative approach
We define the declarative approach to cluster management using the Kubernetes principles 
as the process where you define the state you want within custom resource objects and the 
controllers or customer operators ensure that the system moves toward that desired state.

## Distributed Container Management Environment (DCME)
An infrastructure setup focused on managing containerized applications across various, 
often geographically dispersed, locations and platforms. k0rdent 
is designed to provide platform engineers with the tools to build and operate a DCME.

## Dry Run
A feature or operational mode within k0rdent that enables users to 
simulate the outcome of an action, such as deploying or modifying a cluster or service, 
without making any actual changes to the infrastructure. Running a command in `--dry-run` mode 
helps in validating configurations and understanding potential impacts.

## EKS / EKS cluster
Refers to Amazon Elastic Kubernetes Service (EKS), a managed Kubernetes service by AWS. 
k0rdent supports creating and managing EKS clusters, as well
as using EKS to host the management cluster.

## Entra-ID
Microsoft Entra ID (formerly Azure Active Directory) is a cloud-based identity and access 
management service. k0rdent can integrate with Entra-ID for 
authentication purposes.

## Internal Developer Platform (IDP)
A platform built by an organization to provide its developers with self-service capabilities 
for accessing tools, services, and infrastructure required for software development and 
deployment. k0rdent aims to enable platform engineers to compose 
and deliver IDPs.

## IP Address Management (IPAM)
The general concept and practice of planning, tracking, allocating, and managing IP address 
space within a network. In k0rdent, this refers to the systems or 
features, such as `ClusterIPAM` and `ClusterIPAMClaim`, used for managing IP addresses for 
clusters and services.

## k0rdent Cluster Manager (KCM)
Deployment and life-cycle management of Kubernetes clusters, including configuration, 
updates, and other CRUD operations.

## k0rdent CRDs
The collective term for the set of Custom Resource Definitions (CRDs) that are specific 
to k0rdent. These CRDs extend the Kubernetes API to define 
and manage k0rdent-specific resources, configurations, and functionalities, forming the 
core of its declarative management capabilities.

## k0rdent Observability and FinOps (KOF)
Cluster and beach-head services monitoring, events and log management.

## k0rdent State Manager (KSM)
Installation and life-cycle management of deployed services.

## k0s / k0s cluster
Refers to k0s, an open-source, lightweight, and certified Kubernetes distribution. 
k0rdent supports creating and managing k0s clusters,
as well as running the Management Cluster on k0s.

## Hosted Control Plane (HCP)
An HCP is a Kubernetes control plane that runs outside of the clusters it manages. 
Instead of running the control plane components (like the API server, controller 
manager, and etcd) within the same cluster as the worker nodes, the control plane is 
hosted on a separate, often centralized, infrastructure. This approach can provide 
benefits such as easier management, improved security, and better resource utilization, 
as the control plane can be scaled independently of the worker nodes.

## Infrastructure provider (see also [CAPI provider](#capi-provider-see-also-infrastructure-provider))
An infrastructure provider (aka `InfrastructureProvider`) is a Kubernetes custom 
resource (CR) that defines the infrastructure-specific configuration needed for managing 
Kubernetes clusters. It enables Cluster API (CAPI) to provision and manage clusters on 
a specific infrastructure platform (for example, AWS, Azure, VMware, OpenStack, and so on.).

## LocalSourceRef
A defined structure within k0rdent Custom Resource Definitions 
that specifies a local source for configuration data, such as a kustomize manifest stored 
within the management cluster (for example, in a `ConfigMap` or `Secret`).

# Management (CRD)
A Custom Resource Definition (CRD) in k0rdent. While 
"Management Cluster" refers to the Kubernetes cluster where k0rdent 
itself is installed and operates, the `Management` CRD represents a specific 
k0rdent resource type for a core management-related 
configuration or entity within the ecosystem.

## ManagementBackup (CRD)
A Custom Resource Definition (CRD) in k0rdent specifically 
designed for configuring, triggering, and managing backup operations related to the management 
plane components or the configuration of the management cluster itself.

## Multi-Cluster Service
The `MultiClusterService` is a custom resource used to manage services' deployment across multiple clusters.

## Management Cluster
The Kubernetes cluster where k0rdent is installed and from which all other managed 
clusters are managed.

## Okta
An identity and access management (IAM) service. k0rdent can integrate 
with Okta to handle user authentication and authorization for accessing k0rdent 
functionality.

## PluggableProvider (CRD)
A Custom Resource Definition (CRD) in k0rdent that represents a configured 
instance of an external provider (e.g., infrastructure, services). It enables the integration of such 
providers into the k0rdent system in a modular or "pluggable" fashion, specifically 
by adhering to a defined `ProviderInterface`.

## Project Sveltos
An open-source Kubernetes add-on controller that k0rdent, particularly its 
k0rdent State Manager (KSM) component, leverages for managing the deployment and lifecycle of add-ons and 
applications across managed Kubernetes clusters.

## ProviderInterface (CRD)
A Custom Resource Definition (CRD) in k0rdent that defines a standardized 
contract or API structure for how k0rdent interacts with various external 
infrastructure or service providers (for example, cloud platforms or storage systems). This abstraction 
layer enables consistent provider integration and management.

## ProviderTemplate (CRD)
A Custom Resource Definition (CRD) in k0rdent used for creating reusable 
and parameterized templates for the configuration of specific infrastructure providers (such as AWS, 
Azure, GCP). These templates abstract provider-specific details and promote consistency in cluster 
provisioning.

## Release (CRD)
A Custom Resource Definition (CRD) in k0rdent primarily used to define and 
manage aspects of k0rdent's own internal software lifecycle. `Release` plays 
a role in tracking the versions of different components, coordinating updates or rollbacks of the 
k0rdent platform itself on the management cluster, or specifying the 
collection of software artifacts and configurations that constitute a particular internal k0rdent release.

## RemoteSourceSpec
A defined structure within k0rdent Custom Resource Definitions that specifies 
a remote source for configuration data. This can include sources such as  a Git repository or an 
S3-compatible object storage bucket (defined by `bucketName`, `endpoint`, etc.), often used for kustomize 
manifests or Helm charts.

## Role Based Access Control (RBAC)
Role-Based Access Control (RBAC) defines roles, permissions, and rules governing user and system access to 
k0rdent resources and the clusters it manages, ensuring secure and controlled operations.

## Service (definition for deployment)
Within k0rdent's CRDs (for example, as part of `MultiClusterService` or templates), 
this refers to a specific schema or object structure that defines a service to be deployed onto a cluster. 
It typically includes attributes such as the service's name (often the chart release name), the template to 
use, target namespace, Helm values, and `valuesFrom` for sourcing configuration from `ConfigMap` or `Secret`
objects.

## ServiceTemplate (CRD)
A Custom Resource Definition (CRD) in k0rdent that provides a reusable template 
for defining how a specific service, application, or set of Kubernetes resources (such as a database, monitoring 
agent, or custom workload) is deployed and configured on managed Kubernetes clusters.

## ServiceTemplateChain (CRD)
A Custom Resource Definition (CRD) in k0rdent that defines an ordered sequence 
or a collection of `ServiceTemplate` objects. This enables the orchestrated deployment of multiple services 
or applications as a cohesive logical unit onto managed clusters. The `ServiceTemplateChain` also defines
potential upgrade paths.

## TargetNamespaces
A component within the `AccessManagement` CRD that defines the specific Kubernetes namespaces within 
managed clusters where selected k0rdent resources (such as `ClusterTemplate`, `Credential`, and `ServiceTemplate` 
objects defined in an `AccessRule`) will be distributed or made available.

## templateResourceRefs
A structure commonly found within k0rdent CRDs (Custom Resource Definitions) that 
enables a template to reference existing Kubernetes resources (such as `Secret` or `ConfigMap` objects) 
residing in the management cluster. These referenced resources can then be fetched and their data 
injected or used during the instantiation of the k0rdent template for a target cluster or service.