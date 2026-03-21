#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../backend" || exit 1

echo "Verifying heritage ledger..."
node -e "
const { verifyLedger } = require('./audit');
const result = verifyLedger(process.env.LEDGER_PATH || './heritage_ledger.log');
if (!result.ok) {
  console.error('Ledger verification failed:', result);
  process.exit(1);
}
console.log('Ledger OK. Entries:', result.count);
" || exit 1

echo "Starting AetherOS server..."
node server.js
