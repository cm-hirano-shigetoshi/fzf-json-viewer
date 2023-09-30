#!/usr/bin/env bash
set -euo pipefail

if [[ "$1" = "filter" ]]; then
    shift
    SERVER_PORT=$1
    shift
    ASTER="$*"
    SELECTED_ITEMS="${ASTER// /,}"
    curl "localhost:${SERVER_PORT}?filter='${SELECTED_ITEMS}'"
fi
