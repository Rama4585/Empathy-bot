from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db_funcs import get_balance

router = Router()

# Сюда перенеси свои функции get_main_menu, get_back_menu, start_cmd, channel, back, example, info
# Везде замени @dp на @router
