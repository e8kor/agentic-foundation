---
name: foundation-core
description: "Framework core: self-management (memory/profile/skills/learnings) + open extension system. The seed every skill, tool, and plugin plugs into."
version: 3.3.0
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

1. **Motivation** (§1) — why the framework exists, and how skills build on it.
2. **Identity** (§2) — what this framework is.
3. **Contract** (§3) — what the framework guarantees.
4. **Structure** (§4) — where things live.
5. **Data** (§5–7) — the stores and how they're loaded.
6. **Extensibility** (§8–11) — the seams, schema, hooks, and core skills.
7. **Lifecycle** (§12–13) — curation and memory.
8. **Quality** (§14–15) — authoring and evaluation.
9. **Governance** (§16–17) — versioning and hard rules.
10. **Verification** (§18) — how to confirm the framework is consistent.
11. **Security & trust** (§19) — skill supply-chain vetting and attestation.

---

## 1. Motivation

**Purpose:** explain why Agentic Foundation exists and what it is a foundation
*for* — so every skill and extension knows the intent behind the structure.

### 1.1 The problem it solves

Coding agents are powerful but **stateless and forgetful**. Each session starts
from a blank context window: the agent re-learns the project, re-discovers
conventions, repeats mistakes it was already corrected on, and loses the
hard-won knowledge of how work actually gets done. This is not a model problem —
it is the absence of deliberate structure around an agent's accumulated
knowledge.

### 1.2 The idea

Agentic Foundation treats an agent's **skills, memory, profile, and learnings as
durable, structured, and self-managed assets** — the "self-improving nature" of a
coding agent, made portable and pluggable. Instead of a one-off prompt or a
single memory file, it provides a *framework*: a contract, a directory
convention, safe lifecycle rules, and extension points that any skill, tool, or
plugin can build on.

### 1.3 Why it is a *foundation* (not just a skill)

The name is deliberate. A foundation is something **other things are built on
top of**. In this framework:

- **Core skills** (`core-skills/`) are the framework's own building blocks —
  they demonstrate the pattern for every other skill.
- **Extension points** (§8) are the seams where new capabilities plug in without
  touching the core.
- **Stores** (§5) hold the shared state that every skill can read and write.
- **The curator** (§12) keeps the whole thing safe as it grows.

A skill written for this framework inherits: a stable home, a discoverability
mechanism, a lifecycle, and a safety net. The skill author focuses on the
procedure; the framework handles the plumbing.

### 1.4 The three commitments

Any skill, plugin, or adapter built on this foundation can rely on:

1. **Stability** — the contract and directory layout do not change arbitrarily;
   changes are versioned (semver) and gated.
2. **Safety** — nothing is ever hard-deleted; the curator backs up, archives,
   and honors provenance and pinning.
3. **Portability** — the framework is agent-agnostic and dependency-free, so a
   skill written once works across Copilot, Claude Code, Codex, and more (§8
   `adapter`).

### 1.5 Design principles

- **Dependency-free** — plain files + instructions; no runtime, no software
  dependencies (the only tool is a stdlib validator).
- **Context is a public good** — load only what's needed, when it's needed
  (§7 load policy).
- **Safe by default** — the max destructive action is *archive*, never *delete*.
- **Thin core, rich ecosystem** — the core provides structure and safety;
  everything else is an extension.

---

## 2. Identity

**Purpose:** state what Agentic Foundation is and is not.

- It is a **portable, dependency-free framework** for self-managing agent state:
  skills, memory, user profile, and learnings.
- It runs on **plain files + instructions**, with no runtime daemon and no
  software dependencies. The only tool is a Python-standard-library validator.
- It is **agent-agnostic**: adapters (see §8 `adapter`) expose it to Copilot,
  Claude Code, Codex, and others via their native formats (`AGENTS.md`,
  `SKILL.md`, `extension.yml`).
- It is **safe by default**: the curator backs up, archives (never deletes), and
  honors provenance and pinning.

---

## 3. The core contract

**Purpose:** define what every extension can rely on.

