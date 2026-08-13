---
name: foundation-core
description: "Framework core: self-management (memory/profile/skills/learnings) + open extension system. The seed every skill, tool, and plugin plugs into."
version: 3.0.0
author: Agentic Foundation
license: MIT
platforms: [linux, macos, windows]
metadata:
  foundation:
    manifest: MANIFEST.md
    extension_points: [skill, memory, tool, hook, policy, adapter, mcp]
    provenance: core
---

# Agentic Foundation — Framework Core

**Purpose:** define the contract for an open, extensible skill ecosystem that an
agent maintains across sessions — the self-improving nature of a coding agent,
made portable, pluggable, and dependency-free.

This is a **framework core**, not a task skill. It is deliberately thin: the
core provides structure and safety; everything else is an extension.

The sections below form a single logical flow:

1. **Identity** (§1) — what this framework is.
2. **Contract** (§2) — what the framework guarantees.
3. **Structure** (§3) — where things live.
4. **Data** (§4–6) — the stores and how they're loaded.
5. **Extensibility** (§7–9) — the seams, schema, and lifecycle.
6. **Lifecycle** (§10–12) — curation, memory, and evolution.
7. **Quality** (§13–14) — authoring and evaluation.
8. **Governance** (§15–16) — versioning and hard rules.
9. **Verification** (§17) — how to confirm the framework is consistent.

---

## 1. Identity

**Purpose:** state what Agentic Foundation is and is not.

- It is a **portable, dependency-free framework** for self-managing agent state:
  skills, memory, user profile, and learnings.
- It runs on **plain files + instructions**, with no runtime daemon and no
  software dependencies. The only tool is a Python-standard-library validator.
- It is **agent-agnostic**: adapters (see §7 `adapter`) expose it to Copilot,
  Claude Code, Codex, and others via their native formats (`AGENTS.md`,
  `SKILL.md`, `extension.yml`).
- It is **safe by default**: the curator backs up, archives (never deletes), and
  honors provenance and pinning.

---

## 2. The core contract

**Purpose:** define what every extension can rely on.

The framework guarantees to every skill, plugin, and extension:

1. **A stable root and naming conventions** — one directory tree (§3).
2. **A discovery mechanism** — the manifest (§5) always reflects what's installed.
3. **Named extension points** — fixed seams to plug into (§7).
4. **Safe curation** — backup → archive → pin, never delete (§11).
5. **Versioning + a compatibility gate** — semver and `core` ranges (§15).

---

## 3. Directory layout

**Purpose:** specify the single convention root and what each part is for.

```
<root>/                            # repo: .foundation/   global: ~/.foundation/
  CORE.md                          # this spec — the authoritative contract
  MANIFEST.md                      # registry: what is installed and valid (§5)
  SKILL.md                         # boot entry — loads CORE.md when installed as a skill
  AGENTS.md                        # adapter for Copilot/Codex (§7)
  memory/
    memory.md                      # store 1 — durable environment facts
    profile.md                     # store 2 — who the user is
    episodic/                      # store 3 — raw session history
  learnings/                       # store 4 — distilled how-to-work knowledge
  core-skills/
    <name>/SKILL.md                # framework skills (provenance: core)
  extensions/
    <plugin>/                      # one dir per extension
      plugin.yaml                  # plugin manifest (§8)
      README.md
      skills/                      # SKILL.md procedures this plugin contributes
      memory/                      # memory facts this plugin contributes
      tools/                       # executable helpers this plugin contributes
      hooks/                       # lifecycle hook scripts (§9)
  curator/
    .usage.json                    # per-skill usage ledger (§11)
    .backup/                       # pre-curation snapshots (rollback source)
    .traces/                       # observability-as-convention (plain text)
    archived/                      # stale items — never hard-deleted
  tools/
    validate_manifest.py           # stdlib-only validator (§17)
```

