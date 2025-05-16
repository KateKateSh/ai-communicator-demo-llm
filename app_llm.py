import streamlit as st
from llm_handler import query_llm

# Настройка страницы
st.set_page_config(page_title="AI-коммуникатор спроса", page_icon="🤖")
st.title("🤖 AI-коммуникатор спроса")
st.caption("LLM-помощник для событийного прогнозирования спроса в логистике и маркетинге")

# Ввод события от пользователя
user_input = st.text_input(
    "Введите событие для анализа",
    placeholder="Например: Концерт Imagine Dragons в Лужниках + жара"
)

# Выбор LLM-провайдера и модели
provider = st.selectbox("Провайдер LLM", ["together", "deepseek"])
default_model = "meta-llama/Llama-3-8b-chat-hf" if provider == "together" else "deepseek-ai/deepseek-coder-6.7b-instruct"
model = st.text_input("Название модели", value=default_model)

# Кнопка генерации
if st.button("Сгенерировать рекомендации") and user_input:
    with st.spinner("⏳ AI думает..."):
        output = query_llm(user_input, provider=provider, model=model)

    st.markdown("### 📌 Ответ от AI:")
    st.markdown(output)

# Подвал
st.markdown("---")
st.caption("v1.2 · Отправка ответа в Telegram · by Kate")
