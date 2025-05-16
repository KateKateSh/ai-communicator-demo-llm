import openai
import streamlit as st
import requests

# Конфигурация
TG_TOKEN = st.secrets["TG_TOKEN"]
TOGETHER_API_KEY = st.secrets["together"]["api_key"]
SUBSCRIBERS_FILE = "subscribers.txt"

# Установка API-параметров
openai.api_key = TOGETHER_API_KEY
openai.api_base = "https://api.together.xyz/v1"

def send_to_all_subscribers(text):
    try:
        with open(SUBSCRIBERS_FILE, "r") as f:
            chat_ids = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        chat_ids = []

    for chat_id in chat_ids:
        try:
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            print(f"Ошибка отправки в {chat_id}: {e}")

def query_together_ai(event, model="deepseek-chat"):
    prompt = f"""
Ты — AI-коммуникатор спроса для логистики и e-commerce. Твоя задача — анализировать событие и чётко предлагать действия.

⚠️ ВАЖНО: не выходи за формат. Не повторяй инструкции. Не пиши примеры. Только деловой, краткий и структурированный ответ.

📌 Формат:
📌 Прогноз: ...
✅ Действия:
- ...
- ...
👥 Роли:
- ...
🧠 Почему:
...

Событие: {event}
Ответ:
"""

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=512
        )
        result = response.choices[0].message.content.strip()
        send_to_all_subscribers(result)
        return result
    except Exception as e:
        return f"[❌ Ошибка LLM: {str(e)}]"
