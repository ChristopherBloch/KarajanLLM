#!/bin/bash
# OpenClaw Maintenance Script - Runs every 5 minutes
# Cleans stale lock files and monitors for errors

DOCKER_PATH="/Applications/Docker.app/Contents/Resources/bin/docker"
CONTAINER="clawdbot"
LOG_FILE="/tmp/openclaw-maintenance.log"
MAX_LOG_SIZE=102400  # 100KB

# Rotate log if too large
if [ -f "$LOG_FILE" ] && [ $(stat -f%z "$LOG_FILE" 2>/dev/null || echo 0) -gt $MAX_LOG_SIZE ]; then
    mv "$LOG_FILE" "$LOG_FILE.old"
fi

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Check if container is running
if ! $DOCKER_PATH ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    log "WARNING: Container $CONTAINER is not running"
    exit 0
fi

# Clean stale lock files (older than 2 minutes)
LOCKS_CLEANED=$($DOCKER_PATH exec $CONTAINER sh -c '
    find /root/.openclaw/agents -name "*.lock" -type f -mmin +2 2>/dev/null | while read lock; do
        rm -f "$lock" && echo "$lock"
    done
' 2>/dev/null)

if [ -n "$LOCKS_CLEANED" ]; then
    log "CLEANED LOCKS: $LOCKS_CLEANED"
fi

# Check for recent errors (last 5 minutes)
ERRORS=$($DOCKER_PATH logs $CONTAINER --since 5m 2>&1 | grep -i 'error\|failed\|crash' | tail -5)

if [ -n "$ERRORS" ]; then
    log "RECENT ERRORS:"
    echo "$ERRORS" | while read line; do
        log "  $line"
    done
fi

# Check memory usage inside container
MEM_INFO=$($DOCKER_PATH stats $CONTAINER --no-stream --format '{{.MemUsage}}' 2>/dev/null)
if [ -n "$MEM_INFO" ]; then
    log "Container memory: $MEM_INFO"
fi
