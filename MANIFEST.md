# Agentic Foundation Manifest

- **Framework:** foundation
- **Version:** 3.3.0
- **min_core_version:** 3.3.0
- **Provenance of this file:** core

## Extension points (seams) — see CORE.md §8

| Point | Contributes | Example |
|-------|-------------|---------|
| `skill`   | SKILL.md procedures              | git-workflow skill |
| `memory`  | memory facts / schema            | credential facts |
| `tool`    | executable helpers               | release.py |
| `hook`    | lifecycle callbacks              | lint on save |
| `policy`  | curator / collection overrides   | archive thresholds |
| `adapter` | bridge to other agent formats    | AGENTS.md exporter |
| `mcp`     | declared MCP servers             | Postgres MCP server |

## Hook events (ordered lifecycle) — see CORE.md §10

`on-bootstrap` → `on-load` → `on-save` → `on-curate` → `on-shutdown`

## Installed extensions

| Name | Version | Core range | Extension points | Enabled | Provenance |
|------|---------|-----------|------------------|---------|-----------|
| `example-plugin` | 1.1.0 | `>=2.0.0` | skill, tool, hook, policy, mcp | true | third-party |

## Core skills (`core-skills/`, provenance: core, curator-immune) — see CORE.md §11

| Name | Version | Purpose |
|------|---------|---------|
| `foundation-operator` | 2.1.0 | Operate on the framework across all six edges: audit consistency, extend/improve adapters, extensions, spec-kit packaging, stores, curator (incl. skill improvement & extraction policy), and tooling; bump core versions. Keeps every edge in sync. |
| `extract-learnings` | 1.0.0 | Extract work learnings at task/session end (What/How/Decisions/Gotchas/Repeat/Avoid/Resume) so the next agent starts ahead. |

## Changelog

- **3.3.0** — Security & trust section added (CORE.md §19): risk-tier assessment,
  review checklist, content-hash attestation, trust states. Enforced evaluation
  gate + recall limit added to §15.
- **3.2.0** — Added §1 Motivation: why the framework exists and what it is a
  foundation *for* (problem, idea, foundation-vs-skill, three commitments,
  design principles). Renumbered all sections to 1–18 and updated every
  cross-reference across the framework.
- **3.1.0** — Skill improvement & mutation policy added (CORE.md §12.2–12.4):
  patch-not-rewrite, one-skill-one-job, version-bump-on-change, the **extraction
  (crossing) rule** — when a skill's mutation crosses significantly with a
  distinct potential skill (≥2 signals), extract it into its own skill — and a
  merge/consolidation policy. Operator skill updated with the same rules.
- **3.0.0** — Refactor to a clean, sequential spec (17 sections, logical flow:
  identity → contract → structure → data → extensibility → lifecycle → quality →
  governance → verification). Fixed broken numbering, consolidated hooks, added
  `mcp` to the seams, aligned manifest + adapters.
- **2.1.0** — Learnings store added: distilled how-to-work knowledge
  (What/How/Decisions/Gotchas/Repeat/Avoid/Resume) captured at task/session end
  via the new `extract-learnings` core skill, so the next agent starts ahead.
  Loaded at session start. Five stores now: memory, profile, skills, episodic,
  learnings.
- **2.0.1** — No-software principle codified: `mcp` extension point added
  (declared external systems, not bundled); `allowed_tools` permission scoping;
  episodic memory store + memory lifecycle (provenance `@since`/`@retain`,
  load policy, forget-by-archive, consolidation); authoring rules; skill
  evaluation + trace log. Validator rewritten stdlib-only (no pyyaml).
- **2.0.0** — Core split into a framework: manifest + extension points
  (skill, memory, tool, hook, policy, adapter). Directory convention with a
  single root. Semver compatibility gate. Curation by provenance.
- **1.0.0** — Standalone self-management skill (memory/profile/skills/curator).
