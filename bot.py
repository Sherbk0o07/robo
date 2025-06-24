from telebot import TeleBot, types

bot = TeleBot("8126624116:AAGcm8qc6xHHi-_FHII-DcgnqV6_Ux48FAE")

# 🎮 Start menyu
def menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton("🎲 O'yin boshlash"),
        types.KeyboardButton("❌ Chiqish")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message): 
    
    bot.send_message(message.chat.id,
        "Salom do‘stim! 🎯 \n\nBu yerda tosh tashlab raqam chiqishini ko‘rish mumkin. O‘yin uchun tugmani bosing!",
        reply_markup=menu())

@bot.message_handler(func=lambda msg: msg.text == "🎲 O'yin boshlash")
def game(message):
    bot.send_message(message.chat.id, "Tosh tashlanyapti... 🎲")
    bot.send_dice(message.chat.id, emoji="🎲")  # bu yerda 🎲 = 1-6 gacha random son

@bot.message_handler(func=lambda msg: msg.text == "❌ Chiqish")
def exit(message):
    bot.send_message(message.chat.id, "O‘yin tugadi. Ko‘rishguncha! 👋", reply_markup=types.ReplyKeyboardRemove())

# Har qanday boshqa matn
@bot.message_handler(func=lambda msg: True)
def default(message):
    bot.send_message(message.chat.id, "Iltimos, menyudan foydalaning:", reply_markup=menu())

print("Bot ishga tushdi...")
bot.polling()
