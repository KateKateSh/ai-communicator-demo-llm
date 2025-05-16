import requests
import streamlit as st

TG_TOKEN = st.secrets["TG_TOKEN"]
TOGETHER_API_KEY = st.secrets["together"]["api_key"]
SUBSCRIBERS_FILE = "subscribers.txt"

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

def query_together_ai(event, model="deepseek-ai/deepseek-llm-7b-chat"):
    prompt = f"""
Ты — AI-коммуникатор спроса для логистики и e-commerce. Твоя задача — анализировать событие и чётко предлагать действия.

⚠️ ВАЖНО: не выходи за формат. Не повторяй инструкции. Только деловой, краткий и структурированный ответ.

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

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    url = "https://api.together.xyz/inference"

    payload = {
        "model": model,
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.9,
        "repetition_penalty": 1.1,
        "prompt": prompt
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        generated_text = result.get("output", "").strip()
        if generated_text:
            final_output = clean_response(generated_text)
            send_to_all_subscribers(final_output)
            return final_output
        return "[⚠️ Ответ не получен]"
    except Exception as e:
        return f"[❌ Ошибка LLM: {str(e)}]"

def clean_response(raw_text):
    start = raw_text.find("📌 Прогноз:")
    return raw_text[start:].strip() if start != -1 else raw_text.strip()
