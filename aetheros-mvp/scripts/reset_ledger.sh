#!/usr/bin/env bash
set -euo pipefail

LEDGER="$(dirname "$0")/../backend/heritage_ledger.log"
: > "$LEDGER"
echo "Ledger reset: $LEDGER"
