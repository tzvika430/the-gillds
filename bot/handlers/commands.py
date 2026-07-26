from config import *
from database import update_time
from bot_instance import bot

@bot.message_handler(func=lambda m: True)
def every_message(message):
    pass
