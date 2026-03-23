import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# Token va Webhook URL (Render bergan linkni qo'yasiz)
BOT_TOKEN = os.getenv("8673330089:AAHiIeUzTEmmltJ8hgpQZVbp8Ce5d-7UMeU", "SIZNING_BOT_TOKENINGIZ")
WEB_SERVER_HOST = "0.0.0.0"
WEB_SERVER_PORT = int(os.getenv("PORT", 8080)) # Render avtomat port beradi
WEBHOOK_PATH = f"/webhook"
WEBHOOK_URL = f"https://vkmbot-3ooc.onrender.com{WEBHOOK_PATH}"

# Bot va Dispatcher yaratamiz
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# /start komandasi
@dp.message(Command("start"))
async def command_start_handler(message: types.Message):
    await message.answer("Salom! Men VKM botga o'xshagan botman. Qo'shiq nomini yoki qo'shiqchini yozing 🎵")

# Musiqa qidirish (Asosiy logika shu yerda bo'ladi)
@dp.message()
async def search_music(message: types.Message):
    query = message.text
    await message.answer(f"🔍 '{query}' qidirilmoqda... (Bu yerga yt-dlp yoki musiqa API logikasi ulanadi)")
    
    # Kelajakda bu yerda bot musiqani topib, message.answer_audio() orqali yuboradi.

# Webhookni ishga tushirish
async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL)

def main():
    dp.startup.register(on_startup)
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
