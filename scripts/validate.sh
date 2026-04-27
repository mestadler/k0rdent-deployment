#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

source "$SCRIPT_DIR/common.sh"

CONFIG_PATH="${1:-$ROOT_DIR/environments/dev/config.env}"
load_config "$CONFIG_PATH"

require_cmd kubectl

log "Validating rollout status"

if is_enabled "${ENABLE_KCM:-true}"; then
  kubectl --context "$KUBECONFIG_CONTEXT" -n "$KCM_NAMESPACE" rollout status deployment "$KCM_DEPLOYMENT" --timeout=180s
fi

if is_enabled "${ENABLE_KSM:-true}"; then
  kubectl --context "$KUBECONFIG_CONTEXT" -n "$KSM_NAMESPACE" rollout status deployment "$KSM_DEPLOYMENT" --timeout=180s
fi

if is_enabled "${ENABLE_K0RDENT_UI:-true}"; then
  kubectl --context "$KUBECONFIG_CONTEXT" -n "$K0RDENT_UI_NAMESPACE" rollout status deployment "$K0RDENT_UI_DEPLOYMENT" --timeout=180s
fi

log "Validation passed"
