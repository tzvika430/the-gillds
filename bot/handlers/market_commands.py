from config import RESOURCE_EMOJI
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
    listings = get_market_listings(20)
    if not listings:
        bot.reply_to(message, "📭 אין הצעות בשוק כרגע")
        return
    msg = "🏪 **שוק המשאבים:**\n\n"
    for listing in listings:
        listing_id, seller_id, resource, amount, price = listing
        emoji = RESOURCE_EMOJI.get(resource, "")
        msg += f"#{listing_id} | {emoji} {resource} | {amount:.1f} יח' | {price:.2f} Gild ליח'\n"
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
