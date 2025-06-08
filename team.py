import datetime
import logging
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# توکن و آیدی‌ها
TOKEN = "7652160937:AAFK7t-RKbl84Ip2JkAv7mfG_e3jl6AH9Gg"
REPORT_CHANNEL_ID = -1002834651178
IDEA_CHANNEL_ID = -1002899179280

# ساختار لاگ
logging.basicConfig(level=logging.INFO)

# وضعیت کاربران
user_state = {}

# اپ Flask برای زنده نگه‌داشتن
app = Flask(__name__)
@app.route('/')
def home():
    return '✅ Bot is running.', 200

# فرمان /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📋 ارسال گزارش روزانه", callback_data='report')],
        [InlineKeyboardButton("💡 ارسال ایده / پیشنهاد", callback_data='idea')],
    ]
    await update.message.reply_text("چه کاری می‌خوای انجام بدی؟", reply_markup=InlineKeyboardMarkup(keyboard))

# هندل دکمه‌ها
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.from_user.id
    if query.data == 'report':
        user_state[chat_id] = 'waiting_for_report'
        await query.message.reply_text("لطفاً گزارش روزانه خود را ارسال کنید:")
    elif query.data == 'idea':
        user_state[chat_id] = 'waiting_for_idea'
        await query.message.reply_text("لطفاً ایده یا پیشنهاد خود را بنویسید:")

# هندل متن‌ها
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    full_name = update.message.from_user.full_name
    username = f"@{update.message.from_user.username}" if update.message.from_user.username else "بدون یوزرنیم"
    text = update.message.text
    now = datetime.datetime.now().strftime("%Y/%m/%d - %H:%M")

    state = user_state.get(user_id)
    if state == 'waiting_for_report':
        msg = f"""📝 <b>گزارش روزانه</b>

👤 <b>ارسال‌شده توسط:</b> {full_name} ({username})
📅 <b>تاریخ:</b> {now}
🗒️ <b>متن گزارش:</b>
{text}
"""
        await context.bot.send_message(chat_id=REPORT_CHANNEL_ID, text=msg, parse_mode="HTML")
        await update.message.reply_text("✅ گزارش با موفقیت ارسال شد.")
        user_state[user_id] = None

    elif state == 'waiting_for_idea':
        msg = f"""💡 <b>ایده / پیشنهاد جدید</b>

👤 <b>ارسال‌شده توسط:</b> {full_name} ({username})
📅 <b>تاریخ:</b> {now}
🧠 <b>متن ایده:</b>
{text}
"""
        await context.bot.send_message(chat_id=IDEA_CHANNEL_ID, text=msg, parse_mode="HTML")
        await update.message.reply_text("✅ ایده‌ات ثبت شد. ممنون!")
        user_state[user_id] = None
    else:
        await update.message.reply_text("برای شروع /start رو بزن یا از دکمه‌ها استفاده کن.")

# اجرای ربات
def run_bot():
    app_telegram = ApplicationBuilder().token(TOKEN).build()
    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(CallbackQueryHandler(handle_buttons))
    app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app_telegram.run_polling()

# اجرای برنامه
if __name__ == '__main__':
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=8000)
    
