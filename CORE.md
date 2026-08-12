---
name: foundation-core
description: "Framework core: self-management (memory/profile/skills/curator) + open extension system. The seed every skill, tool, and plugin plugs into."
version: 2.0.1
author: Hermes Agent (ported)
license: MIT
platforms: [linux, macos, windows]
metadata:
  foundation:
    manifest: MANIFEST.md
    extension_points: [skill, memory, tool, hook, policy, adapter]
    provenance: core
---

# Foundation — Skill Framework Core

This is a **framework core**, not a task skill. It defines the contract for an
open, extensible skill ecosystem that the agent maintains across sessions — the
self-improving nature of Hermes Agent, made portable and pluggable.

It ships three things:
1. **Core self-management** — memory, user profile, skills, and a safe curator.
2. **A directory convention** — one root everything lives under.
3. **An extension system** — a manifest plus named extension points any skill,
   tool, memory provider, or policy can plug into.

The core is deliberately thin. Everything else is an extension.

---

## 1. The core contract

What the framework guarantees to every extension:
- A stable directory root and naming conventions.
- A manifest/discovery mechanism — the agent can always find what's installed.
- A curator that maintains everything safely (backup → archive → pin, never delete).
- A fixed set of named **extension points** where plugins hook in.
- Semver versioning + a compatibility gate at load time.

---

## 2. Directory tree (single convention root)

```
<root>/                            # repo:  .foundation/
                                   # global: ~/.foundation/
  CORE.md                          # this document (aka SKILL.md when installed)
  MANIFEST.md                      # framework registry (name, version, extension points)
  memory/
    memory.md                      # store 1 — durable environment facts
    profile.md                     # store 2 — who the user is
  core-skills/
    <name>/SKILL.md                # bundled framework skills (provenance: core)
  extensions/
    <plugin>/                      # one dir per extension/plugin
      plugin.yaml                  # plugin manifest (schema in §6)
      README.md
      skills/                      # SKILL.md procedures this plugin contributes
      memory/                      # memory facts this plugin contributes
      tools/                       # executable helpers this plugin contributes
      hooks/                       # lifecycle hook scripts this plugin implements
  curator/
    .usage.json                    # per-skill usage ledger
    .backup/                       # pre-curation snapshots (rollback source)
    archived/                      # stale items moved here — never hard-deleted
```

---

## 3. Manifest — the registry (MANIFEST.md)

The registry the agent reads on bootstrap to know what exists and what is valid.

Declares:
- Framework name, version, `min_core_version`.
- The supported **extension points** (the seams in §4).
- A table of installed extensions: name, version, `core` range they target,
  which extension points they implement, `enabled` state, `provenance`.

Provenance drives curator permissions:
| provenance | curator may | example |
|-----------|-------------|---------|
| `core`     | nothing (bundled)         | framework's own skills |
| `agent`    | fully curatable           | skills the agent created |
| `user`     | archive-only, backup-first, pin-protected | the user's own skills |
| `third-party` | archive-only, backup-first, pin-protected | installed plugins |

---

## 4. Extension points (the seams)

Named interfaces where plugins plug in. Adding a new point is a **minor** core
bump (additive); removing/renaming one is **major** (breaking).

| Point | What it contributes | Example |
|-------|--------------------|---------|
| `skill`   | new SKILL.md procedures                    | a `git-workflow` skill |
| `memory`  | memory facts or a schema                   | account/credential facts |
| `tool`    | executable helpers the agent can call      | a `release.py` script |
| `hook`    | lifecycle callbacks (see below)            | run lint on skill save |
| `policy`  | curator/collection policy overrides        | "never archive anything older than X" |
| `adapter` | bridge to another agent's format           | AGENTS.md exporter for Copilot/Codex |
| `mcp`     | **declared** MCP servers (external systems) | a Postgres MCP server the agent may launch |

**No-software principle:** `tool` and `mcp` are *declarations*, not the software
itself. The framework never ships or installs an MCP server, vector index, or
eval engine. A plugin *declares* how to reach an external system (command, args,
env); the agent launches it with the tools already present. Anything that needs a
new runtime dependency is the plugin author's choice, and stays out of the core.

**Hook events** (the built-in lifecycle, ordered):
- `on-bootstrap` — when the framework initializes.
- `on-load`      — when a skill is invoked.
- `on-save`      — after a memory/skill write.
- `on-curate`    — before/after a curator transition.
- `on-shutdown`  — optional teardown.

