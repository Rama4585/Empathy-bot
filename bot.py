import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# Получаем токен из переменной окружения
TOKEN = os.getenv('BOT_TOKEN')

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

# --- НОВЫЙ ХЕНДЛЕР ДЛЯ ГОЛОСОВЫХ ---
@dp.message(F.voice)
async def handle_voice(message: Message):
    # Получаем информацию о файле и скачиваем в память
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    voice_file = await bot.download_file(file.file_path)
    
    await message.answer("✅ Аудио успешно получено! Сейчас расшифрую...")
    # Здесь позже мы добавим вызов нейросети для расшифровки

# --- ХЕНДЛЕР ДЛЯ ТЕКСТА (чтобы не было ошибок) ---
@dp.message()
async def handle_text(message: Message):
    await message.answer("Я жду от тебя голосовое сообщение для анализа! Пришли мне ГС.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
