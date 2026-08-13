# GitHub Copilot global instructions — Foundation bootstrap

This repository is the **Foundation skill framework**. Copilot Agent reads this
file as repo-wide instructions and `AGENTS.md` for conventions. Together they
teach Copilot to operate with a self-managing, skill-based nature.

## Bootstrap

1. Read `CORE.md` — the authoritative contract (stores, extension points,
   lifecycle, hard rules).
2. Read `MANIFEST.md` — the registry of installed extensions and core skills.
3. Read `extensions/README.md` — the plugin schema.

## What Copilot must maintain (five stores)

1. **Memory** — `memory/memory.md`. Durable environment facts: tool quirks,
   gotchas, working approaches. Save on user preference/correction or a costly
   workaround. Write as declarative facts with `@since YYYY-MM-DD` ("The build
   uses uv"), not directives ("Always use uv").
2. **User profile** — `memory/profile.md`. Who the user is: name, role, voice,
   values, standing preferences. Keep separate from memory; never stale.
3. **Skills** — reusable SKILL.md procedures. Create after a non-trivial 5+-step
   task or a user-corrected workflow. Structure: trigger description + numbered
   steps + Pitfalls + verification. Patch immediately when a run shows staleness.
4. **Episodic log** — `memory/episodic/YYYY-MM-DD.md`. Session history, what
   happened. Append-only, loaded only on continuity requests; promote durable
   facts into semantic memory, archive old episodes.
5. **Learnings** — `learnings/YYYY-MM-DD.md`. Distilled how-to-work knowledge
   (**What / How / Decisions / Gotchas / Repeat / Avoid / Resume**) from each
   work unit, so the next agent starts ahead. Read the latest at session start;
   write it at task/session end. Promote recurring procedures to skills.

## Curator rules (you are the curator)

- Only curate skills tagged `created_by: agent` (provenance). Bundled/user/core
  skills are off-limits.
- **Never hard-delete.** Archive is the max destructive action. Keep a backup;
  rollback must always be possible.
- Honor `pinned` (immune) and `enabled` (dormant stays dormant).
- Validate before registering; quarantine incompatible plugins, never run them.
- Track usage in `curator/.usage.json`; mark stale after long idle, archive
  after that. Consolidate overlapping skills conservatively, archiving originals.
- Verify before adopting a skill (≥2 successful uses or a user-correction);
  trace every curation event in `curator/.traces/`.
- Ask before creating a skill or writing to profile.

## External systems & tools

- Plugins may *declare* MCP servers (`mcp_servers` in `plugin.yaml`) and bound
  tools (`allowed_tools`) — declarations only, never bundling/installing the
  external system (no-software rule).

## Validation

- After adding/editing a plugin, run:
  `python3 tools/validate_manifest.py --root .` (stdlib-only, no installs).
- Run it before finishing any change that touches `extensions/` or `MANIFEST.md`.

## Hard rules (never violate)

1. Never hard-delete. Archive is the max destructive action.
2. Back up before any curation transition.
3. Validate before registering; quarantine unknowns, never run them.
4. Respect `enabled` and `pinned`.
5. Memory is declarative facts, not directives.
6. Respect the budget — prune to make room, don't bloat.
7. Keep memory, profile, skills, episodic history, and learnings separate.
8. No software in the core — external systems are declared, never bundled.
