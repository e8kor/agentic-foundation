# GitHub Issues → Kanban → Agent Dispatch Listener

Bridges GitHub issues into Hermes' kanban board, assigns them to profiles, and
syncs completed work back to GitHub. Built on Hermes' native kanban + webhook
systems — no custom board, no extra daemon.

## Architecture

```
GitHub issue (opened/reopened)
        │  POST /webhooks/github-issues-to-kanban  (HMAC-signed)
        ▼
hermes webhook  ──script──▶  github-issue-to-kanban.py
        │                        │  creates kanban task, assigns profile
        │                        ▼
        │              [SILENT]  (no agent run — dispatcher does the work)
        ▼
kanban board (agentic-foundation)
        │  gateway embedded dispatcher (every 60s)
        ▼
assigned profile (coder/researcher/writer/reviewer/orchestrator) runs the task
        │
        ▼  task completed
kanban-sync-sweep.py  (cron, every 5m)
        │  kanban-sync-back.py
        ▼
GitHub issue: comment + close
```

## Components

| Component | Path | Role |
|-----------|------|------|
| Webhook route | `hermes webhook subscribe github-issues-to-kanban` | Receives GitHub `issues` events |
| Bridge script | `~/.hermes/scripts/github-issue-to-kanban.py` | Issue → kanban task, assigns profile by label |
| Kanban board | `agentic-foundation` | Task queue |
| Dispatcher | gateway embedded (every 60s) | Spawns assigned profile |
| Sync-back | `~/.hermes/scripts/kanban-sync-back.py` | Completed task → GitHub comment + close |
| Sweep | `~/.hermes/scripts/kanban-sync-sweep.py` | Idempotent scan of done tasks → sync-back |
| Cron | `kanban-github-sync` (every 5m) | Runs the sweep |

## Profile assignment (by label)

| Label | Profile |
|--------|---------|
| `bug`, `feature`, `refactor` | `coder` |
| `research` | `researcher` |
| `docs` | `writer` |
| `review` | `reviewer` |
| (none / other) | `orchestrator` |

## Setup (already done)

1. **Webhook platform** — enabled in `~/.hermes/config.yaml` (`platforms.webhook.enabled: true`), listening on `:8644`.
2. **Kanban board** — `hermes kanban boards create agentic-foundation`.
3. **Bridge script** — `~/.hermes/scripts/github-issue-to-kanban.py`.
4. **Webhook subscription** — `hermes webhook subscribe github-issues-to-kanban --events issues --script github-issue-to-kanban.py`.
5. **Sync-back + sweep** — `~/.hermes/scripts/kanban-sync-back.py`, `kanban-sync-sweep.py`.
6. **Cron** — `kanban-github-sync` (every 5m, no_agent, runs the sweep).
7. **Dispatcher** — runs inside the gateway (already active); no standalone daemon needed.

## To wire the REAL GitHub webhook (DONE — live via zrok)

The webhook is exposed publicly via **zrok** and registered in the GitHub repo.
Real GitHub issues now flow through automatically.

- **Public URL:** `https://jq7u85t05vmu.shares.zrok.io/webhooks/github-issues-to-kanban`
- **zrok binary:** `~/.local/bin/zrok2` (v2, installed from cached deb; not on PATH by default)
- **zrok share process:** `zrok2 share public http://localhost:8644 --headless` (running in background)
- **GitHub webhook:** registered on `e8kor/agentic-foundation` (hook id `665198849`), events `issues`, HMAC secret from `hermes webhook list`

**Verified live:** created real issue #9 → GitHub POSTed to the zrok URL → webhook created kanban task → dispatcher spawned `coder` → task completed → sync-back closed issue #9 with a comment. Full loop confirmed with real GitHub traffic.

### To re-establish the tunnel after a reboot

```bash
export PATH="$HOME/.local/bin:$PATH"
zrok2 share public http://localhost:8644 --headless   # note the new URL it prints
```

Then update the GitHub webhook URL to the new zrok URL (the zrok URL changes each run unless you use a reserved share).

## Verify

```bash
# Webhook route loaded
hermes webhook list

# Board + tasks
hermes kanban --board agentic-foundation list

# Dispatcher active (in gateway logs)
grep 'kanban dispatcher' ~/.hermes/logs/gateway.log | tail

# Cron sweep
hermes cron list | grep kanban-github-sync
```

## Notes / limitations

- **Local-only webhook:** the endpoint is on localhost; real GitHub traffic needs
  a tunnel. The pipeline was verified by simulating the GitHub POST locally.
- **Sync-back is pull-based** (cron sweep every 5m), not push — a completed task
  may take up to 5 minutes to reflect on GitHub.
- **`kanban show` has a Hermes bug** for completed tasks (closed-DB traceback on
  the non-JSON path); the sync-back uses `--json` which works.
- **Idempotency:** the sweep tracks synced task IDs in
  `~/.hermes/kanban-sync-state.json`; a task is synced once.
