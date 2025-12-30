import streamlit as st
import google.generativeai as genai
import json
import os
import glob
from bs4 import BeautifulSoup
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# --- 1. СИГУРНОСТ И DRIVE ВРЪЗКА ---
def setup_drive():
    try:
        # Създаваме временен файл за библиотеката от твоите Secrets
        secrets_dict = json.loads(st.secrets["CLIENT_SECRETS_JSON"])
        with open("client_secrets.json", "w") as f:
            json.dump(secrets_dict, f)
        
        gauth = GoogleAuth()
        gauth.LoadClientConfigFile("client_secrets.json")
        
        # Опит за автоматично логване (ако имаш mycreds.txt)
        if os.path.exists("mycreds.txt"):
            gauth.LoadCredentialsFile("mycreds.txt")
        
        if gauth.credentials is None:
            # Това ще изпише инструкции в Manage App -> Logs
            print("Нужна е оторизация в Google Drive!")
        elif gauth.access_token_expired:
            gauth.Refresh()
        else:
            gauth.Authorize()
            
        return GoogleDrive(gauth)
    except Exception as e:
        st.error(f"Проблем с Drive връзката: {e}")
        return None

# --- 2. ЗАРЕЖДАНЕ НА СТАРИТЕ HTML СПОМЕНИ ---
def load_html_memories():
    combined_text = ""
    html_files = glob.glob("*.html")
    for file in html_files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                combined_text += soup.get_text() + "\n"
        except:
            continue
    return combined_text

# --- 3. НАСТРОЙКА НА AI (JUDY) ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash-lite')

st.set_page_config(page_title="Чат с Джуди", page_icon="🐰")
st.title("🐰 Джуди: Обща памет (Cloud + Drive)")

# Инициализиране на паметта
if "old_context" not in st.session_state:
    st.session_state.old_context = load_html_memories()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Показване на историята на екрана
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# --- 4. ЧАТ И ЗАПИСВАНЕ ---
if prompt := st.chat_input("Напиши нещо на Джуди..."):
    # Показваме съобщението на Ник
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Джуди мисли (използвайки стария HTML контекст и текущия чат)
    full_prompt = f"Ти си Джуди Хопс. Твоите стари спомени са: {st.session_state.old_context}. Сега разговаряш с Ник. История: {st.session_state.messages}. Отговори на: {prompt}"
    
    response = model.generate_content(full_prompt)
    st.session_state.messages.append({"role": "assistant", "content": response.text})
    st.chat_message("assistant").write(response.text)
    
    # Локално записване в JSON
    with open('memory.json', 'w', encoding='utf-8') as f:
        json.dump(st.session_state.messages, f, ensure_ascii=False, indent=4)
    
    # Опит за качване в Google Drive
    drive = setup_drive()
    if drive:
        try:
            file_list = drive.ListFile({'q': "title='memory.json'"}).GetList()
            file_drive = file_list[0] if file_list else drive.CreateFile({'title': 'memory.json'})
            file_drive.SetContentFile('memory.json')
            file_drive.Upload()
            st.toast("Паметта е синхронизирана с Drive! ☁️")
        except Exception as e:
            st.warning(f"Записано локално, но не и в Drive: {e}")
