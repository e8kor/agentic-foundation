# Foundation — GitHub Landscape & Comparative Review

Companion to `CORE.md` and `RESEARCH.md`. Compares Foundation against the
projects that actually ship this "nature" — agent skills frameworks, memory
hubs, self-evolving agents, plugin ecosystems — using live GitHub API data
(search + repo tree + READMEs), so the comparison is grounded in real repos,
not marketing copy. Raw snapshots: `gh_search.json`, `gh_repos.json`,
`gh_readmes.json`.

Research date: Aug 2026. Star counts as of that date.

---

## 1. The landscape, mapped

| Project | Stars | What it is | How it stores "nature" | Runtime |
|---------|-------|-----------|------------------------|---------|
| **obra/superpowers** | ~271k | Agentic skills framework + SWE methodology | Composable SKILL.md skills + instructions | Ships `.claude-plugin`/`.codex-plugin`/`.cursor-plugin`/`.hermes-plugin` adapters |
| **zhayujie/CowAgent** | ~46k | Open-source super AI assistant / agent harness | Plans, runs tools+skills, **self-evolves** with memory+knowledge | Full app (multi-channel) |
| **volcengine/OpenViking** | ~28k | "Context Database" — unifies agent memory + knowledge RAG + skills | Memory + RAG + skills unified | Self-hosted DB (Rust/Cargo) |
| **TencentCloud/TencentDB-Agent-Memory** | ~20k | Team-level memory hub | 4 memory assets: **Chat Memory, Skill, LLM-Wiki, Code-Graph**, governed | Server (MemoryCore/Proxy/Panel) + SDK |
| **microsoft/SkillOpt** | ~16k | Text-space skill optimizer | Trains reusable NL skills via trajectory edits, **validation-gated** | Python pipeline |
| **memvid/memvid** | ~16k | Memory layer, replaces RAG | Single-file, serverless memory | Rust server |
| **lsdefine/GenericAgent** | ~14k | Minimal self-evolving agent | Grows a **skill tree** from a small seed, system control | Agent loop |
| **FrancyJGLisboa/agent-skill-creator** | ~2.2k | Turns workflows into skills | **Quality gates** (validate/security/eval) before install; **evolve loop** | 17-platform installer |

Common denominator across every serious project: **they all implement the
memory/skill lifecycle as real, running software** — a server, an agent loop, an
optimizer — whereas Foundation deliberately keeps it as **instructions + plain
files + a stdlib validator** (the no-software principle). That is the single
biggest axis of difference, and it's a deliberate tradeoff, not an accident.

---

## 2. Head-to-head: what we can learn from each

### obra/superpowers (★271k) — the closest philosophical cousin
- **Does exactly our `adapter` extension point, at scale**: ships the *same*
  skills via `.claude-plugin`, `.codex-plugin`, `.cursor-plugin`, `.devin-plugin`,
  `.kimi-plugin`, `.opencode`, `.hermes-plugin`. This validates our decision to
  make the core agent-agnostic and expose adapters.
- **What it has we don't:** a large curated *library* of methodology skills
  (brainstorming, planning, TDD) with a strong opinionated workflow; a
  `RELEASE-NOTES.md`/version-bump discipline; per-agent plugin packaging.
- **Lesson:** Foundation is currently a *skeleton* + one example plugin. To be
  useful it needs a **library of real skills** and **packaged adapter dirs**
  (the P4 item in RESEARCH.md). The architecture is right; the content is thin.

### TencentDB-Agent-Memory (★20k) — the richest memory taxonomy
- Four explicit memory assets: **Chat Memory (episodic), Skill (procedural),
  LLM-Wiki (semantic knowledge), Code-Graph (codebase graph)**. This is a more
  complete memory taxonomy than ours.
- **Lesson:** our `memory/` (semantic) + `episodic/` + `profile/` maps well to
  their Chat/Skill/Wiki. They add a **knowledge graph / code-graph** dimension we
  don't have. Worth a `knowledge/` store for project/domain knowledge beyond
  raw facts — a "LLM-Wiki" equivalent.

### volcengine/OpenViking (★28k) — memory + RAG + skills unified
- Positions itself as a **context database**: one store for memory, knowledge
  (RAG), and skills, with retrieval.
- **Lesson:** we split stores by *type* (semantic/episodic/profile/skills) but
  have **no unified retrieval** — the "load on demand" policy in CORE.md §7 is
  advisory, not a retrieval index. Their RAG/vector retrieval is the gap we
  deliberately deferred as "needs software." A future, optional `retrieval`
  provider would close it without violating no-software (it would be a *declared*
  optional tool).

### microsoft/SkillOpt (★16k) — the verification loop, made concrete
- **"validation-gated updates"**: a skill is only adopted when a validator passes.
- **Lesson:** this is exactly the **skill evaluation / verification loop** we
  added in CORE.md §15. Ours is a convention ("≥2 uses, then verify"); theirs is
  an automated optimizer with a validation gate. Our approach is the 
  dependency-free, conservative version of their idea. Confirms §14 is the right
  direction — and that a future `evaluator` hook/point would let us plug in
  real validation.

### FrancyJGLisboa/agent-skill-creator (★2.2k) — quality gates + 17 platforms
- Installs one SKILL.md on **17 platforms**; runs a **security scan** and an
  **eval/rollout** before install; has an **evolve loop**.
