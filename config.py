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
    {"title": "1 разбор", "price": 2, "amount": 1},
    {"title": "10 разборов", "price": 15, "amount": 10},
    {"title": "50 разборов", "price": 60, "amount": 50},
    {"title": "Месячный запас (200)", "price": 200, "amount": 200},
]
