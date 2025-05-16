import requests
import streamlit as st

def query_llm(event, provider="together", model="meta-llama/Llama-3-8b-chat-hf"):
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

    headers = {
        "Content-Type": "application/json"
    }

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
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.6,
        "top_p": 0.85,
        "stream": False
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            return "⚠️ Ответ не содержит текста."
    except Exception as e:
        return f"❌ Ошибка LLM: {str(e)}"
