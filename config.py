import os
from openai import OpenAI
from aiogram import Bot

# Все импорты и настройки теперь берут данные из системы
TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")

client = OpenAI(
    api_key=os.getenv("ROCKAPI_KEY"),
    base_url="https://api.rockapi.ru/openai/v1"
)

bot = Bot(token=TOKEN)

PACKAGES = [
    {"title": "1 минута", "price": 3, "amount": 1},
    {"title": "10 минут", "price": 20, "amount": 10},
    {"title": "30 минут", "price": 55, "amount": 30},
    {"title": "1 час", "price": 90, "amount": 60},
    {"title": "3 часа", "price": 220, "amount": 180},
    {"title": "5 часов", "price": 300, "amount": 300},
]

ADMIN_ID = 5548854946
