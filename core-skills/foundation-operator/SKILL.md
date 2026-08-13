---
name: foundation-operator
description: "Operate on the Agentic Foundation framework: audit, extend, and improve every edge (adapters, stores, extensions, spec-kit packaging, curator, tooling). Use when modifying the framework itself."
version: 2.1.0
author: foundation-core
license: MIT
metadata:
  foundation:
    provenance: core
    core: CORE.md
---

# Foundation Operator

This skill's **only purpose** is to keep the Agentic Foundation framework
consistent and extensible across every one of its **edges** — the boundaries
where the core connects to the outside world. It is a `provenance: core` skill,
so the curator can never archive or modify it.

Operate against the framework root resolved in this order:
`$FOUNDATION_ROOT` → `~/.foundation/` → `.foundation/` in the project.
The core reference is `CORE.md` (the 17-section spec); the registry is
`MANIFEST.md`.

**Read `CORE.md` and `extensions/README.md` before any change** so you follow
the current contract.

---

## The framework's edges

The core has six edges. Every operation in this skill is "improve or extend an
edge." Know them so you never leave one inconsistent:

| Edge | What it is | Lives at | Extends via |
|------|-----------|----------|-------------|
| **E1 · Adapters** | How the framework surfaces to other agents | `AGENTS.md`, `SKILL.md`, `.github/copilot-instructions.md`, `.github/prompts/` | new/updated adapter files |
| **E2 · Extension system** | How plugins plug in | `extensions/`, `MANIFEST.md`, `extensions/README.md` | new plugins, `plugin.yaml`, extension points (§7) |
| **E3 · Spec-kit packaging** | How the framework ships as a spec-kit extension | `speckit-ext/`, `.github/workflows/speckit-extension.yml` | commands, manifest, CI |
| **E4 · Stores** | The five durable stores | `memory/`, `learnings/`, `core-skills/` | new store types, new core skills |
| **E5 · Curator** | Safe lifecycle maintenance | `curator/` | policy, traces, backup rules |
| **E6 · Tooling** | The validator & scripts | `tools/` | `validate_manifest.py` |

---

## 1. Audit integrity (do this first, and regularly)

Confirm every edge is consistent before and after any operation.

```bash
ROOT="${FOUNDATION_ROOT:-$HOME/.foundation}"; [ -d "$ROOT" ] || ROOT=".foundation"
cd "$ROOT"
# E1: every extension dir has a plugin.yaml and is registered
for d in extensions/*/; do
  [ -f "$d/plugin.yaml" ] && echo "ok plugin.yaml  $d" || echo "MISSING plugin.yaml  $d"
done
# E6: validator passes (schema + core-version gate)
python3 tools/validate_manifest.py --root .
```

Cross-check `MANIFEST.md` "Installed extensions" against what's actually in
`extensions/`. Every plugin must appear in both. Also verify:
- **E1:** adapters still reference the current core version and store count.
- **E3:** `speckit-ext/extension.yml` version matches its `commands/` files.
- **E5:** `curator/` scaffolding (`.usage.json`, `.backup/`, `.traces/`,
  `archived/`) all present.

Note any drift (see §7).

---

## 2. Improve / extend an adapter (E1)

Adapters translate the framework into another agent's native format. Keep them
in sync with CORE.md — the adapter's store list, version, and section refs must
match.

- **Copilot / Codex:** `AGENTS.md` (repo) or `.github/copilot-instructions.md`
  (global). Body only, no YAML frontmatter.
- **Claude Code / Hermes:** `SKILL.md` — the boot entry that loads `CORE.md`.
- **Slash command:** `.github/prompts/foundation.prompt.md` — a `/foundation`
  command that runs the audit.

**To improve:** after any CORE.md change, propagate to every adapter:
- Store count (currently **five**): memory, profile, episodic, learnings, skills.
- Core version (currently **3.0.0**).
- Any hard rule or load-policy change.

**Verify:** every adapter's "stores" list matches CORE.md §5; versions match.

---

## 3. Improve / extend the extension system (E2)

### Add an extension
```bash
ROOT=...  # as above
mkdir -p "extensions/<plugin>/skills" "extensions/<plugin>/tools" \
         "extensions/<plugin>/hooks" "extensions/<plugin>/memory"
# write extensions/<plugin>/plugin.yaml  (schema: extensions/README.md, CORE.md §9)
python3 tools/validate_manifest.py --root .        # must pass
```
Register it in `MANIFEST.md` under "Installed extensions" (name, version, core
range, extension points, enabled, provenance). Run audit again.

