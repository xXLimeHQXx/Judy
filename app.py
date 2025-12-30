import streamlit as st
import google.generativeai as genai
import json
import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# 1. Настройка на AI
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash-lite')

# 2. Настройка на Google Drive (Връзка)
# Трябва да поставиш твоите Client Secrets в Streamlit Secrets!
def get_drive():
    gauth = GoogleAuth()
    # Тук използваме автоматична оторизация за облака
    return GoogleDrive(gauth)

def save_to_drive(filename):
    drive = get_drive()
    file_list = drive.ListFile({'q': f"title='{filename}'"}).GetList()
    if file_list:
        file_drive = file_list[0] # Обновява съществуващ файл
    else:
        file_drive = drive.CreateFile({'title': filename}) # Създава нов
    file_drive.SetContentFile(filename)
    file_drive.Upload()

# --- Инициализация на паметта ---
if "messages" not in st.session_state:
    # Тук можеш да добавиш код, който първо тегли файла от Drive
    st.session_state.messages = []

st.title("🐰 Джуди: Обща памет (Cloud)")

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Пиши тук..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    response = model.generate_content(str(st.session_state.messages))
    st.session_state.messages.append({"role": "assistant", "content": response.text})
    st.chat_message("assistant").write(response.text)
    
    # АВТОМАТИЧНО ЗАПИСВАНЕ
    with open('memory.json', 'w', encoding='utf-8') as f:
        json.dump(st.session_state.messages, f, ensure_ascii=False, indent=4)
    
    # Качване в Drive
    try:
        save_to_drive('memory.json')
        st.toast("Споменът е записан в Drive! ☁️")
    except Exception as e:
        st.error(f"Грешка при запис в Drive: {e}")
