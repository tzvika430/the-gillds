#!/usr/bin/env python3
"""
הרצת הבוט עם ניהול שגיאות
"""
import sys
import os
import logging
import time
from pathlib import Path

# הוספת נתיבים
sys.path.insert(0, "/data/data/com.termux/files/home/SLH-DEV/bot")
sys.path.insert(0, "/data/data/com.termux/files/home/SLH-DEV/bot/services")
sys.path.insert(0, "/data/data/com.termux/files/home/SLH-DEV/bot/handlers")

# הגדרת לוג
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """הפעל את הבוט בבטחה"""
    logger.info("🚀 מפעיל את הבוט עם SafeBot...")
    
    try:
        from config import TOKEN
        from telegram_bot import bot
        from error_handler import SafeBot
        
        safe_bot = SafeBot(bot, max_retries=5, retry_delay=5)
        
        try:
            safe_bot.safe_polling()
        except KeyboardInterrupt:
            logger.info("🛑 נעצר על ידי המשתמש")
            safe_bot.stop()
        except Exception as e:
            logger.error(f"❌ שגיאה חמורה: {e}")
            safe_bot.stop()
            sys.exit(1)
            
    except ImportError as e:
        logger.error(f"❌ שגיאת ייבוא: {e}")
        logger.info("📝 בדוק שהקבצים קיימים:")
        logger.info("  - bot/config.py")
        logger.info("  - bot/telegram_bot.py")
        logger.info("  - bot/error_handler.py")
        sys.exit(1)

if __name__ == "__main__":
    main()
