#!/bin/bash
# Cleanup script for aria_memories and workspace
# Run inside clawdbot container: docker exec clawdbot bash /root/repo/scripts/cleanup_memories.sh
# Or from host: docker exec clawdbot bash -c "$(cat scripts/cleanup_memories.sh)"

set -e

WORKSPACE="/root/.openclaw/workspace"
MEMORIES="/root/.openclaw/aria_memories"

echo "=== Aria Memories Cleanup ==="
echo "Workspace: $WORKSPACE"
echo "Memories:  $MEMORIES"
echo ""

# --- 1. Move misplaced files from workspace to aria_memories ---
echo "--- Moving misplaced files from workspace to aria_memories ---"

# Move immunefi report to research/
if [ -f "$WORKSPACE/immunefi_scan_report_2026-02-07.md" ]; then
    mv "$WORKSPACE/immunefi_scan_report_2026-02-07.md" "$MEMORIES/research/"
    echo "  Moved: immunefi_scan_report_2026-02-07.md -> research/"
fi

# Move spending schema to income_ops/
if [ -f "$WORKSPACE/spending_schema.sql" ]; then
    mkdir -p "$MEMORIES/income_ops"
    mv "$WORKSPACE/spending_schema.sql" "$MEMORIES/income_ops/"
    echo "  Moved: spending_schema.sql -> income_ops/"
fi

# Move workspace logs to aria_memories/logs/
if [ -d "$WORKSPACE/logs" ]; then
    for f in "$WORKSPACE/logs"/*; do
        [ -f "$f" ] || continue
        mv "$f" "$MEMORIES/logs/"
        echo "  Moved: logs/$(basename $f) -> aria_memories/logs/"
    done
    rmdir "$WORKSPACE/logs" 2>/dev/null || true
fi

# --- 2. Delete stale/duplicate content from workspace ---
echo ""
echo "--- Removing stale content from workspace ---"

# Remove bubble/ (1.7MB git clone - shouldn't be in workspace)
if [ -d "$WORKSPACE/bubble" ]; then
    rm -rf "$WORKSPACE/bubble"
    echo "  Deleted: bubble/ (1.7MB git clone)"
fi

# Remove duplicate ssv/ (already in aria_memories/ssv/)
if [ -d "$WORKSPACE/ssv" ]; then
    rm -rf "$WORKSPACE/ssv"
    echo "  Deleted: ssv/ (duplicate of aria_memories/ssv/)"
fi

# Remove stale configs directory
if [ -d "$WORKSPACE/configs" ]; then
    rm -rf "$WORKSPACE/configs"
    echo "  Deleted: configs/ (stale 402 fallback)"
fi

# --- 3. Clean stale scripts from aria_memories ---
echo ""
echo "--- Removing stale scripts from aria_memories ---"

# These are one-off hacks that are superseded by proper litellm config
for f in "model_with_402_fallback.sh" "openrouter_402_handler.py" "setup_spending_tracking.py"; do
    if [ -f "$MEMORIES/$f" ]; then
        rm "$MEMORIES/$f"
        echo "  Deleted: $f (stale script)"
    fi
done

# Remove empty write test
if [ -f "$MEMORIES/logs/write_test.txt" ]; then
    rm "$MEMORIES/logs/write_test.txt"
    echo "  Deleted: logs/write_test.txt (empty test file)"
fi

# --- 4. Organize root-level files into proper categories ---
echo ""
echo "--- Organizing root-level files ---"

# Bug report -> logs/
if [ -f "$MEMORIES/BUG_REPORT_CLAUDE_20260206.md" ]; then
    mv "$MEMORIES/BUG_REPORT_CLAUDE_20260206.md" "$MEMORIES/logs/"
    echo "  Moved: BUG_REPORT_CLAUDE_20260206.md -> logs/"
fi

# Telegram request -> logs/
if [ -f "$MEMORIES/telegram_ping_request_20260206.md" ]; then
    mv "$MEMORIES/telegram_ping_request_20260206.md" "$MEMORIES/logs/"
    echo "  Moved: telegram_ping_request_20260206.md -> logs/"
fi

# Research files -> research/
for f in "token_income_research.md" "token_income_quick_ref.md" "immunefi_scan_report_2026-02-06.md"; do
    if [ -f "$MEMORIES/$f" ]; then
        mv "$MEMORIES/$f" "$MEMORIES/research/"
        echo "  Moved: $f -> research/"
    fi
done

# Survey -> logs/ (it's a status report)
if [ -d "$MEMORIES/surveys" ]; then
    for f in "$MEMORIES/surveys"/*; do
        [ -f "$f" ] || continue
        mv "$f" "$MEMORIES/logs/"
        echo "  Moved: surveys/$(basename $f) -> logs/"
    done
    rmdir "$MEMORIES/surveys" 2>/dev/null || true
    echo "  Removed: surveys/ directory"
fi

# --- 5. Summary ---
echo ""
echo "=== Cleanup Complete ==="
echo ""
echo "aria_memories structure:"
find "$MEMORIES" -type f | sort | sed "s|$MEMORIES/|  |"
echo ""
echo "workspace loose files (should be empty except kernel .md/.py files):"
find "$WORKSPACE" -maxdepth 1 -type f | sort | sed "s|$WORKSPACE/|  |"
