#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_PATH="$SCRIPT_DIR/PDF编辑工具集成版"

if [ ! -x "$APP_PATH" ]; then
  chmod +x "$APP_PATH"
fi

cd "$SCRIPT_DIR"
exec "$APP_PATH" "$@"
