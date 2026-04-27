#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

source "$SCRIPT_DIR/common.sh"

CONFIG_PATH="${1:-$ROOT_DIR/environments/dev/config.env}"
load_config "$CONFIG_PATH"

LOCK_PATH="$ROOT_DIR/$LOCK_FILE"
require_file "$LOCK_PATH"

log "Catalog lock file present: $LOCK_PATH"
log "Use this file as the authoritative artifact set for deployment"
