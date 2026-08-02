"""
ניהול לחיצות על כפתורי הבורסה
"""
import sys
sys.path.insert(0, "/data/data/com.termux/files/home/SLH-DEV/bot/services")
sys.path.insert(0, "/data/data/com.termux/files/home/SLH-DEV/bot/handlers/exchange")

from exchange_handler import ExchangeHandler
from telegram import Update
from telegram.ext import CallbackContext

class ExchangeCallback:
    """מטפל בלחיצות כפתורי בורסה"""
    
    def __init__(self):
        self.exchange = ExchangeHandler()
    
    def handle_callback(self, update: Update, context: CallbackContext):
        """טיפול כללי בלחיצות"""
        query = update.callback_query
        data = query.data
        
        # תפריט ראשי
        if data == "exchange_main":
            return self.show_main_menu(query)
        
        # המרות
        elif data == "exchange_gilds_to_slh":
            return self.show_amount_selection(query, "gilds_to_slh", "GILDS")
        elif data == "exchange_slh_to_gilds":
            return self.show_amount_selection(query, "slh_to_gilds", "SLH_SYSTEM")
        
        # מידע
        elif data == "exchange_rate":
            return self.show_rate(query)
        elif data == "exchange_wallet":
            return self.show_wallet(query)
        elif data == "exchange_history":
            return self.show_history(query)
        
        # כמות
        elif data.startswith("exchange_amount_"):
            return self.handle_amount_selection(query, data, context)
        
        # אישור
        elif data.startswith("exchange_confirm_"):
            return self.handle_confirm(query, data)
        
        # ניווט
        elif data == "exchange_back_to_main":
            return self.show_main_menu(query)
        elif data == "exchange_close":
            query.message.delete()
            return
        
        return query.answer("❓ פעולה לא מוכרת")
    
    def show_main_menu(self, query):
        """הצג תפריט ראשי"""
        from exchange_buttons import ExchangeButtons
        query.edit_message_text(
            "📊 **בורסה מדומה**\n\n"
            "בחר פעולה:\n"
            "💱 המר בין מטבעות\n"
            "📊 עקוב אחר שערים\n"
            "💰 נהל את הארנק שלך",
            reply_markup=ExchangeButtons.main_menu(),
            parse_mode='Markdown'
        )
        query.answer()
    
    def show_amount_selection(self, query, action, currency):
        """הצג בחירת סכום"""
        from exchange_buttons import ExchangeButtons
        
        emoji = "🪙" if currency == "GILDS" else "💎"
        query.edit_message_text(
            f"{emoji} **בחר סכום להמרה**\n\n"
            f"מטבע: {currency}\n"
            f"שער נוכחי: {self.exchange.rate.get_current_rate():.6f}",
            reply_markup=ExchangeButtons.amount_buttons(action, currency),
            parse_mode='Markdown'
        )
        query.answer()
    
    def show_rate(self, query):
        """הצג שער נוכחי"""
        rate = self.exchange.rate.get_current_rate()
        query.edit_message_text(
            f"📊 **שער נוכחי**\n\n"
            f"🪙 1 GILDS = {rate:.6f} 💎 SLH_SYSTEM",
            reply_markup=self.get_back_buttons(),
            parse_mode='Markdown'
        )
        query.answer()
    
    def show_wallet(self, query):
        """הצג ארנק"""
        user_id = query.from_user.id
        wallet = self.exchange.wallet.get_wallet(user_id)
        
        from exchange_buttons import ExchangeButtons
        query.edit_message_text(
            f"💰 **הארנק שלך**\n\n"
            f"🪙 GILDS: {wallet['gilds']:.2f}\n"
            f"💎 SLH_SYSTEM: {wallet['slh_system']:.6f}\n\n"
            f"📊 שווי כולל: {wallet['gilds'] + (wallet['slh_system'] / self.exchange.rate.get_current_rate()):.2f} GILDS",
            reply_markup=ExchangeButtons.wallet_display(wallet),
            parse_mode='Markdown'
        )
        query.answer()
    
    def show_history(self, query):
        """הצג היסטוריה"""
        user_id = query.from_user.id
        history = self.exchange.get_history(user_id, 5)
        
        if not history:
            text = "📜 **אין היסטוריית עסקאות**"
        else:
            text = "📜 **היסטוריית עסקאות אחרונות**\n\n"
            for t in history:
                text += f"• {t[1]} → {t[2]}: {t[3]:.2f} → {t[4]:.6f}\n"
                text += f"  שער: {t[5]:.6f}\n\n"
        
        from exchange_buttons import ExchangeButtons
        query.edit_message_text(
            text,
            reply_markup=ExchangeButtons.history_buttons(0),
            parse_mode='Markdown'
        )
        query.answer()
    
    def handle_amount_selection(self, query, data, context):
        """טיפול בבחירת סכום"""
        parts = data.split('_')
        action = parts[2]
        currency = parts[3]
        amount = parts[4] if len(parts) > 4 else "custom"
        
        if amount == "custom":
            query.answer("✏️ הקלד את הסכום הרצוי (מספר)")
            context.user_data['exchange_action'] = action
            context.user_data['exchange_currency'] = currency
            return
        
        # הצג אישור
        from exchange_buttons import ExchangeButtons
        query.edit_message_text(
            f"✅ **אשר המרה**\n\n"
            f"🪙 סכום: {amount} {currency}\n"
            f"📊 שער: {self.exchange.rate.get_current_rate():.6f}\n\n"
            f"לחץ 'אשר' להשלמת הפעולה",
            reply_markup=ExchangeButtons.confirm_buttons(action, amount, currency, "SLH_SYSTEM" if currency == "GILDS" else "GILDS"),
            parse_mode='Markdown'
        )
        query.answer()
    
    def handle_confirm(self, query, data):
        """טיפול באישור עסקה"""
        parts = data.split('_')
        action = parts[2]
        amount = float(parts[3])
        currency_from = parts[4]
        currency_to = parts[5]
        
        user_id = query.from_user.id
        
        if action == "gilds_to_slh":
            success, msg = self.exchange.convert_gilds_to_slh(user_id, amount)
        else:
            success, msg = self.exchange.convert_slh_to_gilds(user_id, amount)
        
        if success:
            query.edit_message_text(
                f"✅ {msg}\n\n"
                f"📊 שער: {self.exchange.rate.get_current_rate():.6f}",
                reply_markup=self.get_back_buttons(),
                parse_mode='Markdown'
            )
        else:
            query.edit_message_text(
                f"❌ {msg}\n\n"
                f"נסה שוב או בחר סכום אחר",
                reply_markup=self.get_back_buttons(),
                parse_mode='Markdown'
            )
        query.answer()
    
    def get_back_buttons(self):
        """כפתור חזרה"""
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [[InlineKeyboardButton("🔙 חזור", callback_data="exchange_back_to_main")]]
        return InlineKeyboardMarkup(keyboard)
    
    def close(self):
        self.exchange.close()
