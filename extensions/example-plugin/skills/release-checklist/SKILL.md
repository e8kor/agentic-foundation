---
name: release-checklist
description: "Release workflow: verify tests, build, changelog, tag. Use before cutting a release."
version: 1.0.0
author: example-plugin
license: MIT
metadata:
  foundation:
    provenance: third-party
    plugin: example-plugin
---

# Release Checklist

Use this before cutting a release. Follow in order; do not skip verification.

1. **Run the test suite** — `./scripts/test` (or the repo's equivalent). Fix any
   failure before proceeding; do not release red.
2. **Build** — produce the artifact: `./scripts/build`. Confirm the artifact
   exists at the expected path.
3. **Update the changelog** — add this release's notes under the new version
   heading; date it.
4. **Bump the version** — edit the version file per the repo's scheme
   (semver unless stated otherwise).
5. **Tag** — create an annotated tag: `git tag -a v<version> -m "v<version>"`.
6. **Verify** — confirm the tag matches HEAD and the changelog + version file are
   committed.

## Pitfalls

- Releasing red: never tag until the suite is green.
- Forgetting to commit before tagging — the tag must point at committed work.
- Bumping the version in two places and forgetting one.

## Verify

`git status --porcelain` clean, tag present, changelog updated.
