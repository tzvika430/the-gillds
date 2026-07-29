from telebot import types
from bot_instance import bot

@bot.message_handler(func=lambda m: m.text in ["💰 כלכלה", "⚔️ צבא", "🏗️ בניה", "👥 קהילה", "👤 פרופיל", "📚 מדריך", "💬 שיחה", "📋 תפריט", "↩️ תפריט ראשי", "🎯 גיוס", "🕵️ מודיעין", "⚔️ מלחמה", "🏪 שוק", "🛒 חנות", "🏆 מובילים", "💳 תשלום"])
def handle_all_buttons(message):
    text = message.text
    
    if text == "📋 תפריט" or text == "↩️ תפריט ראשי":
        show_main_menu(message.chat.id)
        return
    
    if text == "💰 כלכלה":
        bot.send_message(message.chat.id, "💰 **כלכלה**\n\n🏪 שוק — קנה/מכור לשחקנים\n🛒 חנות — קנה/מכור למערכת\n🏆 מובילים — טבלת דירוג\n💳 תשלום — המשך משחק", reply_markup=get_economy_menu())
        return
    
    if text == "⚔️ צבא":
        bot.send_message(message.chat.id, "⚔️ **צבא**\n\n🎯 גיוס — גייס חיילים\n🕵️ מודיעין — שלח מרגלים\n⚔️ מלחמה — תקוף שחקנים", reply_markup=get_army_menu())
        return
    
    if text == "🏗️ בניה":
        bot.send_message(message.chat.id, "🏗️ **בניה**\n\n🏠 צריף קש — בסיסי\n🧱 בית לבנים — מתקדם\n🪚 מנסרה — עוד עץ\n🏰 בסיס צבאי — גייס חיילים\n🕵️ בית מרגלים — שלח מרגלים", reply_markup=get_build_menu())
        return
    
    if text == "👥 קהילה":
        bot.send_message(message.chat.id, "👥 **קהילה**\n\n📢 /shout — שלח לכולם\n📋 /board — לוח מודעות", reply_markup=get_community_menu())
        return
    
    if text == "👤 פרופיל":
        from basic_commands import profile_cmd
        profile_cmd(message)
        return
    
    if text == "📚 מדריך":
        from admin_commands import doc_cmd
        doc_cmd(message)
        return
    
    if text == "💬 שיחה":
        from msg_handler import chat_cmd
        chat_cmd(message)
        return
    
    # תת-תפריטים
    if text == "🎯 גיוס":
        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        keyboard.add("🪖 חייל", "🎖️ מפ�кад", "👑 גנרל")
        keyboard.add("↩️ תפריט ראשי")
        bot.send_message(message.chat.id, "🎯 **גיוס חיילים**", reply_markup=keyboard)
        return
    
    if text == "🕵️ מודיעין":
        from spy_handler import spy_cmd
        spy_cmd(message)
        return
    
    if text == "⚔️ מלחמה":
        from attack_handler import attack_cmd
        attack_cmd(message)
        return
    
    if text == "🏪 שוק":
        from trade_handler import trade_menu
        trade_menu(message)
        return
    
    if text == "🛒 חנות":
        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        keyboard.add("🛒 קנה", "💰 מכור")
        keyboard.add("↩️ תפריט ראשי")
        bot.send_message(message.chat.id, "🛒 **חנות**\n\nקנייה: 500 יח׳ = 1 Gild\nמכירה: 250 יח׳ = 1 Gild", reply_markup=keyboard)
        return
    
    if text == "🏆 מובילים":
        from basic_commands import leaderboard
        leaderboard(message)
        return
    
    if text == "💳 תשלום":
        from admin_commands import pay_cmd
        pay_cmd(message)
        return

def show_main_menu(chat_id):
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    keyboard.add("👤 פרופיל", "📚 מדריך", "⚔️ צבא")
    keyboard.add("💰 כלכלה", "🏗️ בניה", "👥 קהילה")
    keyboard.add("👤 פרופיל", "📚 מדריך", "💬 שיחה", "📋 תפריט")
    bot.send_message(chat_id, "📋 תפריט ראשי:", reply_markup=keyboard)

def get_economy_menu():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add("🏪 שוק", "🛒 חנות")
    keyboard.add("🏆 מובילים", "💳 תשלום")
    keyboard.add("↩️ תפריט ראשי")
    return keyboard

def get_army_menu():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add("🎯 גיוס", "🕵️ מודיעין")
    keyboard.add("⚔️ מלחמה")
    keyboard.add("↩️ תפריט ראשי")
    return keyboard

def get_build_menu():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add("🏠 צריף קש", "🧱 בית לבנים")
    keyboard.add("🪚 מנסרה", "🏰 בסיס צבאי")
    keyboard.add("🕵️ בית מרגלים")
    keyboard.add("↩️ תפריט ראשי")
    return keyboard

def get_community_menu():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add("📢 /shout", "📋 /board")
    keyboard.add("↩️ תפריט ראשי")
    return keyboard
