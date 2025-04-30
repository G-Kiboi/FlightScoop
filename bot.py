from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flight_api import get_flight_data, get_top_deals
from config import TELEGRAM_BOT_TOKEN
import logging
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
from datetime import datetime

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Store last chat ID for scheduled posting
last_chat_id = None

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_chat_id
    last_chat_id = update.effective_chat.id
    msg = (
        "🌍 *Welcome to Flight Scoop!*\n\n"
        "Find cheap flights in real-time.\n\n"
        "Use:\n"
        "`/cheap JFK DXB 2025-06-01`\n"
        "`/flight NYC LON`\n"
        "`/postdeal` – Show hot deals\n"
        "`/help` – List of commands"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

# /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_chat_id
    last_chat_id = update.effective_chat.id
    msg = (
        "🛫 *Flight Scoop Commands:*\n\n"
        "`/cheap ORIGIN DEST [DATE]` – Search cheap flights\n"
        "`/flight ORIGIN DEST [DATE]` – Alias for /cheap\n"
        "`/postdeal` – Show 10 hot flight routes\n"
        "`/start` – Welcome message\n"
        "`/help` – This help menu"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

# /cheap and /flight command
async def cheap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_chat_id
    last_chat_id = update.effective_chat.id

    try:
        args = context.args
        if len(args) < 2:
            raise ValueError("Usage: /cheap ORIGIN DEST [DATE optional]")

        origin = args[0].upper()
        destination = args[1].upper()
        date = args[2] if len(args) > 2 else None

        logger.info(f"Searching flights: {origin} to {destination}, date={date}")
        result = get_flight_data(origin, destination, date)

        # Adding inline button for flight booking
        keyboard = [
            [InlineKeyboardButton("Book Now", url=f"https://www.aviasales.com/search/{origin.lower()}{destination.lower()}1?marker=559862")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            result,
            parse_mode="Markdown",
            disable_web_page_preview=False,
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(
            "❌ Usage: /cheap ORIGIN DEST [DATE optional]\n"
            "Example: /cheap JFK DXB 2025-05-01"
        )

# /postdeal command
async def postdeal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_chat_id
    last_chat_id = update.effective_chat.id
    deals_message = get_top_deals()
    await update.message.reply_text(deals_message, parse_mode="Markdown", disable_web_page_preview=False)

# Scheduler for daily auto post
def scheduled_posting():
    if last_chat_id:
        try:
            deals_message = get_top_deals()
            app.bot.send_message(
                chat_id=last_chat_id,
                text=deals_message,
                parse_mode="Markdown",
                disable_web_page_preview=False
            )
        except Exception as e:
            logger.error(f"[ERROR] Failed to send scheduled post: {e}")

# Scheduler config
scheduler = BackgroundScheduler(timezone=pytz.timezone("US/Eastern"))
scheduler.add_job(scheduled_posting, 'cron', hour=9, minute=0)
scheduler.start()

# App setup
app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("cheap", cheap))
app.add_handler(CommandHandler("flight", cheap))  # Alias
app.add_handler(CommandHandler("postdeal", postdeal))

if __name__ == "__main__":
    print("🚀 Flight Scoop bot running...")
    app.run_polling()
