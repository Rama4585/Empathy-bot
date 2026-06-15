from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URL

# Подключение к MongoDB
db_client = AsyncIOMotorClient(MONGO_URL)
db = db_client.bot_database
users_col = db.users

# ФУНКЦИИ БД (Вместо JSON)
async def get_balance(uid):
    user = await users_col.find_one({"uid": str(uid)})
    return user["balance"] if user else 5

async def update_balance(uid, amount_change):
    await users_col.update_one(
        {"uid": str(uid)},
        {"$inc": {"balance": amount_change}},
        upsert=True
    )

async def save_analysis(uid, text):
    await users_col.update_one(
        {"uid": str(uid)},
        {
            "$push": {
                "analyses": {
                    "$each": [text],
                    "$slice": -20
                }
            }
        },
        upsert=True
    )
    
async def get_analyses(uid):

    user = await users_col.find_one(
        {"uid": str(uid)}
    )
    if not user:
        return []
        
    return user.get(
        "analyses",
        []
    )