- **Lesson:** two concrete gaps for us: (1) **security scanning of skills/tools**
  before adoption (we only check file paths), and (2) a real **per-skill eval
  spec** rather than our manual "confirm the outcome." Both are P3 items worth
  upgrading. Their 17-platform breadth validates our `adapter` design.

### CowAgent / GenericAgent / OpenViking (★14k-46k) — self-evolution as a feature
- All three literally advertise **"self-evolves"** / "grows a skill tree from a
  small seed" / "6x less token consumption." This is the industry's headline
  feature and the whole reason Foundation exists.
- **Lesson:** our curator (usage → stale → archive, backup, pin) is the *safe*
  version of self-evolution. The frontier is **autonomous skill generation** —
  the agent writing new skills from scratch and validating them. Foundation's
  curator could grow an optional "skill generation" hook (gated, archived, never
  deleting) that moves toward this without abandoning safety.

### memvid (★16k) — serverless single-file memory
- Shows memory can be **lightweight and dependency-free** — validating our
  plain-files ethos, just with a small Rust server for retrieval.

---

## 3. Comparison matrix — Foundation vs. the field

| Capability | Foundation | superpowers | Tencent | OpenViking | SkillOpt | agent-skill-creator |
|-----------|-----------|-------------|---------|-----------|----------|---------------------|
| Procedural skills | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| Memory: episodic | ✔ (episodic/) | ~ | ✔ (Chat) | ✔ | ~ | ~ |
| Memory: semantic | ✔ | ~ | ✔ (Wiki) | ✔ (RAG) | ~ | ~ |
| Memory: code-graph | ✘ | ✘ | ✔ | ~ | ✘ | ✘ |
| User profile | ✔ | ~ | ~ | ~ | ~ | ~ |
| Retrieval/vector | ✘ (policy only) | ~ | ✔ | ✔ | ~ | ~ |
| Skill lifecycle/curator | ✔ (backup→archive→pin) | ~ | ✔ (governed) | ✔ | ✔ (validation) | ✔ (gates) |
| **Skill verification loop** | ◐ (manual) | ~ | ~ | ~ | ✔ (auto) | ✔ (eval spec) |
| **Security scan** | ✘ | ✘ | ~ | ✘ | ✘ | ✔ |
| Plugin/extension model | ✔ (extensions+manifest) | ✔ (adapters) | ✘ | ✘ | ✘ | ✘ |
| MCP / external systems | ◐ (declared) | ~ | ~ | ~ | ✘ | ✘ |
| Distributable packages | ✘ (P4) | ✔ | ✘ | ✘ | ✘ | ✔ (installer) |
| **Agent-agnostic adapters** | ✔ (AGENTS.md, SKILL.md) | ✔ (7 plugins) | ~ | ~ | ~ | ✔ (17 platforms) |
| Runs with zero deps | ✔ (stdlib) | ~ | ✘ (needs server) | ✘ (DB) | ✘ (pipeline) | ✘ (pipeline) |

✔ have · ◐ partial · ~ not primary · ✘ missing

---

## 4. What to add to Foundation (prioritized, dependency-free only)

Given the no-software principle, the highest-value additions that stay **inside
instructions**:

1. **A `knowledge/` store** (LLM-Wiki analog) — beyond raw semantic facts, a
   place for project/domain *knowledge* (concepts, architecture, glossaries),
   distinct from both `memory/` (facts) and `profile/` (person). Tencent's
   taxonomy shows the value. Cheap to add as a 4th/5th store; no software.
2. **Upgrade the verification loop** (SkillOpt / agent-skill-creator lesson) —
   make §14 concrete: a `curator/eval/` dir holding one small **eval spec**
   (`inputs` + `expected`) per skill, so "verify" is reproducible rather than a
   hand-wave. Still plain files + the agent running them; no framework software.
3. **A security gate** (agent-skill-creator lesson) — before a plugin/skill is
   adopted, the agent inspects its scripts/tools for obvious dangers (no secrets
   baked in, no destructive commands). A documented checklist, not a scanner.
4. **Package the framework as real adapters** (superpowers/agent-skill-creator
   lesson) — emit `.claude-plugin/` / `AGENTS.md` / a `README` for each consumer,
   so "put it in GitHub Copilot" is a one-step copy, not a manual step. We have
   `AGENTS.md`; add the packaged install layout.

## 5. What we do that most don't (our defensible strengths)

- **Zero software dependency** — every other serious framework ships a server,
  agent loop, or optimizer. Foundation runs on plain files + the Python stdlib.
  That is genuinely unusual and matches the user's "keep it in instructions,
  portable" requirement.
- **Non-destructive curation by design** — backup→archive→pin, never delete,
  provenance-gated. Many self-evolution projects delete or mutate aggressively.
- **Agent-agnostic from day one** — SKILL.md + AGENTS.md adapters, whereas
  several are Claude- or app-locked.

---

## 6. Sources
- GitHub Search API → `research/gh_search.json` (8 queries × 5 repos).
- GitHub Repos/Tree API → `research/gh_repos.json` (top-level layout of 8 repos).
- GitHub Contents API → `research/gh_readmes.json` (README heads of 6 repos).
