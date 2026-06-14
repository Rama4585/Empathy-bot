from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice, PreCheckoutQuery
from database.db_funcs import get_balance, update_balance
from services.ai_service import process_audio
from config import bot
import os
import asyncio

from config import PACKAGES  # Теперь он увидит список пакетов
router = Router()

# ​В common.py перенести все КЛАВИАТУРЫ и
# хендлеры команд (/start, channel и т.д.).
# И везде заменить @dp на @router.

#=========================
#КЛАВИАТУРЫ
#=========================
def get_main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎙 Отправить голосовое", callback_data="send_audio")],
            [InlineKeyboardButton(text="⚡ Пополнить минуты", callback_data="buy_menu")]
        ]
    )
def get_back_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]]
  )
    
#=====================================
# Хендлеры кнопок, справка итнавигация
#=====================================
@router.message(Command("start"))
async def start_cmd(message: Message):

    uid = message.from_user.id
    bal = max(0, await get_balance(uid))

if bal > 0:
    text = f"""
🎙 <b>Разберу голосовое за 5–15 секунд</b>

✓ Покажу главное
✓ Определю настроение
✓ Предложу варианты ответа

⏱ Осталось: <b>{bal} мин обработки</b>
"""
else:
    text = """
⚠️ <b>Минуты закончились</b>
Пополни баланс или получи бонус
"""
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_main_menu()
    )

@router.callback_query(F.data == "send_audio")
async def send_audio(callback: CallbackQuery):

    bal = max(0, await get_balance(callback.from_user.id))

    if bal <= 0:
        await callback.answer("⚠️ Минуты закончились", show_alert=True)

        await callback.message.answer(
            "⚡ Пополни баланс через кнопку ниже",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="⚡ Пополнить минуты", callback_data="buy_menu")]
                ]
            )
        )

        return
    await callback.answer()
    await callback.message.answer("🎤 Пришли голосовое сообщение для разбора")

@router.callback_query(F.data == "channel")
async def channel(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Перейти на канал", url="https://t.me/empathy_community")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
        ]
    )
    await callback.message.edit_text(
        "🚀 Подпишись на канал\n\nЧто получишь:\n\n🚀 новые функции раньше всех\n🎁 дополнительные разборы\n🛠 показываем как развивается бот\n💬 можно предлагать идеи\n\nПрисоединяйся 👇",
        reply_markup=keyboard
    )
    
@router.callback_query(F.data == "main_menu")
async def back(callback: CallbackQuery):
    bal = await get_balance(callback.from_user.id)
    await callback.message.edit_text(
        "🎙 <b>Разберу голосовое за 5-15 секунд</b>\n\n✓ Покажу главное\n✓ Определю настроение\n✓ Предложу 3 ответа\n\n👇 Отправь голосовое",
        parse_mode="HTML",
        reply_markup=get_main_menu(bal)
    )

@router.callback_query(F.data == "example")
async def example(callback: CallbackQuery):
    await callback.message.edit_text(
"""
🎧 Голосовое • 1:28
📝 Суть: Человек расстроен, но хочет договориться
🙂 Настроение: Раздражение + открытость
💬 Готовые ответы:
1. «Понял тебя. Давай спокойно обсудим»
2. «Что именно тебя больше всего задело?»
3. «Сейчас не готов это обсуждать, но услышал тебя»
""",
        reply_markup=get_back_menu()
    )

@router.callback_query(F.data == "how_it_works")
async def info(callback: CallbackQuery):
    await callback.message.edit_text(
        "🎧 Ты отправляешь голосовое\n\n1. Перевожу в текст\n2. Убираю лишнее\n3. Определяю эмоции\n4. Даю готовые ответы\n\n⏱ Обычно ответ занимает 5-15 секунд",
        reply_markup=get_back_menu()
    ) 

@router.callback_query(F.data == "buy_menu")
async def buy(callback: CallbackQuery):
    kb = [[InlineKeyboardButton(text=f"{p['title']} • {p['price']}⭐", callback_data=f"pay_{p['price']}_{p['amount']}")] for p in PACKAGES]
    kb.append([InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")])
    await callback.message.edit_text("💎 Выбери пакет", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
