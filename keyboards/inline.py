from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

MINI_APP_URL = "https://jjasurbek866-jake.github.io/english-master-app/"

def get_sub_keyboard(channel_username: str):
    buttons = [
        [InlineKeyboardButton(text="📢 Kanalga obuna bo'lish", url=f"https://t.me/{channel_username.replace('@', '')}")],
        [InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_subscription")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_app_keyboard():
    buttons = [
        [InlineKeyboardButton(text="📱 English Master App'ni ochish", web_app=WebAppInfo(url=MINI_APP_URL))]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
