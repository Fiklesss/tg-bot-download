import os
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
import yt_dlp

# Токен от BotFather
TOKEN = os.getenv('TELEGRAM_TOKEN')

# Опции для скачивания видео
ydl_opts = {
    'format': 'bestvideo+bestaudio/best',
    'outtmpl': 'video.%(ext)s',
    'quiet': True,
}

# Регулярное выражение для проверки валидности ссылки на YouTube
youtube_regex = re.compile(r'^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$')

async def start(update: Update, context) -> None:
    await update.message.reply_text('Привет! Отправь ссылку на YouTube видео, и я помогу тебе скачать его.')

async def handle_message(update: Update, context) -> None:
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
        await update.message.reply_text('Выберите качество для скачивания:', reply_markup=reply_markup)
    else:
        await update.message.reply_text('Пожалуйста, отправь валидную ссылку на YouTube.')

async def button(update: Update, context) -> None:
    query = update.callback_query
    await query.answer()

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
                await query.message.reply_video(f)
        else:
            await query.message.reply_text('Видео слишком большое для отправки через Telegram. Вот ссылка для скачивания:')
            await query.message.reply_document(document=open(video_file, 'rb'))
    except Exception as e:
        await query.message.reply_text(f'Произошла ошибка при скачивании видео: {str(e)}')

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button))

    # Запуск веб-приложения Flask
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    main()
