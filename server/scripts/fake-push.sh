#!/usr/bin/env bash
set -euo pipefail

FIXTURE="$(dirname "$0")/../fixtures/push.json"
ENV_FILE="$(dirname "$0")/../../.env"

# load WEBHOOK_SECRET from .env
set -a
source "$ENV_FILE"
set +a

BODY="$(cat "$FIXTURE")"
SIG="sha256=$(printf '%s' "$BODY" | openssl dgst -sha256 -hmac "$WEBHOOK_SECRET" | awk '{print $2}')"

curl -si -X POST http://localhost:3000/webhook \
  -H 'Content-Type: application/json' \
  -H 'X-GitHub-Event: push' \
  -H "X-Hub-Signature-256: $SIG" \
  --data "$BODY"