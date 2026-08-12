# Agentic Foundation — Self-Managing Agent Skill Framework

A portable, **dependency-free** skill framework that gives any coding agent
(GitHub Copilot, Claude Code, Codex) a "self-improving" nature: it maintains its
own **skills, memory, user profile, and learnings** across sessions, and is open
to **extensions/plugins** — all through plain files and instructions, with
**zero software dependencies** (the only tool is a Python-stdlib validator).

This is the framework core. It is not a task skill; it is the seed every skill
and plugin plugs into.

---

## What it gives you

- **Five durable stores** (kept separate):
  - `memory/memory.md` — semantic memory: durable *environment facts*
  - `memory/profile.md` — *who the user is* (role, voice, preferences)
  - `memory/episodic/` — session history (*what happened*, not what is true)
  - `learnings/` — distilled *how-to-work-efficiently* knowledge
  - `core-skills/` + `extensions/` — procedural knowledge (reusable SKILL.md)
- **An open extension system**: `extensions/<plugin>/plugin.yaml` manifests that
  plug into named **extension points** — `skill`, `memory`, `tool`, `hook`,
  `policy`, `adapter`, `mcp`.
- **A safe curator**: usage tracking → stale → archive (never delete), with
  backup + pin protection and a provenance gate.
- **Cross-agent adapters**: the same framework installs into GitHub Copilot
  (via `AGENTS.md` / `.github/`), Claude Code (`.claude/skills/`), and Codex.

---

## Quick start

```bash
# Validate the framework is consistent (stdlib-only, no pip installs):
python3 tools/validate_manifest.py --root .
```

To **bootstrap a project** with this nature, copy this whole tree into your
repo (or reference it), and read `CORE.md` — it is the authoritative contract.

### GitHub Copilot
Copilot Agent reads this repo automatically via:
- `AGENTS.md` (root) — repo conventions
- `.github/copilot-instructions.md` — global instruction bootstrap
- `.github/prompts/foundation.prompt.md` — a `/foundation` slash command

### Claude Code
Copy `SKILL.md` → `.claude/skills/foundation-core/SKILL.md` (or the whole tree).

### Codex
Codex reads `AGENTS.md` at the repo root.

---

## Layout

```
AGENTS.md                     # agent-facing entry (Copilot/Codex)
CORE.md                       # THE authoritative contract (read this)
MANIFEST.md                   # installed-extension registry
SKILL.md                      # Claude-Code boot entry
core-skills/                  # curator-immune framework skills
extensions/                   # plugins (each has plugin.yaml)
extensions/README.md          # how to build a plugin
memory/                       # semantic + profile + episodic stores
learnings/                    # distilled how-to-work knowledge
curator/                      # usage ledger, backup, archive, traces
tools/validate_manifest.py    # stdlib-only validator
research/                     # industry research + comparison
```

---

## Documentation
- `CORE.md` — framework contract: stores, extension points, lifecycle, hard rules.
- `extensions/README.md` — plugin schema and how to contribute.
- `research/RESEARCH.md` — industry best-practice research.
- `research/COMPARISON.md` — comparison against the GitHub landscape
  (superpowers, OpenViking, TencentDB-Agent-Memory, SkillOpt, agent-skill-creator, …).

---

## License
MIT © Eugene Korniichuk. See [LICENSE](LICENSE).
