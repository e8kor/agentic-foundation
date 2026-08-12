# Foundation — Industry Research & Gap Analysis

Companion to `CORE.md`. Documents what the industry calls the things Foundation
does, the best-practice sources, and a gap analysis of what Foundation has vs.
what mature agent-skill/memory ecosystems provide. Sources cited inline with
URLs; full raw search/extract snapshots in `research/`.

Scope: agent skills, agent memory, plugin/extension ecosystems, MCP, AGENTS.md,
self-evolving skills, observability. Research date: Aug 2026.

---

## 1. How the industry names what Foundation does

### Skills = procedural knowledge (Anthropic Agent Skills, open standard)
The dominant model is **Agent Skills**: a directory containing a `SKILL.md`
(Markdown + YAML frontmatter) plus optional `scripts/`, `references/`, `assets/`.
Anthropic published it as an **open standard** (Dec 2025) for cross-platform
portability. The canonical framing: *"MCP is about capabilities. Agent Skills
are about expertise."* — skills give the agent *procedural knowledge* (how to
review code, cut a release), MCP gives it *external system access* (databases,
APIs, browsers).
- https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- https://github.com/agentskills/agentskills (open spec)
- https://github.com/anthropics/skills (reference implementations)

**SKILL.md frontmatter fields (per agentskills spec):**
| Field | Required | Notes |
|-------|----------|-------|
| `name` | yes | ≤64 chars, lowercase/numbers/hyphens |
| `description` | yes | ≤1024 chars, "what + when to use" |
| `license` | no | |
| `compatibility` | no | env requirements |
| `metadata` | no | arbitrary key-value map |
| `allowed-tools` | no | pre-approved tools (experimental) |

**Authoring best practice (Claude docs):** *concise is key* — the context window
is a public good. Only name+description pre-load at startup; SKILL.md is read
only when relevant. So the description is the trigger; the body should be lean.
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices

### AGENTS.md = cross-agent instruction convention
A separate standard (agents.md) for per-repo agent instructions. Adopted by
GitHub Copilot, Codex, Cursor, and more. Complements README.md (which is for
humans) with agent-focused context: build steps, tests, conventions.
- https://agents.md/
- https://github.com/agentsmd/agents.md

### Memory = a data-management system, not a blob
Industry (arXiv "Agent-Native Memory System") decomposes agent memory into four
core modules:
1. **Representation & storage** — how memories are structured and persisted.
2. **Extraction** — what gets stored from a session.
3. **Retrieval & routing** — which memory to load, when.
4. **Maintenance** — consolidation, forgetting, staleness, lifecycle.

A widely-cited practical guide (hidekazu-konishi) frames it as three decisions:
**what to store, when to load, when to forget.** Working / long-term / procedural
memory; forgetting & staleness are first-class design concerns, not afterthoughts.
- https://arxiv.org/html/2606.24775
- https://hidekazu-konishi.com/entry/ai_agent_memory_design_guide.html
- Episodic-semantic memory: https://aclanthology.org/2026.findings-acl.1108/
- Graph-based agent memory: https://arxiv.org/html/2602.05665

Industry distinguishes **episodic** (session history/events), **semantic**
(durable facts), and **procedural** (skills) memory.

### Plugins = packaged, distributable components
The **Agent Plugins Specification** (agentplugins.org) defines a canonical,
versioned plugin package format: plugin package model, a **manifest**, component
**discovery**, named **component types**, and versioning. OpenAI also defines a
plugin/extension architecture. This is the closest industry analogue to
Foundation's `extensions/` + `plugin.yaml`.
- https://github.com/agentplugins/agent-plugins-spec
- https://developers.openai.com/plugins/concepts/plugins

### MCP = the tool/capability protocol
MCP is the standard for *external system access*: a server exposes **tools** the
agent calls. Skills ≠ MCP; they're complementary. MCP servers are running
processes; skills are markdown knowledge.
- https://www.agentshelf.dev/blog/mcp-vs-agent-skills
- https://academy.claude.com/courses/introduction-to-agent-skills

### Self-evolving skills = the research frontier
Work on **self-evolution of skills**: agents autonomously generate/refine
skills, with **verification** loops (co-evolving a surrogate verifier that gives
feedback without ground-truth tests). EvoSkills, SkillOpt (Microsoft).
Foundation's curator-consolidation is the conservative, on-premises cousin of
this. These papers confirm curation/evolution is the right direction — and that
verification is the missing ingredient.
- https://arxiv.org/abs/2604.01687 (EvoSkills)
- https://microsoft.github.io/SkillOpt/

### Observability & evaluation
LangChain/Harrison Chase: agent observability = **tracing** (what the agent
actually did), and **traces power evaluation**. You can't validate improvements
without systematic eval. Different from software observability — no stack trace,
you're debugging reasoning.
- https://www.langchain.com/blog/agent-observability-powers-agent-evaluation

---

## 2. Gap analysis — Foundation vs. industry

Legend: ✔ have it · ◐ partial · ✘ missing

