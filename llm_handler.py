import requests
import streamlit as st

HF_TOKEN = st.secrets["HF_TOKEN"]

def query_huggingface(event, model="HuggingFaceH4/zephyr-7b-beta"):
    prompt = f"""
Ты — AI-коммуникатор спроса для логистики и e-commerce. Твоя задача — анализировать внешние события (погода, акции, праздники, концерты) и формировать краткие рекомендации, как сервису подготовиться к изменению спроса.

Формат ответа:
📌 Прогноз: ...
✅ Действия:
- ...
- ...
- ...
👥 Роли:
- ...
🧠 Почему:
...

Пример:

Событие: "14 февраля, День всех влюблённых, снег в Москве"

📌 Прогноз: ожидается рост спроса на цветы, подарки, доставку еды. Из-за снегопада возможны задержки курьеров.

✅ Действия:
- Увеличить запасы подарков и вина в центре Москвы
- Увеличить количество курьеров с 16:00 до 22:00
- Настроить push с предложением “вечерний подарок”
- Создать витрину “романтический набор”

👥 Роли:
- Логистика
- Склад
- Маркетинг

🧠 Почему:
Снег + праздник создают пиковый спрос и возможные сбои в доставке. Нужно подготовиться заранее.

---

Теперь обработай следующее событие:

Событие: {event}
"""

    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 300,
            "temperature": 0.7,
            "top_p": 0.9
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"]
        return "[⚠️ Ответ не содержит текста]"
    except Exception as e:
        return f"[❌ Ошибка LLM: {str(e)}]"