### Update an extension (version bump)
- Edit the plugin's files, bump `version` in `plugin.yaml` (semver).
- If it no longer targets this core, update `core:`, else the gate quarantines it.
- Re-run `tools/validate_manifest.py --root .`.
- Update the row in `MANIFEST.md` + add a changelog line.

### Remove / disable
- **Disable:** `enabled: false` in `plugin.yaml` and `MANIFEST.md`. Stays
  discoverable but dormant.
- **Remove:** **archive, never delete.** Move to `curator/archived/`, remove the
  `MANIFEST.md` row, back up to `curator/.backup/` first.

### Add an extension point (new seam)
Adding a new extension point (e.g. `retrieval`, `evaluator`) is a **MINOR** core
bump. Do it in CORE.md §8, update the validator's `KNOWN_POINTS`, and note it in
the changelog.

---

## 4. Improve / extend spec-kit packaging (E3)

The framework ships as a spec-kit extension (`speckit-ext/`) built and verified
by GitHub Actions (`.github/workflows/speckit-extension.yml`).

- **Add a command:** create `speckit-ext/commands/<name>.md`, declare it in
  `speckit-ext/extension.yml` under `provides.commands` (namespaced
  `speckit.foundation.<name>`), and add a config template if needed.
- **Bump the extension version:** edit `speckit-ext/extension.yml`
  (`extension.version`) AND create a git tag `v<version>` so the CI publishes a
  Release with the zip.
- **The CI already:** validates the manifest, packs the zip (extension.yml at
  root), installs it into a real spec-kit project (localhost HTTP), asserts the
  commands/skills register, and publishes the Release on tags.

**To improve:** keep `speckit-ext/` and `extensions/` conceptually aligned —
spec-kit commands can wrap core operations (audit, memory, learnings). If you
add a core store or operation, consider a matching speckit command.

**Verify:** `specify extension list` shows the extension enabled; the CI
"Verify it installs" job passes; the Release zip contains `extension.yml` at root.

---

## 5. Improve / extend the stores (E4)

The five stores (CORE.md §5):
1. Semantic memory (`memory/memory.md`) — facts.
2. User profile (`memory/profile.md`) — who the user is.
3. Episodic log (`memory/episodic/`) — history.
4. Learnings (`learnings/`) — how-to-work knowledge.
5. Skills (`core-skills/` + `extensions/`) — procedures.

### Add / maintain a core skill
- Framework-native skills: `core-skills/<name>/SKILL.md` with
  `provenance: core` (curator-immune). Register in MANIFEST.md.
- Every SKILL.md: frontmatter (`name`, `description`, `version`, `provenance`),
  numbered steps with exact commands, a **Pitfalls** section, a **Verify**
  section. Description's first ~57 chars states the trigger.
- Patch immediately when a run shows staleness.

### Add a new store type (e.g. `knowledge/` for domain knowledge)
This is a **MINOR** core bump. Add it to CORE.md §5 (the table + a subsection),
add the dir, update the adapters' store list, and note in the changelog. Keep the
load policy (CORE.md §7) updated with when it loads.

---

## 6. Improve / extend the curator (E5)

Follow CORE.md §12 curation + §12 memory lifecycle — you are the curator:
- Track usage in `curator/.usage.json` (use_count, view_count, patch_count,
  last_activity_at, state, pinned) after each use.
- Idle for `stale_after_days` → mark stale; past `archive_after_days` → archive
  into `curator/archived/`. **Never hard-delete.**
- Back up to `curator/.backup/` before every transition.
- Honor `pinned` and `provenance` (`core`/`user`/`third-party` → archive-only;
  only `agent` is fully curatable).
- Consolidate overlapping skills into an umbrella only when clearly beneficial;
  archive originals. Off unless opted in.
- **Verify before adopting:** a skill is eligible only after ≥2 successful uses
  or a user-correction. Before consolidating, verify the umbrella against one
  example from each source skill.
- **Trace every event** to `curator/.traces/` (what/why/before/after/result).

### Skill improvement & mutation policy (CORE.md §12.2–11.4)
- **Improve by patching, not rewriting.** Preserve working structure, identity,
  and provenance; bump the skill's version on any change.
- **Keep one skill one job.** A skill used for two distinct jobs is a signal to
  split.
