import asyncio
from aiogram import Dispatcher
from config import bot
from handlers import common, voice

dp = Dispatcher()

async def main():
    dp.include_router(common.router)
    dp.include_router(voice.router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    # Тут можно добавить логику запуска web-сервера, если нужно
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
