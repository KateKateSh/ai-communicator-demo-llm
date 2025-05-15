import requests
import streamlit as st

HF_TOKEN = st.secrets["HF_TOKEN"]
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

def query_huggingface(event, model="HuggingFaceH4/zephyr-7b-beta"):
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

Пример:

Событие: "14 февраля, День всех влюблённых, снег в Москве"

📌 Прогноз: ожидается рост спроса на цветы, подарки, доставку еды. Из-за снегопада возможны задержки курьеров в центре города.
✅ Действия:
- Увеличить запасы подарков и шоколада в центральных районах
- Добавить курьеров в ЦАО с 16:00 до 21:00
- Настроить push с предложением “вечерний подарок”
- Обновить витрину с “романтическими наборами” в Лавке
👥 Роли:
- Склад
- Логистика
- Маркетинг
🧠 Почему:
Праздник и снег дадут резкий пик спроса + замедление доставки. Необходимо подготовиться заранее, чтобы не потерять выручку.

[СТОП ПРИМЕР]

Событие: {event}
Ответ:
"""

    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 300,
            "temperature": 0.6,
            "top_p": 0.85
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        if isinstance(result, list) and "generated_text" in result[0]:
            final_output = clean_response(result[0]["generated_text"])
            send_to_all_subscribers(final_output)
            return final_output
        return "[⚠️ Ответ не содержит текста]"
    except Exception as e:
        return f"[❌ Ошибка LLM: {str(e)}]"

def clean_response(raw_text):
    if "[СТОП ПРИМЕР]" in raw_text:
        raw_text = raw_text.split("[СТОП ПРИМЕР]")[-1]
    if "[СТОП СТРУКТУРИРОВАННЫЙ ОТВЕТ]" in raw_text:
        raw_text = raw_text.split("[СТОП СТРУКТУРИРОВАННЫЙ ОТВЕТ]")[0]
    if "<<END>>" in raw_text:
        raw_text = raw_text.split("<<END>>")[0]
    start = raw_text.find("📌 Прогноз:")
    return raw_text[start:].strip() if start != -1 else raw_text.strip()
