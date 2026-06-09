import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
Message,
InlineKeyboardMarkup,
InlineKeyboardButton,
CallbackQuery,
LabeledPrice,
PreCheckoutQuery
)

from aiohttp import web
from openai import OpenAI
from motor.motor_asyncio import AsyncIOMotorClient

#=========================

#ИНИЦИАЛИЗАЦИЯ

#=========================

TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")

client = OpenAI(
api_key=os.getenv("OPENAI_API_KEY")
)

bot = Bot(token=TOKEN)
dp = Dispatcher()

Подключение к MongoDB

db_client = AsyncIOMotorClient(MONGO_URL)
db = db_client.bot_database
users_col = db.users

ФУНКЦИИ БД (Вместо JSON)

async def get_balance(uid):
user = await users_col.find_one({"uid": str(uid)})
return user["balance"] if user else 5

async def update_balance(uid, amount_change):
await users_col.update_one(
{"uid": str(uid)},
{"$inc": {"balance": amount_change}},
upsert=True
)

#=========================

#ПАКЕТЫ

#=========================

PACKAGES = [
{"title": "1 разбор", "price": 2, "amount": 1},
{"title": "10 разборов", "price": 15, "amount": 10},
{"title": "50 разборов", "price": 60, "amount": 50},
{"title": "Месячный запас (200)", "price": 200, "amount": 200},
]

#=========================

#КЛАВИАТУРЫ

#=========================

def get_main_menu(balance):
return InlineKeyboardMarkup(
inline_keyboard=[
[InlineKeyboardButton(text=f"🎤 Разобрать голосовое • осталось {balance}", callback_data="send_audio")],
[InlineKeyboardButton(text="✨ Посмотреть пример", callback_data="example")],
[InlineKeyboardButton(text="💎 Получить ещё попытки", callback_data="buy_menu")],
[InlineKeyboardButton(text="🚀 Подписаться на канал", callback_data="channel")],
[InlineKeyboardButton(text="❓ Как это работает", callback_data="how_it_works")]
]
)

def get_back_menu():
return InlineKeyboardMarkup(
inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]]
)

#=========================

#OPENAI

#=========================

def process_audio(file_path):
with open(file_path, "rb") as audio_file:
transcript = client.audio.transcriptions.create(
model="whisper-1",
file=audio_file
)

prompt = """

Ты — эксперт по эмоциональному интеллекту и эффективной коммуникации.

Проанализируй текст голосового сообщения и представь результат строго по пунктам:

1. Анализ эмоций:
Определи явные и скрытые эмоции отправителя (гнев, неуверенность, манипуляция, радость и т.д.).


2. Суть сообщения:
Что человек на самом деле хочет донести до меня?
(убери лишнюю "воду").


3. Варианты ответа:



Дружелюбный/креативный:
[Текст]

Профессиональный:
[Текст]

Личные границы:
[Вежливый отказ или установление дистанции]


Важно:
Пиши лаконично,
без лишних вступлений и заключений.
Только по делу.
"""
response = client.chat.completions.create(
model="gpt-4o-mini",
messages=[{"role": "system", "content": prompt}, {"role": "user", "content": transcript.text}]
)
return transcript.text, response.choices[0].message.content

#=========================

#ХЕНДЛЕРЫ

#=========================

@dp.message(Command("start"))
async def start_cmd(message: Message):
uid = message.from_user.id
bal = await get_balance(uid)

text = """

🎧 <b>Отправь голосовое</b>

Я быстро выделю главное
Покажу настроение
Предложу варианты ответа

⏱ Обычно ответ занимает 5–15 секунд
"""

await message.answer(  
    text,  
    parse_mode="HTML",  
    reply_markup=get_main_menu(bal))

@dp.callback_query(F.data == "send_audio")
async def send_audio_prompt(callback: CallbackQuery):
bal = await get_balance(callback.from_user.id)
if bal <= 0:
await callback.answer("⚠️ Получи ещё попытки", show_alert=True)
else:
await callback.answer("🎧 Отправь голосовое\n\nЯ быстро выделю главное, покажу настроение и предложу варианты ответа", show_alert=True)

@dp.callback_query(F.data == "channel")
async def channel(callback: CallbackQuery):

keyboard = InlineKeyboardMarkup(  
    inline_keyboard=[  
        [InlineKeyboardButton(  
            text="🚀 Перейти в канал",  
            url="https://t.me/empathy_community"  
        )],  
        [InlineKeyboardButton(  
            text="🔙 Назад",  
            callback_data="main_menu"  
        )]  
    ]  
)  

