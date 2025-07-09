import os
from dotenv import load_dotenv
from datetime import datetime
from telegram import Update, InputMediaPhoto
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes
)

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")

FANSITE_NAME = "𝙠𝙞𝙞𝙞𝙠𝙞𝙞𝙞'𝙨 "
AGENCY_NAME = "𝙎𝙩𝙖𝙧𝙨𝙝𝙞𝙥𝙀𝙣𝙩’𝙨 "

platforms = {
    "info": "#info",
    "reels": "#reels",
    "fansign": "#fansign",
    "tiktok": "#tiktok",
    "twit": "#twit",
    "youtube": "#youtube",
    "ins": "#ins",
    "instastory": "#instastory",
    "bubble": "#bubble",
    "berriz": "#berriz",
    "blog": "#blog"
}

user_state = {}

async def start_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_state[update.effective_user.id] = {
        "step": "choose_platform",
        "images": []
    }
    await update.message.reply_text(
        "Pilih platform:\n- " + "\n- ".join(platforms.keys()) +
        "\n\nSilakan *ketik* salah satu platform di atas.\n"
        "Kamu juga bisa ketik platform *custom* (misalnya: melon, weverse, dll).",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message

    if user_id not in user_state:
        return

    state = user_state[user_id]
    step = state["step"]
    text = message.text.strip()

    if step == "choose_platform":
        platform = text.lower()
        state["platform"] = platform
        state["step"] = "caption"

        if platform in platforms:
            await message.reply_text(f"Kamu pilih: {platform}\nSekarang kirim *caption*.", parse_mode="Markdown")
        else:
            await message.reply_text(
                f"Kamu pilih platform *custom*: `{platform}`\nSekarang kirim *caption*.",
                parse_mode="Markdown"
            )

    elif step == "caption":
        state["caption"] = text
        state["step"] = "tags"
        await message.reply_text("Sekarang kirim *tagar*.\nContoh: `#kiiikiii #haum`\n\n📸 Kirim gambar satu per satu lalu ketik `/done` jika selesai.", parse_mode="Markdown")

    elif step == "tags":
        state["tags"] = text
        if state["platform"] == "youtube":
            state["step"] = "link"
            await message.reply_text("Kirim link YouTube-nya.")
        else:
            state["step"] = "wait_images"
            await message.reply_text("📸 Kirim gambar satu per satu lalu ketik `/done` jika selesai.")

    elif step == "link":
        state["link"] = text
        state["step"] = "wait_images"
        await message.reply_text("📸 Kirim gambar satu per satu lalu ketik `/done` jika selesai.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message

    if user_id not in user_state:
        return

    state = user_state[user_id]
    if state.get("step") != "wait_images":
        return

    photo = message.photo[-1]  # Resolusi tertinggi
    file = await photo.get_file()
    state["images"].append(file.file_id)

async def finish_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_state:
        return

    state = user_state[user_id]
    images = state.get("images", [])

    tanggal = datetime.now().strftime("%y/%m/%d")
    platform = state["platform"]
    caption = state["caption"]
    tags = state["tags"]
    link_line = f"\n\n🔗 {state['link']}" if "link" in state else ""

    platform_tag = platforms.get(platform, f"#{platform}")
    is_known = platform in platforms
    on_or_at = "on" if is_known and platform != "fansign" else "at"
    prefix = (
        FANSITE_NAME if platform in ["tiktok", "youtube", "instastory", "reels"]
        else AGENCY_NAME if platform == "blog"
        else ""
    )

    isi_post = (
        f"{tanggal} 𐙚\n\n"
        f"❝ 𝙝𝙖𝙪𝙢'𝙨  {on_or_at} {prefix}{platform_tag} .ᐟ ❞\n"
        f"── {caption}{link_line}\n\n"
        f"{tags} ✮⋆˙"
    )

    if images:
        media = [
            InputMediaPhoto(media=img, caption=isi_post if i == 0 else None)
            for i, img in enumerate(images)
        ]
        await context.bot.send_media_group(chat_id=CHANNEL_USERNAME, media=media)
    else:
        await context.bot.send_message(chat_id=CHANNEL_USERNAME, text=isi_post)

    await update.message.reply_text("✅ Post berhasil dikirim ke channel.")
    user_state.pop(user_id)

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("post", start_post))
    app.add_handler(CommandHandler("done", finish_post))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Bot berjalan...")
    app.run_polling()

if __name__ == "__main__":
    main()
