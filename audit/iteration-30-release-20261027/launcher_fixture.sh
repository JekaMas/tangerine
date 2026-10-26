#!/bin/sh
# Test network isolation only. Every command uses the actual Docker CLI/engine.
# The downloaded sources, launcher and build contexts remain unmodified.
set -eu
if [ "${1:-}" = compose ] && [ "${2:-}" = --env-file ]; then
 shift
 operator=$2; runtime=$4; source=$6
 shift 6
 exec /usr/local/bin/docker compose --env-file "$operator" --env-file "$runtime" \
  -f "$source" -f /i30/network-override.yaml "$@"
fi
exec /usr/local/bin/docker "$@"
