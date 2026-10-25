#!/bin/sh
# Read-only native DTO replay of explicitly saved synthetic observations.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
cd "$root"
docker build --target build -t tangerine-recurring-observation:local -f services/api/Dockerfile . >&2
docker run --rm --network none -v "$root/data/recurring-errors-20261025:/evidence" \
  -e TANGERINE_RECURRING_OBSERVATION=/evidence --entrypoint go \
  tangerine-recurring-observation:local "$@"
