import os
import sqlite3
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, 
    ReplyKeyboardMarkup, KeyboardButton
)

# استفاده از مقادیر عمومی و تست برای عبور از ارور سایت تلگرام
API_ID = 611335
API_HASH = "d524b414d21f4d3e708af9b6b06353d7"
BOT_TOKEN = "8975637630:AAGldM14z3YF6M-PhjohByUq0g-RENnH7M4"  # توکن ربات خود را اینجا وارد کنید
ADMIN_ID = 8635403087
CARD_NUMBER = "6104337300101910"

app = Client("ConfigSalesBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def get_db():
    conn = sqlite3.connect('bot_database.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def is_admin(user_id):
    if user_id == ADMIN_ID:
        return True
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM admins WHERE user_id = ?", (user_id,))
    res = cursor.fetchone()
    db.close()
    return res is not None

def main_menu(user_id):
    keyboard = [
        [KeyboardButton("🛒 خرید کانفینگ"), KeyboardButton("📦 کانفینگ‌های خریداری‌شده")],
        [KeyboardButton("🎁 وارد کردن کد هدیه"), KeyboardButton("💳 شارژ حساب")],
        [KeyboardButton("⭐️خرید با امتیاز"), KeyboardButton("⭐️امتیاز های من")],
        [KeyboardButton("👥 زیرمجموعه‌گیری"), KeyboardButton("🛟 پشتیبانی")]
    ]
    if is_admin(user_id):
        keyboard.append([KeyboardButton("🛠 پنل مدیریت")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def admin_menu():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🎁 ساخت کد هدیه"), KeyboardButton("💰 درخواست‌های شارژ")],
        [KeyboardButton("📢 پیام همگانی"), KeyboardButton("⚙️ تنظیمات ربات")],
        [KeyboardButton("📊 آمار ربات"), KeyboardButton("📦 مدیریت پکیج‌ها")],
        [KeyboardButton("🛠 پنل مدیریت (دکمه‌ها)"), KeyboardButton("➕ افزودن ادمین")],
        [KeyboardButton("💻افزودن کانال اجباری"), KeyboardButton("⭐️انتقال امتیاز")],
        [KeyboardButton("👨‍🔧مسدود کاربر"), KeyboardButton("👨‍🔧رفع مسدودیت کاربر")],
        [KeyboardButton("🗽آمار کاربر"), KeyboardButton("🔙 بازگشت به منوی اصلی")]
    ], resize_keyboard=True)

async def check_forced_join(client, user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT channel_username FROM forced_channels")
    channels = cursor.fetchall()
    db.close()

    for ch in channels:
        ch_name = ch['channel_username']
        try:
            member = await client.get_chat_member(ch_name, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            pass
    return True

@app.on_message(filters.command("start"))
async def start_command(client, message):
    user_id = message.from_user.id
    username = message.from_user.username or "None"
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    args = message.text.split()
    if not user:
        referrer_id = None
        if len(args) > 1 and args[1].isdigit():
            ref_id = int(args[1])
            if ref_id != user_id:
                cursor.execute("SELECT * FROM users WHERE user_id = ?", (ref_id,))
                if cursor.fetchone():
                    referrer_id = ref_id
                    cursor.execute("UPDATE users SET points = points + 5 WHERE user_id = ?", (ref_id,))
        
        cursor.execute("INSERT INTO users (user_id, username, referrer_id) VALUES (?, ?, ?)", (user_id, username, referrer_id))
        db.commit()

    cursor.execute("SELECT is_blocked FROM users WHERE user_id = ?", (user_id,))
    b_status = cursor.fetchone()
    if b_status and b_status['is_blocked'] == 1:
        db.close()
        return await message.reply("❌ شما توسط ادمین مسدود شده‌اید.")
    db.close()

    is_joined = await check_forced_join(client, user_id)
    if not is_joined:
        join_text = "لطفا ابتدا در چنل‌های زیر عضو شوید:\n@kanfing_plus_ir\n@jadoooi\nسپس /start را بزنید."
        return await message.reply(join_text)

    welcome_text = (
        "به ربات فروش کانفینگPlus خوش آمدید♻️☎️\n"
        "لطفا یکی از دکمه‌های زیر را انتخاب کنید👨‍🔧"
    )
    await message.reply(welcome_text, reply_markup=main_menu(user_id))

@app.on_message(filters.regex("🛒 خرید کانفینگ"))
async def buy_config(client, message):
    prices_text = (
        "لیست قیمت‌های کانفینگ⭐️\n\n"
        "10گیگ+1ماه+150تومان❗️\n"
        "15گیگ+1ماه+225تومان❗️\n"
        "20گیگ+1ماه+300تومان❗️\n"
        "30گیگ+1ماه+375تومان❗️\n"
        "40گیگ+2ماه+465تومان❗️\n"
        "50گیگ+2ماه+555تومان❗️\n"
        "100گیگ+4ماه+700تومان❗️\n\n"
        f"💳 برای خرید، مبلغ را به شماره کارت زیر واریز کرده و رسید آن را ارسال کنید:\n`{CARD_NUMBER}`"
    )
    await message.reply(prices_text, parse_mode="markdown")

@app.on_message(filters.photo & filters.private)
async def handle_receipt(client, message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        return

    admin_keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ تایید رسید", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton("❌ رد رسید", callback_data=f"reject_{user_id}")
        ]
    ])
    
    caption = f"📦 رسید جدید از طرف کاربر: `{user_id}`\nلطفاً بررسی کنید."
    await message.forward(ADMIN_ID)
    await client.send_message(ADMIN_ID, caption, reply_markup=admin_keyboard, parse_mode="markdown")
    await message.reply("✅ رسید شما با موفقیت برای پشتیبانی ارسال شد. منتظر تایید باشید.")

@app.on_callback_query(filters.regex("^(approve|reject)_"))
async def callback_receipt(client, callback_query):
    data = callback_query.data.split("_")
    action = data[0]
    target_user_id = int(data[1])

    if action == "approve":
        await client.send_message(target_user_id, "پول انتقال یافته شما توسط پشتیبانی تایید شد، منتظر دریافت کانفینگ باشید👨‍💻")
        await callback_query.message.edit_text("✅ رسید تایید شد و پیام به کاربر ارسال گردید.")
    else:
        await client.send_message(target_user_id, "پشتیبانی پولی که شما زده اید را رد کرد لطفا مجددا تلاش بفرمایید❌")
        await callback_query.message.edit_text("❌ رسید رد شد و پیام به کاربر ارسال گردید.")

@app.on_message(filters.regex("⭐️امتیاز های من"))
async def my_points(client, message):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT points FROM users WHERE user_id = ?", (message.from_user.id,))
    res = cursor.fetchone()
    db.close()
    points = res['points'] if res else 0
    await message.reply(f"⭐️ امتیازهای فعلی شما: {points} امتیاز")

@app.on_message(filters.regex("⭐️خرید با امتیاز"))
async def buy_with_points(client, message):
    points_shop_text = (
        "لیست قیمت‌های خرید با امتیاز⭐️\n\n"
        "20امتیاز+1گیگ+2روز❗️\n"
        "30امتیاز+4گیگ+6روز❗️\n"
        "50امتیاز+8گیگ+20روز❗️\n"
        "60امتیاز+8گیگ+25روز❗️\n"
        "70امتیاز+9گیگ+25روز❗️\n"
        "80امتیاز+10گیگ+25روز❗️\n"
        "100امتیاز+13گیگ+30روز❗️\n\n"
        "برای خرید پکیج مورد نظر، سیستم موجودی شما را بررسی می‌کند."
    )
    await message.reply(points_shop_text)

@app.on_message(filters.regex("👥 زیرمجموعه‌گیری"))
async def referral_link(client, message):
    bot_info = await client.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={message.from_user.id}"
    text = (
        "👥 سیستم زیرمجموعه‌گیری:\n\n"
        "با دعوت هر دوست ۵ امتیاز هدیه بگیرید!\n\n"
        f"🔗 لینک اختصاصی شما:\n`{ref_link}`"
    )
    await message.reply(text, parse_mode="markdown")

@app.on_message(filters.regex("🛟 پشتیبانی"))
async def support_section(client, message):
    await message.reply("پیام موردنظر خود را ارسال کنید:")

@app.on_message(filters.text & filters.private & ~filters.regex("^/"))
async def user_text_handler(client, message):
    user_id = message.from_user.id
    text = message.text

    if user_id == ADMIN_ID:
        return

    menu_options = [
        "🛒 خرید کانفینگ", "📦 کانفینگ‌های خریداری‌شده", "🎁 وارد کردن کد هدیه", 
        "💳 شارژ حساب", "⭐️خرید با امتیاز", "⭐️امتیاز های من", 
        "👥 زیرمجموعه‌گیری", "🛟 پشتیبانی", "🛠 پنل مدیریت", "🔙 بازگشت به منوی اصلی"
    ]
    if text not in menu_options:
        await message.reply("پیام شما ارسال شد. پشتیبانی به زودی پاسخ می‌دهد.")
        await client.send_message(ADMIN_ID, f"💬 پیام جدید از کاربر `{user_id}`:\n\n{text}", parse_mode="markdown")

@app.on_message(filters.regex("🔙 بازگشت به منوی اصلی"))
async def back_to_main(client, message):
    await message.reply("به منوی اصلی برگشتید:", reply_markup=main_menu(message.from_user.id))

@app.on_message(filters.regex("🛠 پنل مدیریت"))
async def admin_panel(client, message):
    if not is_admin(message.from_user.id):
        return
    await message.reply("به پنل مدیریت خوش آمدید:", reply_markup=admin_menu())

if __name__ == "__main__":
    print("Bot is running...")
    app.run()
  
