# Agent Shadow Report - 2026-04-27

## Summary

| Metric | Value |
|---|---:|
| Total cases | 30 |
| Top-1 acceptable | 30/30 (100.0%) |
| Low confidence (<4.5) | 0 |
| Out-of-scope matches | 0 |
| Missing route IDs | 0 |

## Category Breakdown

| Area | Cases | Acceptable Top-1 | % |
|---|---:|---:|---:|
| api | 1 | 1 | 100.0 |
| authentication | 2 | 2 | 100.0 |
| crd | 3 | 3 | 100.0 |
| deployment | 1 | 1 | 100.0 |
| installation | 2 | 2 | 100.0 |
| quickstart | 1 | 1 | 100.0 |
| quickstart-aws | 1 | 1 | 100.0 |
| quickstart-azure | 1 | 1 | 100.0 |
| quickstart-gcp | 1 | 1 | 100.0 |
| quickstart-kubevirt | 1 | 1 | 100.0 |
| quickstart-openstack | 1 | 1 | 100.0 |
| quickstart-remote | 1 | 1 | 100.0 |
| service-templates | 2 | 2 | 100.0 |
| services | 3 | 3 | 100.0 |
| templates | 3 | 3 | 100.0 |
| troubleshooting | 2 | 2 | 100.0 |
| upgrade | 1 | 1 | 100.0 |
| user-guide | 1 | 1 | 100.0 |
| validation | 2 | 2 | 100.0 |

## Detailed Results

| # | Query | Expected Area | Top Route | Confidence | Acceptable | Alternative Used |
|---:|---|---|---|---:|---|---|
| 1 | how do i install this platform | installation | install-k0rdent | 12.528 | True | False |
| 2 | what command installs kcm | installation | install-k0rdent | 7.453 | True | False |
| 3 | install checks after helm | validation | verify-k0rdent-install | 13.589 | True | False |
| 4 | pods in kcm-system are not all ready | validation | verify-k0rdent-install | 12.464 | True | False |
| 5 | bootstrap local management cluster quickly | quickstart | quickstart-management-cluster | 12.903 | True | False |
| 6 | run deployment scripts for dev environment | deployment | deploy-workflow-dev | 11.315 | True | False |
| 7 | i need the aws child cluster quickstart | quickstart-aws | quickstart-aws | 13.535 | True | False |
| 8 | aks clusterdeployment example | quickstart-azure | quickstart-azure | 12.727 | True | False |
| 9 | gke quickstart steps | quickstart-gcp | quickstart-gcp | 13.258 | True | False |
| 10 | openstack child cluster walkthrough | quickstart-openstack | quickstart-openstack | 6.936 | True | False |
| 11 | remote cluster onboarding quickstart | quickstart-remote | quickstart-remote | 13.052 | True | False |
| 12 | kubevirt workload cluster quickstart | quickstart-kubevirt | quickstart-kubevirt | 15.025 | True | False |
| 13 | cluster template yaml shape | templates | cluster-template-format | 16.193 | True | False |
| 14 | where is clustertemplate schema documented | templates | cluster-template-format | 14.947 | True | False |
| 15 | provider template list by cloud | templates | template-reference | 12.091 | True | False |
| 16 | service template format and examples | service-templates | service-template-format | 9.443 | True | False |
| 17 | servicetemplate parameters reference | service-templates | service-template-format | 9.597 | True | False |
| 18 | clusterdeployment crd fields | crd | user-create-cluster | 9.687 | True | True |
| 19 | servicetemplate crd spec | crd | service-template-format | 10.163 | True | True |
| 20 | show me all k0rdent crds | crd | crd-reference | 12.383 | True | False |
| 21 | create clusterdeployment from template | user-guide | user-create-cluster | 11.874 | True | False |
| 22 | how to attach services to a clusterdeployment | services | services-management | 13.949 | True | False |
| 23 | upgrade a deployed service | services | services-management | 12.969 | True | False |
| 24 | what is multiclusterservice | services | services-management | 8.614 | True | False |
| 25 | configure oidc authentication for management cluster | authentication | configure-authentication | 11.619 | True | False |
| 26 | okta auth setup steps | authentication | configure-authentication | 7.162 | True | False |
| 27 | how to upgrade k0rdent from current version | upgrade | upgrade-k0rdent | 12.060 | True | False |
| 28 | event troubleshooting commands | troubleshooting | troubleshoot-events | 5.315 | True | False |
| 29 | something is failing and i need diagnostics | troubleshooting | troubleshoot-general | 9.330 | True | False |
| 30 | where is the api spec for k0rdent | api | api-reference | 10.640 | True | False |

## Suggested Tuning Actions

- No tuning actions suggested for this run.
