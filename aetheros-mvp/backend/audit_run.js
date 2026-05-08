require('dotenv').config();
const path = require('path');
const { verifyLedger } = require('./audit');

const ledgerPath = path.resolve(process.env.LEDGER_PATH || './heritage_ledger.log');
const result = verifyLedger(ledgerPath);

if (!result.ok) {
  console.error('AUDIT FAILED:', result);
  process.exit(1);
}

console.log(`AUDIT OK: ${result.count} entries`);
