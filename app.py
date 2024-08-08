import os
import re
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
import yt_dlp

# Токен Telegram бота
TOKEN = os.getenv('TELEGRAM_TOKEN')

# Опции для скачивания видео
ydl_opts = {
    'format': 'bestvideo+bestaudio/best',
    'outtmpl': 'video.%(ext)s',
    'quiet': True,
}

# Регулярное выражение для проверки валидности ссылки на YouTube
youtube_regex = re.compile(r'^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$')

# Flask приложение
app = Flask(__name__)

def start(update: Update, context) -> None:
    update.message.reply_text('Привет! Отправь ссылку на YouTube видео, и я помогу тебе скачать его.')

def handle_message(update: Update, context) -> None:
    url = update.message.text
    if youtube_regex.match(url):
        keyboard = [
            [
                InlineKeyboardButton("240p", callback_data=f'240p|{url}'),
                InlineKeyboardButton("360p", callback_data=f'360p|{url}'),
                InlineKeyboardButton("480p", callback_data=f'480p|{url}'),
                InlineKeyboardButton("720p", callback_data=f'720p|{url}'),
                InlineKeyboardButton("1080p", callback_data=f'1080p|{url}'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Выберите качество для скачивания:', reply_markup=reply_markup)
    else:
        update.message.reply_text('Пожалуйста, отправь валидную ссылку на YouTube.')

def button(update: Update, context) -> None:
    query = update.callback_query
    query.answer()

    quality, url = query.data.split('|')
    format_id = {
        '240p': '18',
        '360p': '18',
        '480p': '135',
        '720p': '136',
        '1080p': '137',
    }[quality]

    ydl_opts['format'] = format_id
    video_file = 'video.mp4'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if os.path.getsize(video_file) < 50 * 1024 * 1024:  # 50MB
            with open(video_file, 'rb') as f:
                query.message.reply_video(f)
        else:
            query.message.reply_text('Видео слишком большое для отправки через Telegram. Вот ссылка для скачивания:')
            query.message.reply_document(document=open(video_file, 'rb'))
    except Exception as e:
        query.message.reply_text(f'Произошла ошибка при скачивании видео: {str(e)}')

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook() -> str:
    update = Update.de_json(request.get_json(force=True), Application.current.dispatcher.bot)
    Application.current.update_queue.put(update)
    return 'ok'

@app.route('/')
def index() -> str:
    return 'Hello, this is the Telegram bot server.'

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button))

    # Запуск webhook вместо polling
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv('PORT', 5000)),
        url_path=TOKEN,
        webhook_url=f"https://{os.getenv('RENDER_EXTERNAL_URL')}/{TOKEN}"
    )

if __name__ == '__main__':
    main()
