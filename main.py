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
            reply = (
                "Привет. Я цифровой помощник консультанта по зависимостям. "
                "Помогаю решить проблемы, связанные с употреблением алкоголя, наркотиков. "
                "Здесь можно поговорить, задать вопрос или просто быть услышанным. "
                "При необходимости я свяжу с реальным, живым консультантом."
            )
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

    return '', 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

                          

