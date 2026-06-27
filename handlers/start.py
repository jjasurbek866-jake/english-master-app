from aiogram import Router, html, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from database.connection import db
from keyboards.inline import get_sub_keyboard, get_app_keyboard
from config import CHANNEL_ID

start_router = Router()

async def is_user_subscribed(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
    except Exception:
        return False
    return False

@start_router.message(CommandStart())
async def command_start_handler(message: Message, bot: Bot):
    user_id = message.from_user.id
    
    user = await db.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
    if not user:
        await db.execute(
            "INSERT INTO users (user_id, username, full_name) VALUES ($1, $2, $3)",
            user_id, message.from_user.username, message.from_user.full_name
        )
        await db.execute("INSERT INTO user_progress (user_id) VALUES ($1)", user_id)

    subscribed = await is_user_subscribed(bot, user_id)
    if not subscribed:
        await message.answer(
            f"Salom, {html.bold(message.from_user.full_name)}! Botdan foydalanish uchun rasmiy kanalimizga a'zo bo'ling:",
            reply_markup=get_sub_keyboard(CHANNEL_ID)
        )
    else:
        await message.answer(
            f"Xush kelibsiz! Pastdagi tugmani bosib ilovani oching va darslarni boshlang 👇",
            reply_markup=get_app_keyboard()
        )

@start_router.callback_query(lambda c: c.data == "check_subscription")
async def check_sub_callback(callback: CallbackQuery, bot: Bot):
    subscribed = await is_user_subscribed(callback.bot, callback.from_user.id)
    if subscribed:
        await callback.message.edit_text(
            "Obuna tasdiqlandi! Quyidagi tugma orqali ilovani ochishingiz mumkin:",
            reply_markup=get_app_keyboard()
        )
    else:
        await callback.answer("Siz hali kanalga a'zo bo'lmadingiz!", show_alert=True)
