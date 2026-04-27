# k0rdent Deployment Plan (kcm + ksm + k0rdent-ui)

This repository-level plan defines how to deploy k0rdent for multicluster management
using agent-driven execution. `kof` is intentionally out of scope for this rollout.

## Scope

- In scope: `kcm`, `ksm`, `catalog`, `k0rdent-ui`
- Out of scope: `kof`
- Artifact preference: OCI Helm charts/images with pinned versions and digests

## Phases

1. Foundation
   - Define environments (`dev`, `stage`, `prod`), naming, registry policy, and secrets handling.
2. Preflight
   - Verify CLI tooling, Kubernetes access, base platform prerequisites, and registry login.
3. Core Install
   - Deploy `kcm` first, then `ksm`.
4. UI Install
   - Deploy `k0rdent-ui` with ingress/TLS and API endpoint connectivity.
5. Validation
   - Validate workloads, APIs, CRDs/webhooks, and run smoke tests for multicluster onboarding.
6. Operate and Upgrade
   - Track drift, define rollback, and codify upgrade workflows.

## Execution Order

Planner -> Preflight -> Catalog Lock -> Deploy kcm -> Deploy ksm -> Deploy k0rdent-ui -> Validate -> Report

## Inputs and Outputs

- Standard input contract: `environment`, `cluster_context`, `version_set`, `artifact_lock`, `policy_profile`
- Standard output contract: `status`, `evidence`, `next_action`, `rollback_hint`, `updated_artifacts`
- Run state path: `state/<run-id>/`

## Definition of Done

- `kcm`, `ksm`, and `k0rdent-ui` are healthy in target environment.
- Artifacts are pinned and recorded.
- Smoke onboarding checks pass.
- Run report and operational notes are captured for audit and handoff.
