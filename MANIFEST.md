# Foundation Framework Manifest

- **Framework:** foundation
- **Version:** 2.0.0
- **min_core_version:** 2.0.0
- **Provenance of this file:** core

## Extension points (seams)

| Point | Contributes | Example |
|-------|-------------|---------|
| `skill`   | SKILL.md procedures              | git-workflow skill |
| `memory`  | memory facts / schema            | credential facts |
| `tool`    | executable helpers               | release.py |
| `hook`    | lifecycle callbacks              | lint on save |
| `policy`  | curator / collection overrides   | archive thresholds |
| `adapter` | bridge to other agent formats    | AGENTS.md exporter |

## Hook events (ordered lifecycle)

`on-bootstrap` → `on-load` → `on-save` → `on-curate` → `on-shutdown`

## Installed extensions

| Name | Version | Core range | Extension points | Enabled | Provenance |
|------|---------|-----------|------------------|---------|-----------|
| `example-plugin` | 1.1.0 | `>=2.0.0` | skill, tool, hook, policy, mcp | true | third-party |

## Core skills (`core-skills/`, provenance: core, curator-immune)

| Name | Version | Purpose |
|------|---------|---------|
| `foundation-operator` | 1.1.0 | Governance: add/update/remove extensions, audit consistency, curate skills, manage memory lifecycle, declare MCP, bump core versions. Keeps the framework itself consistent. |

## Changelog

- **2.0.1** — No-software principle codified: `mcp` extension point added
  (declared external systems, not bundled); `allowed_tools` permission scoping;
  episodic memory store + memory lifecycle (provenance `@since`/`@retain`,
  load policy, forget-by-archive, consolidation); authoring rules; skill
  evaluation + trace log. Validator rewritten stdlib-only (no pyyaml).
- **2.0.0** — Core split into a framework: manifest + extension points
  (skill, memory, tool, hook, policy, adapter). Directory convention with a
  single root. Semver compatibility gate. Curation by provenance.
- **1.0.0** — Standalone self-management skill (memory/profile/skills/curator).
