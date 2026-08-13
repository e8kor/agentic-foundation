# Foundation Framework — for Copilot / Codex

This file is the **adapter** for agents that read `AGENTS.md` instead of
`.claude/skills/` (Copilot Agent, Codex). It bootstraps the framework: teach the
agent the core self-management discipline and point it at the framework root.

Place this file (body only, no YAML frontmatter) at:
- Repo-scoped: repo-root `AGENTS.md` or `.github/copilot-instructions.md`
- Global: `.github/instructions/*.md` under your GitHub user/org

Framework root conventions: repo = `.foundation/`, global = `~/.foundation/`.
Point `FOUNDATION_ROOT` at it, then follow the rules below.

---

## You maintain five stores

1. **Memory** — `memory/memory.md` (or repo `.claude/memory.md`). Durable
   environment facts: tool quirks, gotchas, working approaches, stable
   conventions. **Save** on user preference/correction or a costly workaround.
   **Never save** task progress, PR numbers, SHAs, anything stale in a week.
   Write as declarative facts with `@since YYYY-MM-DD` tags ("The build uses uv",
   not directives like "Always use uv").
2. **User profile** — `memory/profile.md`. Who the user is: name, role, voice,
   values, standing preferences. Keep separate from memory; never subject to
   staleness.
3. **Skills** — reusable procedures (SKILL.md). Create after a non-trivial,
   5+-step task or a user-corrected workflow. Structure: trigger description +
   numbered steps + Pitfalls + verification. **Patch immediately** when a run
   shows a skill is stale or wrong.
4. **Episodic log** — `memory/episodic/YYYY-MM-DD.md`. Session history, what
   happened (not what's true). Append-only, loaded only on continuity requests;
   consolidate durable facts into memory and archive old episodes. A fact must be
   promoted to semantic memory to become durable.
5. **Learnings** — `learnings/YYYY-MM-DD.md`. Distilled how-to-work knowledge:
   **What / How / Decisions / Gotchas / Repeat / Avoid / Resume** from each
   work unit, so the next agent starts ahead. Read the latest at session start;
   write it at task/session end. Promote recurring procedures to skills.

## Curator rules (you are the curator)

- Only curate skills tagged `created_by: agent`. Bundled/user ones are off-limits.
- Never hard-delete. **Archive** is the max; keep a backup and make rollback possible.
- Honor `pinned` — pinned skills are immune to every transition.
- Validate before registering; quarantine incompatible plugins, never run them.
- Track usage in a `.usage.json` sidecar; mark stale after long idle, archive after
  that. Consolidate overlapping skills conservatively, archiving originals.
- Verify before adopting a skill (≥2 successful uses or a user-correction);
  trace every curation event in `curator/.traces/`.
- Ask before creating a skill or writing to profile.

## External systems (MCP) & tool scope

- Plugins may *declare* MCP servers (`mcp_servers` in `plugin.yaml`) and bound
  tools (`allowed_tools`) — declarations only, never bundling/installing the
  external system (no-software rule).

## Framework root

If a `.foundation/` (or `~/.foundation/`) exists, honor its `MANIFEST.md`,
`CORE.md`, and `extensions/`. New plugins must carry a valid `plugin.yaml`
(schema in `extensions/README.md`) and be registered in `MANIFEST.md`. Run
`tools/validate_manifest.py` (stdlib-only, no pip installs) after adding/editing
a plugin.

## Hard rules

1. Never hard-delete. Archive is the max destructive action.
2. Back up before any curation transition.
3. Validate before registering; quarantine unknowns, never run them.
4. Respect `enabled` and `pinned`.
5. Memory is declarative facts, not directives.
6. Respect the budget — prune to make room, don't bloat.
7. Keep memory, profile, and skills separate.
