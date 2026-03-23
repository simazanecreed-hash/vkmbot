import os
import logging
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
import yt_dlp

# --- SOZLAMALAR ---
BOT_TOKEN = "8673330089:AAHiIeUzTEmmltJ8hgpQZVbp8Ce5d-7UMeU"
WEB_SERVER_HOST = "0.0.0.0"
WEB_SERVER_PORT = int(os.getenv("PORT", 8080))
WEBHOOK_PATH = "/webhook"

# SIZNING RENDER LINKINGIZ JOYLASHDIRILDI:
BASE_URL = "https://vkmbot-3ooc.onrender.com" 
WEBHOOK_URL = f"{BASE_URL}{WEBHOOK_PATH}"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- MUSIQA QIDIRISH VA YUKLASH FUNKSIYASI ---
async def download_music(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'default_search': 'ytsearch1:',
        'outtmpl': 'music.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
    }
    # Render (Linux) uchun yt-dlp ni ishlatish
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, lambda: ydl.extract_info(query, download=True))
        title = info['entries'][0]['title'] if 'entries' in info else info['title']
        return "music.mp3", title

# --- BOT KOMANDALARI ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("🎵 Salom! Men VKM botga o'xshagan botman.\n\nQo'shiq nomini yoki ijrochini yozing, men uni topib beraman!")

@dp.message(F.text)
async def handle_message(message: types.Message):
    query = message.text
    # Foydalanuvchi kutib turishi uchun xabar
    processing_msg = await message.answer(f"🔍 '{query}' qidirilmoqda... Iltimos, kuting ⏳")
    
    try:
        file_path, title = await download_music(query)
        audio_file = types.FSInputFile(file_path)
        
        # Musiqani yuborish
        await message.answer_audio(
            audio=audio_file, 
            caption=f"✅ {title}\n\n🤖 @vkmbot_bot orqali yuklandi"
        )
        
        # Vaqtinchalik xabarni o'chirish va faylni serverdan o'chirish
        await processing_msg.delete()
        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        logging.error(f"Xatolik yuz berdi: {e}")
        await processing_msg.edit_text("❌ Kechirasiz, musiqa topilmadi yoki yuklashda xatolik yuz berdi.")

# --- WEBHOOK ISHGA TUSHIRISH ---
async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook o'rnatildi: {WEBHOOK_URL}")

def main():
    dp.startup.register(on_startup)
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
