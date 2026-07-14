import telebot
from telebot import types

with open("/data/data/com.termux/files/home/SLH-DEV/.token_backup", "r") as f:
    TOKEN = f.read().strip()

bot = telebot.TeleBot(TOKEN)

try:
    bot_info = bot.get_me()
    print(f"✅ טוקן תקין! מחובר לבוט @{bot_info.username}")
except Exception as e:
    print(f"❌ טוקן לא תקין או אין חיבור לאינטרנט: {e}")
    raise SystemExit(1)
