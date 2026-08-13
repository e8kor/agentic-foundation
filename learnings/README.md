# Learnings store — distilled how-to-work-efficiently knowledge

This directory holds the durable, actionable lessons about **what work was done
and how it was done** in this project. The next agent reads the latest entry at
session start to orient and start ahead.

## How this differs from the other stores

| Store | Holds | Loaded when |
|-------|-------|-------------|
| `learnings/` (this) | **How to work efficiently here** — approach, gotchas, decisions, next steps | Next agent at session start |
| `memory/memory.md` | Durable **facts** about the environment | On demand |
| `memory/episodic/` | Raw **what happened** history | Continuity requests |
| `memory/profile.md` | **Who the user is** | Every session |

## Conventions

- Entries: `YYYY-MM-DD.md` (per session/work unit) or `<topic>.md` (discrete
  feature). See `core-skills/extract-learnings/SKILL.md` for the full process.
- Each item: **What / How / Decisions / Gotchas / Repeat / Avoid / Resume**.
- Be concrete: exact commands, files, and traps.
- Promote recurring procedures to a skill rather than leaving them only here.

## Files

(Add entries as you complete work. The most recent file is what a new agent
should read first.)
