#!/bin/bash
ERRORS=0

echo "🔍 בודק ספגטי..."

# 1. בדיקה שאין הגדרות כפולות של get_main_keyboard
COUNT=$(grep -rl "def get_main_keyboard" ~/SLH-DEV/bot/ --include="*.py" | grep -v menu.py | wc -l)
if [ "$COUNT" -gt 0 ]; then
    echo "❌ נמצאו $COUNT הגדרות כפולות של get_main_keyboard:"
    grep -rl "def get_main_keyboard" ~/SLH-DEV/bot/ --include="*.py" | grep -v menu.py
    ERRORS=$((ERRORS + 1))
else
    echo "✅ אין הגדרות כפולות של get_main_keyboard"
fi

# 2. בדיקת ייבואים מעגליים
CIRCULAR=$(grep -rn "from handlers\|from services" ~/SLH-DEV/bot/handlers/*.py 2>/dev/null | grep -v "bot_instance\|config\|database\|building_service\|economy_service\|market_service\|menu" | wc -l)
if [ "$CIRCULAR" -gt 0 ]; then
    echo "❌ נמצאו $CIRCULAR ייבואים מעגליים אפשריים"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ אין ייבואים מעגליים"
fi

echo ""
if [ "$ERRORS" -eq 0 ]; then
    echo "✅✅✅ הכל נקי!"
    exit 0
else
    echo "❌ נמצאו $ERRORS בעיות."
    exit 1
fi
