from telebot import TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from telebot.types import (
    Message, BotCommand,
    ReplyKeyboardMarkup, KeyboardButton,
    ReplyKeyboardRemove
)
from telebot.handler_backends import State, StatesGroup

# --- State definitions ---
class Register(StatesGroup):
    fio = State()
    phone = State()
    age = State()

# --- Keyboard helpers ---
def phone_number():
    """ReplyKeyboardMarkup for requesting user's contact."""
    markup = ReplyKeyboardMarkup(
        one_time_keyboard=True,
        resize_keyboard=True
    )
    btn = KeyboardButton(
        text='📞 Telefonni ulashish',
        request_contact=True
    )
    markup.add(btn)
    return markup

# --- Bot Initialization ---
state_storage = StateMemoryStorage()
bot = TeleBot("YOUR_BOT_TOKEN", state_storage=state_storage)
bot.add_custom_filter(custom_filters.StateFilter)

# Set up bot commands
bot.set_my_commands([
    BotCommand('start', 'Botni qayta yuklash'),
    BotCommand('help', 'Yordam olish')
])

# --- Handlers ---
@bot.message_handler(commands=['start'])
def start_handler(message: Message):
    chat_id = message.chat.id
    bot.send_message(
        chat_id,
        "Assalomu alaykum! Ro'yxatdan o'tish uchun 'Royhatdan otish 🖋️' tugmasini bosing."
    )

@bot.message_handler(regexp='Royhatdan otish 🖋️')
def register_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    bot.set_state(chat_id, user_id, Register.fio)
    bot.send_message(
        chat_id,
        "Iltimos ism-familyangizni kiriting.",
        reply_markup=ReplyKeyboardRemove()
    )

@bot.message_handler(content_types=['text'], state=Register.fio)
def ful_name_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text.strip()

    # Validate full name (at least two words, only letters)
    if len(text.split()) < 2:
        bot.send_message(chat_id, "Iltimos, ism-familyangizni to'liq kiriting. Namuna: Alijon Valiyev")
        return
    if not text.replace(" ", "").isalpha():
        bot.send_message(chat_id, "Iltimos faqat harflardan foydalaning (raqam va belgilarsiz).")
        return
    if len(text) < 3 or len(text) > 40:
        bot.send_message(chat_id, "Ism-familya uzunligi 3 dan 40 harfgacha bo'lishi kerak.")
        return

    # Save and move to phone state
    with bot.retrieve_data(user_id, chat_id) as data:
        data['fio'] = text

    bot.set_state(chat_id, user_id, Register.phone)
    bot.send_message(
        chat_id,
        "📞 Telefon raqamingizni ulashing.",
        reply_markup=phone_number()
    )

@bot.message_handler(content_types=['contact', 'text'], state=Register.phone)
def phone_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # If user shared their own contact
    if message.contact and message.contact.user_id == user_id:
        phone = message.contact.phone_number
        with bot.retrieve_data(user_id, chat_id) as data:
            data['phone'] = phone

        # Remove keyboard and prompt age
        bot.send_message(
            chat_id,
            "✔️ Telefon raqamingiz qabul qilindi.",
            reply_markup=ReplyKeyboardRemove()
        )
        bot.set_state(chat_id, user_id, Register.age)
        bot.send_message(chat_id, "Iltimos, yoshingizni kiriting.")
        return

    # Fallback: ask again
    bot.send_message(
        chat_id,
        "❌ Iltimos, 'Telefonni ulashish' tugmasi orqali raqamingizni yuboring.",
        reply_markup=phone_number()
    )

@bot.message_handler(content_types=['text'], state=Register.age)
def age_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text.strip()

    if not text.isdigit():
        bot.send_message(chat_id, "Iltimos, faqat son kiriting.")
        return
    age = int(text)
    if age < 1 or age > 120:
        bot.send_message(chat_id, "Iltimos, haqiqiy yoshni kiriting.")
        return

    with bot.retrieve_data(user_id, chat_id) as data:
        data['age'] = age

    # Registration complete
    bot.send_message(
        chat_id,
        f"Registratsiya yakunlandi!\nIsm: {data['fio']}\nTel: {data['phone']}\nYosh: {data['age']}"
    )
    bot.delete_state(chat_id, user_id)

# --- Start polling ---
if __name__ == '__main__':
    print("Bot ishga tushdi...")
    bot.infinity_polling()
