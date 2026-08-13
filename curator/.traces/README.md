# Curator trace log — observability as convention (plain text, no daemon).

Per CORE.md §12: one small file per curation or skill-use event, recording
WHAT changed, WHY, and the RESULT. This is the framework's audit trail.

Each file: <timestamp>-<event>.md  (e.g. 2026-08-12T10-00-consolidate.md)
Contents: what | why | before | after | result | verification.

Lifecycle: traces are kept for a retention window, then archived into
`../archived/`. Never deleted (hard rule #1).

This directory is created by the framework; do not delete it.
