from flask import Flask, request
import requests
import os
import openai

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

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
            reply = "Привет! Я — цифровой помощник Владимира. Можешь задать мне любой вопрос о зависимости, выздоровлении, мотивации или АА. Я рядом."
        else:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "Ты консультант по зависимостям. Говори по-русски, дружелюбно, по делу, без осуждения. Общайся с пользователями как Владимир: честно, мягко, с юмором и поддержкой. Приветствуй новичков фразой 'Рад тебя видеть. Можешь задать мне любой вопрос.'"
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

    return '', 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))




