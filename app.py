import streamlit as st
import google.generativeai as genai
import json
import os

# 1. Настройка на AI
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash-lite')

# 2. Функция за зареждане на паметта (JSON)
def load_memory():
    if os.path.exists('memory.json'):
        with open('memory.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# 3. Функция за записване
def save_memory(messages):
    with open('memory.json', 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_status=False, indent=4)

# Инициализация на чата
if "messages" not in st.session_state:
    st.session_state.messages = load_memory()

# Показване на историята
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Писане на ново съобщение
if prompt := st.chat_input("Кажи нещо на Джуди..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Джуди отговаря, като знае историята (Memory)
    full_history = str(st.session_state.messages)
    response = model.generate_content(f"Ти си Джуди Хопс. Това е историята ни досега: {full_history}. Отговори на: {prompt}")
    
    st.session_state.messages.append({"role": "assistant", "content": response.text})
    st.chat_message("assistant").write(response.text)
    
    # ЗАПИСВАНЕ
    save_memory(st.session_state.messages)
