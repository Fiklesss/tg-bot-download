import os
import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import yt_dlp

TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = Bot(token=TOKEN)

app = Flask(__name__)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

def start(update: Update, context) -> None:
    update.message.reply_text('Привет! Отправь мне ссылку на YouTube видео, и я скачаю его для тебя.')

def download_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        video_url = ydl.prepare_filename(info_dict)
        ydl.download([url])
        return video_url

def handle_message(update: Update, context) -> None:
    url = update.message.text
    try:
        video_path = download_video(url)
        with open(video_path, 'rb') as video:
            bot.send_video(chat_id=update.message.chat_id, video=video)
    except Exception as e:
        update.message.reply_text(f'Произошла ошибка при загрузке видео: {e}')

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook() -> None:
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put(update)
    return 'ok'

@app.route('/')
def index() -> str:
    return 'Hello, this is the Telegram bot server.'

if __name__ == '__main__':
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Убедитесь, что Flask-приложение прослушивает правильный порт
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
