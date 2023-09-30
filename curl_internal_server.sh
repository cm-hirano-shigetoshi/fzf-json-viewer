#!/usr/bin/env bash
set -euo pipefail

if [[ "$1" = "selected" ]]; then
    shift
    SERVER_PORT=$1
    shift
    ASTER="$*"
    SELECTED_ITEMS="${ASTER// /,}"
    curl "localhost:${SERVER_PORT}?selected='${SELECTED_ITEMS}'"
fi
