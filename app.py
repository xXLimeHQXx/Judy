import streamlit as st
import google.generativeai as genai
import json
import os
import glob
from bs4 import BeautifulSoup # Трябва да я добавим в requirements.txt

# 1. Настройка на AI
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash-lite')

# 2. Функция за четене на ВСИЧКИ стари HTML спомени
def load_all_old_memories():
    combined_text = ""
    html_files = glob.glob("*.html") # Търси всички HTML файлове в папката
    for file in html_files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                combined_text += soup.get_text() + "\n"
        except:
            continue
    return combined_text

# 3. Зареждане на новата JSON памет
def load_json_memory():
    if os.path.exists('memory.json'):
        with open('memory.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Инициализация
if "old_memories" not in st.session_state:
    st.session_state.old_memories = load_all_old_memories()

if "messages" not in st.session_state:
    st.session_state.messages = load_json_memory()

st.title("🐰 Джуди: Връзка със спомените")

# Показване на чата
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Писане на съобщение
if prompt := st.chat_input("Ник, кажи ми нещо..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Джуди получава стария контекст + новия чат
    context = f"Ти си Джуди Хопс. Твоите стари спомени от HTML файловете са: {st.session_state.old_memories}. Твоят нов разговор е: {st.session_state.messages}. Отговори на: {prompt}"
    
    response = model.generate_content(context)
    st.session_state.messages.append({"role": "assistant", "content": response.text})
    st.chat_message("assistant").write(response.text)
    
    # ЗАПИС в JSON
    with open('memory.json', 'w', encoding='utf-8') as f:
        json.dump(st.session_state.messages, f, ensure_ascii=False, indent=4)
