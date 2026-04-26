import streamlit as st
from openai import OpenAI
import json
import requests
import time

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
UNSPLASH_KEY = st.secrets["UNSPLASH_ACCESS_KEY"]

st.set_page_config(
    page_title="LiteraryLens",
    page_icon="📚",
    layout="centered"
)

st.title("📚 LiteraryLens")
st.subheader("Понимай книги через живой опыт")
st.divider()

color_map = {
    "Главный герой":   {"bg": "#EEEDFE", "text": "#3C3489"},
    "Главная героиня": {"bg": "#FBEAF0", "text": "#72243E"},
    "Антагонист":      {"bg": "#FAECE7", "text": "#712B13"},
    "Второстепенный":  {"bg": "#E1F5EE", "text": "#085041"}
}

if "used_images" not in st.session_state:
    st.session_state.used_images = set()

if "characters" not in st.session_state:
    st.session_state.characters = []

if "analysis" not in st.session_state:
    st.session_state.analysis = ""

if "active_char" not in st.session_state:
    st.session_state.active_char = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "book_title" not in st.session_state:
    st.session_state.book_title = ""

def build_query(char):
    gender = char.get("gender", "")
    emotion = char.get("emotion_en", "")
    role = char.get("role", "")
    return f"{gender} {emotion} {role} portrait face cinematic lighting -group -crowd"

def get_character_image(char, max_attempts=3):
    query = build_query(char)
    url = "https://api.unsplash.com/search/photos"
    for _ in range(max_attempts):
        try:
            response = requests.get(url, params={
                "query": query,
                "client_id": UNSPLASH_KEY,
                "per_page": 10
            }, timeout=5)
            data = response.json()
            for img in data.get("results", []):
                if img["id"] not in st.session_state.used_images:
                    st.session_state.used_images.add(img["id"])
                    return img["urls"]["regular"]
        except:
            pass
        time.sleep(1)
    return None

def show_image(url, colors, initials):
    if url:
        st.markdown(f"""
        <div style="width:100%;height:280px;overflow:hidden;border-radius:12px;">
            <img src="{url}" style="width:100%;height:100%;object-fit:cover;object-position:top;">
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background:{colors['bg']};color:{colors['text']};
        width:100%;height:280px;border-radius:12px;
        display:flex;align-items:center;justify-content:center;
        font-size:48px;font-weight:500;">{initials}</div>
        """, unsafe_allow_html=True)

book_title = st.text_input("Название книги:", placeholder="Например: Мастер и Маргарита")

if st.button("Анализировать", type="primary", use_container_width=True):
    if not book_title:
        st.warning("Введи название книги!")
    else:
        st.session_state.book_title = book_title
        st.session_state.active_char = None
        st.session_state.messages = []
        st.session_state.used_images = set()

        with st.spinner("анализирую книгу..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Ты литературный эксперт. Отвечай просто и понятно, без академичности."},
                    {"role": "user", "content": f"Книга: {book_title}\n\nДай краткий анализ: о чём эта книга, главные темы и идеи. Максимум 3 абзаца."}
                ]
            )
            st.session_state.analysis = response.choices[0].message.content

        with st.spinner("анализирую персонажей..."):
            char_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Ты литературный эксперт. Отвечай ТОЛЬКО валидным JSON без markdown и без пояснений."},
                    {"role": "user", "content": f"""Книга: {book_title}

Верни JSON массив с главными персонажами (максимум 4).
Отвечай ТОЛЬКО на русском языке.
Формат каждого персонажа:
{{
  "name": "Имя персонажа на русском",
  "gender": "male или female",
  "role": "Главный герой / Главная героиня / Антагонист / Второстепенный",
  "emotion": "Основная эмоция на русском",
  "emotion_en": "Same emotion in English",
  "goal": "Главная цель на русском в одном предложении",
  "conflict": "Главный конфликт на русском в одном предложении"
}}"""}
                ]
            )
            st.session_state.characters = json.loads(char_response.choices[0].message.content)

        for char in st.session_state.characters:
            char["img_url"] = get_character_image(char)

