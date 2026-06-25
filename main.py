import asyncio
import logging
import sys
import json
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web

from config import BOT_TOKEN
from database.connection import db
from database.models import create_tables
from handlers.start import start_router
from services.vocabulary import VocabularyService

# --- MINI APP API ENDPOINTS ---

async def get_profile_api(request):
    user_id = int(request.rel_url.query.get('user_id', 0))
    query = """
        SELECT u.current_level, u.target_score, u.streak, u.coins,
               p.vocabulary_score, p.grammar_score, p.reading_score, p.listening_score, p.writing_score, p.speaking_score
        FROM users u JOIN user_progress p ON u.user_id = p.user_id WHERE u.user_id = $1
    """
    row = await db.fetchrow(query, user_id)
    if not row:
        return web.json_response({"error": "User not found"}, status=404)
    return web.json_response(dict(row))

async def get_vocabulary_api(request):
    level = request.rel_url.query.get('level', 'A1')
    words = await VocabularyService.get_words_by_level(level)
    return web.json_response([dict(w) for w in words])

async def update_progress_api(request):
    data = await request.json()
    user_id = int(data.get('user_id'))
    section = data.get('section')
    score = float(data.get('score')) # Masalan: 80.0 (foizda)
    
    # 1. Progressni saqlash
    query = f"UPDATE user_progress SET {section}_score = $1 WHERE user_id = $2"
    await db.execute(query, score, user_id)
    
    # 2. Har 10% uchun 1 ball (coin) hisoblash va qo'shish
    calculated_coins = int(score // 10)
    if calculated_coins > 0:
        await db.execute("UPDATE users SET coins = coins + $1 WHERE user_id = $2", calculated_coins, user_id)
        
    return web.json_response({"status": "updated", "earned_coins": calculated_coins})

# --- MAIN RUNNER ---

async def main():
    await db.connect()
    await create_tables()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(start_router)

    app = web.Application()
    app.router.add_get('/api/profile', get_profile_api)
    app.router.add_get('/api/vocabulary', get_vocabulary_api)
    app.router.add_post('/api/progress', update_progress_api)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    
    asyncio.create_task(site.start())
    print("API Server va Bot muvaffaqiyatli ishga tushdi...")
    
    try:
        await dp.start_polling(bot)
    finally:
        await db.disconnect()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())