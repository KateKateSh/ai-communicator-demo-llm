import requests
import streamlit as st

HF_TOKEN = st.secrets["HF_TOKEN"]

def query_huggingface(prompt, model="mistralai/Mistral-7B-Instruct-v0.1"):
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
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        result = response.json()
        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"]
        else:
            return "[⚠️ Ответ не распознан от модели Hugging Face]"
    except Exception as e:
        return f"[❌ Ошибка LLM: {str(e)}]"
