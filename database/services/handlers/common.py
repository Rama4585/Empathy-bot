# Сюда перенеси свои функции get_main_menu, get_back_menu, start_cmd, channel, back, example, info
# Везде замени @dp на @router

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db_funcs import get_balance
from config import PACKAGES

router = Router()

def get_main_menu(balance):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🎤 Разобрать голосовое • осталось {balance}", callback_data="send_audio")],
        [InlineKeyboardButton(text="✨ Посмотреть пример", callback_data="example")],
        [InlineKeyboardButton(text="💎 Получить ещё попытки", callback_data="buy_menu")],
        [InlineKeyboardButton(text="🚀 Подписаться на канал", callback_data="channel")],
        [InlineKeyboardButton(text="❓ Как это работает", callback_data="how_it_works")]
    ])

def get_back_menu():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]])

@router.message(Command("start"))
async def start_cmd(message: Message):
    bal = await get_balance(message.from_user.id)
    await message.answer("🎧 <b>Отправь голосовое</b>", parse_mode="HTML", reply_markup=get_main_menu(bal))

@router.callback_query(F.data == "channel")
async def channel(callback: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🚀 Перейти", url="https://t.me/empathy_community")], [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]])
    await callback.message.edit_text("🚀 Подпишись на канал", reply_markup=kb)

@router.callback_query(F.data == "main_menu")
async def back(callback: CallbackQuery):
    bal = await get_balance(callback.from_user.id)
    await callback.message.edit_text("🎙 <b>Разберу голосовое</b>", parse_mode="HTML", reply_markup=get_main_menu(bal))

@router.callback_query(F.data == "example")
async def example(callback: CallbackQuery):
    await callback.message.edit_text("🎧 Пример разбора...", reply_markup=get_back_menu())

@router.callback_query(F.data == "how_it_works")
async def info(callback: CallbackQuery):
    await callback.message.edit_text("Как это работает...", reply_markup=get_back_menu())

@router.callback_query(F.data == "buy_menu")
async def buy(callback: CallbackQuery):
    kb = [[InlineKeyboardButton(text=f"{p['title']} • {p['price']}⭐", callback_data=f"pay_{p['price']}_{p['amount']}")] for p in PACKAGES]
    kb.append([InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")])
    await callback.message.edit_text("💎 Выбери пакет", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
