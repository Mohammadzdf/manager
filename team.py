import datetime
import logging
import asyncio
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

import uvicorn

TOKEN = "7652160937:AAFK7t-RKbl84Ip2JkAv7mfG_e3jl6AH9Gg"
REPORT_CHANNEL_ID = -1002834651178
IDEA_CHANNEL_ID = -1002899179280

user_state = {}
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)

@app.route("/")
def home():
    return "OK"

async def run_web_server_async():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info", loop="asyncio")
    server = uvicorn.Server(config)
    await server.serve()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📋 ارسال گزارش روزانه", callback_data='report')],
        [InlineKeyboardButton("💡 ارسال ایده / پیشنهاد", callback_data='idea')],
    ]
    await update.message.reply_text("چه کاری می‌خوای انجام بدی؟", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        chat_id = query.from_user.id
        if query.data == 'report':
            user_state[chat_id] = 'waiting_for_report'
            await query.message.reply_text("لطفاً گزارش روزانه خود را ارسال کنید:")
        elif query.data == 'idea':
            user_state[chat_id] = 'waiting_for_idea'
            await query.message.reply_text("لطفاً ایده یا پیشنهاد خود را بنویسید:")
    except Exception as e:
        logging.error(f"handle_buttons error: {e}", exc_info=True)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.message.from_user.id
        full_name = update.message.from_user.full_name
        username = f"@{update.message.from_user.username}" if update.message.from_user.username else "بدون یوزرنیم"
        text = update.message.text
        now = datetime.datetime.now().strftime("%Y/%m/%d - %H:%M")

        state = user_state.get(user_id)

        if state == 'waiting_for_report':
            log = f"""📝 <b>گزارش روزانه</b>

👤 <b>ارسال‌شده توسط:</b> {full_name} ({username})
📅 <b>تاریخ:</b> {now}
🗒️ <b>متن گزارش:</b>
{text}
"""
            await context.bot.send_message(chat_id=REPORT_CHANNEL_ID, text=log, parse_mode="HTML")
            await update.message.reply_text("✅ گزارش با موفقیت ارسال شد.")
            user_state.pop(user_id, None)  # پاک کردن وضعیت کاربر

        elif state == 'waiting_for_idea':
            log = f"""💡 <b>ایده / پیشنهاد جدید</b>

👤 <b>ارسال‌شده توسط:</b> {full_name} ({username})
📅 <b>تاریخ:</b> {now}
🧠 <b>متن ایده:</b>
{text}
"""
            await context.bot.send_message(chat_id=IDEA_CHANNEL_ID, text=log, parse_mode="HTML")
            await update.message.reply_text("✅ ایده‌ات ثبت شد. ممنون!")
            user_state.pop(user_id, None)  # پاک کردن وضعیت کاربر

        else:
            await update.message.reply_text("برای شروع /start رو بزن یا از دکمه‌ها استفاده کن.")
    except Exception as e:
        logging.error(f"handle_text error: {e}", exc_info=True)

async def run_bot():
    app_telegram = ApplicationBuilder().token(TOKEN).build()
    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(CallbackQueryHandler(handle_buttons))
    app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    await app_telegram.run_polling()

async def main():
    # اجرای همزمان وب‌سرور و ربات بدون مسدود کردن یکدیگر
    web_task = asyncio.create_task(run_web_server_async())
    bot_task = asyncio.create_task(run_bot())

    await asyncio.gather(web_task, bot_task)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Stopped by user")
        
