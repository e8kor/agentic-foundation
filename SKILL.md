---
name: foundation-core
description: "Framework core: self-management + open extension system. Loads CORE.md (the authoritative spec). Use as the framework entrypoint."
version: 2.0.0
author: Hermes Agent (ported)
license: MIT
metadata:
  foundation:
    core: CORE.md
---

# Foundation — entry point

This skill is the **boot entry** for the Foundation skill framework. The
authoritative spec lives in `CORE.md` in the framework root (repo `.foundation/`
or global `~/.foundation/`); this file simply loads it.

Read, in order:

1. **`CORE.md`** — the framework contract: directory convention, manifest,
   extension points (skill / memory / tool / hook / policy / adapter), lifecycle,
   versioning, the three self-management stores, and the hard rules.
2. **`MANIFEST.md`** — the installed-extension registry; what is enabled and valid.
3. **`extensions/README.md`** — how to build a plugin (`plugin.yaml` schema,
   contributing skills/tools/hooks/policy/adapters).

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
