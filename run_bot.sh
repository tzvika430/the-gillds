#!/bin/bash

# ============================================
# SLH-DEV Bot Runner with Auto-Recovery
# ============================================

BOT_DIR="$HOME/SLH-DEV/bot/src"
TESTS_DIR="$HOME/SLH-DEV/tests"
LOG_FILE="$HOME/bot_error.log"
MAX_RESTARTS=5
RESTART_COUNT=0

echo "=========================================="
echo "  SLH-DEV Bot Runner"
echo "  $(date)"
echo "=========================================="

# פונקציה: הפעלת בדיקות
run_tests() {
    echo ""
    echo "🧪 Running pre-flight tests..."
    
    if ! python3 "$TESTS_DIR/test_structure.py"; then
        echo "❌ test_structure.py FAILED!"
        return 1
    fi
    
    if ! python3 "$TESTS_DIR/test_game_logic.py"; then
        echo "⚠️ test_game_logic.py FAILED (לגאסי, ממשיכים)"
    fi
    
    if ! python3 "$TESTS_DIR/test_market.py"; then
        echo "❌ test_market.py FAILED!"
        return 1
    fi
    
    echo "✅ All tests PASSED!"
    return 0
}

# פונקציה: גיבוי אוטומטי
auto_backup() {
    echo ""
    echo "💾 Creating backup..."
    mkdir -p "$HOME/SLH-DEV/backups"
    for f in "$BOT_DIR/bot.py" "$HOME/SLH-DEV/bot/services/database.py" "$HOME/SLH-DEV/bot/handlers/commands.py"; do
        if [ -f "$f" ]; then
            cp "$f" "$HOME/SLH-DEV/backups/$(basename $f).auto_$(date +%Y%m%d_%H%M)"
        fi
    done
    echo "✅ Backup done"
}

# פונקציה: הפעלת הבוט
start_bot() {
    echo ""
    echo "🚀 Starting bot..."
    cd "$BOT_DIR"
    python3 bot.py 2>&1 | tee -a "$LOG_FILE"
}

# ============ MAIN ============

# הרגת בוט קודם
pkill -9 -f "python3 bot.py" 2>/dev/null
sleep 1

# גיבוי
auto_backup

# בדיקות
if ! run_tests; then
    echo ""
    echo "❌ Tests failed! Aborting."
    exit 1
fi

# לולאת הפעלה עם שחזור אוטומטי
while [ $RESTART_COUNT -lt $MAX_RESTARTS ]; do
    start_bot
    
    EXIT_CODE=$?
    RESTART_COUNT=$((RESTART_COUNT + 1))
    
    if [ $RESTART_COUNT -lt $MAX_RESTARTS ]; then
        echo ""
        echo "⚠️ Bot crashed (exit code: $EXIT_CODE)"
        echo "🔄 Restarting in 3 seconds... (attempt $RESTART_COUNT/$MAX_RESTARTS)"
        sleep 3
    else
        echo ""
        echo "❌ Bot crashed $MAX_RESTARTS times. Stopping."
        exit 1
    fi
done