if st.session_state.analysis:
    st.success("Готово!")
    st.markdown(st.session_state.analysis)
    st.divider()
    st.subheader("🎬 Ключевые сцены")

    with st.spinner("Анализирую сцены..."):
        scenes_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты литературный эксперт. Отвечай ТОЛЬКО валидным JSON без markdown и без пояснений."},
                {"role": "user", "content": f"""Книга: {book_title}

Верни JSON массив с 4 ключевыми сценами книги.
Отвечай ТОЛЬКО на русском языке.
Формат каждой сцены:
{{
  "title": "Название сцены",
  "description": "Описание сцены в 2-3 предложениях",
  "mood": "Настроение сцены одним словом",
  "mood_emoji": "Один эмодзи отражающий настроение",
  "characters": "Персонажи через запятую"
}}"""}
            ]
        )
        scenes = json.loads(scenes_response.choices[0].message.content)

    mood_colors = {
        "тревога": "#2D1B1B",
        "страх": "#1A1A2E",
        "любовь": "#2D1B2D",
        "радость": "#1B2D1B",
        "грусть": "#1B1B2D",
        "напряжение": "#2D2D1B",
        "мистика": "#1B2D2D",
        "надежда": "#1B2B1B"
    }

    for i, scene in enumerate(scenes):
        bg_color = mood_colors.get(scene['mood'].lower(), "#1E1E2E")
        st.markdown(f"""
        <div style="
            background:{bg_color};
            border-radius:12px;
            padding:20px;
            margin-bottom:16px;
            border-left:4px solid #6C63FF;">
            <div style="color:#888;font-size:12px;margin-bottom:4px">СЦЕНА {i+1}</div>
            <div style="color:white;font-size:20px;font-weight:600;margin-bottom:8px">
                {scene['mood_emoji']} {scene['title']}
            </div>
            <div style="color:#CCC;font-size:14px;margin-bottom:12px">
                {scene['description']}
            </div>
            <div style="color:#888;font-size:12px">
                👥 {scene['characters']} &nbsp;&nbsp; 🎭 {scene['mood']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.subheader("🎭 Персонажи")

    for char in st.session_state.characters:
        colors = color_map.get(char['role'], {"bg": "#F1EFE8", "text": "#444441"})
        initials = "".join([w[0] for w in char['name'].split()][:2]).upper()

        with st.container(border=True):
            col_img, col_info = st.columns([1, 2])
            with col_img:
                show_image(char.get("img_url"), colors, initials)
            with col_info:
                st.markdown(f"### {char['name']}")
                st.markdown(f"<span style='background:{colors['bg']};color:{colors['text']};padding:2px 10px;border-radius:8px;font-size:12px'>{char['role']}</span>", unsafe_allow_html=True)
                st.markdown(f"**Эмоция:** {char.get('emotion', '')}")
                st.markdown(f"**Цель:** {char['goal']}")
                st.markdown(f"**Конфликт:** {char['conflict']}")
                if st.button(f"💬 Поговорить с {char['name']}", key=f"chat_{char['name']}"):
                    st.session_state.active_char = char
                    st.session_state.messages = []
                    st.rerun()

if st.session_state.active_char:
    char = st.session_state.active_char
    colors = color_map.get(char['role'], {"bg": "#F1EFE8", "text": "#444441"})

    st.divider()
    st.subheader(f"💬 Чат с {char['name']}")

    if st.button("🔄 Выбрать другого персонажа"):
        st.session_state.active_char = None
        st.session_state.messages = []
        st.rerun()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input(f"Напиши {char['name']}...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        system_prompt = f"""Ты {char['name']} из книги "{st.session_state.book_title}".
Твоя роль: {char['role']}.
Твоя эмоция: {char['emotion']}.
Твоя цель: {char['goal']}.
Твой конфликт: {char['conflict']}.

Отвечай от первого лица, в характере персонажа.
Говори как этот персонаж — его словами, его эмоциями.
Отвечай на русском языке. Максимум 3-4 предложения."""

        with st.spinner(f"{char['name']} думает..."):
            chat_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *st.session_state.messages
                ]
            )
            reply = chat_response.choices[0].message.content

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()
