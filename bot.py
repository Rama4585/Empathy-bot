import telebot
from telebot import types

TOKEN = '8820084050:AAEFCyVI0erEt22eLuHi28ysha00d1tDR04'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    description = (
        "👋 Привет! Я твой ИИ-ассистент для анализа голосовых сообщений.\n\n"
        "Как я работаю:\n"
        "1. Ты присылаешь мне длинное голосовое сообщение.\n"
        "2. Я перевожу его в текст и анализирую смысл.\n"
        "3. Предлагаю 3 варианта ответа с разной эмоциональной окраской.\n\n"
        "Просто нажми кнопку ниже, чтобы начать!"
    )
    markup = types.InlineKeyboardMarkup()
    btn_start = types.InlineKeyboardButton("Загрузить сообщение", callback_data='upload_voice')
    btn_help = types.InlineKeyboardButton("Как это работает?", callback_data='how_it_works')
    markup.add(btn_start, btn_help)
    bot.send_message(message.chat.id, description, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'upload_voice':
        bot.edit_message_text("Я готов! Присылай свое голосовое сообщение.", 
                              call.message.chat.id, call.message.message_id)
    elif call.data == 'how_it_works':
        bot.edit_message_text("Ты отправляешь аудио -> Я расшифровываю -> Генерирую 3 варианта ответа.", 
                              call.message.chat.id, call.message.message_id)

bot.infinity_polling()
