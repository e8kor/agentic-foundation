---
name: extract-learnings
description: "Extract work learnings at task/session end: what was done, how it was done, and what the next agent needs to be more efficient. Use when wrapping up work."
version: 1.0.0
author: foundation-core
license: MIT
metadata:
  foundation:
    provenance: core
    core: CORE.md
---

# Extract Learnings

At the end of a task or session, capture the durable, reusable knowledge about
**what work was done and how it was done** so the next agent working in this
project starts far ahead instead of re-learning from scratch. This is the
portable, dependency-free version of the industry "pre-compaction flush" /
"extract-memories" pattern.

Write into the **learnings store** (`learnings/`). This is distinct from the
other stores:
- `memory/memory.md` — durable *facts* about the environment (the what-is-true).
- `memory/episodic/` — raw *what happened* history (the transcript).
- `learnings/` — the distilled *how to work efficiently here* (the actionable
  summary the next agent reads first).

**Rule of thumb:** if it would save the next agent a lookup, a mistake, or a
discovery, it belongs in learnings.

---

## When to extract

- **Task completion** — after finishing a meaningful unit of work (a feature,
  a fix, a refactor, a research pass).
- **Session end** — before wrapping up, flush the session's durable insights.
- **On user request** — "save what we learned" / "capture this for next time".
- **Before context compaction** (if you're in an agent that compacts) — flush
  first so the knowledge survives the summary.

## What to capture (the extraction checklist)

Answer each of these concisely:

1. **What was done** — the work product: feature/fix/change, files touched,
   scope. One short paragraph or bullet list.
2. **How it was done** — the actual approach that worked: commands, build/test
   steps, tooling, the sequence. Concrete, not vague.
3. **Decisions & rationale** — choices made and *why*, so the next agent doesn't
   re-litigate them. Include dead-ends explored and rejected.
4. **Gotchas / pitfalls** — errors, traps, non-obvious failures and their fixes.
   These are the highest-value items (they prevent repeated pain).
5. **Repeat this** — patterns, commands, conventions that worked and should be
   reused (link to an existing skill if one now covers it).
6. **Avoid this** — things that didn't work, were wasteful, or are risky.
7. **State to resume from** — next steps, incomplete work, open questions, so a
   future agent can pick up cleanly.

Keep each item to a line or two. The whole entry should be scannable in under a
minute.

## How to write

- **One entry per work unit** — a dated file `learnings/YYYY-MM-DD.md` for the
  session, or a topic-named file for a discrete feature (`learnings/<topic>.md`).
  Group related entries in one file where sensible; don't fragment into dozens.
- **Use a consistent header per item:** a bold label plus a line, e.g.:
  ```md
  ## YYYY-MM-DD — <topic>
  **What:** <one line>
  **How:** <the working approach / commands>
  **Decisions:** <choice + why>
  **Gotchas:** <what bit us + fix>
  **Repeat:** <reusable pattern>
  **Avoid:** <what not to do>
  **Resume:** <next steps / open questions>
  ```
- **Be concrete and specific** — the exact command, the exact file, the exact
  trap. "Use `uv pip install`" beats "install dependencies correctly."
- **Prefer promoting to a skill** — if a repeatable procedure emerges, create or
  update a skill (see `foundation-operator` §5) rather than leaving it only in a
  dated learnings file.
- **Don't duplicate facts** — durable environment facts stay in `memory.md`;
  reference them, don't copy them.

## Where it lives

```
learnings/
├── README.md          # this index/explainer
├── YYYY-MM-DD.md      # per-session or per-work-unit entries
└── <topic>.md         # topic-named entries for discrete features
```

The next agent should **read the latest learnings file(s) at session start** to
orient, and append to the current date's file as work progresses.

## Pitfalls

- **Writing prose instead of bullets** — the next agent scans; keep it tight.
- **Recording raw history, not distilled knowledge** — don't copy the transcript;
  extract the *how-to-be-efficient* essence.
- **Leaving knowledge only in the agent's head** — if it isn't written down, the
  next session doesn't have it. Always write before wrapping up.
- **Storing facts in learnings instead of `memory.md`** — keep the stores clean:
  facts → memory, history → episodic, actionable how-to → learnings.
- **Not promoting to a skill** — a pattern used 3+ times should become a skill,
  not stay buried in a dated file.
- **Ignoring the resume field** — always record next steps so handoff is clean.

## Verify

- A learnings entry exists for the work unit or session (dated or topic-named).
- It covers What / How / Decisions / Gotchas / Repeat / Avoid / Resume.
- It is concrete (exact commands, files, traps), not vague.
- No durable fact was duplicated here that belongs in `memory.md`.
- Any recurring procedure was promoted to a skill.
