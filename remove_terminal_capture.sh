#!/bin/bash
# Script to remove Terminal Teacher command capture from bash

echo "🧹 Terminal Teacher - Cleanup Script"
echo "===================================="
echo ""

# Check if Terminal Teacher is installed
if ! grep -q "Terminal Teacher" ~/.bashrc 2>/dev/null; then
    echo "✅ Terminal Teacher is not installed in ~/.bashrc"
    echo "   Nothing to remove!"
    exit 0
fi

echo "Found Terminal Teacher installation in ~/.bashrc"
echo ""

# Create backup
BACKUP_FILE=~/.bashrc.backup.$(date +%Y%m%d_%H%M%S)
cp ~/.bashrc "$BACKUP_FILE"
echo "📦 Created backup: $BACKUP_FILE"

# Count how many lines will be removed
LINES_BEFORE=$(wc -l < ~/.bashrc)

# Remove all Terminal Teacher sections
sed -i '/# Terminal Teacher/,/^export PROMPT_COMMAND=.*terminal_teacher/d' ~/.bashrc

LINES_AFTER=$(wc -l < ~/.bashrc)
REMOVED=$((LINES_BEFORE - LINES_AFTER))

echo "🗑️  Removed $REMOVED lines from ~/.bashrc"
echo ""

# Verify it's gone
if grep -q "Terminal Teacher" ~/.bashrc 2>/dev/null; then
    echo "⚠️  Warning: Some Terminal Teacher code may still remain"
    echo "   Please check ~/.bashrc manually"
    exit 1
else
    echo "✅ Terminal Teacher completely removed!"
    echo ""
    echo "To apply changes:"
    echo "  1. Close this terminal and open a new one"
    echo "  OR"
    echo "  2. Run: source ~/.bashrc"
    echo ""
    echo "Your backup is saved at: $BACKUP_FILE"
fi
