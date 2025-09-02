import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables (set these in Render)
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "123456789"))   # Replace with your Telegram ID
LOGGER_GROUP_ID = int(os.getenv("LOGGER_GROUP_ID", "-1001234567890"))  # Replace with group ID


# === Commands ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 Hello! I am **NSFW Protection Bot**.\n\n"
        "✅ I will automatically scan & delete adult/NSFW stickers and images in your groups.\n"
        "⚡ Add me as *Admin* with **Delete + Ban** rights.\n\n"
        "👮 Warnings system:\n"
        "3 ❌ = Auto Ban 🚫"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


# === Example NSFW check (dummy for now) ===
def is_nsfw(file_path: str) -> bool:
    # 👉 Abhi ke liye demo: sticker/image ko delete karne ke liye False return karo
    # Baad me API integrate kar sakte ho
    return False


# === Message Handler ===
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_path = None

    # Photo
    if update.message.photo:
        file = await update.message.photo[-1].get_file()
        file_path = "photo.jpg"
        await file.download_to_drive(file_path)

    # Sticker
    elif update.message.sticker and not update.message.sticker.is_animated:
        file = await update.message.sticker.get_file()
        file_path = "sticker.png"
        await file.download_to_drive(file_path)

    if file_path and is_nsfw(file_path):
        try:
            await update.message.delete()
            await context.bot.send_message(
                chat_id=LOGGER_GROUP_ID,
                text=f"⚠️ NSFW content deleted in {update.effective_chat.title} from {update.effective_user.mention_html()}",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Error deleting message: {e}")


# === Main ===
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Sticker.ALL, handle_file))

    logger.info("Bot started!")
    app.run_polling()


if __name__ == "__main__":
    main()
