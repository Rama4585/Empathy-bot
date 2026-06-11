# Сюда перенеси buy_menu, invoice, pre_checkout, payment, voice
# Везде замени @dp на @router

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db_funcs import get_balance, update_balance
from services.ai_service import process_audio
from config import bot
import asyncio, os

router = Router()

@router.callback_query(F.data == "send_audio")
async def send_audio_prompt(callback: CallbackQuery):
    if await get_balance(callback.from_user.id) <= 0:
        await callback.answer("⚠️ Купи попытки", show_alert=True)
    else:
        await callback.answer("🎧 Отправь голосовое", show_alert=True)

@router.callback_query(F.data.startswith("pay_"))
async def invoice(callback: CallbackQuery):
    _, price, amount = callback.data.split("_")
    await bot.send_invoice(callback.message.chat.id, title=f"{amount} разборов", description="Разбор", payload=f"add_{amount}", currency="XTR", prices=[LabeledPrice(label="Оплата", amount=int(price))])

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
    if await get_balance(uid) <= 0: return await message.answer("⚠️ Нет попыток")
    status = await message.answer("🎧 Слушаю...")
    path = f"voice_{message.voice.file_id}.ogg"
    await bot.download_file((await bot.get_file(message.voice.file_id)).file_path, path)
    try:
        transcript, answer = await asyncio.to_thread(process_audio, path)
        await update_balance(uid, -1)
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔁 Ещё", callback_data="main_menu")]])
        await message.answer(f"📝 {answer}", reply_markup=kb)
    finally:
        if os.path.exists(path): os.remove(path)
        await status.delete()
                 
