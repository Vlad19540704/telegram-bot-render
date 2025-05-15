from flask import Flask, request
import requests
import os
import openai
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("Что такое зависимость?", callback_data='about_addiction'),
        InlineKeyboardButton("Как остановиться?", callback_data='how_to_stop')
    ],
    [
        InlineKeyboardButton("Расскажи про АА", callback_data='about_aa'),
        InlineKeyboardButton("Связаться с консультантом", callback_data='contact')
    ]
])

@app.route('/')
def index():
    return "Бот работает!"

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    data = request.get_json()

    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"]["text"]

        if user_message == "/start":
            welcome_text = (
                "Привет. Я цифровой помощник консультанта по зависимостям.\n"
                "Помогаю решать проблемы, связанные с алкоголем и наркотиками.\n"
                "Можешь задать вопрос или просто поговорить. Я рядом."
            )

            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={
                "chat_id": chat_id,
                "text": welcome_text,
                "reply_markup": keyboard.to_dict()
            })
            return '', 200

        else:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Ты консультант по зависимостям. Говори по-русски, спокойно, уважительно, дружелюбно. "
                                "Общайся с пользователями как Владимир: честно, по существу, без осуждения и давления. "
                                "Помни, что твоя задача — быть рядом и поддержать. Не пиши ничего на английском, даже если не понял запрос."
                            )
                        },
                        {"role": "user", "content": user_message}
                    ]
                )
                reply = response.choices[0].message.content
            except Exception as e:
                reply = f"Ошибка при обращении к OpenAI: {str(e)}"

            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={
                "chat_id": chat_id,
                "text": reply
            })

    elif "callback_query" in data:
        callback = data["callback_query"]
        chat_id = callback["message"]["chat"]["id"]
        data_value = callback["data"]

        if data_value == "about_addiction":
            text = "Зависимость — это хроническое, прогрессирующее заболевание, влияющее на мозг, эмоции и поведение."
        elif data_value == "how_to_stop":
            text = "Первый шаг — признать проблему. Дальше стоит поговорить с консультантом или обратиться в сообщество."
        elif data_value == "about_aa":
            text = "АА — это сообщество людей, помогающее друг другу оставаться трезвыми. Собрания бесплатны и анонимны."
        elif data_value == "contact":
            text = "Если ты хочешь поговорить с живым консультантом — просто напиши. Я передам сообщение."
        else:
            text = "Не совсем понял, что ты имел в виду 🙂"

        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={
            "chat_id": chat_id,
            "text": text
        })

    return '', 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

          

