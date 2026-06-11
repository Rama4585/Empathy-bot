# =========================
# WEB + MAIN (Стабильный запуск)
# =========================

async def on_startup():
    print("Бот запущен и готов к работе")


async def main():
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

    await dp.start_polling(bot, on_startup=on_startup)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
