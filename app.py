import os
import json
import threading
import logging
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# === НАСТРОЙКИ ===
BOT_TOKEN = os.environ.get("8793997691:AAGNe0PQs674SYYnNLwdr9giqAeb-8wfC0o")  # Берем из переменных окружения Render
ADMIN_ID = 976653458  # ТВОЙ ID (НЕ МЕНЯЙ)

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Flask приложение для Render
app = Flask(__name__)

# === ОБРАБОТЧИКИ КОМАНД БОТА ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    await update.message.reply_text(
        "👋 Привет! Это бот для заказа одежды STYLEVTB.\n\n"
        "👇 Нажми на кнопку меню (иконка внизу слева), чтобы открыть приложение и сделать заказ.\n\n"
        "📌 Связаться с админом: @vodkatrip"
    )

async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка данных из веб-приложения"""
    try:
        # Получаем данные от пользователя
        data = json.loads(update.message.web_app_data.data)
        
        # Проверяем, что это заказ
        if data.get('action') == 'new_order':
            # Получаем сообщение для админа
            message_text = data.get('message', '')
            
            # Отправляем админу
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=message_text,
                parse_mode='HTML'
            )
            
            # Отвечаем пользователю, что заказ принят
            await update.message.reply_text(
                "✅ Ваш заказ принят!\n"
                "Админ свяжется с вами в ближайшее время.\n\n"
                "📌 @vodkatrip"
            )
            
            # Отправляем админу дополнительное уведомление
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text="🔔 Новый заказ! Проверьте сообщение выше."
            )
        else:
            await update.message.reply_text("ℹ️ Получены данные, но это не заказ.")
            
    except Exception as e:
        print(f"Ошибка: {e}")
        await update.message.reply_text("❌ Произошла ошибка при обработке заказа. Попробуйте еще раз.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    await update.message.reply_text(
        "📖 Как сделать заказ:\n\n"
        "1. Нажми на кнопку меню (иконка внизу слева)\n"
        "2. Выбери категорию товара\n"
        "3. Заполни все поля (размер, цвет, бюджет, адрес)\n"
        "4. Нажми 'ОТПРАВИТЬ'\n\n"
        "💬 Связь с админом: @vodkatrip"
    )

# === ЗАПУСК БОТА В ОТДЕЛЬНОМ ПОТОКЕ ===
def run_bot():
    """Запускает Telegram бота в фоновом потоке"""
    try:
        # Создаем приложение бота
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(
            filters.StatusUpdate.WEB_APP_DATA, 
            handle_webapp_data
        ))
        
        print("🤖 Бот STYLEVTB запущен!")
        print(f"📨 Заказы будут отправляться админу (ID: {ADMIN_ID})")
        print("Нажми Ctrl+C для остановки")
        
        # Запускаем polling
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")

# === FLASK ДЛЯ RENDER ===
@app.route('/')
def home():
    """Главная страница для проверки работы"""
    return "🤖 Бот STYLEVTB работает! Заказы принимаются."

@app.route('/health')
def health():
    """Endpoint для проверки здоровья (UptimeRobot)"""
    return "OK", 200

# === ТОЧКА ВХОДА ===
if __name__ == '__main__':
    # Запускаем бота в фоновом потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Запускаем Flask сервер для Render
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Flask сервер запущен на порту {port}")
    app.run(host='0.0.0.0', port=port)
