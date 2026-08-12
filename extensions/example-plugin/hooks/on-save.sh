#!/usr/bin/env bash
# Example hook: fired on-save. Warn if a memory/skill file grew huge.
set -uo pipefail

: "${PLUGIN_DIR:?missing PLUGIN_DIR}"
: "${EVENT:?missing EVENT}"

# Optional: read the changed file path if the framework passes it.
changed="${CHANGED_FILE:-}"

if [[ -n "$changed" && -f "$changed" ]]; then
  size=$(wc -c < "$changed")
  if (( size > 20000 )); then
    echo "on-save hook [$EVENT]: $changed is ${size}B — consider pruning." >&2
  fi
fi

# Hooks must never abort the framework.
exit 0