---

## 5. Lifecycle & discovery

1. **BOOTSTRAP** — load `CORE.md` + `MANIFEST.md`; enumerate `extensions/`.
2. **VALIDATE** — check each `plugin.yaml` against the schema (§6) and the core
   version gate. **Invalid or incompatible → quarantine** into `curator/archived/`
   and report; never delete, never silently run.
3. **REGISTER** — valid plugins enter the active registry; `enabled: false` are
   present but dormant.
4. **EXECUTE** — the agent uses core self-management plus contributed
   skills/tools; hooks fire at their events.
5. **CURATE** — the curator maintains everything per provenance (usage → stale →
   archive; backup before every transition; pin to protect). Policy extensions may
   override thresholds.
6. **EVOLVE** — new skills/extensions are added via the self-management lifecycle
   below; the manifest is updated on every add/remove/version change.

---

## 6. Plugin manifest schema (plugin.yaml)

```yaml
name: <slug>                # required, lowercase-hyphens
version: 1.0.0              # required, semver
core: ">=2.0.0"             # required, core version range this targets
provenance: agent|user|third-party   # default: user
enabled: true
extension_points: [skill, tool, hook]   # which seams this uses
contributes:
  skills: []                # dirs under this plugin
  memory: []                # memory fact files
  tools:  []                # executable entrypoints
hooks:
  on-bootstrap: ""
  on-load: ""
  on-save: ""
  on-curate: ""
allowed_tools: []          # optional: restrict the tools this plugin may use
mcp_servers:               # optional: declared external systems (launch by config, not bundled)
  - name: ""
    command: ""            # e.g. "npx @modelcontextprotocol/server-postgres"
    args: []
    env: {}                # env placeholders resolved at launch ($VAR)
description: "..."
```

Validation rules: unknown `extension_points`, missing `core` range, or a hook
pointing at a non-existent path → quarantine.

---

## 7. Versioning & compatibility

- Core and plugins use **semver** (MAJOR.MINOR.PATCH).
- A plugin declares the `core` range it targets; bootstrap enforces it.
- Core bumps: **MINOR** = additive (new extension point), **MAJOR** = breaking.
- Incompatible plugins are quarantined + reported, never deleted.

---

## 8. Core self-management (the three stores)

### Store 1 — Memory (`memory/memory.md`)
Durable **environment facts**: tool quirks, working approaches, gotchas, stable
conventions. **Save** when the user states a preference/correction or you discover
a costly workaround. **Never save** task progress, completed-work logs, PR numbers,
SHAs, or anything stale in a week (recover from session history). Write as
**declarative facts**, not imperatives ("The build uses uv" ✓ / "Always use uv" ✗).
Respect the budget — prune/consolidate in one pass rather than bloat.

### Store 2 — User profile (`memory/profile.md`)
**Identity + preferences**: name, role, voice/tone, values, standing preferences.
Person ≠ environment ≠ procedure. Keep separate from Memory. Profile is the most
stable store: it changes rarely, is read every turn, and is never subject to
staleness — only explicit update or user correction.

### Store 3 — Skills & curator (`core-skills/` + `extensions/`)
Reusable procedures. **Create** after 5+ tool calls, non-trivial error recovery,
a user correction that worked, or a repeatable workflow. Each SKILL.md: trigger
description, numbered steps with exact commands, a Pitfalls section, verification.
**Patch immediately** when a run shows it's stale/wrong — an unmaintained skill is
a liability. Structure per the format in §2's `core-skills/<name>/SKILL.md`.

### Store 4 — Episodic log (`memory/episodic/`, per-session files)
A lightweight **session history** distinct from semantic facts. This is the
industry "episodic memory": *what happened*, not *what is true*. On session end
(or on request), append a short dated entry
(`memory/episodic/YYYY-MM-DD.md`) recording: what was attempted, what worked,
what failed, decisions taken. It is **append-only and cheap** — no per-turn
budgeting — and is *not injected* every turn. Load it only when the user asks
"what did we do before" or when continuity matters. **Lifecycle:** old episodes
are consolidated (see §11) and forgotten past a retention window; they are never
used to justify a current fact on their own — a fact must be promoted into
`memory.md` (semantic) to become durable.

