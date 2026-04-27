#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

source "$SCRIPT_DIR/common.sh"

CONFIG_PATH="${1:-$ROOT_DIR/environments/dev/config.env}"
load_config "$CONFIG_PATH"

require_cmd kubectl
require_cmd helm

log "Deploying k0rdent components (kof excluded)"

if is_enabled "${ENABLE_KCM:-true}"; then
  ensure_namespace "$KCM_NAMESPACE"
  helm upgrade --install "$KCM_RELEASE" "$KCM_CHART" \
    --kube-context "$KUBECONFIG_CONTEXT" \
    --namespace "$KCM_NAMESPACE" \
    --version "$KCM_VERSION" \
    -f "$ROOT_DIR/$VALUES_DIR/kcm.yaml"
fi

if is_enabled "${ENABLE_KSM:-true}"; then
  ensure_namespace "$KSM_NAMESPACE"
  helm upgrade --install "$KSM_RELEASE" "$KSM_CHART" \
    --kube-context "$KUBECONFIG_CONTEXT" \
    --namespace "$KSM_NAMESPACE" \
    --version "$KSM_VERSION" \
    -f "$ROOT_DIR/$VALUES_DIR/ksm.yaml"
fi

if is_enabled "${ENABLE_K0RDENT_UI:-true}"; then
  ensure_namespace "$K0RDENT_UI_NAMESPACE"
  helm upgrade --install "$K0RDENT_UI_RELEASE" "$K0RDENT_UI_CHART" \
    --kube-context "$KUBECONFIG_CONTEXT" \
    --namespace "$K0RDENT_UI_NAMESPACE" \
    --version "$K0RDENT_UI_VERSION" \
    -f "$ROOT_DIR/$VALUES_DIR/k0rdent-ui.yaml"
fi

log "Deploy completed"
