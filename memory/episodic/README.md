# Episodic memory log — per-session history, append-only.

Purpose (per CORE.md §4 Store 3): record *what happened*, not *what is true*.
Each session appends a dated file here. These entries are NOT injected every
turn; load them only on continuity requests.

Lifecycle (per CORE.md §12):
- @since tags track provenance on every entry.
- Old episodes are consolidated into `../memory.md` (durable facts promoted),
  then archived past retention. Never used alone to justify a current fact.

Files:
- YYYY-MM-DD.md — one per session.

This directory is created by the framework; do not delete it (hard rule #1).
