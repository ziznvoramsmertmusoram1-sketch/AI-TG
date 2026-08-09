import os
import requests
from flask import Flask, request

BOT_TOKEN = "8859582099:AAHBgl7hq8EaigxHJZzFrr4cS1AhFwJQPCc"
GROQ_API_KEY = "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"

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
GROQ_API = "https://api.groq.com/openai/v1/chat/completions"

app = Flask(__name__)

user_histories = {}


def ask_ai(user_id, text):
    history = user_histories.setdefault(user_id, [])
    history.append({"role": "user", "content": text})
    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        payload = {"model": "llama-3.3-70b-versatile", "messages": history}
        response = requests.post(GROQ_API, headers=headers, json=payload, timeout=30)
        data = response.json()
        if "choices" not in data:
            return f"Ошибка от AI: {data}"
        reply = data["choices"][0]["message"]["content"]
        history.append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        return f"Ошибка при обращении к AI: {e}"


def send_message(chat_id, text):
    requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=15)


def send_photo(chat_id, prompt):
    import urllib.parse
    encoded_prompt = urllib.parse.quote(prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
    try:
        requests.post(
            f"{TELEGRAM_API}/sendPhoto",
            json={"chat_id": chat_id, "photo": image_url, "caption": f"🎨 {prompt}"},
            timeout=30,
        )
    except Exception as e:
        send_message(chat_id, f"Не удалось создать картинку: {e}")


@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()
    message = update.get("message")

    if message and "text" in message:
        chat_id = message["chat"]["id"]
        text = message["text"]

        if text == "/start":
            send_message(chat_id, "Привет! Я AI-бот.\n\nПиши мне что угодно для чата.\nИли используй /image описание — сгенерирую картинку.")
        elif text.startswith("/image"):
            prompt = text.replace("/image", "", 1).strip()
            if not prompt:
                send_message(chat_id, "Напиши, что нарисовать. Пример: /image кот в космосе")
            else:
                send_photo(chat_id, prompt)
        else:
            reply = ask_ai(chat_id, text)
            send_message(chat_id, reply)

    return "OK", 200


@app.route("/")
def index():
    return "Бот работает!"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
