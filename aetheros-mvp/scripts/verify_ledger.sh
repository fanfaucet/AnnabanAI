#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../backend" || exit 1
node -e "
const { verifyLedger } = require('./audit');
const result = verifyLedger(process.env.LEDGER_PATH || './heritage_ledger.log');
console.log(result.ok ? 'Ledger OK ✅' : 'Ledger INVALID ❌', result);
"
