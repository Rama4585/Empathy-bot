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


# =========================
# ИНИЦИАЛИЗАЦИЯ
# =========================

TOKEN = os.getenv("BOT_TOKEN")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

bot = Bot(token=TOKEN)
dp = Dispatcher()


# временная память
user_balances = {}


# =========================
# ПАКЕТЫ
# =========================

PACKAGES = [
    {"title": "1 разбор", "price": 2, "amount": 1},
    {"title": "10 разборов", "price": 15, "amount": 10},
    {"title": "50 разборов", "price": 60, "amount": 50},
    {"title": "Месячный запас (200)", "price": 200, "amount": 200},
]


# =========================
# КЛАВИАТУРЫ
# =========================

def get_main_menu(balance):

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text=f"🎤 Разобрать голосовое • осталось {balance}",
                    callback_data="send_audio"
                )
            ],

            [
                InlineKeyboardButton(
                    text="✨ Посмотреть пример",
                    callback_data="example"
                )
            ],

            [
                InlineKeyboardButton(
                    text="💎 Ещё разборы",
                    callback_data="buy_menu"
                )
            ],

            [
                InlineKeyboardButton(
                    text="❓ Как это работает",
                    callback_data="how_it_works"
                )
            ]
        ]
    )


def get_back_menu():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="main_menu"
                )
            ]
        ]
    )


# =========================
# OPENAI
# =========================

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

- Дружелюбный/креативный:
[Текст]

- Профессиональный:
[Текст]

- Личные границы:
[Вежливый отказ или установление дистанции]

Важно:
Пиши лаконично,
без лишних вступлений и заключений.
Только по делу.
"""

    response = client.chat.completions.create(

        model="gpt-4o-mini",

        messages=[

            {
                "role": "system",
                "content": prompt
            },

            {
                "role": "user",
                "content": transcript.text
            }

        ]
    )

    return (
        transcript.text,
        response.choices[0].message.content
    )


# =========================
# СТАРТ
# =========================

@dp.message(Command("start"))
async def start_cmd(message: Message):

    user_id = message.from_user.id

    if user_id not in user_balances:
        user_balances[user_id] = {
            "balance": 5
        }

    text = """
🎙 <b>Разберу голосовое за 5 секунд</b>

✓ Покажу суть сообщения  
✓ Определю настроение  
✓ Предложу 3 ответа  

👇 Просто отправь голосовое
"""

    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_main_menu(
            user_balances[user_id]["balance"]
        )
    )


@dp.callback_query(F.data == "main_menu")
async def back(callback: CallbackQuery):

    balance = (
        user_balances
        .get(callback.from_user.id, {})
        .get("balance", 0)
    )

    text = """
🎙 <b>Разберу голосовое за 5 секунд</b>

✓ Покажу главное  
✓ Определю настроение  
✓ Предложу 3 ответа  

👇 Отправь голосовое
"""

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_main_menu(balance)
    )


# =========================
# ПРИМЕР
# =========================

@dp.callback_query(F.data == "example")
async def example(callback: CallbackQuery):

    text = """
🎧 Голосовое • 1:28

📝 Суть:
Человек расстроен,
но хочет договориться

🙂 Настроение:
Раздражение + открытость

💬 Ответы:

1. Поддержать
2. Уточнить детали
3. Вежливо отказать
"""

    await callback.message.edit_text(
        text,
        reply_markup=get_back_menu()
    )


# =========================
# КАК РАБОТАЕТ
# =========================

@dp.callback_query(F.data == "how_it_works")
async def info(callback: CallbackQuery):

    text = """
🎧 Ты отправляешь голосовое

1. Перевожу в текст
2. Убираю лишнее
3. Определяю эмоции
4. Даю готовые ответы

⏱ Обычно несколько секунд
"""

    await callback.message.edit_text(
        text,
        reply_markup=get_back_menu()
    )


# =========================
# ПОКУПКА
# =========================

@dp.callback_query(F.data == "buy_menu")
async def buy(callback: CallbackQuery):

    kb = []

    for p in PACKAGES:

        kb.append([
            InlineKeyboardButton(
                text=f"{p['title']} • {p['price']}⭐",
                callback_data=f"pay_{p['price']}_{p['amount']}"
            )
        ])

    kb.append([
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="main_menu"
        )
    ])

    await callback.message.edit_text(
        "💎 Выбери пакет",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=kb
        )
    )


@dp.callback_query(F.data.startswith("pay_"))
async def invoice(callback: CallbackQuery):

    _, price, amount = callback.data.split("_")

    await bot.send_invoice(

        chat_id=callback.message.chat.id,

        title=f"{amount} разборов",

        description="Разбор голосовых",

        payload=f"add_{amount}",

        currency="XTR",

        prices=[
            LabeledPrice(
                label="Оплата",
                amount=int(price)
            )
        ]
    )


@dp.pre_checkout_query()
async def pre_checkout(
        query: PreCheckoutQuery
):
    await query.answer(ok=True)


@dp.message(F.successful_payment)
async def payment(message: Message):

    amount = int(
        message
        .successful_payment
        .invoice_payload
        .split("_")[1]
    )

    user_id = message.from_user.id

    user_balances[user_id]["balance"] += amount

    await message.answer(
        f"✅ Добавлено {amount} разборов"
    )


# =========================
# АУДИО
# =========================

@dp.callback_query(F.data == "send_audio")
async def ask(callback: CallbackQuery):

    await callback.message.answer(
        "🎤 Просто пришли голосовое"
    )

    await callback.answer()


@dp.message(F.voice)
async def voice(message: Message):

    user_id = message.from_user.id

    if (
        user_balances
        .get(user_id, {})
        .get("balance", 0)
        <= 0
    ):

        await message.answer(
            "⚠️ Разборы закончились\n\nКупи пакет через меню /start"
        )

        return

    status = await message.answer(
        "🎧 Слушаю...\n▰▱▱▱▱"
    )

    file = await bot.get_file(
        message.voice.file_id
    )

    path = (
        f"voice_"
        f"{message.voice.file_id}.ogg"
    )

    await bot.download_file(
        file.file_path,
        path
    )

    try:

        await status.edit_text(
            "🧠 Анализирую...\n▰▰▰▱▱"
        )

        transcript, answer = (
            await asyncio.to_thread(
                process_audio,
                path
            )
        )

        user_balances[user_id]["balance"] -= 1

        await message.answer(
f"""
🎧 Разбор готов

📝 Расшифровка:

{transcript}

{answer}

✨ Осталось:
{user_balances[user_id]["balance"]}
"""
        )

    except Exception as e:

        await message.answer(
            f"⚠️ Ошибка:\n{e}"
        )

    finally:

        if os.path.exists(path):
            os.remove(path)

        await status.delete()


# =========================
# WEB
# =========================

async def start_web():

    app = web.Application()

    app.router.add_get(
        "/",
        lambda r:
        web.Response(
            text="Бот работает"
        )
    )

    runner = web.AppRunner(app)

    await runner.setup()

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        int(
            os.getenv(
                "PORT",
                10000
            )
        )
    )

    await site.start()


async def main():
    await start_web()

    await bot.delete_webhook(
        drop_pending_updates=True
    )

    try:
        await dp.start_polling(bot)

    except Exception as e:
        print("POLLING ERROR:", e)
        raise

    finally:
        print("BOT STOPPED")


if __name__ == "__main__":
    asyncio.run(main())
