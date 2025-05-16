import requests
import streamlit as st

TG_TOKEN = st.secrets["TG_TOKEN"]
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

def query_llm(event, provider="together", model="meta-llama/Llama-3-8b-chat-hf"):
    system_prompt = (
        "Ты — AI-коммуникатор спроса для логистики и e-commerce. "
        "Твоя задача — анализировать событие и чётко предлагать действия. "
        "Формат ответа: 📌 Прогноз, ✅ Действия, 👥 Роли, 🧠 Почему. "
        "Отвечай строго по структуре. Не добавляй вводных слов."
    )

    user_prompt = f"Событие: {event}\nОтвет:"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    headers = {"Content-Type": "application/json"}

    if provider == "together":
        api_key = st.secrets["together"]["api_key"]
        headers["Authorization"] = f"Bearer {api_key}"
        url = "https://api.together.xyz/v1/chat/completions"
    elif provider == "deepseek":
        api_key = st.secrets["deepseek"]["api_key"]
        headers["Authorization"] = f"Bearer {api_key}"
        url = "https://api.deepseek.com/v1/chat/completions"
    else:
        return "❌ Неверный провайдер LLM."

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.6,
        "top_p": 0.85,
        "stream": False
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            final_output = result["choices"][0]["message"]["content"]
            send_to_all_subscribers(final_output)
            return final_output
        return "⚠️ Ответ не содержит текста."
    except Exception as e:
        return f"❌ Ошибка LLM: {str(e)}"