| Capability | Industry name | Foundation | Gap |
|-----------|----------------|-----------|-----|
| Procedural skills | Agent Skills (open std) | ✔ `skills/`, `core-skills/` | **Not conformant to the agentskills spec** (missing `license`/`compatibility`/`allowed-tools` frontmatter; our `metadata.foundation.provenance` is a custom extension). |
| Skill authoring discipline | "concise is key" | ◐ | Description triggers load; body should be lean. Add explicit authoring rules. |
| Cross-agent instructions | AGENTS.md | ✔ `AGENTS.md` adapter | Good. Could note agents.md standard + per-repo vs global. |
| **External tools/capabilities** | **MCP** | ✘ | **Biggest gap.** No MCP bridge. We have "tool" as a file-based extension point, but no standard protocol for external systems (DBs, APIs, browsers). |
| Memory: semantic (facts) | semantic memory | ✔ `memory/memory.md` | ✔ |
| Memory: procedural | procedural memory | ✔ skills | ✔ |
| Memory: **episodic (session history)** | episodic memory | ✘ | No session-history store / working memory concept. Our profile+memory are semantic only. |
| Memory: **retrieval & routing** | retrieval/routing | ◐ | Flat markdown + "read at bootstrap." No semantic/vector retrieval, no "which memory to load when" routing. |
| Memory: **extraction** | extraction | ◐ | "Save on preference/correction" is manual. No systematic extraction policy. |
| Memory: **forgetting/staleness/TTL** | maintenance/forgetting | ◐ | Curator handles *skill* staleness; *memory* has no TTL/forgetting policy. |
| Memory: consolidation | consolidation | ◐ | Curator optional consolidation (off by default). |
| **User profile/persona** | user-preference memory, personalization | ✔ `memory/profile.md` | Good; matches AWS Bedrock / Glean user-preference memory. |
| Plugins (distributable) | Agent Plugins spec | ◐ | We have `extensions/` + `plugin.yaml` + discovery + versioning + quarantine. **Missing a packaged/distributable plugin format** (tar.gz + registry) and component-type enumeration. |
| **Security / tool permissioning** | allowed-tools | ✘ | No permission scoping for skills/tools. `allowed-tools` is experimental in the spec but a real concern. |
| Versioning & compat gate | semver + conformance | ✔ `core` range + quarantine | Strong. Could add `min_core_version`. |
| Self-evolution with **verification** | EvoSkills/SkillOpt | ◐ | Curator consolidates conservatively; **no automated skill evaluation/verification loop** (test a skill against examples before adopting). |
| **Observability** | tracing + evaluation | ◐ | `.usage.json` telemetry exists. **No trace/log of what skills actually did; no skill evaluation harness.** |
| Curator safety | (best-practice) | ✔ backup→archive→pin, never delete | Strong. |

---

## 3. Recommended additions to Foundation (priority order)

### P0 — align to the open standards (cheap, high value)
1. **Conform SKILL.md frontmatter to the agentskills spec** — add optional
   `license`, `compatibility` fields; keep `metadata` for provenance. This makes
   Foundation skills portable into Claude Code / Copilot / Codex verbatim.
2. **Add an authoring best-practices section** (concise description = trigger;
   lean body; numbered steps + pitfalls + verify) — we mostly do this; codify it.

### P1 — close the two biggest capability gaps
3. **Add an `mcp` extension point** — a plugin can declare MCP server(s) to
   expose external-system tools (the industry capability protocol). This is the
   single largest missing capability vs. the ecosystem.
4. **Add memory retrieval & routing** — define *when* memory is loaded: not just
   "injected every turn," but "episodic history on demand; semantic facts on
   demand; profile always." Document a retrieval policy even if backing is flat
   files (future: vector index).

### P2 — memory lifecycle completeness
5. **Add an episodic (session) store** — `memory/episodic/` or a session log,
   distinct from semantic facts, with its own curation (consolidate old sessions,
   forget beyond TTL).
6. **Add a forgetting/TTL policy for memory** — `memory.md` entries carry a
   `@since` / expiry; curator prunes stale facts (mirrors the existing skill
   staleness, extended to memory).

### P3 — reliability & security
7. **Add `allowed-tools`/permission scoping** for skills/tools (matching the
   agentskills experimental field) so a plugin's reach is bounded.
8. **Add a skill evaluation harness** — the verification loop: before the curator
   adopts/consolidates a skill, run it against example inputs and keep a pass/fail
   trace (the EvoSkills/SkillOpt insight, done conservatively). Pair with
   observability: a `curator/.traces/` log of curation + skill-use events.

### P4 — distribution (optional, later)
9. **Packaged plugin format + registry** — tar.gz plugin bundles + a catalog, per
   the Agent Plugins spec, so extensions can be shared across machines/agents.

---

## 4. Sources (raw data)

- `research/search_results.json` — 10 queries × 5 results.
- `research/extract_batch1.json`, `research/extract_batch2.json` — extracted
  content from the key authoritative pages.
