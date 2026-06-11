from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from database.db_funcs import get_balance, update_balance
from services.ai_service import process_audio
import asyncio, os
from config import bot

router = Router()

# Сюда перенеси buy_menu, invoice, pre_checkout, payment, voice
# Везде замени @dp на @router
