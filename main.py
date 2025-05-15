from flask import Flask, request
import requests
import os
from openai import OpenAI
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

@app.route('/')
def index():
    return "Бот работает!"

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            welcome = (
                "Привет. Я цифровой помощник консультанта по зависимостям.\n"
                "Помогаю решить проблемы, связанные с употреблением алкоголя, наркотиков.\n"
                "Здесь можно поговорить, задать вопрос или просто быть услышанным.\n"
                "При необходимости я свяжу с реальным, живым консультантом."
            )
            keyboard = [
                [InlineKeyboardButton("Мне тяжело, не знаю, с чего начать…", callback_data="start")],
                [InlineKeyboardButton("Как помочь близкому с зависимостью?", callback_data="help_family")],
                [InlineKeyboardButton("Хочу бросить, но не получается. Что делать?", callback_data="cant_quit")],
                [InlineKeyboardButton("Можно поговорить с кем-то живым?", callback_data="human")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": welcome, "reply_markup": reply_markup.to_dict()}
            )
        else:
            reply = rag_or_gpt_response(text)
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": reply}
            )

    elif "callback_query" in data:
        chat_id = data["callback_query"]["message"]["chat"]["id"]
        query = data["callback_query"]["data"]

        answers = {
            "start": "Я рядом. Даже если ты не знаешь, с чего начать — начни с честности. Напиши, что чувствуешь. Я тебя слышу.",
            "help_family": "Важно понять: спасти близкого невозможно, но можно помочь. Главное — перестать покрывать и начать говорить правду.",
            "cant_quit": "Если ты хочешь, но не получается — это уже не про силу воли. Это про зависимость. И с этим можно работать. Я подскажу, с чего начать.",
            "human": "Я могу связать тебя с живым консультантом. Напиши: 'Свяжи меня'. И мы найдём, кто сможет поговорить лично."
        }

        reply = answers.get(query, "Неизвестная команда")
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": reply}
        )

    return '', 200

def rag_or_gpt_response(user_message):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_message}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка при обращении к OpenAI: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))


          