- **Extraction rule (the crossing rule):** when a skill's mutation begins to
  cross significantly with a distinct potential skill, extract it into its own
  skill. Trigger when **two or more** hold: two audiences/triggers, two
  unrelated workflows, body >~1 page (or Pitfalls covering two failure domains),
  or shared knowledge with another skill. Back up first, create the new skill
  with provenance preserved, remove the extracted concern from the source (add a
  pointer), bump the source version, register the new skill in MANIFEST.md,
  verify both (§14), and trace.
- **Don't extract prematurely.** One coherent procedure with two steps is not two
  skills; the crossing must be *significant*.
- **Merge upward** only when it reduces cognitive load and stays single-purpose;
  never merge two skills with different triggers just to reduce count.

### Memory lifecycle (CORE.md §13)
- New entries: declarative facts with `@since YYYY-MM-DD`, optional `@retain`.
- Session-end: append to `memory/episodic/YYYY-MM-DD.md`.
- Consolidate: promote durable facts from episodic → semantic memory; archive
  old episodes.
- **Forget by archiving** (never delete). Keep profile stable (no staleness).

### Improve a policy
- Plugin `policy:` blocks (in `plugin.yaml`) override curator defaults for that
  plugin's items — but hard rules (CORE.md §17) always win.

### Vet a skill for security (CORE.md §19)
- Run the risk-tier assessment (§19.1) and review checklist (§19.2) before
  enabling any third-party or internal skill.
- Record a `@digest sha256:<hash>` for content-hash attestation (§19.3).
- **Separation of duties:** don't review your own skill.
- Quarantine anything that fails review (per §17.3), never delete.

---

## 7. Improve / extend tooling (E6)

The only tool is `tools/validate_manifest.py` — the stdlib-only validator.

- **Add a new extension point:** update `KNOWN_POINTS` in the validator.
- **Add a new plugin field:** add the field to the validator's checks.
- **Extend validation:** the validator currently checks extensions/ AND
  core-skills/; it could also validate `speckit-ext/extension.yml` (spec-kit
  schema) and cross-check `MANIFEST.md` rows against `extensions/`.

**Rule:** keep the validator stdlib-only (no pyyaml, no third-party imports) —
this is a hard constraint (CORE.md §18).

---

## 8. Bump the core version (cross-cutting)

Adding an extension point or store = **MINOR** bump; removing/renaming one =
**MAJOR** bump.

- Edit `version` + `min_core_version` in `MANIFEST.md` and `CORE.md` frontmatter.
- Update each plugin's `core:` range to remain compatible, else it quarantines.
- Propagate to every adapter (E1) and `SKILL.md` boot entry.
- Add a "Changelog" line in `MANIFEST.md` describing the change.

---

## Pitfalls

- **Editing CORE.md schema without bumping core version** — silently breaks the
  compatibility gate. Always bump when the contract changes.
- **Registering a plugin without validating** — manifest and `extensions/` drift;
  audit then fails.
- **Deleting instead of archiving** — violates hard rule #1.
- **Ignoring provenance** — only `agent`-created skills are curatable. Treating
  `core` skills as curatable breaks the framework's own skills.
- **Wrong root** — operating against repo `.foundation/` when global
  `~/.foundation/` is active (or vice versa). Resolve `$FOUNDATION_ROOT` first.
- **Leaving an edge inconsistent** — every core change must propagate to all six
  edges (adapters, extensions, spec-kit, stores, curator, tooling). An edge you
  forget is an edge that drifts.
- **Adding a dependency to the validator** — breaks the no-software principle
  (CORE.md §18). Keep it stdlib-only.
- **Bumping speckit extension but not tagging** — CI only publishes a Release on
  `v*` tags; bump the version AND tag it, or the zip never ships.

## Verify

- `python3 tools/validate_manifest.py --root .` exits 0.
- Every dir in `extensions/*/` has a `plugin.yaml` and a matching `MANIFEST.md`
  row; nothing registered-but-missing or present-but-unregistered.
- `curator/.usage.json`, `curator/.backup/`, `curator/.traces/`, and
  `curator/archived/` exist.
- Every adapter's store count + version matches CORE.md.
- `speckit-ext/extension.yml` version matches its commands; CI "Verify it
  installs" passes.
- No skill or plugin was ever hard-deleted; everything archived is restorable.
- The audit in §1 lists no drift before you finish.
