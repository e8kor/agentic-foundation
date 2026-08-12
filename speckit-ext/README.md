# Foundation — Spec Kit Extension

Exposes the **Foundation skill framework**'s self-management nature as
[Spec Kit](https://github.com/github/spec-kit) extension commands, so a
spec-kit-driven project gets the same skills/memory/curator discipline without
running a full agent.

## What it provides

| Command | Purpose |
|---------|---------|
| `/speckit.foundation.audit` | Validate manifests, check drift, verify curator state |
| `/speckit.foundation.add-extension` | Scaffold a new `extensions/<plugin>/` from the schema |
| `/speckit.foundation.memory` | Record a durable memory fact or read the store |
| hook `after_plan` | Optional audit after planning |

## Install (dev)

```bash
cd /path/to/your/spec-kit-project
specify extension add --dev /path/to/hermes-foundation/speckit-ext
specify extension list        # should show Foundation Skill Framework v1.0.0
```

Or from a git URL/ZIP release once published.

## Configure

```bash
cp .specify/extensions/foundation/foundation-config.template.yml \
   .specify/extensions/foundation/foundation-config.yml
# edit framework_root, curator thresholds, load policy
```

## Use

```bash
/speckit.foundation.audit
/speckit.foundation.add-extension my-plugin
/speckit.foundation.memory save "The build uses uv" @since 2026-08-12
/speckit.foundation.memory read
```

## Manifest

`extension.yml` follows the Spec Kit extension schema v1.0. Requires spec-kit
`>=0.1.0`. See the full API reference in the spec-kit repo:
`extensions/EXTENSION-API-REFERENCE.md`.

## License

MIT. Part of the `e8kor/hermes-foundation` project.
