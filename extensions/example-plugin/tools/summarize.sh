#!/usr/bin/env bash
# Example contributed tool. Summarize a markdown file's headings.
# Usage: summarize.sh <path-to-md>
set -euo pipefail

file="${1:?usage: summarize.sh <path-to-md>}"
[[ -f "$file" ]] || { echo "not found: $file" >&2; exit 1; }

echo "# $file"
grep -E '^#{1,6} ' "$file" | sed -E 's/^#{1,6} /  - /'
