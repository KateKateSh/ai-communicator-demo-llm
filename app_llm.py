import streamlit as st
import json
from pathlib import Path
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

# Путь к prompt-шаблону
PROMPT_PATH = Path("prompts/event_template.txt")

@st.cache_resource
def load_model():
    tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
    model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")
    return pipeline("text2text-generation", model=model, tokenizer=tokenizer)

llm_pipeline = load_model()

def ai_response_with_llm(event_text: str) -> str:
    prompt_template = PROMPT_PATH.read_text(encoding="utf-8")
    input_text = f"{prompt_template}\n\nСобытие: {event_text}"
    result = llm_pipeline(input_text, max_new_tokens=256)[0]["generated_text"]
    return result

# Streamlit UI
st.set_page_config(page_title="AI-коммуникатор спроса", layout="centered")
st.title("🤖 AI-коммуникатор спроса")

event_text = st.text_area("Введите событие", placeholder="Пример: 14 февраля в Москве снег + акция на цветы")

if st.button("Проанализировать"):
    if not event_text.strip():
        st.warning("Пожалуйста, введите описание события.")
    else:
        st.markdown("⏳ Анализируем...")
        result = ai_response_with_llm(event_text)
        st.markdown(result)
