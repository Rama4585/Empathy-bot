from aiogram import Router
router = Router()

# Все что касается голосовых и оплаты👇
# Везде заменены @dp на @router.

@router.callback_query(F.data == "send_audio")
async def send_audio_prompt(callback: CallbackQuery):
    bal = await get_balance(callback.from_user.id)
    if bal <= 0:
        await callback.answer("⚠️ Получить ещё минуты", show_alert=True)
    else:
        await callback.answer("🎧 Отправь голосовое\n\nЯ быстро выделю главное, покажу настроение и предложу варианты ответа", show_alert=True)

@router.callback_query(F.data.startswith("pay_"))
async def invoice(callback: CallbackQuery):
    _, price, amount = callback.data.split("_")
    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title=f"{amount} разборов",
        description="Разбор голосовых",
        payload=f"add_{amount}",
        currency="XTR",
        prices=[LabeledPrice(label="Оплата", amount=int(price))]
    )

@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)

@router.message(F.successful_payment)
async def payment(message: Message):
    amount = int(message.successful_payment.invoice_payload.split("_")[1])
    await update_balance(message.from_user.id, amount)
    await message.answer(f"✅ Добавлено {amount} разборов")

@router.message(F.voice)
async def voice(message: Message):
    uid = message.from_user.id
    if await get_balance(uid) <= 0:
        await message.answer("⚠️ Разборы закончились. Пополните баланс через меню старт /start")
        return
    status = await message.answer("🎧 Слушаю... ▰▱▱▱▱")
    file = await bot.get_file(message.voice.file_id)
    path = f"voice_{message.voice.file_id}.ogg"
    await bot.download_file(file.file_path, path)
    try:
        transcript, answer = await asyncio.to_thread(process_audio, path)
        await update_balance(uid, -1)
        new_bal = await get_balance(uid)
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔁 Разобрать ещё одно", callback_data="main_menu")],
            [InlineKeyboardButton(text="💎 Купить попытки", callback_data="buy_menu")]
        ])
        await message.answer(f"📝 **Результат разбора:**\n\n{answer}\n\n✨ Осталось: {new_bal}", reply_markup=kb)
    except Exception as e:
        print(f"Error: {e}") 
        await message.answer("⚠️ Ошибка при анализе. Попробуйте позже.")
    finally:
        if os.path.exists(path): os.remove(path)
        await status.delete()

