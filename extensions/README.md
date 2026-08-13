# Extension points reference — how to build a plugin

Plugins live in `extensions/<plugin>/` with a `plugin.yaml` manifest.
Register every plugin in `MANIFEST.md` (`Installed extensions` table).

## Minimal plugin.yaml

```yaml
name: my-plugin
version: 1.0.0
core: ">=2.0.0"
provenance: third-party
enabled: true
extension_points: [skill]
contributes:
  skills:
    - skills/
description: "Does a thing."
```

## Contributing a skill

`extensions/<plugin>/skills/<name>/SKILL.md` — same structure as any core skill:
frontmatter (name, description, version, provenance) + numbered steps + Pitfalls
+ verification. The description's first ~57 chars should state the trigger.

## Contributing a tool

`extensions/<plugin>/tools/<name>` — an executable (python/bash script). The
agent may invoke it; keep it self-contained and non-destructive by default.

## Contributing memory

`extensions/<plugin>/memory/*.md` — durable facts merged into memory at bootstrap.
Keep them declarative and scoped to what the plugin owns.

## Contributing hooks

In `plugin.yaml`:

```yaml
hooks:
  on-save: hooks/on-save.sh
```

Paths are relative to the plugin dir. Hook runs with `PLUGIN_DIR` and `EVENT`
in the environment. Non-zero exit → warn, never abort the framework.

## Contributing a policy

`plugin.yaml` may add a `policy:` block (e.g. `archive_after_days: 365`,
`allow_archive: [agent]`). These override curator defaults for that plugin's
items. If a policy contradicts a hard rule in CORE.md §16, the hard rule wins.

## Declaring an external system (MCP)

The `mcp` extension point lets a plugin **declare** MCP servers it may launch,
without the framework bundling or installing anything (no-software rule):

```yaml
mcp_servers:
  - name: example-db
    command: "npx @modelcontextprotocol/server-postgres"
    args: []
    env:
      DATABASE_URL: "$EXAMPLE_DB_URL"   # resolved at launch, not stored
```

`command`/`args`/`env` describe *how to reach* the system; the agent launches it
with the tools already present. `env` placeholders (`$VAR`) are resolved at
launch. The validator checks each server has `name` + `command`.

## Restricting tools

`allowed_tools` bounds which tools a plugin may use (a port of the agentskills
experimental `allowed-tools` field):

```yaml
allowed_tools: [bash, python, git]
```

The validator rejects unknown tool names against a known set.

## Contributing an adapter

An adapter bridges this framework to another agent's format — e.g. exporting
core content as an `AGENTS.md` for Copilot/Codex, or a `.claude/skills/`
layout. Ship it as a tool + document its usage in the plugin README.

## Compatibility

- Bump MAJOR on breaking changes, MINOR on additive, PATCH on fixes.
- Declare the `core` range you target; bootstrap enforces it.
- Unknown `extension_points` or a broken `core` range → plugin is quarantined
  into `curator/archived/`, never deleted, never silently run.
