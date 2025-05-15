import requests
import streamlit as st

HF_TOKEN = st.secrets["HF_TOKEN"]

def query_huggingface(event, model="HuggingFaceH4/zephyr-7b-beta"):
prompt = f"""
Внимание: тебе дано событие, и ты должен выдать только рекомендации по бизнес-действиям в логистике и маркетинге.

Формат:
📌 Прогноз: ...
✅ Действия:
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
- Увеличить запасы подарков и вина
- Расширить зону доставки
- Подготовить push для вечернего времени
- Настроить витрину “романтика”

👥 Роли:
- Логистика
- Склад
- Маркетинг

🧠 Почему:
Праздник + снег = пиковый спрос, нужно избежать задержек.

---

Событие: {event}

Ответ:
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
            return result[0]["generated_text"].split("---")[-1].strip()
        return "[⚠️ Ответ не содержит текста]"
    except Exception as e:
        return f"[❌ Ошибка LLM: {str(e)}]"
