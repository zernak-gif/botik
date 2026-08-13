import os
import json
import threading
import logging
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# === НАСТРОЙКИ ===
BOT_TOKEN ="8793997691:AAGNe0PQs674SYYnNLwdr9giqAeb-8wfC0"
BOT_TOKEN = os.environ.get("8793997691:AAGNe0PQs674SYYnNLwdr9giqAeb-8wfC0")
ADMIN_ID = 976653458

# === ПРОВЕРКА ТОКЕНА ===
if not BOT_TOKEN:
    print("❌ ОШИБКА: TELEGRAM_TOKEN не найден в переменных окружения!")
else:
    print(f"✅ Токен загружен: {BOT_TOKEN[:10]}...")

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

app = Flask(__name__)

# === ОБРАБОТЧИКИ БОТА ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Это бот для заказа одежды STYLEVTB.\n\n"
        "👇 Нажми на кнопку меню (иконка внизу слева), чтобы открыть приложение и сделать заказ.\n\n"
        "📌 Связаться с админом: @vodkatrip"
    )

async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = json.loads(update.message.web_app_data.data)
        if data.get('action') == 'new_order':
            message_text = data.get('message', '')
            await context.bot.send_message(chat_id=ADMIN_ID, text=message_text, parse_mode='HTML')
            await update.message.reply_text(
                "✅ Ваш заказ принят!\n"
                "Админ свяжется с вами в ближайшее время.\n\n"
                "📌 @vodkatrip"
            )
    except Exception as e:
        print(f"❌ Ошибка: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Как сделать заказ:\n\n"
        "1. Нажми на кнопку меню\n"
        "2. Выбери категорию\n"
        "3. Заполни поля\n"
        "4. Нажми 'ОТПРАВИТЬ'"
    )

# === ЗАПУСК БОТА ===
def run_bot():
    if not BOT_TOKEN:
        print("❌ Бот не запущен: нет токена")
        return
    
    try:
        print("🚀 Запускаю бота...")
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(
            filters.StatusUpdate.WEB_APP_DATA,
            handle_webapp_data
        ))
        
        print("🤖 Бот STYLEVTB успешно запущен!")
        print(f"📨 Заказы будут отправляться админу (ID: {ADMIN_ID})")
        
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()

# === FLASK ===
@app.route('/')
def home():
    return "🤖 Бот STYLEVTB работает! Заказы принимаются."

@app.route('/health')
def health():
    return "OK", 200

# === ГЛАВНАЯ ТОЧКА ВХОДА ===
# Запускаем бота в фоновом потоке ПРИ ЗАГРУЗКЕ МОДУЛЯ
print("🔄 Запуск бота в фоновом потоке...")
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()
print("✅ Поток бота запущен")

# Точка входа для Gunicorn
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Flask сервер запущен на порту {port}")
    app.run(host='0.0.0.0', port=port)
