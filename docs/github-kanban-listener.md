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

## To wire the REAL GitHub webhook (DONE — live via zrok systemd service)

The webhook is exposed publicly via **zrok** (managed as a user systemd service)
and registered in the GitHub repo. Real GitHub issues flow through automatically
and the tunnel survives reboots.

- **Public URL:** `https://0y5hvey9hyy0.shares.zrok.io/webhooks/github-issues-to-kanban`
- **zrok binary:** `~/.local/bin/zrok2` (v2, installed from cached deb; not on PATH by default)
- **systemd service:** `zrok2-share.service` (user service, enabled + lingering)
  - `systemctl --user status zrok2-share.service`
  - `systemctl --user restart zrok2-share.service`
  - Logs: `journalctl --user -u zrok2-share.service -f`
- **GitHub webhook:** registered on `e8kor/agentic-foundation` (hook id `665198849`), events `issues`, HMAC secret from `hermes webhook list`

**Verified live:** created real issue #9 → GitHub POSTed to the zrok URL → webhook created kanban task → dispatcher spawned `coder` → task completed → sync-back closed issue #9 with a comment. Full loop confirmed with real GitHub traffic.

### Note: zrok URL changes on each restart

The zrok public URL is **not stable** — it changes every time the share restarts
(unless you reserve a share). After a restart, get the new URL from the service
log and update the GitHub webhook:

```bash
# Get the new URL
journalctl --user -u zrok2-share.service --no-pager | grep -oE '[a-z0-9]+\.shares\.zrok\.io' | tail -1

# Update the GitHub webhook URL (via API or repo Settings → Webhooks)
```

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

- **Backfill:** a done kanban task with **no GitHub issue link** in its body now
  gets a **mirror issue created** (labeled `kanban-mirror`) in the project repo,
  then commented + closed — so nothing is left unsynced. Configure the target
  repo via `KANBAN_SYNC_REPO` (default `e8kor/agentic-foundation`).
- **Local-only webhook:** the endpoint is on localhost; real GitHub traffic needs
  a tunnel. The pipeline was verified by simulating the GitHub POST locally.
- **Sync-back is pull-based** (cron sweep every 5m), not push — a completed task
  may take up to 5 minutes to reflect on GitHub.
- **`kanban show` has a Hermes bug** for completed tasks (closed-DB traceback on
  the non-JSON path); the sync-back uses `--json` which works.
- **Idempotency:** the sweep tracks synced task IDs in
  `~/.hermes/kanban-sync-state.json`; a task is synced once. Both scripts load
  `GITHUB_TOKEN` from `~/.hermes/.env` so they work under cron's fresh env.
