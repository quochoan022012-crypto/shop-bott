import telebot, json, os, time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN", "TOKEN")
ADMIN_ID = 8521321159

BANK_NAME = "MB Bank"
BANK_OWNER = "Nguyen Thi Tuyet Mai"
BANK_STK = "208082009"

# ================= INIT =================
bot = telebot.TeleBot(TOKEN)

DB = "db.json"
HISTORY = "history.json"
COOLDOWN = {}
ADD_MODE = {}

os.makedirs("accounts", exist_ok=True)

# ================= DB =================
def load(file):
    if not os.path.exists(file):
        return {}
    try:
        return json.load(open(file, "r", encoding="utf-8"))
    except:
        return {}

def save(file, data):
    json.dump(data, open(file, "w", encoding="utf-8"), indent=4)

def get_user(uid):
    db = load(DB)
    uid = str(uid)
    if uid not in db:
        db[uid] = {"balance": 0}
        save(DB, db)
    return db[uid]

def add_money(uid, amount):
    db = load(DB)
    uid = str(uid)
    if uid not in db:
        db[uid] = {"balance": 0}
    db[uid]["balance"] += amount
    save(DB, db)

def add_history(uid, text):
    h = load(HISTORY)
    uid = str(uid)
    if uid not in h:
        h[uid] = []
    h[uid].append(text)
    save(HISTORY, h)

def get_history(uid):
    h = load(HISTORY)
    return "\n".join(h.get(str(uid), [])[-5:]) or "Chưa có"

# ================= ACC SHOP =================
def get_acc(price):
    file = f"accounts/{price}.txt"
    if not os.path.exists(file):
        return None
    lines = open(file, "r", encoding="utf-8").readlines()
    if not lines:
        return None
    acc = lines[0].strip()
    open(file, "w", encoding="utf-8").writelines(lines[1:])
    return acc

def count_acc(price):
    file = f"accounts/{price}.txt"
    if not os.path.exists(file):
        return 0
    return len(open(file, "r", encoding="utf-8").readlines())

# ================= UI =================
def menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("💰 Số dư", callback_data="balance"),
        InlineKeyboardButton("💳 Nạp tiền", callback_data="nap")
    )
    kb.add(InlineKeyboardButton("🛒 Mua acc", callback_data="shop"))
    kb.add(InlineKeyboardButton("📜 Lịch sử", callback_data="history"))
    kb.add(InlineKeyboardButton("👑 Admin", callback_data="admin"))
    return kb

def shop_menu():
    text = "🛒 *KHU VỰC MUA ACC*\n\n"
    text += f"⚡ ACC LV5\n• Giá: 3.000đ\n• Kho: {count_acc(3000)}\n\n"
    text += f"💎 ACC KC\n• Giá: 40.000đ\n• Kho: {count_acc(40000)}\n\n"
    text += "👇 Chọn loại acc"

    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("⚡ LV5 (3K)", callback_data="buy_3000"),
        InlineKeyboardButton("💎 KC (40K)", callback_data="buy_40000")
    )
    kb.add(InlineKeyboardButton("⬅️ Quay lại", callback_data="back"))
    return text, kb

def admin_menu():
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("➕ Thêm acc", callback_data="add_acc"),
        InlineKeyboardButton("📦 Xem kho", callback_data="stock")
    )
    kb.add(InlineKeyboardButton("💰 Cộng tiền", callback_data="addmoney_help"))
    kb.add(InlineKeyboardButton("⬅️ Quay lại", callback_data="back"))
    return kb

# ================= START =================
@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "🏠 MENU CHÍNH", reply_markup=menu())

# ================= CALLBACK =================
@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    uid = c.from_user.id
    user = get_user(uid)

    if uid in COOLDOWN and time.time() - COOLDOWN[uid] < 2:
        bot.answer_callback_query(c.id, "⏳ Slow down")
        return
    COOLDOWN[uid] = time.time()

    if c.data == "shop":
        text, kb = shop_menu()
        bot.edit_message_text(text, c.message.chat.id, c.message.message_id,
                              reply_markup=kb, parse_mode="Markdown")

    elif c.data == "back":
        bot.edit_message_text("🏠 MENU CHÍNH",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=menu())

    elif c.data == "balance":
        bot.answer_callback_query(c.id, f"💰 {user['balance']}đ", show_alert=True)

    elif c.data == "history":
        bot.send_message(uid, "📜 Lịch sử:\n" + get_history(uid))

    elif c.data == "nap":
        code = f"nap_{uid}"
        bot.send_message(uid,
            f"💳 NẠP TIỀN\n\n"
            f"🏦 Ngân hàng: {MB BANK}\n"
            f"👤 Tên chủ TK: {NGUYEN THI TUYET MAI}\n"
            f"🔢 STK: {208082009}\n\n"
            f"📌 Nội dung:\n{code}")

    elif c.data.startswith("buy_"):
        price = int(c.data.split("_")[1])

        if user["balance"] < price:
            bot.answer_callback_query(c.id, "❌ Không đủ tiền")
            return

        acc = get_acc(price)
        if not acc:
            bot.answer_callback_query(c.id, "❌ Hết hàng")
            return

        add_money(uid, -price)
        add_history(uid, f"Mua acc {price}đ")

        bot.send_message(uid, f"✅ ACC:\n{acc}")

    elif c.data == "admin":
        if uid != ADMIN_ID:
            bot.answer_callback_query(c.id, "❌ Không phải admin")
            return
        bot.edit_message_text("👑 ADMIN PANEL",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=admin_menu())

    elif c.data == "stock":
        bot.send_message(uid,
            f"📦 Kho:\n3K: {count_acc(3000)}\n35K: {count_acc(35000)}")

    elif c.data == "addmoney_help":
        bot.send_message(uid, "Dùng: /addmoney user_id amount")

    elif c.data == "add_acc":
        ADD_MODE[uid] = True
        bot.send_message(uid, "Nhập: 3000|tk|mk")

# ================= ADMIN ADD ACC =================
@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID)
def handle_admin(m):
    uid = m.from_user.id

    if ADD_MODE.get(uid):
        if m.text == "/cancel":
            ADD_MODE[uid] = False
            bot.send_message(uid, "❌ Đã hủy")
            return

        if "|" in m.text:
            price, tk, mk = m.text.split("|")
            with open(f"accounts/{price}.txt", "a", encoding="utf-8") as f:
                f.write(f"{tk}|{mk}\n")
            bot.send_message(uid, "✅ Đã thêm acc")
            ADD_MODE[uid] = False

# ================= ADD MONEY =================
@bot.message_handler(commands=['addmoney'])
def addmoney(m):
    if m.from_user.id != ADMIN_ID:
        return
    try:
        _, uid, amount = m.text.split()
        add_money(uid, int(amount))
        bot.send_message(m.chat.id, "OK")
    except:
        bot.send_message(m.chat.id, "Sai cú pháp")

# ================= RUN =================
bot.infinity_polling()
