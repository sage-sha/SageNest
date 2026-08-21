#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

case "${1:-}" in
  frontend)
    cd client && npm run dev
    ;;
  backend)
    cd server && cargo run
    ;;
  traefik)
    docker compose up -d
    ;;
  start)
    docker compose up -d
    trap 'kill 0' EXIT
    (cd server && cargo run) &
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
