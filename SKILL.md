---
name: foundation-core
description: "Agentic Foundation framework core: self-management + open extension system. Loads CORE.md (the authoritative spec). Use as the framework entrypoint."
version: 3.1.0
author: Agentic Foundation
license: MIT
metadata:
  foundation:
    core: CORE.md
---

# Agentic Foundation — entry point

This skill is the **boot entry** for the Agentic Foundation framework. The
authoritative spec lives in `CORE.md` in the framework root (repo `.foundation/`
or global `~/.foundation/`); this file simply loads it.

Read, in order:

1. **`CORE.md`** — the framework contract (17 sections): identity, contract,
   directory layout, the five stores, manifest, load policy, extension points,
   plugin schema, hooks, core skills, curation, memory lifecycle, authoring,
   evaluation, versioning, hard rules, and verify.
2. **`MANIFEST.md`** — the installed-extension registry; what is enabled and valid.
3. **`extensions/README.md`** — how to build a plugin (`plugin.yaml` schema,
   contributing skills/tools/hooks/policy/adapters/mcp).

## Quick bootstrap

- Framework root: `FOUNDATION_ROOT` env var, else `~/.foundation/` (global) or
  `.foundation/` in the project.
- After adding/editing a plugin, run `tools/validate_manifest.py` to confirm it
  is valid and compatible; invalid plugins are quarantined, never deleted.
- To expose the same framework to Copilot/Codex (which read `AGENTS.md`, not
  `.claude/skills/`), use the `AGENTS.md` adapter in the framework root.

## Verify

`MANIFEST.md` lists every extension in `extensions/`, each has a valid
`plugin.yaml`, and `tools/validate_manifest.py` exits 0.
