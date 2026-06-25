import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web

from config import BOT_TOKEN
from database.connection import db
from database.models import create_tables
from handlers.start import start_router
from services.vocabulary import VocabularyService
from services.gemini_ai import GeminiLanguageService

ai_service = GeminiLanguageService()

async def get_profile_api(request):
    user_id = int(request.rel_url.query.get('user_id', 0))
    query = """
        SELECT u.current_level, u.target_score, u.streak, u.coins,
               p.grammar_score, p.vocabulary_score, p.reading_score, p.listening_score, p.writing_score, p.speaking_score
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
    score = float(data.get('score')) 
    
    query = f"UPDATE user_progress SET {section}_score = $1 WHERE user_id = $2"
    await db.execute(query, score, user_id)
    
    calculated_coins = int(score // 10)
    if calculated_coins > 0:
        await db.execute("UPDATE users SET coins = coins + $1 WHERE user_id = $2", calculated_coins, user_id)
        
    return web.json_response({"status": "updated", "earned_coins": calculated_coins})

async def check_writing_api(request):
    try:
        data = await request.json()
        user_id = int(data.get('user_id'))
        topic = data.get('topic')
        essay_text = data.get('essay_text')
        
        if not essay_text or len(essay_text.strip()) < 10:
            return web.json_response({"error": "Matn juda qisqa"}, status=400)
            
        ai_result = await ai_service.check_essay(essay_text, topic)
        
        if "band_score" in ai_result and ai_result["band_score"] != "Nomalum":
            await db.execute("UPDATE users SET coins = coins + 5 WHERE user_id = $1", user_id)
            ai_result["earned_coins"] = 5
        else:
            ai_result["earned_coins"] = 0
            
        return web.json_response(ai_result)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def main():
    await db.connect()
    await create_tables()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(start_router)

    app = web.Application()
    
    async def cors_middleware(app, handler):
        async def middleware(request):
            if request.method == "OPTIONS":
                response = web.Response()
            else:
                response = await handler(request)
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type"
            return response
        return middleware
        
    app.middlewares.append(cors_middleware)

    app.router.add_get('/api/profile', get_profile_api)
    app.router.add_get('/api/vocabulary', get_vocabulary_api)
    app.router.add_post('/api/progress', update_progress_api)
    app.router.add_post('/api/check-writing', check_writing_api)
    
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