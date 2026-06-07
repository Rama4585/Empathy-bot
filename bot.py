import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiohttp import web

# 1. Настройка бота
TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher()

# 2. Фиктивный веб-сервер для Render (чтобы он видел порт и не отключал бота)
async def handle(request):
    return web.Response(text="Бот запущен и работает!")

app = web.Application()
app.router.add_get('/', handle)

async def start_web_server():
    runner = web.AppRunner(app)
    await runner.setup()
    # Берем порт из переменной окружения, которую дает Render
    port = int(os.environ.get('PORT', 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Web server started on port {port}")

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

# --- ХЕНДЛЕРЫ ---

@dp.message(Command("start"))
async def start_cmd(message: Message):
    text = """👋 Привет! Я твой ИИ-ассистент для анализа голосовых сообщений.
Я перевожу аудио в текст, анализирую смысл и эмоции собеседника. Предлагаю 3 варианта ответа."""
    await message.answer(text, reply_markup=get_main_menu())

@dp.callback_query(F.data == "how_it_works")
async def show_info(callback: CallbackQuery):
    text = "⚙️ Как это работает:\n1. Присылаешь ГС (голосовое сообщение).\n2. Я расшифровываю его.\n3. Генерирую 3 варианта ответа."
    await callback.message.edit_text(text, reply_markup=get_back_menu())

@dp.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery):
    text = "👋 Привет! Я твой ИИ-ассистент для анализа голосовых сообщений."
    await callback.message.edit_text(text, reply_markup=get_main_menu())

@dp.callback_query(F.data == "send_audio")
async def ask_for_audio(callback: CallbackQuery):
    await callback.message.answer("🎙 Отлично! Теперь просто запиши и пришли мне голосовое сообщение.")
    await callback.answer() # Убирает «часики» загрузки на кнопке

# --- ХЕНДЛЕР ДЛЯ ГОЛОСОВЫХ ---
@dp.message(F.voice)
async def handle_voice(message: Message):
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    # Скачиваем файл (в памяти)
    voice_file = await bot.download_file(file.file_path)
    
    await message.answer("✅ Аудио успешно получено! Сейчас расшифрую...")

# --- ХЕНДЛЕР ДЛЯ ТЕКСТА ---
@dp.message()
async def handle_text(message: Message):
    await message.answer("Я жду от тебя голосовое сообщение для анализа! Пришли мне ГС.")

# --- ЗАПУСК ---
async def main():
    # Запускаем веб-сервер в фоне
    await start_web_server()
     # Эту строку нужно добавить сюда, чтобы сбросить конфликты
    await bot.delete_webhook(drop_pending_updates=True)
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

