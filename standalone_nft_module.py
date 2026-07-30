import telebot
from telebot import types

def show_nft_menu(bot, chat_id):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add("🪙 Mint NFT", "📊 סטטוס NFT")
    keyboard.add("🔗 OpenSea", "🔑 ארנק")
    keyboard.add("↩️ חזור")
    bot.send_message(chat_id, "🎨 **תפריט NFT**\n\n"
                              "🪙 Mint NFT – הנפקת NFT חדש\n"
                              "📊 סטטוס NFT – בדיקת אוסף\n"
                              "🔗 OpenSea – צפייה באוסף\n"
                              "🔑 ארנק – ניהול ארנק", reply_markup=keyboard, parse_mode='Markdown')

def register_nft_handlers(bot):
    @bot.message_handler(func=lambda message: message.text == "🎨 NFT")
    def handle_nft_menu(message):
        show_nft_menu(bot, message.chat.id)

    @bot.message_handler(func=lambda message: message.text == "🪙 Mint NFT")
    def handle_mint(message):
        bot.reply_to(message, "🪙 תהליך המינט התחיל!")

    @bot.message_handler(func=lambda message: message.text == "📊 סטטוס NFT")
    def handle_status(message):
        bot.reply_to(message, "📊 סטטוס NFT – 0/10")

    @bot.message_handler(func=lambda message: message.text == "🔗 OpenSea")
    def handle_opensea(message):
        bot.reply_to(message, "🔗 צפה באוסף: https://opensea.io/...")

    @bot.message_handler(func=lambda message: message.text == "🔑 ארנק")
    def handle_wallet(message):
        bot.reply_to(message, "🔑 שלח את כתובת הארנק שלך:")
