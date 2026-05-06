import os
import json
import time
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# =====================
# CONFIG
# =====================
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise Exception("TOKEN chưa được set trong Railway Variables")

bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 8521321159

DB_FILE = "db.json"
HISTORY_FILE = "history.json"

COOLDOWN = {}
ADD_MODE = {}

# =====================
# LOAD / SAVE JSON
# =====================
def load(file):
    if not os.path.exists(file):
        return {}
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

db = load(DB_FILE)
history = load(HISTORY_FILE)

# =====================
# START
# =====================
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "🤖 Bot đã hoạt động!\nDùng /help để xem lệnh."
    )

# =====================
# HELP
# =====================
@bot.message_handler(commands=["help"])
def help_cmd(message):
    bot.send_message(
        message.chat.id,
        "/start - bắt đầu\n/help - trợ giúp"
    )

# =====================
# ADMIN CHECK
# =====================
def is_admin(user_id):
    return user_id == ADMIN_ID

# =====================
# ECHO TEST
# =====================
@bot.message_handler(func=lambda m: True)
def echo(message):
    bot.send_message(message.chat.id, f"Bạn gửi: {message.text}")

# =====================
# RUN BOT
# =====================
print("Bot is running...")
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print("Error:", e)
        time.sleep(5)
