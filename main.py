from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
import requests, os, random, io

# AMBIL DATA DARI ENV VARIABLE
TOKEN = os.environ.get("8114502494:AAGEpfA_KRvJ8ku_sG5Fhn17VTbfZd7nw-I")
ADMIN_ID = int(os.environ.get("ADMIN_ID",6977522417))  # Default kalau belum di-set
IMGBB_API = os.environ.get("IMGBB_API", "YOUR_IMGBB_API")

curhat_list = []

async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🎵 YouTube ke MP3", callback_data='ytmp3')],
        [InlineKeyboardButton("📥 Video DL (YT/TikTok/IG)", callback_data='vid')],
        [InlineKeyboardButton("🖼️ Stiker ke Gambar", callback_data='sticker')],
        [InlineKeyboardButton("🌈 Teks ke Gambar", callback_data='textimg')],
        [InlineKeyboardButton("🤖 AI Chat", callback_data='ai')],
        [InlineKeyboardButton("💌 Anon Curhat", callback_data='curhat')],
        [InlineKeyboardButton("🔗 Shortlink", callback_data='short')],
        [InlineKeyboardButton("🎧 Video ke MP3", callback_data='v2a')],
        [InlineKeyboardButton("🌟 Random Quote", callback_data='quote')],
        [InlineKeyboardButton("👤 Info Kamu", callback_data='me')],
    ]
    await update.message.reply_text("Selamat datang! Pilih fitur yang kamu mau:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    data = query.data

    context.user_data['mode'] = data

    if data == 'quote':
        quotes = [
            "Jangan menyerah, besok mungkin lebih baik.",
            "Anime teaches us: never give up.",
            "Hidup bukan soal menunggu badai reda, tapi belajar menari di tengah hujan.",
        ]
        await query.edit_message_text(random.choice(quotes))
    elif data == 'me':
        user = query.from_user
        await query.edit_message_text(f"🆔 ID: `{user.id}`\n👤 Username: @{user.username}")
    else:
        pesan = {
            'ytmp3': "Kirim link YouTube untuk diubah ke MP3.",
            'vid': "Kirim link video dari YouTube, TikTok, atau Instagram.",
            'sticker': "Kirim stiker untuk dikonversi ke gambar PNG.",
            'textimg': "Tulis teks aesthetic yang mau dijadiin gambar.",
            'ai': "Tanya apa aja ke AI.",
            'curhat': "Ketik curhatan kamu secara anonim:",
            'short': "Kirim link panjang yang mau diperpendek.",
            'v2a': "Kirim video untuk diubah ke audio."
        }
        await query.edit_message_text(pesan.get(data, "Silakan kirim pesan."))

async def message_handler(update: Update, context: CallbackContext):
    mode = context.user_data.get('mode')
    text = update.message.text

    if mode == 'ytmp3':
        await update.message.reply_text("Fitur ini perlu API tambahan. Sementara belum aktif.")
    elif mode == 'vid':
        await update.message.reply_text("Fitur ini perlu API downloader. Masih dikembangkan.")
    elif mode == 'textimg':
        await update.message.reply_text("Fitur upload image ke ImgBB sementara dummy (belum jalan).")
    elif mode == 'ai':
        await update.message.reply_text("Jawaban dari AI (simulasi):\n" + text[::-1])
    elif mode == 'curhat':
        curhat_list.append(text)
        await update.message.reply_text("Curhatan kamu sudah dikirim secara anonim. ❤️")
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"Ada curhat anonim:\n{text}")
    elif mode == 'short':
        shorted = f"https://short.url/{random.randint(1000,9999)}"
        await update.message.reply_text(f"Link pendek: {shorted}")
    else:
        await update.message.reply_text("Pilih fitur dulu ya dengan /start.")

async def sticker_handler(update: Update, context: CallbackContext):
    if context.user_data.get('mode') == 'sticker':
        file = await context.bot.get_file(update.message.sticker.file_id)
        await file.download_to_drive("sticker.png")
        await update.message.reply_document(document=open("sticker.png", "rb"))

async def video_handler(update: Update, context: CallbackContext):
    if context.user_data.get('mode') == 'v2a':
        file = await update.message.video.get_file()
        await file.download_to_drive("video.mp4")
        os.system("ffmpeg -i video.mp4 audio.mp3")
        await update.message.reply_audio(audio=open("audio.mp3", "rb"))

async def admin_reply(update: Update, context: CallbackContext):
    if str(update.message.chat_id) == str(ADMIN_ID) and update.message.reply_to_message:
        target_id = update.message.reply_to_message.text.split("ID: ")[-1]
        await context.bot.send_message(chat_id=target_id, text=update.message.text)

# === JALANKAN BOT ===
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
app.add_handler(MessageHandler(filters.Sticker.ALL, sticker_handler))
app.add_handler(MessageHandler(filters.Video.ALL, video_handler))
app.add_handler(MessageHandler(filters.TEXT & filters.REPLY, admin_reply))
app.run_polling()