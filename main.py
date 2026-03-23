import os
import logging
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
import yt_dlp
import static_ffmpeg

# FFmpeg-ni tizimga ulaymiz (Render uchun shart)
static_ffmpeg.add_paths()

# --- SOZLAMALAR ---
# Tokenni BotFather'dan olinganiga almashtiring
BOT_TOKEN = "8673330089:AAHiIeUzTEmmltJ8hgpQZVbp8Ce5d-7UMeU"

# Render'da "Web Service" yaratganingizdan so'ng beriladigan linkni qo'ying
BASE_URL = "https://vkmbot-3ooc.onrender.com" 

WEB_SERVER_HOST = "0.0.0.0"
WEB_SERVER_PORT = int(os.getenv("PORT", 8080))
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{BASE_URL}{WEBHOOK_PATH}"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- MUSIQA YUKLASH LOGIKASI ---
async def download_music(query):
    # Fayl nomini vaqtinchalik yaratamiz
    file_id = f"music_{hash(query)}"
    outtmpl = f"{file_id}.%(ext)s"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'default_search': 'ytsearch1:',
        'outtmpl': file_id, # Fayl nomi
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
        'prefer_ffmpeg': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        loop = asyncio.get_event_loop()
        # YouTube-dan qidirish va yuklash
        info = await loop.run_in_executor(None, lambda: ydl.extract_info(query, download=True))
        title = info['entries'][0]['title'] if 'entries' in info else info['title']
        return f"{file_id}.mp3", title

# --- BOT KOMANDALARI ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "🎵 **VKM Bot Clone**-ga xush kelibsiz!\n\n"
        "Qo'shiq nomi yoki ijrochini yozing, men uni topib beraman."
    )

@dp.message(F.text)
async def handle_message(message: types.Message):
    query = message.text
    status_msg = await message.answer(f"🔍 '{query}' qidirilmoqda... kuting ⏳")
    
    try:
        # Musiqani yuklaymiz
        file_path, title = await download_music(query)
        
        # Audio faylni yuboramiz
        audio_file = types.FSInputFile(file_path)
        await message.answer_audio(
            audio=audio_file, 
            caption=f"✅ {title}\n\n🤖 @vkmbot_bot orqali yuklandi"
        )
        
        # Holat xabarini o'chirish va faylni tozalash
        await status_msg.delete()
        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await status_msg.edit_text("❌ Kechirasiz, musiqa topilmadi yoki yuklashda xato berdi.")

# --- WEBHOOK VA STARTUP ---
async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL)

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
