#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

CONFIG_PATH="${1:-$ROOT_DIR/environments/dev/config.env}"
RUN_ID="${2:-$(date -u +%Y%m%dT%H%M%SZ)}"

"$ROOT_DIR/scripts/preflight.sh" "$CONFIG_PATH"
"$ROOT_DIR/scripts/catalog-lock.sh" "$CONFIG_PATH"
"$ROOT_DIR/scripts/deploy.sh" "$CONFIG_PATH"
"$ROOT_DIR/scripts/validate.sh" "$CONFIG_PATH"
"$ROOT_DIR/scripts/smoke.sh" "$CONFIG_PATH"
"$ROOT_DIR/scripts/report.sh" "$CONFIG_PATH" "$RUN_ID"

printf 'Pipeline complete. Run ID: %s\n' "$RUN_ID"
