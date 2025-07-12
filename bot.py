
import logging
import time
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext, CallbackQueryHandler
import json

# توکن ربات و آی‌دی تلگرامی شما
BOT_TOKEN = "7878841275:AAEt8FiuYHAzg4no_c-jnXYZ_ZPUu2Ct160"
AUTHORIZED_USER_ID = 6006382205  # آی‌دی شما

# ذخیره زمان آخرین بررسی
last_check_file = "last_check.txt"

# تابع گرفتن بازی‌های رایگان از API عمومی
def get_free_games():
    url = "https://www.gamerpower.com/api/giveaways"
    try:
        response = requests.get(url)
        data = response.json()
    except:
        return []

    games = []
    for item in data:
        if item["platforms"] and "steam" in item["platforms"].lower():
            games.append({
                "title": item["title"],
                "worth": item["worth"],
                "end_date": item["end_date"],
                "description": item["description"],
                "open_giveaway_url": item["open_giveaway_url"],
                "gameplay": f"https://www.youtube.com/results?search_query={item['title'].replace(' ', '+')}+gameplay"
            })
    return games

def filter_new_games(games):
    try:
        with open(last_check_file, "r") as f:
            last_time = f.read().strip()
    except:
        last_time = "2000-01-01T00:00:00Z"

    last_dt = datetime.strptime(last_time, "%Y-%m-%dT%H:%M:%SZ")
    new_games = []

    for game in games:
        try:
            game_dt = datetime.strptime(game["end_date"], "%Y-%m-%d %H:%M:%S")
            if game_dt > last_dt:
                new_games.append(game)
        except:
            continue
    return new_games

def update_last_check():
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(last_check_file, "w") as f:
        f.write(now)

async def start(update: Update, context: CallbackContext):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        await update.message.reply_text("❌ شما مجاز به استفاده از این ربات نیستید.")
        return

    keyboard = [[InlineKeyboardButton("🎮 بررسی بازی‌های رایگان", callback_data="check_games")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام داداش 👋\nبرای دیدن بازی‌های رایگان دکمه زیر رو بزن:", reply_markup=reply_markup)

async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != AUTHORIZED_USER_ID:
        await query.edit_message_text("❌ شما مجاز به استفاده از این ربات نیستید.")
        return

    if query.data == "check_games":
        games = get_free_games()
        new_games = filter_new_games(games)

        if not new_games:
            await query.edit_message_text("هیچ بازی رایگان جدیدی از آخرین بررسی پیدا نشد 😕")
            return

        await query.edit_message_text("✅ بازی‌های رایگان جدید پیدا شد:")

        for game in new_games[:5]:
            message = f"🎮 <b>{game['title']}</b>\n\n"
            message += f"📖 توضیح: {game['description'][:300]}...\n"
            message += f"⏳ رایگان تا: {game['end_date']}\n"
            message += f"🔗 <a href='{game['open_giveaway_url']}'>صفحه بازی</a>\n"
            message += f"▶️ <a href='{game['gameplay']}'>گیم‌پلی بازی</a>\n"
            try:
                await context.bot.send_message(chat_id=AUTHORIZED_USER_ID, text=message, parse_mode="HTML", disable_web_page_preview=True)
            except:
                pass

        update_last_check()

def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    app.run_polling()

if __name__ == "__main__":
    main()
