---
description: "Audit the Foundation framework: validate manifests, check drift, verify curator state."
# No MCP tools required — runs entirely against local files + the stdlib validator.
tools: []
---

# Audit the Foundation Framework

Verifies that the Foundation skill framework (the repo this extension lives in,
or the root configured in `foundation-config.yml`) is consistent: manifests
valid, no drift between `extensions/` and `MANIFEST.md`, curator state present.

## Prerequisites

1. The framework root exists (default: `.foundation/` in the project, or the
   repo root if running from `hermes-foundation`).
2. Python 3 available (stdlib only — no pip installs).

## User Input

$ARGUMENTS

## Steps

### Step 1: Resolve the framework root

```bash
ROOT="${SPECKIT_FOUNDATION_FRAMEWORK_ROOT:-.foundation}"
[ -d "$ROOT" ] || ROOT="."   # fall back to current dir (repo root)
echo "Auditing framework root: $ROOT"
```

### Step 2: Run the stdlib validator

```bash
cd "$ROOT"
python3 tools/validate_manifest.py --root . || {
  echo "❌ Validator failed — manifest invalid or incompatible."
  exit 1
}
```

### Step 3: Check for drift between extensions/ and MANIFEST.md

```bash
echo "--- extensions present ---"
for d in extensions/*/; do
  [ -f "$d/plugin.yaml" ] && echo "ok plugin.yaml  $d" || echo "MISSING plugin.yaml  $d"
done
echo "--- registered in MANIFEST.md ---"
grep -E '^\| `' MANIFEST.md || echo "(no extension rows found in MANIFEST.md)"
```

Compare the two lists manually. Anything in `extensions/` but missing from
`MANIFEST.md` (or vice versa) is drift — report it and follow the
`foundation-operator` skill to fix.

### Step 4: Verify curator state

```bash
for dir in curator/.usage.json curator/.backup curator/archived curator/.traces memory/episodic; do
  [ -e "$dir" ] && echo "ok   $dir" || echo "MISSING $dir"
done
```

### Step 5: Report

Print a concise report:
- Validator result (pass/fail).
- Any drift between `extensions/` and `MANIFEST.md`.
- Any missing curator/memory scaffolding.

## Configuration Reference

- `framework_root` (default `.foundation`) — where the framework lives.
- Env override: `SPECKIT_FOUNDATION_FRAMEWORK_ROOT`.

## Notes

- This command is read-only: it audits and reports, it does not modify anything.
- For repairs, see `core-skills/foundation-operator/SKILL.md`.
