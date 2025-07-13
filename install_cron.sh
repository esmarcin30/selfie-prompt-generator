#!/bin/bash

# MacBook Deal Tracker - Cron Job Installation Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRON_TIME="0 9 * * *"  # 9 AM daily

echo "🍎 MacBook Deal Tracker - Cron Job Setup"
echo "========================================"

# Check if cron is installed
if ! command -v crontab &> /dev/null; then
    echo "❌ Error: cron is not installed on this system"
    exit 1
fi

# Create the cron job entry
CRON_JOB="$CRON_TIME cd $SCRIPT_DIR && python3 test_tracker.py >> $SCRIPT_DIR/macbook_tracker.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "test_tracker.py"; then
    echo "ℹ️  Cron job already exists. Updating..."
    # Remove existing job
    crontab -l 2>/dev/null | grep -v "test_tracker.py" | crontab -
fi

# Add the new cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ Cron job installed successfully!"
echo "📅 The tracker will run daily at 9:00 AM"
echo "📁 Working directory: $SCRIPT_DIR"
echo "📄 Log file: $SCRIPT_DIR/macbook_tracker.log"
echo ""
echo "To view current cron jobs: crontab -l"
echo "To remove the cron job: crontab -e (then delete the line)"
echo "To view logs: tail -f $SCRIPT_DIR/macbook_tracker.log"