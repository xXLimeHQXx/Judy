import streamlit as st
import google.generativeai as genai

# Заглавие на приложението
st.title("🐰 Чат с Джуди Хопс")

# Настройка на ключа - Провери дали името в кавичките съвпада с това в Secrets!
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # Пълното име на модела за по-сигурно
    model = genai.GenerativeModel('models/gemini-1.5-flash') 
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Напиши нещо на Джуди..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # Тук добавяме инструкции за личността на Джуди
            full_prompt = f"Ти си Джуди Хопс от Зоотрополис. Отговори на Ник: {prompt}"
            response = model.generate_content(full_prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

except Exception as e:
    st.error(f"Грешка при свързването: {e}")
