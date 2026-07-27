from telebot import types
from bot_instance import bot
from config import RESOURCE_EMOJI, ALL_RESOURCE_IDX
from database import get_resources

@bot.message_handler(func=lambda m: m.text == "💰 מכור למערכת")
def sell_to_system_start(message):
    user_id = message.from_user.id
    row = get_resources(user_id)
    
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for res in ['water', 'coal', 'copper', 'gold', 'wheat', 'soil', 'wood', 'stones']:
        idx = ALL_RESOURCE_IDX.get(res, -1)
        balance = row[idx] if row and idx < len(row) else 0
        emoji = RESOURCE_EMOJI.get(res, "")
        if balance > 0:
            keyboard.add(types.KeyboardButton(f"{emoji} {res} ({balance:.0f})"))
    keyboard.add("↩️ תפריט ראשי")
    bot.send_message(message.chat.id, "💰 **מכירה למערכת**\n\nבחר משאב:\n(100 יח׳ = 1 Gild)", reply_markup=keyboard)

sell_state = {}

@bot.message_handler(func=lambda m: m.from_user.id in sell_state or any(
    f"{emoji} {res}" in (m.text or "") for emoji in RESOURCE_EMOJI.values() for res in ALL_RESOURCE_IDX))
def handle_sell_resource_click(message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if text == "↩️ תפריט ראשי":
        if user_id in sell_state:
            del sell_state[user_id]
        from button_handler import show_main_menu
        show_main_menu(user_id)
        return
    
    # בדוק אם זה כפתור משאב
    for res in ALL_RESOURCE_IDX:
        if res in text:
            row = get_resources(user_id)
            idx = ALL_RESOURCE_IDX[res]
            balance = row[idx] if row and idx < len(row) else 0
            
            sell_state[user_id] = {"resource": res, "step": "amount"}
            
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            keyboard.add("↩️ תפריט ראשי")
            bot.send_message(user_id, f"💰 **{res}**\nיתרה: {balance:.1f}\n\nהקלד כמות למכירה:", reply_markup=keyboard)
            return
    
    # אם במצב מכירה ומקליד כמות
    if user_id in sell_state and sell_state[user_id].get("step") == "amount":
        try:
            amount = float(text)
            if amount <= 0:
                raise ValueError
        except:
            bot.send_message(user_id, "❌ הקלד מספר חיובי:")
            return
        
        resource = sell_state[user_id]["resource"]
        del sell_state[user_id]
        
        message.text = f"/sellstore {resource} {amount}"
        from resource_commands import sellstore_cmd
        sellstore_cmd(message)
