from aiogram import Router
router = Router()
# ​В common.py перенести все КЛАВИАТУРЫ и
# хендлеры команд (/start, channel и т.д.).
# И везде заменить @dp на @router.
#=========================

#КЛАВИАТУРЫ

#=========================
def get_main_menu(balance):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"🎤 Разобрать голосовое • осталось {balance}", callback_data="send_audio")],
            [InlineKeyboardButton(text="✨ Посмотреть пример", callback_data="example")],
            [InlineKeyboardButton(text="💎 Получить ещё попытки", callback_data="buy_menu")],
            [InlineKeyboardButton(text="🚀 Подписаться на канал", callback_data="channel")],
            [InlineKeyboardButton(text="❓ Как это работает", callback_data="how_it_works")]
        ]
    )

def get_back_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]]
  )
  
