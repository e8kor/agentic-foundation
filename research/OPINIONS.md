# Agentic Foundation — Research: Genuine Opinions on Foundational Skill Frameworks

Companion to `CORE.md` and `research/RESEARCH.md`. Captures the **genuine,
unfiltered opinions** — praise, skepticism, and criticism — about foundational
skill frameworks like ours, from the open-source community and from
organizations. Sources are cited inline; this is a synthesis of what practitioners
actually say, not vendor marketing.

Research date: Aug 2026.

---

## 1. The honest consensus

Across Hacker News, engineering blogs, and enterprise docs, the community has
converged on a nuanced view:

- **Skills are real and valuable** — but they are a **context-management
  strategy**, not a new capability. As Steve Kinney puts it: *"You're not making
  the model more capable by handing it a skill. You're deciding what it should
  know, when it should know it, and how to prove the work is done."*
- **The hard problems are routing, scoping, and verification** — not writing the
  `SKILL.md`. The actual skill file is the easy part.
- **Skills are "discipline encoded as infrastructure"** — the contrarian take is
  that you can approximate everything a skill does with well-structured prompts
  and a good `CLAUDE.md`. The difference is *consistency*: a skill makes you
  follow the checklist every time, not just when you remember to.

---

## 2. What the open-source community genuinely says

### 2.1 The praise (why they're worth it)

- **Progressive disclosure is the real innovation.** Loading only name+description
  at startup, then the body on match, then supporting files on demand — this is
  what lets you install dozens of skills without blowing the context window.
  Simon Willison: *"Claude Skills are awesome, maybe a bigger deal than MCP."*
- **Cross-vendor portability is real.** The open Agent Skills standard is adopted
  by ~40 clients (Copilot, VS Code, Cursor, Codex, Gemini CLI, Goose, OpenCode,
  Roo Code, Spring AI, Databricks, Snowflake). VS Code treats skills as
  open-standard artifacts — the clearest proof the format is becoming
  cross-agent infrastructure.
- **Skills fix the "always-on bloat" problem.** Pulling specialized workflows
  out of `CLAUDE.md` into on-demand skills dramatically improves routing accuracy
  and output relevance. The always-on file stays focused.

### 2.2 The skepticism (the honest pushback)

- **"It's just markdown / a prompt-engineering trick."** A vocal contingent
  argues skills are a design pattern, not a technology. Hacker News: *"Skills are
  cool, but to me it's more of a design pattern/prompt engineering trick than
  something in need of a hard spec."* And: *"Fundamentally you're getting hyped
  over a framework to append text to your prompt?"*
- **Context isn't free.** Every matching skill loads into context. As the
  library grows, you pay in tokens, latency, and attention budget. More skills
  competing for relevance = more likely the wrong one wins.
- **Triggering is fuzzy and non-deterministic.** Skills activate by description
  matching, not deterministic rules. A subtle reword changes when one fires.
  Two overlapping skills can both fire, neither fire, or fire in the wrong order.
  There's no compiler to catch this — you find out in production. Practitioners
  report skills "suddenly stopping firing for no reason."
- **Non-determinism leaks into workflows.** A skill is a hint the agent may or may
  not act on, in an order it picks. Same input, potentially different path. That's
  fine for exploration, painful for anything you need to test or audit.
- **Testing is hard.** You can't unit-test "the agent should use the docx skill
  when asked for a Word doc." You write evals — slow, expensive, probabilistic.
  CI cycles balloon; regressions hide because an eval suite "always passes at
  around 94%."
- **It's a new kind of tech debt.** Adding a skill is often easier than fixing the
  underlying flow. Six months later you have a layer of skills papering over real
  problems, and refactoring the real code means rewriting all the skills that
  depend on its quirks.
- **Skills don't travel well.** Paul Swail: workflows are context-specific, closer
  to dotfiles than code libraries. Nobody installs someone else's `.bashrc`
  unchanged. Most shared skills get forked and customized per project, then the
  update path is abandoned. There's no structural separation between first-party,
  managed, and forked skills, and no author namespacing.

