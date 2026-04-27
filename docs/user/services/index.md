---
intent: manage-services-on-clusterdeployment
audience: platform-engineers
prereqs: existing-clusterdeployment-and-available-servicetemplates
inputs: target-clusterdeployment-and-service-template-selection
outputs: service-lifecycle-management-guidance-for-managed-clusters
related_docs: docs/user/services/understanding-servicetemplates.md, docs/user/services/servicetemplate-parameters.md, docs/user/services/add-service-to-clusterdeployment.md, docs/reference/crds/index.md
last_verified_version: 1.8.0
---

# Deploy Services to a Managed Cluster

At its heart, everything in k0rdent is based on templates that help define Kubernetes objects. For clusters, these are `ClusterTemplate` objects. For applications and services, these are `ServiceTemplate` objects.

You can find numerous useful applications in the [k0rdent Catalog](https://catalog.k0rdent.io/), or you can create them yourself.

- [Understanding ServiceTemplates](understanding-servicetemplates.md)
- [Adding a Service to a ClusterDeployment](add-service-to-clusterdeployment.md)
- [Beach Head Services](beach-head.md)
- [Checking Status](checking-status.md)
- [Remove Beach Head Services](remove-beach-head.md)
- [Pause Beach Head Services Reconciliation](service-pause.md)
- [ServiceTemplate Parameters](servicetemplate-parameters.md)
- [Service Upgrades and ServiceTemplateChain](service-upgrade.md)