The framework guarantees to every skill, plugin, and extension:

1. **A stable root and naming conventions** — one directory tree (§4).
2. **A discovery mechanism** — the manifest (§6) always reflects what's installed.
3. **Named extension points** — fixed seams to plug into (§8).
4. **Safe curation** — backup → archive → pin, never delete (§12).
5. **Versioning + a compatibility gate** — semver and `core` ranges (§16).

---

## 4. Directory layout

**Purpose:** specify the single convention root and what each part is for.

```
<root>/                            # repo: .foundation/   global: ~/.foundation/
  CORE.md                          # this spec — the authoritative contract
  MANIFEST.md                      # registry: what is installed and valid (§6)
  SKILL.md                         # boot entry — loads CORE.md when installed as a skill
  AGENTS.md                        # adapter for Copilot/Codex (§8)
  memory/
    memory.md                      # store 1 — durable environment facts
    profile.md                     # store 2 — who the user is
    episodic/                      # store 3 — raw session history
  learnings/                       # store 4 — distilled how-to-work knowledge
  core-skills/
    <name>/SKILL.md                # framework skills (provenance: core)
  extensions/
    <plugin>/                      # one dir per extension
      plugin.yaml                  # plugin manifest (§9)
      README.md
      skills/                      # SKILL.md procedures this plugin contributes
      memory/                      # memory facts this plugin contributes
      tools/                       # executable helpers this plugin contributes
      hooks/                       # lifecycle hook scripts (§10)
  curator/
    .usage.json                    # per-skill usage ledger (§12)
    .backup/                       # pre-curation snapshots (rollback source)
    .traces/                       # observability-as-convention (plain text)
    archived/                      # stale items — never hard-deleted
  tools/
    validate_manifest.py           # stdlib-only validator (§18)
```

**Naming rules:** every directory and file uses lowercase, hyphens, no spaces.
Extension/skill names must match `^[a-z0-9-]+$`.

---

## 5. The stores (data model)

**Purpose:** define the five durable stores, what each holds, and when it's loaded.
These are the framework's memory; keeping them separate is a hard rule (§17.8).

| # | Store | Path | Holds | Loaded when |
|---|-------|------|-------|-------------|
| 1 | Semantic memory | `memory/memory.md` | durable **environment facts** | on demand |
| 2 | User profile | `memory/profile.md` | **who the user is** (role, voice, prefs) | every session |
| 3 | Episodic log | `memory/episodic/YYYY-MM-DD.md` | raw **what happened** history | continuity requests |
| 4 | Learnings | `learnings/YYYY-MM-DD.md` | distilled **how-to-work** knowledge | session start |
| 5 | Skills | `core-skills/` + `extensions/` | reusable **procedures** | on demand (§14) |

**One-line rule of thumb:**
- **facts** → semantic memory
- **who you are** → profile
- **what happened** → episodic
- **how to work efficiently** → learnings
- **how to do a task** → skills

### 5.1 Semantic memory
Durable environment facts: tool quirks, gotchas, working approaches, stable
conventions. **Save** on user preference/correction or a costly workaround.
**Never save** task progress, PR numbers, SHAs, or anything stale in a week.
Write as **declarative facts**, not imperatives ("The build uses uv" ✓ /
"Always use uv" ✗). Respect the budget — prune/consolidate in one pass.

### 5.2 User profile
Identity + preferences. The most stable store: changes rarely, read every
session, never subject to staleness — only explicit update or user correction.

### 5.3 Episodic log
Per-session history, append-only. Records what was attempted/worked/failed,
decisions. Not injected every turn. Lifecycle in §13. A fact only becomes
durable by being promoted into semantic memory.

### 5.4 Learnings
Distilled how-to-work knowledge captured via the `extract-learnings` core skill
(§11). Loaded at session start to orient. Facts stay in memory; raw history in
episodic; the actionable summary lives here.

### 5.5 Skills
Reusable procedures (SKILL.md). Lifecycle in §12, authoring in §14.

---