**Naming rules:** every directory and file uses lowercase, hyphens, no spaces.
Extension/skill names must match `^[a-z0-9-]+$`.

---

## 4. The stores (data model)

**Purpose:** define the five durable stores, what each holds, and when it's loaded.
These are the framework's memory; keeping them separate is a hard rule (§16.8).

| # | Store | Path | Holds | Loaded when |
|---|-------|------|-------|-------------|
| 1 | Semantic memory | `memory/memory.md` | durable **environment facts** | on demand |
| 2 | User profile | `memory/profile.md` | **who the user is** (role, voice, prefs) | every session |
| 3 | Episodic log | `memory/episodic/YYYY-MM-DD.md` | raw **what happened** history | continuity requests |
| 4 | Learnings | `learnings/YYYY-MM-DD.md` | distilled **how-to-work** knowledge | session start |
| 5 | Skills | `core-skills/` + `extensions/` | reusable **procedures** | on demand (§13) |

**One-line rule of thumb:**
- **facts** → semantic memory
- **who you are** → profile
- **what happened** → episodic
- **how to work efficiently** → learnings
- **how to do a task** → skills

### 4.1 Semantic memory
Durable environment facts: tool quirks, gotchas, working approaches, stable
conventions. **Save** on user preference/correction or a costly workaround.
**Never save** task progress, PR numbers, SHAs, or anything stale in a week.
Write as **declarative facts**, not imperatives ("The build uses uv" ✓ /
"Always use uv" ✗). Respect the budget — prune/consolidate in one pass.

### 4.2 User profile
Identity + preferences. The most stable store: changes rarely, read every
session, never subject to staleness — only explicit update or user correction.

### 4.3 Episodic log
Per-session history, append-only. Records what was attempted/worked/failed,
decisions. Not injected every turn. Lifecycle in §12. A fact only becomes
durable by being promoted into semantic memory.

### 4.4 Learnings
Distilled how-to-work knowledge captured via the `extract-learnings` core skill
(§10). Loaded at session start to orient. Facts stay in memory; raw history in
episodic; the actionable summary lives here.

### 4.5 Skills
Reusable procedures (SKILL.md). Lifecycle in §11, authoring in §13.

---

## 5. The manifest (MANIFEST.md)

**Purpose:** be the authoritative registry of what is installed and valid.

Declares:
- Framework name and version.
- The supported **extension points** (§7).
- A table of installed extensions: name, version, `core` range, extension
  points, `enabled` state, `provenance`.
- The **core skills** (curator-immune) shipped in `core-skills/`.
- A **changelog** of core versions.

The agent reads the manifest on bootstrap to know what exists and what is valid.
The manifest and `extensions/` must never drift apart (see §17).

### 5.1 Provenance (who owns what)
Provenance drives curator permissions:

| provenance | curator may | example |
|-----------|-------------|---------|
| `core`       | nothing (bundled, immune)      | framework's own skills |
| `agent`      | fully curatable                | skills the agent created |
| `user`       | archive-only, backup-first, pin-protected | the user's own skills |
| `third-party`| archive-only, backup-first, pin-protected | installed plugins |

---

## 6. Load policy (retrieval & routing)

**Purpose:** specify which store reaches the agent when, to keep context lean
("the context window is a public good").

| Store | Load |
|-------|------|
| Profile | **always** (stable, small) |
| Semantic memory | **on demand** — when the task needs it |
| Learnings (latest) | **at session start** — to orient |
| Episodic log | **only** on continuity requests |
| Skills | **lazy** — only the name+description pre-load; body loads when relevant |

---

## 7. Extension points (the seams)

**Purpose:** define the fixed, named interfaces where plugins plug in.
Adding a point is a **minor** core bump (additive); removing/renaming is
**major** (breaking).

