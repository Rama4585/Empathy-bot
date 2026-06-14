import os
import sys
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from openai import OpenAI

# 1. КОНФИГУРАЦИЯ И ПЕРЕМЕННЫЕ
TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")

# Настройка клиента OpenAI
client = OpenAI(
    api_key=os.getenv("ROCKAPI_KEY"),
    base_url="https://api.rockapi.ru/openai/v1"
)

# Инициализация бота
bot = Bot(token=TOKEN)
dp = Dispatcher()

# 2. ИМПОРТ РОУТЕРОВ (после инициализации dp и bot)
from handlers.common import router as common_router
from handlers.voice import router as voice_router

# 3. ОСНОВНОЙ ФУНКЦИОНАЛ
async def on_startup():
    print("Бот запущен и готов к работе")

async def main():
    dp.include_router(common_router)
    dp.include_router(voice_router)
    
    await bot.delete_webhook(drop_pending_updates=True)

    # Веб-сервер для Render
    app = web.Application()
    app.router.add_get("/", lambda r: web.Response(text="Бот работает"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", 10000)))
    await site.start()

    # Запуск бота
    await dp.start_polling(bot, on_startup=on_startup)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Ошибка запуска: {e}")
        
