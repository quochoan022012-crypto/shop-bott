import telebot, json, os, time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8640486596:AAHNd71gPSav2Kikh-R4inRkul6kvXh11ig"
ADMIN_ID = 8521321159

bot = telebot.TeleBot(TOKEN)

DB = "db.json"
HISTORY = "history.json"
COOLDOWN = {}
ADD_MODE = {}

# ===== DATABASE =====
def load(file):
    if not os.path.exists(file):
        return {}
    return json.load(open(file))

def save(file, data):
    json.dump(data, open(file, "w"), indent=4)

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

# ===== HISTORY =====
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

# ===== ACC =====
def get_acc(price):
    file = f"accounts/{price}.txt"
    if not os.path.exists(file):
        return None

    lines = open(file).readlines()
    if not lines:
        return None

    acc = lines[0].strip()
    open(file, "w").writelines(lines[1:])
    return acc

def count_acc(price):
    file = f"accounts/{price}.txt"
    if not os.path.exists(file):
        return 0
    return len(open(file).readlines())

# ===== MENU =====
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
    text += f"💎 ACC KC\n• Giá: 35.000đ\n• Kho: {count_acc(35000)}\n\n"
    text += "👇 Chọn loại acc"

    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("⚡ LV5 (3.000đ)", callback_data="buy_3000"),
        InlineKeyboardButton("💎 KC (35K)", callback_data="buy_35000")
    )
    kb.add(InlineKeyboardButton("⬅️ Quay lại", callback_data="back"))

    return text, kb

def admin_menu():
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("➕ Thêm acc", callback_data="add_acc"),
        InlineKeyboardButton("📦 Xem kho", callback_data="stock")
    )
    kb.add(
        InlineKeyboardButton("💰 Cộng tiền", callback_data="addmoney_help")
    )
    kb.add(InlineKeyboardButton("⬅️ Quay lại", callback_data="back"))
    return kb

# ===== START =====
@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "🏠 MENU CHÍNH", reply_markup=menu())

# ===== CALLBACK =====
@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    uid = c.from_user.id
    user = get_user(uid)

    # chống spam
    if uid in COOLDOWN and time.time() - COOLDOWN[uid] < 2:
        bot.answer_callback_query(c.id, "⏳ Đừng bấm nhanh")
        return
    COOLDOWN[uid] = time.time()

    # ===== USER =====
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
            f"🏦 MB Bank\n"
            f"STK: 208082009\n\n"
            f"Nội dung:\n{code}\n\n"
            f"Gửi bill cho admin")

    elif c.data.startswith("buy_"):
        price = int(c.data.split("_")[1])

        if user["balance"] < price:
            bot.answer_callback_query(c.id, "❌ Không đủ tiền")
            return

        acc = get_acc(price)
        if not acc:
            bot.answer_callback_query(c.id, "❌ Hết acc")
            return

        add_money(uid, -price)
        add_history(uid, f"Mua acc {price}đ")

        bot.send_message(uid, f"✅ ACC:\n{acc}")

    # ===== ADMIN =====
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
        bot.send_message(uid,
            "💰 Dùng lệnh:\n/addmoney user_id amount")

    elif c.data == "add_acc":
        ADD_MODE[uid] = True
        bot.send_message(uid,
            "📥 Nhập acc:\n\n"
            "1 acc:\n3000|tk|mk\n\n"
            "Nhiều acc:\n3000\n"
            "tk|mk\n"
            "tk|mk")

# ===== ADD ACC =====
@bot.message_handler(func=lambda m: True)
def handle_add(m):
    uid = m.from_user.id

    if uid == ADMIN_ID and ADD_MODE.get(uid):

        lines = m.text.strip().split("\n")

        # nhiều acc
        if len(lines) > 1 and lines[0].isdigit():
            price = lines[0]
            count = 0

            os.makedirs("accounts", exist_ok=True)
            file = f"accounts/{price}.txt"

            with open(file, "a") as f:
                for acc in lines[1:]:
                    if "|" in acc:
                        f.write(acc.strip() + "\n")
                        count += 1

            bot.send_message(uid, f"✅ Đã thêm {count} acc {price}")
            ADD_MODE[uid] = False
            return

        # 1 acc
        if "|" in m.text:
            try:
                price, tk, mk = m.text.split("|")

                os.makedirs("accounts", exist_ok=True)
                file = f"accounts/{price}.txt"

                with open(file, "a") as f:
                    f.write(f"{tk}|{mk}\n")

                bot.send_message(uid, f"✅ Đã thêm acc {price}")
                ADD_MODE[uid] = False
                return
            except:
                bot.send_message(uid, "❌ Sai format")

# ===== ADD MONEY =====
@bot.message_handler(commands=['addmoney'])
def addmoney(m):
    if m.from_user.id != ADMIN_ID:
        return
    try:
        _, uid, amount = m.text.split()
        add_money(uid, int(amount))
        bot.send_message(m.chat.id, "✅ OK")
    except:
        bot.send_message(m.chat.id, "Sai cú pháp")

bot.infinity_polling()