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

# === ОБРАБОТЧИК КОМАНДЫ /start ===
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Привет! Это бот STYLEVTB.\n"
        "Нажми кнопку меню, чтобы сделать заказ."
    )

# === ОБРАБОТЧИК WEB_APP_DATA ===
@bot.message_handler(content_types=['web_app_data'])
def handle_webapp_data(message):
    try:
        print(f"📩 Получены данные: {message.web_app_data.data}")
        data = json.loads(message.web_app_data.data)
        
        if data.get('action') == 'new_order':
            order_text = data.get('message', '')
            
            # Отправляем админу
            bot.send_message(ADMIN_ID, order_text, parse_mode='HTML')
            
            # Подтверждение пользователю
            bot.send_message(
                message.chat.id,
                "✅ Заказ принят! Админ свяжется с вами."
            )
            
            # Дополнительное уведомление админу
            bot.send_message(ADMIN_ID, "🔔 Новый заказ!")
            
            print("✅ Заказ отправлен админу!")
        else:
            print(f"⚠️ Неизвестное действие: {data.get('action')}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при обработке заказа.")

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
    return "🤖 Бот STYLEVTB работает!"

@app.route('/health')
def health():
    return "OK", 200

# === ЗАПУСК ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