### 2.3 The security alarm (the biggest genuine concern)

This is where the community is most worried, and it's backed by real incidents:

- **Skills are an execution surface.** A skill is a folder of instructions and
  scripts the agent loads and runs with the agent's full permissions. A malicious
  skill can execute with the same access as your agent — hidden instructions,
  embedded prompt injection, or scripts with full shell access.
- **OWASP Agentic Skills Top 10 — AST02 (Supply Chain Compromise, Critical):**
  skill registries lack the provenance controls of mature package ecosystems.
  Real evidence: a malicious skill entered a ~36K-star community marketplace via
  an accepted PR and reached 26,000+ agents; a scan of 142,836 live skills found
  ~12.4% rest on at least one untrusted external resource; 925 skills serving
  ~134K agents sit on instantly hijackable sources (deleted accounts,
  unregistered packages, expired domains).
- **The "lethal trifecta"** (Simon Willison): skills + tools + untrusted input
  combine into a dangerous attack surface. Claude Code CVEs show repo config
  files becoming execution paths — cloning a malicious repo can trigger RCE.
- **The spec itself lacks security guidance.** A GitHub issue (#418) on the
  agentskills spec asked for provenance/attestation and a Security Considerations
  section; the maintainer closed it as "outside the scope of the spec," arguing
  attestation belongs at the distribution layer. The gap remains open.

### 2.4 The governance criticism (spec-level)

Dachary Carey's deep-dive is the most cited critique of the Agent Skills *spec*:

- **The spec is unversioned.** No v1.0/v1.1, no changelog, no review process for
  breaking changes. Changes land as "visual cleanups" that alter what a valid
  skill looks like.
- **It's Anthropic-controlled.** The agentskills org has two members, both
  Anthropic-affiliated. Community PRs proposing governance (versioning, changelogs,
  labels) get converted to discussions that don't get actioned.
- **Platform-specific bias.** The `allowed-tools` field uses Claude-specific tool
  names (`Read`, `Write`, `Bash`) in a supposedly platform-neutral spec. A skill
  that works on Claude Code may silently fail on Cursor or Copilot.
- **The incentive problem:** Anthropic benefits from a spec that tracks their
  product; everyone else benefits from a stable, versioned, neutral one. Right
  now Anthropic's goals win by default.

---

## 3. What organizations genuinely say (enterprise perspective)

Anthropic's own enterprise guide and the broader org-adoption discourse reveal
what organizations actually care about:

### 3.1 The value organizations see

- **Skills encode organizational knowledge.** They capture "how we do it here" —
  internal libraries, conventions, workflows — that the model doesn't know.
- **They're cheap to start.** Writing a skill is markdown in folders. Low barrier
  to entry for teams.
- **They're the portable, vendor-neutral way to encode repeatable workflows.**
  Recommended for any team building with coding agents.

### 3.2 The governance organizations demand

The enterprise guide is essentially a **governance checklist** — this is what orgs
need before they'll deploy skills at scale:

- **Security review and vetting** — a risk-tier assessment (code execution,
  instruction manipulation, MCP references, network access, hardcoded creds,
  filesystem scope) and a review checklist before any skill is approved.
- **Evaluation before deployment** — require 3–5 representative queries per skill
  (should-trigger, should-not-trigger, ambiguous edge cases), tested across
  models. Evaluate triggering accuracy, isolation, coexistence, instruction
  following, output quality.
- **Separation of duties** — skill authors should not be their own reviewers.
- **Lifecycle management** — track usage, rerun evals periodically, deprecate
  skills that consistently fail.
- **Recall limits** — limit the number of active skills; each skill's metadata
  competes for attention. Stop adding when recall degrades. (API caps at 8 skills
  per request.)
- **Start specific, consolidate later** — narrow workflow skills first, merge
  into role-based bundles only when evals confirm equivalent performance.
- **Internal registry** — purpose, owner, version, dependencies, evaluation status.
- **Version control + rollback** — pin versions, checksums, signed commits,
  rollback plan.
- **Role-based bundles** — group skills by org role (sales, engineering, finance)
  to keep each user's active set focused.

### 3.3 The organizational risks

- **Supply-chain trust** is the #1 blocker. Orgs need private mirrors, allowlists,
  automated scanning, change management, and inventory tracking. Trail of Bits:
  "curate dependencies in an internal/approved marketplace, pin versions, and
  control who can publish or update — automated scanning cannot replace that."
- **Onboarding gets weirder.** New teammates must learn which skills exist, when
  they trigger, how they compose, which are load-bearing. That knowledge lives in
  descriptions and behavior, not stack traces — it becomes tribal knowledge.
- **Maintenance is owned, not free.** Skills age; APIs change; model behavior
  drifts. There's no clean changelog telling you what broke. You discover the
  breakage when the agent quietly does the wrong thing.

---

## 4. What this means for Agentic Foundation

Our framework already addresses several of the community's biggest concerns, and
has clear gaps. Honest self-assessment:

### 4.1 Where we're already strong (validated by the research)

- **Progressive disclosure / load policy** (CORE.md §7) — we explicitly treat
  context as a public good and route by load policy. This is the community's #1
  praised mechanism.
- **One-skill-one-job + extraction policy** (CORE.md §12) — directly addresses
  the "bloated skill" and "routing ambiguity" failure modes. The crossing rule
  (extract when a skill crosses with a distinct concern) is exactly what the
  community says prevents routing competition.
- **Evaluation / verification loop** (CORE.md §15) — the community and enterprise
  guide both say "build evals first, verify before adopting." We have this as a
  convention.
- **Safe curation** (backup → archive → pin, never delete) — addresses the
  "skills are tech debt" concern by making mutation deliberate and reversible.
- **Provenance** — we track who owns what, which the community says is missing
  from the ecosystem.

### 4.2 Where we have gaps (the honest gaps the research exposes)

1. **Security review is not yet a first-class policy.** The community's biggest
   concern is supply-chain trust. We have `allowed_tools` and provenance, but no
   explicit **security review checklist** (the enterprise guide's risk-tier
   assessment) before adopting a skill. This is the highest-value gap to close.
2. **No attestation / integrity signal.** OWASP AST02 and the spec issue #418 both
   call for content-hash binding and provenance. We could add a `@digest` /
   content-hash convention to skills.
3. **Evaluation is a convention, not enforced.** The enterprise guide requires
   eval suites before deployment. Ours is "≥2 uses, then verify" — lighter than
   what orgs demand.
4. **No recall limit guidance.** The community warns against too many active
   skills. We don't yet cap or bundle skills by role.
5. **Distribution/portability is real but not absolute.** Client-specific
   metadata and deployment differ. Our adapters help, but the "boring work" of
   distribution and control planes is where portability breaks.

### 4.3 The strategic takeaway

The research validates our **core design choices** (progressive disclosure,
one-skill-one-job, safe curation, provenance, evaluation) — these are exactly what
the community and enterprises say matter. The biggest opportunity is to **add a
security-review policy and an integrity/attestation convention**, because that is
the single most-cited genuine concern across both open source and organizations.

---

## 5. Sources

- Steve Kinney, "Agent Skills, Stripped of Hype" — stevekinney.com/writing/agent-skills
- Jorge Castillo, "The Downsides of Agentic Skills" — newsletter.jorgecastillo.dev
- Paul Swail, "Agent skills don't travel well" — paulswail.com/agent-skills-distribution
- Dachary Carey, "Why a Platform Shouldn't Own an Open Spec" — dacharycarey.com
- Simon Willison, "Agent Skills" — simonwillison.net/2025/Dec/19/agent-skills
- Tom MacWright, "First-run with agent skills from Anthropic" — macwright.com
- Ry Walker Research, "Anthropic Skills" — rywalker.com/research/anthropic-skills
- Anthropic, "Equipping agents for the real world with Agent Skills" — anthropic.com
- Anthropic, "Skills for enterprise" — platform.claude.com/docs/.../enterprise
- OWASP Agentic Skills Top 10, AST02 (Supply Chain Compromise) — owasp.org
- agentskills/agentskills issue #418 (security/verification gap)
