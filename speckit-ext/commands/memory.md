---
description: "Record a durable memory fact (with @since tag) or read the memory store."
tools: []
---

# Foundation Memory

Manage the Foundation semantic memory store (`memory/memory.md`) — the durable
facts the agent remembers across sessions.

## User Input

$ARGUMENTS

Two forms:
- `read` — print the current memory store.
- `save <fact> [@since YYYY-MM-DD]` — append a declarative fact. If no date
  given, use today.

## Steps

### Step 1: Resolve the memory file

```bash
ROOT="${SPECKIT_FOUNDATION_FRAMEWORK_ROOT:-.foundation}"
[ -d "$ROOT" ] || ROOT="."
MEMFILE="$ROOT/memory/memory.md"
```

### Step 2: read or save

```bash
if [ "$1" = "read" ]; then
  echo "=== Memory store ($MEMFILE) ==="
  cat "$MEMFILE" 2>/dev/null || echo "(empty or missing)"
  exit 0
fi

if [ "$1" = "save" ]; then
  shift
  FACT="$*"
  # optional @since date
  SINCE=""
  if [[ "$FACT" == *@since* ]]; then
    SINCE=$(echo "$FACT" | sed -n 's/.*@since \([0-9-]*\).*/\1/p')
  fi
  if [ -z "$SINCE" ]; then
    SINCE=$(date +%Y-%m-%d)
  fi
  # strip any trailing @since from the fact text
  FACT=$(echo "$FACT" | sed 's/ *@since [0-9-]*//')

  mkdir -p "$(dirname "$MEMFILE")"
  {
    echo "- $FACT  (@since $SINCE)"
  } >> "$MEMFILE"
  echo "Saved: - $FACT (@since $SINCE)"
  exit 0
fi

echo "Usage: $0 read | save <fact> [@since YYYY-MM-DD]"
exit 1
```

### Step 3: Verify

```bash
tail -3 "$MEMFILE"
```

Confirm the fact was appended with its `@since` provenance tag.

## Configuration Reference

- `framework_root` (default `.foundation`).
- Env override: `SPECKIT_FOUNDATION_FRAMEWORK_ROOT`.

## Notes

- Write declarative facts, not directives ("The build uses uv" ✓ / "Always use
  uv" ✗).
- Never store task progress, PR numbers, or SHAs (per CORE.md §11).
