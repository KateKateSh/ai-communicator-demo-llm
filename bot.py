import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TG_TOKEN = os.environ.get("TG_TOKEN") or "your_token_here"
SUBSCRIBERS_FILE = "subscribers.txt"

def load_subscribers():
    if os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE, "r") as f:
            return set(map(str.strip, f.readlines()))
    return set()

def save_subscriber(chat_id):
    subscribers = load_subscribers()
    if str(chat_id) not in subscribers:
        with open(SUBSCRIBERS_FILE, "a") as f:
            f.write(f"{chat_id}\n")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    save_subscriber(chat_id)
    await context.bot.send_message(chat_id=chat_id, text="✅ Вы подписаны на уведомления от AI-коммуникатора спроса!")

def get_all_subscribers():
    return list(load_subscribers())

def send_to_all_subscribers(text):
    chat_ids = get_all_subscribers()
    for chat_id in chat_ids:
        try:
            url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            print(f"Ошибка при отправке в {chat_id}: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TG_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()
