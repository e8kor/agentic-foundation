---
name: foundation-operator
description: "Maintain the Foundation skill framework: add/update/remove extensions, audit consistency, curate skills, bump versions. Use when operating ON the framework itself."
version: 1.1.0
author: foundation-core
license: MIT
metadata:
  foundation:
    provenance: core
    core: CORE.md
---

# Foundation Operator

This skill's **only purpose** is to keep the Foundation framework consistent:
its manifest, its extensions, its core spec, and its curator state must never
drift out of sync. It is a `provenance: core` skill, so the curator can never
archive or modify it.

Operate against the framework root resolved in this order:
`$FOUNDATION_ROOT` → `~/.foundation/` → `.foundation/` in the project.
The core reference is `CORE.md`; the registry is `MANIFEST.md`.

Read `CORE.md` and `extensions/README.md` before any change so you follow the
current contract.

---

## 1. Audit integrity (do this first, and regularly)

Confirm the framework is consistent before and after any operation.

```bash
ROOT="${FOUNDATION_ROOT:-$HOME/.foundation}"; [ -d "$ROOT" ] || ROOT=".foundation"
cd "$ROOT"
# 1. every extension dir has a plugin.yaml and is registered
for d in extensions/*/; do
  [ -f "$d/plugin.yaml" ] && echo "ok plugin.yaml  $d" || echo "MISSING plugin.yaml  $d"
done
# 2. validator passes (schema + core-version gate)
python3 tools/validate_manifest.py --root .
```

Cross-check `MANIFEST.md` "Installed extensions" against what's actually in
`extensions/`. Every plugin must appear in both. Note drift (see §6).

## 2. Add an extension

```bash
ROOT=...  # as above
mkdir -p "extensions/<plugin>/skills" "extensions/<plugin>/tools" \
         "extensions/<plugin>/hooks" "extensions/<plugin>/memory"
# write extensions/<plugin>/plugin.yaml  (schema: extensions/README.md)
python3 tools/validate_manifest.py --root .        # must pass
```
Then register it in `MANIFEST.md` under "Installed extensions" (name, version,
core range, extension points, enabled, provenance). Run audit again.

## 3. Update an extension (version bump)

- Edit the plugin's files, then bump `version` in its `plugin.yaml` (semver).
- If the plugin no longer targets this core, update `core:`, else the gate will
  quarantine it.
- Re-run `tools/validate_manifest.py --root .`.
- Update the plugin's row in `MANIFEST.md` to the new version and add a
  changelog line under "Changelog".

## 4. Remove / disable an extension

- **Disable** (keep, dormant): set `enabled: false` in `plugin.yaml` and in
  `MANIFEST.md`. The plugin stays discoverable but is not run.
- **Remove** (permanent): **archive, never delete.** Move the dir to
  `curator/archived/` and remove its `MANIFEST.md` row. Keep a backup snapshot in
  `curator/.backup/` first. Rollback must always be possible.

## 5. Add / maintain a skill

- Skills contributed by extensions: put them under
  `extensions/<plugin>/skills/<name>/SKILL.md`.
- Framework-native skills: `core-skills/<name>/SKILL.md` with
  `provenance: core` (curator-immune).
- Every SKILL.md must have frontmatter (`name`, `description`, `version`,
  `provenance`), numbered steps with exact commands, a **Pitfalls** section, and
  a **Verify** section. The description's first ~57 chars must state the trigger.
- Patch a skill immediately when a run shows it is stale or wrong.

## 6. Curate (agent-created skills)

Follow CORE.md §4 stores + §12 lifecycle rules — you are the curator:
- Track usage in `curator/.usage.json` (use_count, view_count, patch_count,
  last_activity_at, state, pinned) after each use.
- Idle for `stale_after_days` → mark stale; idle past `archive_after_days` →
  archive into `curator/archived/`. **Never hard-delete.**
- Back up to `curator/.backup/` before every transition.
- Honor `pinned` (immune) and `provenance` (`core`/`user`/`third-party` →
  archive-only; only `agent` is fully curatable).
- Consolidate overlapping skills into an umbrella only when clearly beneficial;
  archive the originals. Consolidation is off unless the user opts in.
- **Verify before adopting:** a skill is eligible only after ≥2 successful uses
  or a user-correction that worked. Before consolidating, run the umbrella's
  steps against one example from each source skill and confirm the outcome.
- **Trace every event:** write a small file to `curator/.traces/` (what/why/
  before/after/result) for each curation or skill-use action. Plain text, no daemon.

## 7. Manage memory lifecycle (per CORE.md §12)

- New memory entries: write as declarative facts with `@since YYYY-MM-DD` and,
  if relevant, `@retain <days>`.
- Session-end: append a dated entry to `memory/episodic/YYYY-MM-DD.md`.
- On a periodic pass, **consolidate**: promote durable facts from the episodic log
  into `memory/memory.md`, drop transient events, archive raw episodes past their
  retention window.
- **Forget by archiving:** when a fact is superseded, its `@retain` expires, or
  it is unreferenced past `stale_after_days`, move it to `curator/archived/`.
  Never delete. Keep profile `memory/profile.md` stable (no staleness).

## 8. Add / declare an external system (mcp)

- Declare MCP servers in a plugin's `plugin.yaml` under `mcp_servers`
  (name, command, args, env). **Do not bundle or install** the server — the
  framework only declares how to reach it.
- `allowed_tools` in `plugin.yaml` bounds which tools a plugin may use.
- `python3 tools/validate_manifest.py --root .` validates these declarations
  with no dependencies beyond the Python standard library.

## 9. Bump the core version

Adding an extension point = MINOR bump; removing/renaming one = MAJOR bump.
- Edit `version` + `min_core_version` in `MANIFEST.md` and `CORE.md` frontmatter.
- Update each plugin's `core:` range to remain compatible, else it quarantines.
- Add a "Changelog" line in `MANIFEST.md` describing the change.

## Pitfalls

- **Editing CORE.md schema without bumping core version** — silently breaks the
  compatibility gate. Always bump when the contract changes.
- **Registering a plugin without validating** — the manifest and `extensions/`
  drift apart; audit then fails.
- **Deleting instead of archiving** — violates hard rule #1. If a plugin must go,
  it goes to `curator/archived/` with a backup.
- **Ignoring provenance** — the curator may only curate `agent`-created skills.
  Treating `core` skills as curatable will break the framework's own skills.
- **Wrong root** — operating against a repo `.foundation/` when a global
  `~/.foundation/` is the active one (or vice versa). Always resolve
  `$FOUNDATION_ROOT` first.

## Verify

- `python3 tools/validate_manifest.py --root .` exits 0.
- Every dir in `extensions/*/` has a `plugin.yaml` and a matching `MANIFEST.md`
  row; nothing is registered but missing (or present but unregistered).
- `curator/.usage.json`, `curator/.backup/`, and `curator/archived/` exist.
- No skill or plugin was ever hard-deleted; everything archived is restorable.
- The audit in §1 lists no drift before you finish.
