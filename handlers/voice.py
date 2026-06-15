from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    LabeledPrice,
    PreCheckoutQuery
)
from database.db_funcs import (
    get_balance,
    update_balance,
    save_analysis
)
from services.ai_service import process_audio
from config import bot

import os
import asyncio

router = Router()


# ==========================
# Кнопка отправки голосового
# ==========================
@router.callback_query(F.data == "send_audio")
async def send_audio_prompt(callback: CallbackQuery):

    bal = await get_balance(callback.from_user.id)

    if bal <= 0:
        await callback.answer(
            "⚠️ Получить ещё минуты",
            show_alert=True
        )

    else:
        await callback.answer(
            "🎧 Отправь голосовое\n\n"
            "Я быстро выделю главное, покажу настроение и предложу варианты ответа",
            show_alert=True
        )


# ==========================
# Покупка минут
# ==========================
@router.callback_query(F.data.startswith("pay_"))
async def invoice(callback: CallbackQuery):

    _, price, amount = callback.data.split("_")

    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title=f"{amount} мин обработки",
        description="Разбор голосовых",
        payload=f"add_{amount}",
        currency="XTR",
        prices=[
            LabeledPrice(
                label="Оплата",
                amount=int(price)
            )
        ]
    )


@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def payment(message: Message):

    amount = int(
        message.successful_payment.invoice_payload.split("_")[1]
    )

    await update_balance(
        message.from_user.id,
        amount * 60
    )

    await message.answer(
        f"✅ Добавлено {amount} мин обработки"
    )


# ==========================
# Обработка голосового
# ==========================
@router.message(F.voice)
async def voice(message: Message):

    uid = message.from_user.id

    if await get_balance(uid) <= 0:
        await message.answer(
            "⏱ Время разбора закончилось\n\n"
            "Можно получить ещё разборы или пригласить друга 🎁"
        )
        return

    status = await message.answer(
        "🎧 Голосовое получено\n\n"
        "⏳ Анализирую ▰▱▱▱▱"
    )

    file = await bot.get_file(
        message.voice.file_id
    )

    path = f"voice_{message.voice.file_id}.ogg"

    await bot.download_file(
        file.file_path,
        path
    )

    async def loading():

        frames = [
            "▰▱▱▱▱",
            "▰▰▱▱▱",
            "▰▰▰▱▱",
            "▰▰▰▰▱",
            "▰▰▰▰▰"
        ]

        while True:

            for frame in frames:

                try:

                    await status.edit_text(
                        f"🎧 Голосовое получено\n\n"
                        f"⏳ Анализирую {frame}"
                    )

                    await asyncio.sleep(0.4)

                except:
                    return

    loader = asyncio.create_task(
        loading()
    )

    try:

        transcript, answer = await asyncio.to_thread(
            process_audio,
            path
        )
        await save_analysis(
    uid,
    answer
        )

        loader.cancel()

        try:
            await status.delete()
        except:
            pass

        bal = await get_balance(uid)

        spent = min(
            bal,
            message.voice.duration
        )

        await update_balance(
            uid,
            -spent
        )

        new_bal = await get_balance(uid)

        remaining = (
            f"{new_bal / 60:.1f}"
            .rstrip("0")
            .rstrip(".")
        )

        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔁 Разобрать ещё одно",
                        callback_data="main_menu"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="✨ Получить ещё разборы",
                        callback_data="buy_menu"
                    )
                ]
            ]
        )

        await message.reply(
            f"📝 Результат разбора:\n\n"
            f"{answer}\n\n"
            f"⏱ Осталось: {remaining} мин",
            reply_markup=kb
        )

    except Exception as e:

        loader.cancel()

        print(f"Error: {e}")

        try:
            await status.delete()
        except:
            pass

        await message.answer(
            "⚠️ Ошибка при анализе. Попробуйте позже."
        )

    finally:

        if os.path.exists(path):
            os.remove(path)
