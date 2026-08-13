import os
import json
import logging
from flask import Flask, request, jsonify
import telebot

# === НАСТРОЙКИ ===
BOT_TOKEN = "8793997691:AAGNe0PQs674SYYnNLwdr9giqAeb-8wfC0o"
ADMIN_ID = 976653458

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
bot = telebot.TeleBot(BOT_TOKEN)

# Устанавливаем вебхук (будет вызвано при старте)
WEBHOOK_URL = "https://botik-jt40.onrender.com/webhook"

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

# === ВЕБХУК ===
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return jsonify({'status': 'ok'}), 200
    return jsonify({'status': 'error'}), 403

@app.route('/')
def home():
    return "🤖 Бот STYLEVTB работает через вебхук!"

@app.route('/health')
def health():
    return "OK", 200

# === ЗАПУСК ===
if __name__ == "__main__":
    # Удаляем старый вебхук и устанавливаем новый
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    print(f"✅ Вебхук установлен: {WEBHOOK_URL}")
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
