import requests
import streamlit as st

HF_TOKEN = st.secrets["HF_TOKEN"]

def query_huggingface(prompt, model="google/flan-t5-large"):
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.7,
            "top_p": 0.9
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        result = response.json()
        if isinstance(result, list):
            return result[0].get("generated_text", result[0].get("generated_text", "[⚠️ Ответ не распознан]"))
        elif isinstance(result, dict):
            return result.get("generated_text", "[⚠️ Нет текста в ответе]")
        else:
            return "[⚠️ Неподдерживаемый формат ответа от LLM]"
    except Exception as e:
        return f"[❌ Ошибка LLM: {str(e)}]"
