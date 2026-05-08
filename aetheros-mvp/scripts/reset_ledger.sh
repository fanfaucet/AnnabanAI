#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../backend" || exit 1
LEDGER_PATH=${LEDGER_PATH:-./heritage_ledger.log}
echo -n "" > "$LEDGER_PATH"
echo "Ledger cleared at $LEDGER_PATH"
