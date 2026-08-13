import os
import json
import threading
import logging
import time
from flask import Flask
import telebot
from telebot.types import Message

# === НАСТРОЙКИ ===
BOT_TOKEN = "8793997691:AAGNe0PQs674SYYnNLwdr9giqAeb-8wfC0o"
ADMIN_ID = 976653458

print(f"✅ Токен загружен: {BOT_TOKEN[:10]}...")
print(f"👤 Админ ID: {ADMIN_ID}")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

app = Flask(__name__)
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

# === ОБРАБОТЧИК ВСЕХ СООБЩЕНИЙ ===
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    print(f"📩 Получено сообщение. Тип: {message.content_type}")
    
    if hasattr(message, 'web_app_data') and message.web_app_data:
        print(f"📩 Web App Data: {message.web_app_data.data}")
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
                bot.send_message(ADMIN_ID, "🔔 Новый заказ! Проверьте сообщение выше.")
                print("✅ Заказ обработан и отправлен админу!")
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")

# === ЗАПУСК БОТА ===
def run_bot():
    try:
        print("🚀 Запускаю бота...")
        bot_info = bot.get_me()
        print(f"✅ Бот успешно подключен к Telegram! @{bot_info.username}")
        
        # Очистка старых сессий
        print("🔄 Очистка старых сессий...")
        bot.remove_webhook()
        time.sleep(2)
        print("✅ Вебхук удален")
        
        print("🤖 Бот STYLEVTB запущен!")
        print(f"📨 Заказы будут отправляться админу (ID: {ADMIN_ID})")
        print("🔄 Ожидание сообщений...")
        
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
