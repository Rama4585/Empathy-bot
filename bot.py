# =========================
# WEB + MAIN (Стабильный запуск)
# =========================

async import asyncio
import os
from aiogram import Dispatcher
from aiohttp import web
from config import bot
# Импортируем твои роутеры
from handlers.common import router as common_router
from handlers.voice import router as voice_router

import os
import logging
print(f"DEBUG: Token from environment is: {os.getenv('BOT_TOKEN')[:5]}...") 

dp = Dispatcher()

async def on_startup():
    print("Бот запущен и готов к работе")

async def main():
    # 1. ОБЯЗАТЕЛЬНО ПОДКЛЮЧАЕМ РОУТЕРЫ
    dp.include_router(common_router)
    dp.include_router(voice_router)
    
    await bot.delete_webhook(drop_pending_updates=True)

    app = web.Application()
    app.router.add_get("/", lambda r: web.Response(text="Бот работает"))

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        int(os.getenv("PORT", 10000))
    )
    await site.start()

    # 2. Запуск поллинга с учетом роутеров
    await dp.start_polling(bot, on_startup=on_startup)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