| Point | What it contributes | Example |
|-------|--------------------|---------|
| `skill`   | new SKILL.md procedures                    | a `git-workflow` skill |
| `memory`  | memory facts or a schema                   | account/credential facts |
| `tool`    | executable helpers the agent can call      | a `release.py` script |
| `hook`    | lifecycle callbacks (§9)                   | run lint on skill save |
| `policy`  | curator/collection policy overrides        | "never archive older than X" |
| `adapter` | bridge to another agent's format           | AGENTS.md exporter for Copilot/Codex |
| `mcp`     | **declared** MCP servers (external systems) | a Postgres MCP server the agent may launch |

**No-software principle:** `tool` and `mcp` are *declarations*, not software the
framework ships or installs. A plugin *declares* how to reach an external system
(command, args, env); the agent launches it with tools already present. Anything
needing a new runtime dependency is the plugin author's choice and stays out of
the core.

---

## 8. Plugin manifest schema (plugin.yaml)

**Purpose:** specify exactly what a valid plugin looks like, so the validator
(§17) and bootstrap can accept or quarantine deterministically.

```yaml
name: <slug>                # required, ^[a-z0-9-]+$
version: 1.0.0              # required, semver
core: ">=3.0.0"             # required, core version range this targets
provenance: user            # required: agent|user|third-party
enabled: true
extension_points: [skill, tool, hook]   # which seams this uses (§7)
contributes:
  skills: []                # dirs under this plugin
  memory: []                # memory fact files
  tools:  []                # executable entrypoints
hooks:                      # lifecycle callbacks (§9)
  on-bootstrap: ""
  on-load: ""
  on-save: ""
  on-curate: ""
allowed_tools: []          # optional: restrict tools this plugin may use
mcp_servers:               # optional: declared external systems
  - name: ""
    command: ""            # e.g. "npx @modelcontextprotocol/server-postgres"
    args: []
    env: {}                # env placeholders resolved at launch ($VAR)
description: "..."
```

**Validation rules** (→ quarantine if violated, never delete): unknown
`extension_points`, missing/invalid `core` range, unknown `provenance`,
invalid `id`/`version`, a hook pointing at a non-existent path, or
`contributes` dirs that don't exist.

---

## 9. Hooks (lifecycle callbacks)

**Purpose:** let extensions react to framework events without touching core.

Built-in events, ordered:

- `on-bootstrap` — when the framework initializes.
- `on-load`      — when a skill is invoked.
- `on-save`      — after a memory/skill write.
- `on-curate`    — before/after a curator transition.
- `on-shutdown`  — optional teardown.

A hook is a shell script declared in `plugin.yaml`. It runs with `PLUGIN_DIR`
and `EVENT` in the environment; a non-zero exit warns but never aborts the
framework.

---

## 10. Core skills

**Purpose:** enumerate the framework's own (curator-immune) skills.

| Skill | Purpose |
|-------|---------|
| `foundation-operator` | Govern the framework itself: add/remove extensions, audit consistency, curate skills, manage memory lifecycle, declare MCP, bump versions. |
| `extract-learnings` | At task/session end, distill what was done and how into the learnings store. |

Core skills live in `core-skills/<name>/SKILL.md`, carry `provenance: core`,
and are exempt from every curator transition (§16.9).

---

## 11. Curation (skill lifecycle)

**Purpose:** maintain skills safely — the "you are the curator" rule.

1. **Track usage** in `curator/.usage.json` (use_count, view_count,
   patch_count, last_activity_at, state, pinned).
2. **Stale** after `stale_after_days` idle → mark stale.
3. **Archive** past `archive_after_days` → move to `curator/archived/`.
   **Never hard-delete.**
4. **Back up** to `curator/.backup/` before every transition.
5. **Pin** to protect — pinned skills are immune to every transition.
6. **Honor provenance** — only `agent` skills are fully curatable.
7. **Consolidate** overlapping skills into an umbrella only when clearly
   beneficial and verified (§14); archive the originals. Off unless opted in.
8. **Trace** every event to `curator/.traces/` (what, why, before, after,
   result) — observability as convention, no daemon.

