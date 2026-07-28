from telebot import types
from bot_instance import bot

def show_main_menu(chat_id):
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    keyboard.add("👤 פרופיל", "📚 מדריך", "⚔️ צבא")
    keyboard.add("💰 כלכלה", "🏗️ בניה", "👥 קהילה")
    keyboard.add("💬 שיחה", "📋 תפריט")
    bot.send_message(chat_id, "📋 תפריט ראשי:", reply_markup=keyboard)
