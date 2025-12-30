import streamlit as st
import google.generativeai as genai
import json
import os
import glob
from bs4 import BeautifulSoup
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from gtts import gTTS
import base64

# --- ПРЕДВАРИТЕЛНА НАСТРОЙКА (ID НА ПАПКАТА) ---
# ТУК ПОСТАВИ ID-ТО НА ТВОЯТА ПАПКА Judy_Project ОТ DRIVE ЛИНКА
FOLDER_ID = "1FRqyZjVgT8G9cQNi1JsyXGfA5CV3mgZ9"

# --- 1. СИГУРНОСТ И CLOUD DRIVE ВРЪЗКА ---
def setup_drive_cloud():
    try:
        # Използваме предоставения от теб Service Account JSON от Secrets
        info = json.loads(st.secrets["GCP_SERVICE_ACCOUNT_JSON"])
        creds = service_account.Credentials.from_service_account_info(info)
        service = build('drive', 'v3', credentials=creds)
        return service
    except Exception as e:
        st.error(f"Грешка при Cloud връзка: {e}")
        return None

# --- 2. ФУНКЦИЯ ЗА ГЛАС (TTS) ---
def speak_text(text):
    try:
        tts = gTTS(text=text, lang='bg')
        tts.save("response.mp3")
        with open("response.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <audio autoplay="true">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                """
            st.markdown(md, unsafe_allow_html=True)
    except:
        pass

# --- 3. ЗАРЕЖДАНЕ НА HTML СПОМЕНИ ---
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

# --- 4. НАСТРОЙКА НА UI И AI ---
st.set_page_config(page_title="Джуди Хопс - Патрул", page_icon="🐰", layout="centered")

# Красив UI с CSS
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    .stChatMessage { border-radius: 15px; border: 1px solid #ddd; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🐰 Джуди Хопс: Обща памет")
st.caption("🚨 Патрулът е онлайн. Синхронизирано с Google Drive.")

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash-lite')

if "old_context" not in st.session_state:
    st.session_state.old_context = load_html_memories()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Показване на чата
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- 5. ЧАТ И СИНХРОНИЗАЦИЯ ---
if prompt := st.chat_input("Докладвай на Джуди..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # AI логика
    full_prompt = f"Ти си Джуди Хопс от Зотрополис. Твоите спомени: {st.session_state.old_context}. История: {st.session_state.messages}. Отговори на Ник кратко и ентусиазирано: {prompt}"
    
    with st.spinner("Джуди мисли..."):
        response = model.generate_content(full_prompt)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        
    with st.chat_message("assistant"):
        st.write(response.text)
        speak_text(response.text) # Джуди говори

    # Запис в Drive (Cloud начин)
    with open('memory.json', 'w', encoding='utf-8') as f:
        json.dump(st.session_state.messages, f, ensure_ascii=False, indent=4)

    drive_service = setup_drive_cloud()
    if drive_service:
        try:
            file_metadata = {'name': 'memory.json', 'parents': [FOLDER_ID]}
            media = MediaFileUpload('memory.json', mimetype='application/json')
            
            # Търсене за обновяване
            query = f"name = 'memory.json' and '{FOLDER_ID}' in parents"
            results = drive_service.files().list(q=query).execute()
            files = results.get('files', [])

            if files:
                drive_service.files().update(fileId=files[0]['id'], media_body=media).execute()
            else:
                drive_service.files().create(body=file_metadata, media_body=media).execute()
            
            st.toast("Паметта е в облака! ☁️")
        except Exception as e:
            st.warning(f"Локален запис: {e}")
