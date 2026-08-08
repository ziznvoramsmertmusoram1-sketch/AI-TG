import os
import requests
from flask import Flask, request

BOT_TOKEN = "8859582099:AAHBgl7hq8EaigxHJZzFrr4cS1AhFwJQPCc"
GEMINI_API_KEY = "AQ.Ab8RN6J7sQYsTfMJbyvhtNyK3G3joQgtoIrWTTIPjdcB8VV-mQ"

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
GEMINI_API = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"

app = Flask(__name__)

user_histories = {}


def ask_gemini(user_id, text):
    history = user_histories.setdefault(user_id, [])
    history.append({"role": "user", "parts": [{"text": text}]})
    try:
        response = requests.post(GEMINI_API, json={"contents": history}, timeout=30)
        data = response.json()
        if "candidates" not in data:
            return f"Ошибка от Gemini: {data}"
        reply = data["candidates"][0]["content"]["parts"][0]["text"]
        history.append({"role": "model", "parts": [{"text": reply}]})
        return reply
    except Exception as e:
        return f"Ошибка при обращении к Gemini: {e}"


def send_message(chat_id, text):
    requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=15)


@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()
    message = update.get("message")

    if message and "text" in message:
        chat_id = message["chat"]["id"]
        text = message["text"]

        if text == "/start":
            send_message(chat_id, "Привет! Я AI-бот на базе Gemini. Работаю круглосуточно на сервере.")
        else:
            reply = ask_gemini(chat_id, text)
            send_message(chat_id, reply)

    return "OK", 200


@app.route("/")
def index():
    return "Бот работает!"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
