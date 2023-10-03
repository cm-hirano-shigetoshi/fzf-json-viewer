#!/usr/bin/env bash
set -euo pipefail

if [[ "$1" = "filter" ]]; then
    shift
    SERVER_PORT=$1
    shift
    SELECTED_ITEMS="$(echo "$*" | tr ' ' ',' | perl -pe 's/(.)/sprintf "%%%02X", ord $1/ge')"
    curl "localhost:${SERVER_PORT}?filter='${SELECTED_ITEMS}'"
fi
