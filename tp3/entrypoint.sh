#!/usr/bin/env sh
set -eu
echo "[entrypoint] $(date -u +"%Y-%m-%dT%H:%M:%SZ") - Démarrage de todo-api"
exec "$@"
