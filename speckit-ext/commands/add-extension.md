---
description: "Scaffold a new Foundation extension/plugin from the example template."
tools: []
---

# Add a Foundation Extension

Scaffolds a new `extensions/<plugin>/` directory with a `plugin.yaml` manifest,
so you can build a plugin that plugs into the Foundation framework's extension
points (skill, memory, tool, hook, policy, adapter, mcp).

## Prerequisites

1. Framework root resolved (same as the audit command).
2. You have decided on a plugin name (lowercase-hyphens, e.g. `my-plugin`).

## User Input

$ARGUMENTS

The first argument is the plugin id (e.g. `my-plugin`). If omitted, use `my-plugin`.

## Steps

### Step 1: Resolve the framework root

```bash
ROOT="${SPECKIT_FOUNDATION_FRAMEWORK_ROOT:-.foundation}"
[ -d "$ROOT" ] || ROOT="."
PLUGIN="${1:-my-plugin}"
```

### Step 2: Scaffold the extension directory

```bash
mkdir -p "$ROOT/extensions/$PLUGIN/skills" \
         "$ROOT/extensions/$PLUGIN/tools" \
         "$ROOT/extensions/$PLUGIN/hooks" \
         "$ROOT/extensions/$PLUGIN/memory"
echo "Scaffolded: extensions/$PLUGIN/"
```

### Step 3: Create the plugin manifest

Create `extensions/$PLUGIN/plugin.yaml` with:

```yaml
name: $PLUGIN
version: 0.1.0
core: ">=2.0.0"
provenance: third-party
enabled: true
extension_points: [skill, tool]
contributes:
  skills:
    - skills/
  tools: []
hooks: {}
description: "Describe what $PLUGIN contributes."
```

Validate the name matches the schema (lowercase, hyphens) and that every
extension point listed is one of: skill, memory, tool, hook, policy, adapter, mcp.

### Step 4: Register in MANIFEST.md

Add a row to the "Installed extensions" table in `MANIFEST.md`:

```text
| `$PLUGIN` | 0.1.0 | `>=2.0.0` | skill, tool | true | third-party |
```

### Step 5: Validate

```bash
cd "$ROOT"
python3 tools/validate_manifest.py --root .
```

Must exit 0. If it fails, read the error (missing field, unknown extension
point, core-range incompatibility) and fix before continuing.

## Configuration Reference

- `framework_root` (default `.foundation`).
- Env override: `SPECKIT_FOUNDATION_FRAMEWORK_ROOT`.

## Notes

- Never hard-delete a plugin — disable (`enabled: false`) or archive to
  `curator/archived/` (with a backup). See the foundation-operator skill.
- Full plugin schema: `extensions/README.md`.
