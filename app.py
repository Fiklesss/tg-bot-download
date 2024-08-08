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
            print(f"Скачивание видео по URL: {url} с качеством: {quality}")
            ydl.download([url])
            print("Видео успешно скачано")

        if os.path.exists(video_file):
            if os.path.getsize(video_file) < 50 * 1024 * 1024:  # 50MB
                with open(video_file, 'rb') as f:
                    await query.message.reply_video(f)
                    print("Видео отправлено")
            else:
                await query.message.reply_text('Видео слишком большое для отправки через Telegram. Вот ссылка для скачивания:')
                await query.message.reply_document(document=open(video_file, 'rb'))
                print("Видео слишком большое, отправлено как документ")
        else:
            print("Файл видео не найден")
            await query.message.reply_text('Произошла ошибка: файл видео не найден.')
    except Exception as e:
        print(f'Ошибка при скачивании видео: {str(e)}')
        await query.message.reply_text(f'Произошла ошибка при скачивании видео: {str(e)}')
