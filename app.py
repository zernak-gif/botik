import os
import json
import logging
import time
from flask import Flask
import telebot

# === НАСТРОЙКИ ===
BOT_TOKEN = "8793997691:AAGNe0PQs674SYYnNLwdr9giqAeb-8wfC0o"
ADMIN_ID = 976653458

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
bot = telebot.TeleBot(BOT_TOKEN)

# === ОБРАБОТЧИКИ ===
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Привет! Это бот STYLEVTB.\n"
        "Нажми кнопку меню, чтобы сделать заказ."
    )

@bot.message_handler(content_types=['web_app_data'])
def handle_webapp_data(message):
    try:
        data = json.loads(message.web_app_data.data)
        if data.get('action') == 'new_order':
            order_message = data.get('message', '')
            bot.send_message(ADMIN_ID, order_message, parse_mode='HTML')
            bot.send_message(
                message.chat.id,
                "✅ Заказ принят! Админ свяжется с вами."
            )
            bot.send_message(ADMIN_ID, "🔔 Новый заказ!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

# === FLASK ===
@app.route('/')
def home():
    return "🤖 Бот STYLEVTB работает!"

@app.route('/health')
def health():
    return "OK", 200

# === ЗАПУСК ===
if __name__ == "__main__":
    # Принудительно удаляем вебхук и останавливаем старые сессии
    print("🔄 Очистка старых сессий...")
    try:
        bot.remove_webhook()
        print("✅ Вебхук удален")
    except Exception as e:
        print(f"⚠️ Ошибка удаления вебхука: {e}")
    
    time.sleep(2)
    
    print("🚀 Запускаю бота через polling...")
    
    # Запускаем бота в отдельном потоке (чтобы Flask тоже работал)
    import threading
    def run_bot():
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print(f"❌ Ошибка бота: {e}")
    
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    print("✅ Бот запущен в фоновом потоке")
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
