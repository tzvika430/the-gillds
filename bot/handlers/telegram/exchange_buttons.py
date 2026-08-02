"""
כפתורי בורסה מדומה - ממשק משתמש
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class ExchangeButtons:
    """כפתורים שקופים לבורסה"""
    
    @staticmethod
    def main_menu():
        """תפריט ראשי - כפתורים שקופים"""
        keyboard = [
            [
                InlineKeyboardButton("💱 המר GILDS → SLH", callback_data="exchange_gilds_to_slh"),
                InlineKeyboardButton("💱 המר SLH → GILDS", callback_data="exchange_slh_to_gilds")
            ],
            [
                InlineKeyboardButton("📊 שער נוכחי", callback_data="exchange_rate"),
                InlineKeyboardButton("💰 ארנק שלי", callback_data="exchange_wallet")
            ],
            [
                InlineKeyboardButton("📜 היסטוריה", callback_data="exchange_history"),
                InlineKeyboardButton("🔙 סגור", callback_data="exchange_close")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def amount_buttons(action, currency):
        """כפתורי סכום להמרה"""
        keyboard = [
            [
                InlineKeyboardButton("10", callback_data=f"exchange_amount_{action}_{currency}_10"),
                InlineKeyboardButton("50", callback_data=f"exchange_amount_{action}_{currency}_50"),
                InlineKeyboardButton("100", callback_data=f"exchange_amount_{action}_{currency}_100")
            ],
            [
                InlineKeyboardButton("500", callback_data=f"exchange_amount_{action}_{currency}_500"),
                InlineKeyboardButton("1000", callback_data=f"exchange_amount_{action}_{currency}_1000"),
                InlineKeyboardButton("✏️ סכום מותאם", callback_data=f"exchange_amount_{action}_{currency}_custom")
            ],
            [
                InlineKeyboardButton("🔙 חזור", callback_data="exchange_back_to_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def confirm_buttons(action, amount, currency_from, currency_to):
        """כפתורי אישור/ביטול"""
        keyboard = [
            [
                InlineKeyboardButton("✅ אשר", callback_data=f"exchange_confirm_{action}_{amount}_{currency_from}_{currency_to}"),
                InlineKeyboardButton("❌ בטל", callback_data="exchange_back_to_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def wallet_display(wallet_data):
        """תצוגת ארנק עם כפתורים"""
        keyboard = [
            [
                InlineKeyboardButton("🔄 רענן", callback_data="exchange_wallet"),
                InlineKeyboardButton("🔙 חזור", callback_data="exchange_back_to_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def history_buttons(page=0):
        """כפתורי דפדוף בהיסטוריה"""
        keyboard = [
            [
                InlineKeyboardButton("⬅️ הקודם", callback_data=f"exchange_history_{page-1}"),
                InlineKeyboardButton(f"📄 {page+1}", callback_data="exchange_history_current"),
                InlineKeyboardButton("➡️ הבא", callback_data=f"exchange_history_{page+1}")
            ],
            [
                InlineKeyboardButton("🔙 חזור", callback_data="exchange_back_to_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