## 6. The manifest (MANIFEST.md)

**Purpose:** be the authoritative registry of what is installed and valid.

Declares:
- Framework name and version.
- The supported **extension points** (§8).
- A table of installed extensions: name, version, `core` range, extension
  points, `enabled` state, `provenance`.
- The **core skills** (curator-immune) shipped in `core-skills/`.
- A **changelog** of core versions.

The agent reads the manifest on bootstrap to know what exists and what is valid.
The manifest and `extensions/` must never drift apart (see §18).

### 6.1 Provenance (who owns what)
Provenance drives curator permissions:

| provenance | curator may | example |
|-----------|-------------|---------|
| `core`       | nothing (bundled, immune)      | framework's own skills |
| `agent`      | fully curatable                | skills the agent created |
| `user`       | archive-only, backup-first, pin-protected | the user's own skills |
| `third-party`| archive-only, backup-first, pin-protected | installed plugins |

---

## 7. Load policy (retrieval & routing)

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

## 8. Extension points (the seams)

**Purpose:** define the fixed, named interfaces where plugins plug in.
Adding a point is a **minor** core bump (additive); removing/renaming is
**major** (breaking).

| Point | What it contributes | Example |
|-------|--------------------|---------|
| `skill`   | new SKILL.md procedures                    | a `git-workflow` skill |
| `memory`  | memory facts or a schema                   | account/credential facts |
| `tool`    | executable helpers the agent can call      | a `release.py` script |
| `hook`    | lifecycle callbacks (§10)                   | run lint on skill save |
| `policy`  | curator/collection policy overrides        | "never archive older than X" |
| `adapter` | bridge to another agent's format           | AGENTS.md exporter for Copilot/Codex |
| `mcp`     | **declared** MCP servers (external systems) | a Postgres MCP server the agent may launch |

**No-software principle:** `tool` and `mcp` are *declarations*, not software the
framework ships or installs. A plugin *declares* how to reach an external system
(command, args, env); the agent launches it with tools already present. Anything
needing a new runtime dependency is the plugin author's choice and stays out of
the core.

---

## 9. Plugin manifest schema (plugin.yaml)

**Purpose:** specify exactly what a valid plugin looks like, so the validator
(§18) and bootstrap can accept or quarantine deterministically.

