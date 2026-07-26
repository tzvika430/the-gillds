import sqlite3
from config import RESOURCE_EMOJI, DB_PATH
from bot_instance import bot
from market_service import sell_resource, get_market_listings, buy_from_market
from database import update_time

@bot.message_handler(commands=['sell'])
def sell_cmd(message):
    parts = message.text.split()
    if len(parts) != 4:
        bot.reply_to(message, "שימוש: /sell משאב כמות מחיר")
        return
    _, resource, amount_str, price_str = parts
    try:
        amount = float(amount_str)
        price = float(price_str)
    except ValueError:
        bot.reply_to(message, "כמות ומחיר חייבים להיות מספרים")
        return
    if amount <= 0 or price <= 0:
        bot.reply_to(message, "כמות ומחיר חייבים להיות חיוביים")
        return
    update_time(message.from_user.id, message.from_user.username)
    ok, msg = sell_resource(message.from_user.id, resource, amount, price)
    if ok:
        emoji = RESOURCE_EMOJI.get(resource, "")
        bot.reply_to(message, f"✅ הצעה נפתחה: {emoji} {amount} {resource} במחיר {price} Gild ליחידה")
    else:
        bot.reply_to(message, f"❌ {msg}")

@bot.message_handler(commands=['market'])
def market_cmd(message):
    conn = sqlite3.connect(DB_PATH)
    listings = get_market_listings(20)
    if not listings:
        conn.close()
        bot.reply_to(message, "📭 אין הצעות בשוק כרגע")
        return
    msg = "🏪 **שוק המשאבים:**\n\n"
    for listing in listings:
        listing_id, seller_id, resource, amount, price = listing
        emoji = RESOURCE_EMOJI.get(resource, "")
        # קבל שם מוכר
        c2 = conn.cursor()
        c2.execute("SELECT display_name, username FROM users WHERE user_id=?", (seller_id,))
        seller = c2.fetchone()
        seller_name = seller[0] if seller and seller[0] else (seller[1] if seller else str(seller_id))
        msg += f"#{listing_id} | {emoji} {resource} | {amount:.1f} יח' | {price:.2f} Gild | {seller_name}\n"
    conn.close()
    bot.reply_to(message, msg)

@bot.message_handler(commands=['buy'])
def buy_cmd(message):
    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, "שימוש: /buy מספר_הצעה כמות")
        return
    try:
        listing_id = int(parts[1])
        amount_requested = float(parts[2])
    except ValueError:
        bot.reply_to(message, "פורמט לא תקין")
        return
    if amount_requested <= 0:
        bot.reply_to(message, "כמות חייבת להיות חיובית")
        return
    update_time(message.from_user.id, message.from_user.username)
    ok, result = buy_from_market(message.from_user.id, listing_id, amount_requested)
    if ok:
        bot.reply_to(message, f"✅ קנית {amount_requested:.2f} {result['resource']} תמורת {result['cost']:.2f} Gild")
    else:
        bot.reply_to(message, f"❌ {result}")
