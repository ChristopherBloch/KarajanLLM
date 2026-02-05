# Aria's Memory Files

This folder contains files written by Aria during operation.
These files are synced to the git repository for visibility.

## Structure

```
aria_memories/
├── README.md           # This file
├── sessions/           # Session summaries and logs
├── learnings/          # Documented learnings
├── drafts/             # Draft content before publishing
└── exports/            # Exported data and backups
```

## Usage

Aria writes to this folder via:
1. File operations skill (when implemented)
2. Direct file writes from workspace

## Sync

This folder is mounted into the clawdbot container at:
`/root/.openclaw/aria_memories` (needs docker-compose update)

Or via the full repo mount at:
`/root/repo/aria_memories`
