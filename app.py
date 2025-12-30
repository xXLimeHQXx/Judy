import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Judy Chat", page_icon="🐰")
st.title("🐰 Чат с Джуди")

# Настройка на AI
genai.configure(st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# Прост чат интерфейс
if "messages" not in st.session_state:
    st.session_state.messages = []

# Показване на старите съобщения
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Поле за писане
if prompt := st.chat_input("Напиши нещо на Джуди..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Отговор от Джуди
    response = model.generate_content(f"Ти си Джуди Хопс. Отговори на Ник: {prompt}")
    st.session_state.messages.append({"role": "assistant", "content": response.text})
    st.chat_message("assistant").write(response.text)
