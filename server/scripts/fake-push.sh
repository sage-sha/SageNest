#!/usr/bin/env bash
set -euo pipefail

FIXTURE="$(dirname "$0")/../fixtures/push.json"

curl -si -X POST http://localhost:3000/webhook \
  -H 'Content-Type: application/json' \
  -H 'X-GitHub-Event: push' \
  --data @"$FIXTURE"
echo
