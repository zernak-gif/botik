import os
import json
import threading
import logging
from flask import Flask, request
import telebot
from telebot.types import Update

# === НАСТРОЙКИ ===
BOT_TOKEN = "8793997691:AAGNe0PQs674SYYnNLwdr9giqAeb-8wfC0o"  # ← ТВОЙ ТОКЕН
ADMIN_ID = 976653458

print(f"✅ Токен загружен: {BOT_TOKEN[:10]}...")

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

app = Flask(__name__)

# === СОЗДАЕМ БОТА ===
bot = telebot.TeleBot(BOT_TOKEN)

# === ОБРАБОТЧИКИ КОМАНД ===
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Привет! Это бот для заказа одежды STYLEVTB.\n\n"
        "👇 Нажми на кнопку меню (иконка внизу слева), чтобы открыть приложение и сделать заказ.\n\n"
        "📌 Связаться с админом: @vodkatrip"
    )

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "📖 Как сделать заказ:\n\n"
        "1. Нажми на кнопку меню\n"
        "2. Выбери категорию\n"
        "3. Заполни поля\n"
        "4. Нажми 'ОТПРАВИТЬ'"
    )

# === ОБРАБОТЧИК ДАННЫХ ИЗ ВЕБ-ПРИЛОЖЕНИЯ ===
@bot.message_handler(content_types=['web_app_data'])
def handle_webapp_data(message):
    try:
        data = json.loads(message.web_app_data.data)
        if data.get('action') == 'new_order':
            order_message = data.get('message', '')
            # Отправляем админу
            bot.send_message(ADMIN_ID, order_message, parse_mode='HTML')
            # Отвечаем пользователю
            bot.send_message(
                message.chat.id,
                "✅ Ваш заказ принят!\n"
                "Админ свяжется с вами в ближайшее время.\n\n"
                "📌 @vodkatrip"
            )
            # Дополнительное уведомление админу
            bot.send_message(ADMIN_ID, "🔔 Новый заказ! Проверьте сообщение выше.")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        bot.send_message(message.chat.id, "❌ Произошла ошибка при обработке заказа.")

# === ЗАПУСК БОТА ===
def run_bot():
    try:
        print("🚀 Запускаю бота...")
        # Проверка подключения
        bot.get_me()
        print("✅ Бот успешно подключен к Telegram!")
        print("🤖 Бот STYLEVTB запущен!")
        print(f"📨 Заказы будут отправляться админу (ID: {ADMIN_ID})")
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()

# === FLASK ===
@app.route('/')
def home():
    return "🤖 Бот STYLEVTB работает! Заказы принимаются."

@app.route('/health')
def health():
    return "OK", 200

# === ТОЧКА ВХОДА ===
print("🔄 Запуск бота в фоновом потоке...")
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()
print("✅ Поток бота запущен")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Flask сервер запущен на порту {port}")
    app.run(host='0.0.0.0', port=port)
