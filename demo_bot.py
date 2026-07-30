import telebot
from telebot import types
from standalone_nft_module import register_nft_handlers

# ============================================
# BOT DEMO – להרצה עצמאית
# ============================================

TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"  # תשים טוקן אמיתי לבדיקה
bot = telebot.TeleBot(TOKEN)

# רישום כל ה-handlers של NFT
register_nft_handlers(bot)

# פקודת התחלה
@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add("🎨 NFT", "ℹ️ מידע")
    bot.reply_to(message, "ברוכים הבאים! בחר פעולה:", reply_markup=keyboard)

print("🤖 בוט NFT רץ...")
bot.polling()
