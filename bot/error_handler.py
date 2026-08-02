"""
מנגנון ניהול שגיאות לחיבור Telegram
"""
import time
import logging
from telebot import TeleBot
from requests.exceptions import ConnectionError, Timeout

logger = logging.getLogger(__name__)

class SafeBot:
    """בוט עם ניהול שגיאות אוטומטי"""
    
    def __init__(self, bot: TeleBot, max_retries=5, retry_delay=5):
        self.bot = bot
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.is_running = True
    
    def safe_polling(self):
        """הפעל polling עם ניהול שגיאות"""
        retry_count = 0
        
        while self.is_running:
            try:
                logger.info("🔄 מפעיל את הבוט...")
                self.bot.polling(
                    non_stop=True,
                    interval=2,
                    timeout=30,
                    long_polling_timeout=20,
                    allowed_updates=['message', 'callback_query']
                )
                
            except ConnectionError as e:
                retry_count += 1
                logger.error(f"❌ שגיאת התחברות: {e}")
                
                if retry_count > self.max_retries:
                    logger.critical("❌ יותר מדי ניסיונות כושלים, ממתין...")
                    retry_count = 0
                
                wait_time = self.retry_delay * retry_count
                logger.info(f"⏳ ממתין {wait_time} שניות לפני ניסיון חוזר...")
                time.sleep(wait_time)
                
            except Timeout as e:
                logger.error(f"⏰ Timeout: {e}")
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"❌ שגיאה לא צפויה: {e}")
                time.sleep(5)
        
        logger.info("🛑 הבוט נעצר")
    
    def stop(self):
        """עצירת הבוט"""
        self.is_running = False
        logger.info("🛑 עוצר את הבוט...")
