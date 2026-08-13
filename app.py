import os
import json
import logging
import time
import threading
from flask import Flask
import telebot

BOT_TOKEN = "8793997691:AAGNe0PQs674SYYnNLwdr9giqAeb-8wfC0o"
ADMIN_ID = 976653458

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "👋 Бот работает!")

@bot.message_handler(content_types=['web_app_data'])
def handle_webapp_data(message):
    try:
        data = json.loads(message.web_app_data.data)
        if data.get('action') == 'new_order':
            bot.send_message(ADMIN_ID, data.get('message', ''), parse_mode='HTML')
            bot.send_message(message.chat.id, "✅ Заказ принят!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def run_bot():
    while True:
        try:
            bot.remove_webhook()
            print("🚀 Бот запущен через polling")
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print(f"❌ Ошибка: {e}. Перезапуск через 5 секунд...")
            time.sleep(5)

@app.route('/')
def home():
    return "🤖 Бот работает"

@app.route('/health')
def health():
    return "OK", 200

if __name__ == "__main__":
    # Запускаем бота в фоновом потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
