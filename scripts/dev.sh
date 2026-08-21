#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

case "${1:-}" in
  frontend)
    cd client && npm run dev
    ;;
  backend)
    cd server
    [ -d .venv ] || { python3 -m venv .venv && .venv/bin/pip install -r requirements.txt; }
    .venv/bin/uvicorn main:app --host 0.0.0.0 --port 3000 --reload
    ;;
  traefik)
    docker compose up -d
    ;;
  start)
    docker compose up -d
    [ -d server/.venv ] || { python3 -m venv server/.venv && server/.venv/bin/pip install -r server/requirements.txt; }
    trap 'kill 0' EXIT
    (cd server && .venv/bin/uvicorn main:app --host 0.0.0.0 --port 3000 --reload) &
    (cd client && npm run dev) &
    wait
    ;;
  stop)
    docker compose down
    ;;
  fake-push)
    ./server/scripts/fake-push.sh
    ;;
  *)
    echo "usage: ./scripts/dev.sh start | stop | frontend | backend | traefik | fake-push"
    exit 1
    ;;
esac
