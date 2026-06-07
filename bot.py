import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiohttp import web
from openai import OpenAI

# Инициализация
TOKEN = os.getenv('BOT_TOKEN')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- КЛАВИАТУРЫ ---
def get_main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎙 Прислать аудио", callback_data="send_audio")],
        [InlineKeyboardButton(text="❓ Как это работает", callback_data="how_it_works")]
    ])

def get_back_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="main_menu")]
    ])

# --- ЛОГИКА ИИ ---
def process_audio(file_path):
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
    
    prompt = """Ты — эксперт по эмоциональному интеллекту и эффективной коммуникации. 
Проанализируй текст голосового сообщения и представь результат строго по пунктам:
1. Анализ эмоций: Определи явные и скрытые эмоции отправителя (гнев, неуверенность, манипуляция, радость и т.д.).
2. Суть сообщения: Что человек на самом деле хочет донести до меня? (убери лишнюю "воду").
3. Варианты ответа:
   - Дружелюбный/креативный: [Текст]
   - Профессиональный: [Текст]
   - Личные границы: [Вежливый отказ или установление дистанции]

Важно: Пиши лаконично, без лишних вступлений и заключений. Только по делу."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": transcript.text}
        ]
    )
    return transcript.text, response.choices[0].message.content

# --- ХЕНДЛЕРЫ ---
@dp.message(Command("start"))
async def start_cmd(message: Message):
    text = "👋 Привет! Я твой ИИ-ассистент для анализа голосовых сообщений."
    await message.answer(text, reply_markup=get_main_menu())

@dp.callback_query(F.data == "send_audio")
async def ask_for_audio(callback: CallbackQuery):
    await callback.message.answer("🎙 Отлично! Просто запиши и пришли мне голосовое сообщение.")
    await callback.answer()

@dp.callback_query(F.data == "how_it_works")
async def show_info(callback: CallbackQuery):
    text = (
        "⚙️ Как это работает:\n\n"
        "Я перевожу аудио в текст, анализирую смысл и эмоции собеседника. "
        "После этого я предлагаю 3 варианта ответа, чтобы ты мог выбрать лучший."
    )
    await callback.message.edit_text(text, reply_markup=get_back_menu())

@dp.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text("👋 Привет! Я твой ИИ-ассистент.", reply_markup=get_main_menu())

@dp.message(F.voice)
async def handle_voice(message: Message):
    status_msg = await message.answer("🎧 Анализирую...")
    file = await bot.get_file(message.voice.file_id)
    file_path = f"voice_{message.voice.file_id}.ogg"
    await bot.download_file(file.file_path, file_path)
    
    try:
        transcript, ai_reply = await asyncio.to_thread(process_audio, file_path)
        await message.answer(f"📝 **Текст:** {transcript}\n\n🤖 **Анализ:**\n{ai_reply}")
    except Exception as e:
        await message.answer(f"⚠️ Ошибка анализа: {e}")
    finally:
        os.remove(file_path)
        await status_msg.delete()

# --- ВЕБ-СЕРВЕР ---
async def start_web_server():
    app = web.Application()
    app.router.add_get('/', lambda r: web.Response(text="Бот в сети!"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get('PORT', 8080)))
    await site.start()

async def main():
    await start_web_server()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
