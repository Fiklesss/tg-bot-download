import os
import logging
from flask import Flask, request
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import yt_dlp

TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = Bot(token=TOKEN)

app = Flask(__name__)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Функция для команды /start
async def start(update: Update, context) -> None:
    await update.message.reply_text('Привет! Отправь мне ссылку на YouTube видео, и я скачаю его для тебя.')

# Функция для загрузки видео с YouTube
def download_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# Обработка текстовых сообщений
async def handle_message(update: Update, context) -> None:
    url = update.message.text
    try:
        download_video(url)
        with open('downloads/video.mp4', 'rb') as video:
            await bot.send_video(chat_id=update.message.chat_id, video=video)
    except Exception as e:
        logging.error(f"Error downloading video: {e}")
        await update.message.reply_text('Произошла ошибка при загрузке видео.')

# Обработка вебхуков от Telegram
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put(update)
    return 'ok'

# Главная страница
@app.route('/')
def index():
    return 'Hello, this is the Telegram bot server.'

# Основная функция
if __name__ == '__main__':
    # Создаем приложение Telegram
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчики команд и сообщений
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Устанавливаем вебхук
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    bot.setWebhook(webhook_url)

    # Запускаем Flask приложение
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 0)))

    # Запуск Telegram бота
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 0)),
        url_path=TOKEN,
        webhook_url=webhook_url
    )
