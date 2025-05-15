import streamlit as st
import requests

TG_TOKEN = st.secrets["TG_TOKEN"]
SUBSCRIBERS_FILE = "subscribers.txt"

def load_subscribers():
    try:
        with open(SUBSCRIBERS_FILE, "r") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()

def save_subscriber(chat_id: str):
    subscribers = load_subscribers()
    if chat_id not in subscribers:
        with open(SUBSCRIBERS_FILE, "a") as f:
            f.write(f"{chat_id}\n")

def send_to_all_subscribers(text):
    subscribers = load_subscribers()
    for chat_id in subscribers:
        try:
            url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            print(f"Ошибка при отправке в {chat_id}: {e}")
