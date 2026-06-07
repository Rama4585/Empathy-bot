import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# Получаем токен из переменной окружения, настроенной в Render
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
    text = "👋 Привет! Я твой ИИ-ассистент для анализа голосовых сообщений.\n\n" \
           "Я перевожу аудио в текст, анализирую смысл и предлагаю 3 варианта ответа."
    await message.answer(text, reply_markup=get_main_menu())

@dp.callback_query(F.data == "how_it_works")
async def show_info(callback: CallbackQuery):
    text = "⚙️ Как это работает:\n1. Присылаешь ГС.\n2. Я расшифровываю его.\n3. Генерирую 3 варианта ответа с разной эмоцией."
    await callback.message.edit_text(text, reply_markup=get_back_menu())

@dp.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery):
    text = "👋 Привет! Я твой ИИ-ассистент для анализа голосовых сообщений."
    await callback.message.edit_text(text, reply_markup=get_main_menu())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
