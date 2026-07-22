from telebot import types
from bot_instance import bot

@bot.message_handler(func=lambda m: m.text and '📦' in m.text and '/resources' in m.text)
def btn_resources(message):
    from resource_commands import resources_cmd
    resources_cmd(message)

@bot.message_handler(func=lambda m: m.text and '👤' in m.text and '/profile' in m.text)
def btn_profile(message):
    from basic_commands import profile_cmd
    profile_cmd(message)

@bot.message_handler(func=lambda m: m.text and '📚' in m.text and '/doc' in m.text)
def btn_doc(message):
    from admin_commands import doc_cmd
    doc_cmd(message)

@bot.message_handler(func=lambda m: m.text and '🏪' in m.text and '/market' in m.text)
def btn_market(message):
    from market_commands import market_cmd
    market_cmd(message)

@bot.message_handler(func=lambda m: m.text and '🏆' in m.text and '/leaderboard' in m.text)
def btn_leaderboard(message):
    from basic_commands import leaderboard
    leaderboard(message)

@bot.message_handler(func=lambda m: m.text and '⏰' in m.text and '/time' in m.text)
def btn_time(message):
    from basic_commands import time_status
    time_status(message)

@bot.message_handler(func=lambda m: m.text and '🏗️' in m.text and '/build' in m.text)
def btn_build(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add("/build straw_house", "/build brick_house")
    keyboard.add("/build sawmill")
    keyboard.add("↩️ תפריט ראשי")
    bot.send_message(message.chat.id, "🏗️ בחר מבנה:", reply_markup=keyboard)

@bot.message_handler(func=lambda m: m.text and '👷' in m.text and '/hire' in m.text)
def btn_hire(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add("/hire farmer", "/hire lumberjack")
    keyboard.add("/hire water_drawer", "/hire coal_miner")
    keyboard.add("/hire copper_miner", "/hire gold_miner")
    keyboard.add("↩️ תפריט ראשי")
    bot.send_message(message.chat.id, "👷 בחר עובד:", reply_markup=keyboard)

@bot.message_handler(func=lambda m: m.text and '🛒' in m.text and '/store' in m.text)
def btn_store(message):
    bot.send_message(message.chat.id, "🛒 השתמש בפקודה:\n/store [משאב] [כמות]\n\nלדוגמה: /store wood 200")

@bot.message_handler(func=lambda m: m.text == '↩️ תפריט ראשי')
def btn_back(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    keyboard.add("📦 /resources", "👤 /profile", "📚 /doc")
    keyboard.add("🏪 /market", "🏆 /leaderboard", "⏰ /time")
    keyboard.add("🏗️ /build", "👷 /hire", "🛒 /store")
    bot.send_message(message.chat.id, "תפריט ראשי:", reply_markup=keyboard)