---

## 11. Memory lifecycle (forgetting & staleness)

Every memory entry carries a lifecycle. Follow the industry rule — decide **what
to store, when to load, when to forget** — explicitly, in the file, so it survives
across agents.

- **Provenance tags:** write entries as `@since YYYY-MM-DD` and, where useful,
  `@retain <days>` (optional; default is forever until contradicted). These are
  plain text conventions the agent reads — no software needed.
- **Load policy (retrieval & routing):** profile is **always** loaded (stable,
  small). Semantic `memory.md` is **loaded on demand** when the task needs it —
  do not dump it into every prompt; the description/trigger decides. Episodic log
  is loaded **only on continuity requests**. This keeps context lean (the
  industry "context window is a public good" rule).
- **Forgetting:** a fact is **forgotten** (moved to `curator/archived/` or the
  memory archive) when: (a) it is superseded/contradicted, (b) its `@retain`
  window expires and it is no longer used, or (c) it is stale by usage (unreferenced
  for `stale_after_days`). Forgetting is **archival, never deletion**.
- **Consolidation:** on a regular pass (mirror of curator), fold the episodic log
  into semantic `memory.md` (promote durable facts), drop transient events, and
  archive the raw episode files past retention. This is the "extraction" step done
  as a convention.

---

## 12. Authoring rules (concise is key)

The context window is a public good. Only a skill's `name`+`description` pre-load;
the body is read only when relevant. Therefore:

- The `description` is the **trigger** — first ~57 chars must state *what* and
  *when to use* the skill. A vague description = never discovered.
- The body is **lean**: numbered steps, exact commands, a short Pitfalls list, a
  Verify step. Avoid prose, duplicated knowledge, and long examples.
- Prefer several small, single-purpose skills over one sprawling skill.
- Keep SKILL.md frontmatter **conformant** (see §2 / the spec): `name`,
  `description` required; `license`, `compatibility`, `allowed-tools` optional but
  encouraged for portability.

---

## 13. Skill evaluation (verification loop)

Curation without verification is half a loop (EvoSkills/SkillOpt). Adopt a
skill only after it has proven itself:

- A skill is **eligible** once it has been used successfully (≥2 passes) or after
  a user-correction that worked.
- Before the curator **consolidates** two skills into an umbrella, verify the
  result: run the umbrella's steps against one example from each source skill and
  confirm the outcome. Keep a short trace.
- **Trace log:** maintain `curator/.traces/` — one small file per curation or
  skill-use event (what changed, why, result). This is observability-as-convention:
  plain text, no daemon.

---

## 14. Hard rules (never violate)

1. **Never hard-delete.** Archive is the max destructive action, everywhere.
2. **Back up before any curation transition.** Rollback must always be possible.
3. **Validate before registering.** Unknown/incompatible plugins → quarantine, never run.
4. **Respect `enabled` and `pinned`.** Dormant stays dormant; pinned stays immune.
5. **Memory is declarative facts, not directives.** No "always do X".
6. **Respect the budget** — prune to make room, don't bloat.
7. **Ask before creating** a skill or writing to profile.
8. **Keep the stores separate.** Person ≠ environment ≠ procedure ≠ history.
9. **Honor provenance.** `core` is never touched by the curator.
10. **No software in the core.** External systems are *declared*, never bundled or
    installed by the framework.
11. **Forget by archiving, promote by consolidation.** A current fact must live in
    semantic memory; ephemeral events stay in the episodic log.

---

## 15. Verify

- `MANIFEST.md` exists and lists every extension in `extensions/` with a valid
  `plugin.yaml`; none are silently missing.
- `curator/.usage.json`, `curator/.backup/`, `curator/archived/`, and
  `curator/.traces/` exist; `archived/` holds only non-deleted, restorable items.
- Memory + profile + episodic files exist; memory under budget, declarative, no
  task logs/SHAs; entries carry `@since` provenance tags.
- Every plugin declares `core`, `extension_points`, and `provenance`; hooks and
  `mcp_servers` point at real paths; `allowed_tools` are valid if set.
- A new extension added to `extensions/` and registered in `MANIFEST.md` is
  discoverable on next bootstrap.
- The validator (`tools/validate_manifest.py`) exits 0 with no dependencies
  beyond the Python standard library.