await callback.message.edit_text(

"""
🚀 Подпишись на канал

Что получишь:

🚀 новые функции раньше всех
🎁 дополнительные разборы
🛠 показываем как развивается бот
💬 можно предлагать идеи

Присоединяйся 👇
""",
reply_markup=keyboard)

@dp.callback_query(F.data == "main_menu")
async def back(callback: CallbackQuery):
bal = await get_balance(callback.from_user.id)
await callback.message.edit_text("🎙 <b>Разберу голосовое за 5-15 секунд</b>\n\n✓ Покажу главное\n✓ Определю настроение\n✓ Предложу 3 ответа\n\n👇 Отправь голосовое", parse_mode="HTML", reply_markup=get_main_menu(bal))

@dp.callback_query(F.data == "example")
async def example(callback: CallbackQuery):

await callback.message.edit_text(

"""
🎧 Голосовое • 1:28

📝 Суть:
Человек расстроен, но хочет договориться

🙂 Настроение:
Раздражение + открытость

💬 Готовые ответы:

1. «Понял тебя. Давай спокойно обсудим»


2. «Что именно тебя больше всего задело?»


3. «Сейчас не готов это обсуждать, но услышал тебя»
""",
reply_markup=get_back_menu())



@dp.callback_query(F.data == "how_it_works")
async def info(callback: CallbackQuery):
await callback.message.edit_text("🎧 Ты отправляешь голосовое\n\n1. Перевожу в текст\n2. Убираю лишнее\n3. Определяю эмоции\n4. Даю готовые ответы\n\n⏱ Обычно ответ занимает 5-15 секунд", reply_markup=get_back_menu())

@dp.callback_query(F.data == "buy_menu")
async def buy(callback: CallbackQuery):
kb = [[InlineKeyboardButton(text=f"{p['title']} • {p['price']}⭐", callback_data=f"pay_{p['price']}_{p['amount']}")] for p in PACKAGES]
kb.append([InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")])
await callback.message.edit_text("💎 Выбери пакет", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data.startswith("pay_"))
async def invoice(callback: CallbackQuery):
, price, amount = callback.data.split("")
await bot.send_invoice(chat_id=callback.message.chat.id, title=f"{amount} разборов", description="Разбор голосовых", payload=f"add_{amount}", currency="XTR", prices=[LabeledPrice(label="Оплата", amount=int(price))])

@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
await query.answer(ok=True)

@dp.message(F.successful_payment)
async def payment(message: Message):
amount = int(message.successful_payment.invoice_payload.split("_")[1])
await update_balance(message.from_user.id, amount)
await message.answer(f"✅ Добавлено {amount} разборов")

@dp.message(F.voice)
async def voice(message: Message):
uid = message.from_user.id
if await get_balance(uid) <= 0:
await message.answer("⚠️ Разборы закончились\n\nКупи пакет через меню /start")
return

status = await message.answer("🎧 Слушаю...\n▰▱▱▱▱")  
file = await bot.get_file(message.voice.file_id)  
path = f"voice_{message.voice.file_id}.ogg"  
await bot.download_file(file.file_path, path)  
try:  
    transcript, answer = await asyncio.to_thread(process_audio, path)  
    await update_balance(uid, -1)  
    new_bal = await get_balance(uid)  
    await message.answer(

f"""
📝 Разбор готов

{answer}

✨ Осталось попыток: {new_bal}
""",
reply_markup=InlineKeyboardMarkup(
inline_keyboard=[
[InlineKeyboardButton(text="🔁 Разобрать ещё одно", callback_data="main_menu")],
[InlineKeyboardButton(text="📢 Поделиться ботом", switch_inline_query="Попробуй этого бота")],
[InlineKeyboardButton(text="💎 Получить ещё попытки", callback_data="buy_menu")],
[InlineKeyboardButton(text="🚀 Подписаться", callback_data="channel")],
]))
except Exception as e: await message.answer(f"⚠️ Ошибка:\n{e}")
finally:
if os.path.exists(path): os.remove(path)
await status.delete()

#=========================

#WEB + MAIN (Стабильный запуск)

#=========================

async def on_startup():
print("Бот запущен и готов к работе")

async def main():
# Удаляем вебхуки, чтобы polling работал чисто
await bot.delete_webhook(drop_pending_updates=True)

# Запускаем веб-сервер в фоне (Render требует наличия веб-сервера)  
app = web.Application()  
app.router.add_get("/", lambda r: web.Response(text="Бот работает"))  
runner = web.AppRunner(app)  
await runner.setup()  
site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", 10000)))  
await site.start()  
  
# Запускаем самого бота  
await dp.start_polling(bot, on_startup=on_startup)

if name == "main":
try:
asyncio.run(main())
except (KeyboardInterrupt, SystemExit):
pass
