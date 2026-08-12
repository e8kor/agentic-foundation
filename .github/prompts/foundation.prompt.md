---
description: Bootstrap the Foundation skill framework and audit consistency.
---

Run a Foundation framework audit and report the state.

1. Read `CORE.md`, `MANIFEST.md`, and `extensions/README.md` to load the
   current contract.
2. Run the validator: `python3 tools/validate_manifest.py --root .`
3. Cross-check every dir in `extensions/*/` has a `plugin.yaml` and a matching
   row in `MANIFEST.md`; flag any drift.
4. Confirm `curator/.usage.json`, `curator/.backup/`, `curator/archived/`, and
   `curator/.traces/` exist.
5. Report: what is valid, what drifted, and any skill/memory that is stale and
   due for archiving.

Follow the `foundation-operator` skill procedure (`core-skills/foundation-operator/SKILL.md`)
if any repair is needed.
