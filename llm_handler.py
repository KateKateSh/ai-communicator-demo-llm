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
Ты — AI-коммуникатор спроса для логистики и e-commerce. На основе входного события сгенерируй только один структурированный ответ. Не пиши примеры. Не повторяй инструкции. Заверши после первого блока.

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

📌 Прогноз: ожидается рост спроса на цветы, подарки, доставку еды. Возможны задержки курьеров из-за погоды.
✅ Действия:
- Увеличить запасы подарков в центре Москвы
- Усилить логистику в ЦАО в пиковые часы
- Настроить push в 17:00 с акцией на романтический набор
- Актуализировать витрину в Лавке с подарками
👥 Роли:
- Склад
- Логистика
- Маркетинг
🧠 Почему:
Праздник + плохая погода создают нагрузку на доставку. Нужно заранее подготовить товарку и покрытие.

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
    if "<<END>>" in raw_text:
        raw_text = raw_text.split("<<END>>")[0]
    start = raw_text.find("📌 Прогноз:")
    return raw_text[start:].strip() if start != -1 else raw_text.strip()