---

## 12. Memory lifecycle (forgetting & staleness)

**Purpose:** decide what to store, when to load, when to forget — explicitly.

- **Provenance tags:** write `@since YYYY-MM-DD` and optionally `@retain <days>`
  (default: forever until contradicted). Plain-text conventions the agent reads.
- **Forgetting:** a fact is archived when it is (a) superseded/contradicted,
  (b) its `@retain` expires and is unused, or (c) unreferenced past
  `stale_after_days`. Forgetting is **archival, never deletion**.
- **Consolidation:** fold the episodic log into semantic memory (promote durable
  facts), drop transient events, archive raw episodes past retention.

---

## 13. Authoring rules (concise is key)

**Purpose:** specify how to write a good skill, so skills are discoverable and lean.

- The `description` is the **trigger** — first ~57 chars must state *what* and
  *when to use*. A vague description = never discovered.
- The body is **lean**: numbered steps, exact commands, a short Pitfalls list, a
  Verify step. Avoid prose, duplicated knowledge, long examples.
- Prefer several small, single-purpose skills over one sprawling skill.
- Keep SKILL.md frontmatter **conformant**: `name`, `description` required;
  `license`, `compatibility`, `allowed-tools` optional but encouraged.

---

## 14. Skill evaluation (verification loop)

**Purpose:** ensure the curator only adopts proven skills (no blind evolution).

- A skill is **eligible** once used successfully (≥2 passes) or after a
  user-correction that worked.
- Before **consolidating** two skills, verify the umbrella against one example
  from each source; confirm the outcome; trace it.

---

## 15. Versioning & compatibility

**Purpose:** keep the framework and its extensions from silently breaking each other.

- Core and plugins use **semver** (MAJOR.MINOR.PATCH).
- A plugin declares the `core` range it targets; bootstrap enforces it.
- Core bumps: **MINOR** = additive (new extension point / section),
  **MAJOR** = breaking.
- Incompatible plugins are quarantined + reported, never deleted.

---

## 16. Hard rules (never violate)

**Purpose:** enumerate the invariants that cannot be broken.

1. **Never hard-delete.** Archive is the max destructive action, everywhere.
2. **Back up before any curation transition.** Rollback must always be possible.
3. **Validate before registering.** Unknown/incompatible plugins → quarantine,
   never run.
4. **Respect `enabled` and `pinned`.** Dormant stays dormant; pinned stays immune.
5. **Memory is declarative facts, not directives.** No "always do X".
6. **Respect the budget** — prune to make room, don't bloat.
7. **Ask before creating** a skill or writing to profile.
8. **Keep the stores separate.** Person ≠ environment ≠ procedure ≠ history ≠
   how-to-knowledge.
9. **Honor provenance.** `core` is never touched by the curator.
10. **No software in the core.** External systems are *declared*, never bundled
    or installed by the framework.
11. **Forget by archiving, promote by consolidation.** A current fact must live
    in semantic memory; ephemeral events stay in the episodic log.

---

## 17. Verify

**Purpose:** provide the checklist for confirming the framework is consistent.

- `MANIFEST.md` exists and lists every extension in `extensions/` with a valid
  `plugin.yaml`; none are silently missing.
- `curator/.usage.json`, `curator/.backup/`, `curator/.traces/`, and
  `curator/archived/` exist; `archived/` holds only non-deleted, restorable items.
- Memory + profile + episodic + learnings files exist; memory under budget,
  declarative, no task logs/SHAs; entries carry `@since` provenance tags.
- Every plugin declares `core`, `extension_points`, and `provenance`; hooks and
  `mcp_servers` point at real paths; `allowed_tools` are valid if set.
- A new extension added to `extensions/` and registered in `MANIFEST.md` is
  discoverable on next bootstrap.
- The validator exits 0 with no dependencies beyond the Python standard library:
  ```bash
  python3 tools/validate_manifest.py --root .
  ```
