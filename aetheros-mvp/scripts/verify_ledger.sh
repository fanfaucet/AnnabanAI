#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../backend"
node audit_run.js
