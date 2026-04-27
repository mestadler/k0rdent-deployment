#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

source "$SCRIPT_DIR/common.sh"

CONFIG_PATH="${1:-$ROOT_DIR/environments/dev/config.env}"
load_config "$CONFIG_PATH"

require_cmd kubectl
require_cmd helm

log "Running preflight checks for context: $KUBECONFIG_CONTEXT"

kubectl config get-contexts "$KUBECONFIG_CONTEXT" >/dev/null
kubectl --context "$KUBECONFIG_CONTEXT" version >/dev/null
kubectl --context "$KUBECONFIG_CONTEXT" get nodes >/dev/null

if [[ -n "${HELM_REGISTRY_HOST:-}" ]]; then
  log "Checking Helm registry login state for $HELM_REGISTRY_HOST"
  helm registry login "$HELM_REGISTRY_HOST" --help >/dev/null
fi

log "Preflight passed"
