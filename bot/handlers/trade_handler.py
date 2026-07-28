from telebot import types
from bot_instance import bot
from market_service import sell_resource, get_market_listings, buy_from_market
from database import update_time
from config import RESOURCE_EMOJI, ALL_RESOURCE_IDX

# מצב זמני למכירה
sell_state = {}
buy_state = {}


@bot.message_handler(func=lambda m: m.text == '🏪 /market')
def trade_menu(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add("📦 מכור משאב", "🛒 קנה משאב")
    keyboard.add("📋 צפה בהצעות", "↩️ תפריט ראשי")
    bot.send_message(message.chat.id, "🏪 **שוק מסחר**\nמה תרצה לעשות?", reply_markup=keyboard)

# ============ מכירה ============

@bot.message_handler(func=lambda m: m.text == '📦 מכור משאב')
def sell_start(message):
    user_id = message.from_user.id
    sell_state[user_id] = {"step": "choose_resource"}
    
    from database import get_resources
    row = get_resources(user_id)
    
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    for res in ['water', 'coal', 'copper', 'gold', 'wheat', 'soil', 'wood', 'stones']:
        emoji = RESOURCE_EMOJI.get(res, "")
        idx = ALL_RESOURCE_IDX.get(res, -1)
        balance = row[idx] if row and idx >= 0 and idx < len(row) else 0
        keyboard.add(types.KeyboardButton(f"{emoji} {res} ({balance:.0f})"))
    keyboard.add("↩️ תפריט ראשי")
    
    bot.send_message(message.chat.id, "📦 **מכירת משאב**\nאיזה משאב תרצה למכור?", reply_markup=keyboard)

@bot.message_handler(func=lambda m: m.from_user.id in sell_state and sell_state[m.from_user.id]["step"] == "choose_resource")
def sell_choose_resource(message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if text == "↩️ תפריט ראשי":
        del sell_state[user_id]
        bot.send_message(user_id, "בוטל.", reply_markup=get_main_keyboard())
        return
    
    # הסר אימוג'י
    for res in ALL_RESOURCE_IDX:
        if res in text:
            sell_state[user_id]["resource"] = res
            sell_state[user_id]["step"] = "choose_amount"
            
            keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
            keyboard.add("↩️ תפריט ראשי")
            
            # בדוק יתרה
            from database import get_resources
            row = get_resources(user_id)
            idx = ALL_RESOURCE_IDX[res]
            balance = row[idx] if row and idx < len(row) else 0
            bot.send_message(user_id, f"📦 {res}\nיתרה: {balance:.1f}\nכמה יחידות למכור?\n(הקלד מספר)", reply_markup=keyboard)
            return
    
    bot.send_message(user_id, "לא זוהה משאב. נסה שוב.")

@bot.message_handler(func=lambda m: m.from_user.id in sell_state and sell_state[m.from_user.id]["step"] == "choose_amount")
def sell_choose_amount(message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if text == "↩️ תפריט ראשי":
        del sell_state[user_id]
        bot.send_message(user_id, "בוטל.", reply_markup=get_main_keyboard())
        return
    
    try:
        amount = float(text)
        if amount <= 0:
            raise ValueError
    except ValueError:
        bot.send_message(user_id, "❌ צריך מספר חיובי. נסה שוב:")
        return
    
    sell_state[user_id]["amount"] = amount
    sell_state[user_id]["step"] = "choose_price"
    
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    keyboard.add("↩️ תפריט ראשי")
    
    resource = sell_state[user_id]["resource"]
    bot.send_message(user_id, f"📦 {resource} × {amount}\nבאיזה מחיר ליחידה? (Gild)\n(הקלד מספר)", reply_markup=keyboard)

@bot.message_handler(func=lambda m: m.from_user.id in sell_state and sell_state[m.from_user.id]["step"] == "choose_price")
def sell_choose_price(message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if text == "↩️ תפריט ראשי":
        del sell_state[user_id]
        bot.send_message(user_id, "בוטל.", reply_markup=get_main_keyboard())
        return
    
    try:
        price = float(text)
        if price <= 0:
            raise ValueError
    except ValueError:
        bot.send_message(user_id, "❌ צריך מספר חיובי. נסה שוב:")
        return
    
    resource = sell_state[user_id]["resource"]
    amount = sell_state[user_id]["amount"]
    del sell_state[user_id]
    
    update_time(user_id, message.from_user.username)
    ok, msg = sell_resource(user_id, resource, amount, price)
    
    if ok:
        emoji = RESOURCE_EMOJI.get(resource, "")
        bot.send_message(user_id, f"✅ הצעה נפתחה: {emoji} {amount} {resource} במחיר {price} Gild ליחידה", reply_markup=get_main_keyboard())
    else:
        bot.send_message(user_id, f"❌ {msg}", reply_markup=get_main_keyboard())

# ============ קנייה ============

@bot.message_handler(func=lambda m: m.text == '🛒 קנה משאב')
def buy_show_listings(message):
    listings = get_market_listings(10)
    if not listings:
        bot.send_message(message.chat.id, "📭 אין הצעות בשוק כרגע", reply_markup=get_main_keyboard())
        return
    
    msg = "🏪 **הצעות שוק:**\n\n"
    for listing in listings:
        listing_id, seller_id, resource, amount, price = listing
        emoji = RESOURCE_EMOJI.get(resource, "")
        msg += f"#{listing_id} | {emoji} {resource} | {amount:.1f} יח' | {price:.2f} Gild\n"
    
    buy_state[message.from_user.id] = {"step": "choose_listing"}
    
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add("↩️ תפריט ראשי")
    
    bot.send_message(message.chat.id, msg + "\nשלח את מספר ההצעה לקנייה:", reply_markup=keyboard)

@bot.message_handler(func=lambda m: m.from_user.id in buy_state and buy_state[m.from_user.id]["step"] == "choose_listing")
def buy_choose_listing(message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if text == "↩️ תפריט ראשי":
        del buy_state[user_id]
        bot.send_message(user_id, "בוטל.", reply_markup=get_main_keyboard())
        return
    
    try:
        listing_id = int(text)
    except ValueError:
        bot.send_message(user_id, "❌ צריך מספר הצעה. נסה שוב:")
        return
    
    buy_state[user_id]["listing_id"] = listing_id
    buy_state[user_id]["step"] = "choose_amount"
    
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add("↩️ תפריט ראשי")
    
    bot.send_message(user_id, f"🛒 הצעה #{listing_id}\nכמה יחידות לקנות?\n(הקלד מספר)", reply_markup=keyboard)

@bot.message_handler(func=lambda m: m.from_user.id in buy_state and buy_state[m.from_user.id]["step"] == "choose_amount")
def buy_choose_amount(message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if text == "↩️ תפריט ראשי":
        del buy_state[user_id]
        bot.send_message(user_id, "בוטל.", reply_markup=get_main_keyboard())
        return
    
    try:
        amount = float(text)
        if amount <= 0:
            raise ValueError
    except ValueError:
        bot.send_message(user_id, "❌ צריך מספר חיובי. נסה שוב:")
        return
    
    listing_id = buy_state[user_id]["listing_id"]
    del buy_state[user_id]
    
    update_time(user_id, message.from_user.username)
    ok, result = buy_from_market(user_id, listing_id, amount)
    
    if ok:
        bot.send_message(user_id, f"✅ קנית {amount:.2f} {result['resource']} תמורת {result['cost']:.2f} Gild", reply_markup=get_main_keyboard())
    else:
        bot.send_message(user_id, f"❌ {result}", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda m: m.text == '📋 צפה בהצעות')
def view_market(message):
    from market_commands import market_cmd
    market_cmd(message)