```yaml
name: <slug>                # required, ^[a-z0-9-]+$
version: 1.0.0              # required, semver
core: ">=3.0.0"             # required, core version range this targets
provenance: user            # required: agent|user|third-party
enabled: true
extension_points: [skill, tool, hook]   # which seams this uses (§8)
contributes:
  skills: []                # dirs under this plugin
  memory: []                # memory fact files
  tools:  []                # executable entrypoints
hooks:                      # lifecycle callbacks (§10)
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

## 10. Hooks (lifecycle callbacks)

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

## 11. Core skills

**Purpose:** enumerate the framework's own (curator-immune) skills.

| Skill | Purpose |
|-------|---------|
| `foundation-operator` | Govern the framework itself: add/remove extensions, audit consistency, curate skills, manage memory lifecycle, declare MCP, bump versions. |
| `extract-learnings` | At task/session end, distill what was done and how into the learnings store. |

Core skills live in `core-skills/<name>/SKILL.md`, carry `provenance: core`,
and are exempt from every curator transition (§17.9).

---

## 12. Curation & skill improvement (skill lifecycle)

**Purpose:** maintain and improve skills safely — the "you are the curator" rule.

### 12.1 The curation pipeline

1. **Track usage** in `curator/.usage.json` (use_count, view_count,
   patch_count, last_activity_at, state, pinned).
2. **Stale** after `stale_after_days` idle → mark stale.
3. **Archive** past `archive_after_days` → move to `curator/archived/`.
   **Never hard-delete.**
4. **Back up** to `curator/.backup/` before every transition.
5. **Pin** to protect — pinned skills are immune to every transition.
6. **Honor provenance** — only `agent` skills are fully curatable.
7. **Consolidate** overlapping skills into an umbrella only when clearly
   beneficial and verified (§15); archive the originals. Off unless opted in.
8. **Trace** every event to `curator/.traces/` (what, why, before, after,
   result) — observability as convention, no daemon.

### 12.2 Skill improvement policy

Every mutation of a skill (patch, merge, split, rename, or extract) must be
deliberate, safe, and traceable:

- **Improve by patching, not rewriting.** Fix a skill by targeted edits that
  preserve its working structure, identity, and provenance. A full rewrite is a
  last resort and counts as a new skill (see §12.3).
- **Keep one skill one job.** A skill should have a single, cohesive purpose.
  If a skill is being used for two distinct jobs, that is a signal to split.
- **Bump version on change.** Any behavioral change bumps the skill's PATCH
  (or MINOR for a new capability). Update `MANIFEST.md` and the changelog.
- **Trace the change.** Record what changed, why, and the result in
  `curator/.traces/`.

### 12.3 Extraction policy (the crossing rule)

**When a skill's mutation begins to cross significantly with a distinct
potential skill, extract the new concern into its own skill.**

A skill is "crossing" when it starts to accumulate material for a second,
separable concern. Trigger the extraction when **two or more** of these hold:

1. **Two audiences** — different triggers use the skill (the description no
   longer captures all the ways it's invoked).
2. **Two workflows** — the skill has two clear, unrelated step sequences
   (e.g. "release" and "rollback" living in one skill).
3. **Bloating body** — the body exceeds ~1 page (or a "Pitfalls" list that
   covers two distinct failure domains).
4. **Shared knowledge** — another skill or a would-be skill shares the same
   facts, and deduplicating would help both.

**How to extract (safe, per §12.2):**

1. Identify the separable concern (name it, give it a trigger description).
2. **Back up** the source skill to `curator/.backup/`.
3. Create the new skill `core-skills/<name>/SKILL.md` (or
   `extensions/<plugin>/skills/<name>/`) with `provenance` preserved.
4. **Remove** the extracted concern from the source skill and add a pointer to
   the new skill.
5. **Bump** the source skill's version; register the new skill in `MANIFEST.md`.
6. **Verify** both skills independently (§15) and trace the extraction.

**Anti-rule:** do not extract prematurely. A single coherent procedure that
happens to have two steps is not two skills. Extract only when the crossing is
**significant** (two or more signals above), not on every minor addition.

### 12.4 Merging / consolidation policy

- **Merge upward** (fold overlapping skills into an umbrella) only when it
  reduces cognitive load and the merged skill stays single-purpose.
- **Never merge** two skills that serve different triggers just to reduce count —
  that recreates the crossing problem this policy is meant to prevent.
- Verify the umbrella against examples from each source before adopting (§15).

---

## 13. Memory lifecycle (forgetting & staleness)

**Purpose:** decide what to store, when to load, when to forget — explicitly.

- **Provenance tags:** write `@since YYYY-MM-DD` and optionally `@retain <days>`
  (default: forever until contradicted). Plain-text conventions the agent reads.
- **Forgetting:** a fact is archived when it is (a) superseded/contradicted,
  (b) its `@retain` expires and is unused, or (c) unreferenced past
  `stale_after_days`. Forgetting is **archival, never deletion**.
- **Consolidation:** fold the episodic log into semantic memory (promote durable
  facts), drop transient events, archive raw episodes past retention.

---

## 14. Authoring rules (concise is key)

**Purpose:** specify how to write a good skill, so skills are discoverable and lean.

- The `description` is the **trigger** — first ~57 chars must state *what* and
  *when to use*. A vague description = never discovered.
- The body is **lean**: numbered steps, exact commands, a short Pitfalls list, a
  Verify step. Avoid prose, duplicated knowledge, long examples.
- Prefer several small, single-purpose skills over one sprawling skill.
- Keep SKILL.md frontmatter **conformant**: `name`, `description` required;
  `license`, `compatibility`, `allowed-tools` optional but encouraged.

---

## 15. Skill evaluation (verification loop)

**Purpose:** ensure the curator only adopts proven skills (no blind evolution).

- A skill is **eligible** once used successfully (≥2 passes) or after a
  user-correction that worked.
- Before **consolidating** two skills, verify the umbrella against one example
  from each source; confirm the outcome; trace it.
- **Enforced evaluation (adoption gate):** before a skill is promoted to
  `core-skills/` or a plugin is enabled, require a minimal eval suite of
  **3–5 representative queries** covering (a) should-trigger, (b)
  should-not-trigger, and (c) an ambiguous edge case. Record the result in
  `curator/.traces/`. This is the gate that turns "≥2 uses" from a convention
  into a checkable requirement.
- **Recall limit:** keep the number of simultaneously-active skills low. Each
  skill's name+description competes for attention in the system prompt; beyond
  ~8–12 active skills, recall degrades. When a role needs more, **bundle by
  role** (a `policy` extension that activates a focused subset) rather than
  loading everything. Stop adding skills when evaluation shows recall dropping.

---

## 16. Versioning & compatibility

**Purpose:** keep the framework and its extensions from silently breaking each other.

- Core and plugins use **semver** (MAJOR.MINOR.PATCH).
- A plugin declares the `core` range it targets; bootstrap enforces it.
- Core bumps: **MINOR** = additive (new extension point / section),
  **MAJOR** = breaking.
- Incompatible plugins are quarantined + reported, never deleted.

---

## 17. Hard rules (never violate)

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

## 18. Verify

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

---

## 19. Security & trust (skill supply chain)

**Purpose:** treat skills as an execution surface and vet them before adoption —
the single most-cited concern in the ecosystem (OWASP AST02, enterprise guides).

### 19.1 Risk-tier assessment (before adopting any skill)

Evaluate every skill/plugin against these indicators before approval. **High**
concerns require a full audit; **medium** require review:

| Risk indicator | What to look for | Concern |
|----------------|------------------|---------|
| Code execution | bundled `*.py`/`*.sh`/`*.js` scripts | **High** — run with full env access |
| Instruction manipulation | directives to ignore safety, hide actions, alter behavior conditionally | **High** — can bypass controls |
| MCP references | `ServerName:tool_name` in instructions | **High** — extends access beyond the skill |
| Network access | URLs, `fetch`/`curl`/`requests` | **High** — exfiltration vector |
| Hardcoded credentials | API keys/tokens/passwords in files | **High** — secrets leak |
| Filesystem scope | paths outside the skill dir, `../`, broad globs | **Medium** |
| Tool invocations | bash/file ops the skill directs | **Medium** |

### 19.2 Review checklist (before enabling a third-party or internal skill)

1. Read all skill content (SKILL.md + referenced files + scripts).
2. Verify script behavior matches the stated purpose (run in a sandbox).
3. Check for adversarial instructions (ignore-safety, hide-actions, exfil).
4. Search for network calls (`http`, `requests`, `curl`, `fetch`).
5. Confirm no hardcoded credentials (use env vars / secret stores).
6. List the tools/commands the skill invokes; consider combined risk.
7. Confirm external URLs point to expected domains.
8. Check for data-exfiltration patterns (read sensitive → send/encode out).

**Separation of duties:** a skill author should not be their own reviewer.

### 19.3 Integrity & attestation

- **Content-hash binding:** record a `@digest sha256:<hash>` in the skill's
  frontmatter (or `metadata`) covering `SKILL.md` + every declared resource.
  Any post-publish tampering invalidates the digest.
- **Provenance is the trust anchor:** `core` (bundled, immune), `user`
  (pin-protected), `third-party` (archive-only, backup-first). Treat
  `third-party` skills like unaudited dependencies — read before install.
- **Trust state:** a skill is `unverified` until it passes §19.1–19.2; it may be
  `attested` (reviewed + digest recorded) or `revoked` (digest invalidated).
  Hosts may surface or enforce this.
- **Never run an unverified skill** with elevated permissions. Quarantine
  anything that fails review (per §17.3), never delete.
