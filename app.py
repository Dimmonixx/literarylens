import streamlit as st
from openai import OpenAI
import json
import requests
import time
import random

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
UNSPLASH_KEY = st.secrets["UNSPLASH_ACCESS_KEY"]

st.set_page_config(
    page_title="LiteraryLens",
    page_icon="📚",
    layout="wide"
)

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #F0EBF8; }
    [data-testid="stSidebar"] { background-color: #E8E0F5; }
    .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

for key, val in {
    "used_images": set(),
    "characters": [],
    "analysis": "",
    "active_char": None,
    "messages": [],
    "book_title": "",
    "quick_book": "",
    "meta": {},
    "scenes": [],
    "meanings": [],
    "random_books": [],
    "daring_q": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

color_map = {
    "Главный герой":   {"bg": "#EEEDFE", "text": "#3C3489"},
    "Главная героиня": {"bg": "#FBEAF0", "text": "#72243E"},
    "Антагонист":      {"bg": "#FAECE7", "text": "#712B13"},
    "Второстепенный":  {"bg": "#E1F5EE", "text": "#085041"}
}

books_list = [
    "Мастер и Маргарита", "1984", "Гарри Поттер", "Алхимик",
    "Преступление и наказание", "Маленький принц", "Дюна",
    "Война и мир", "Идиот", "Оно"
]

if not st.session_state.random_books:
    st.session_state.random_books = random.sample(books_list, 5)


def build_query(char):
    return f"{char.get('age','')} {char.get('gender','')} {char.get('era','')} {char.get('emotion_en','')} portrait face cinematic lighting -group -crowd"


def get_character_image(char, max_attempts=3):
    url = "https://api.unsplash.com/search/photos"
    for _ in range(max_attempts):
        try:
            data = requests.get(url, params={"query": build_query(char), "client_id": UNSPLASH_KEY, "per_page": 10}, timeout=5).json()
            for img in data.get("results", []):
                if img["id"] not in st.session_state.used_images:
                    st.session_state.used_images.add(img["id"])
                    return img["urls"]["regular"]
        except Exception:
            pass
        time.sleep(1)
    return None


def show_image(url, colors, initials):
    if url:
        st.markdown(f'<div style="width:100%;height:280px;overflow:hidden;border-radius:12px;"><img src="{url}" style="width:100%;height:100%;object-fit:cover;object-position:top;"></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="background:{colors["bg"]};color:{colors["text"]};width:100%;height:280px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:48px;font-weight:500;">{initials}</div>', unsafe_allow_html=True)


# SIDEBAR
with st.sidebar:
    st.title("📚 LiteraryLens")
    st.caption("Понимай книги так, будто ты внутри истории")
    st.divider()
    book_title = st.text_input("Название книги:", value=st.session_state.quick_book, placeholder="Например: Мастер и Маргарита")
    analyze_btn = st.button("Анализировать", type="primary", use_container_width=True)
    if st.session_state.analysis:
        if st.button("🏠 На главную", use_container_width=True):
            for key in ["analysis", "characters", "scenes", "meanings", "meta", "active_char", "messages", "used_images", "book_title", "quick_book"]:
                st.session_state[key] = [] if isinstance(st.session_state[key], list) else {} if isinstance(st.session_state[key], dict) else set() if isinstance(st.session_state[key], set) else None if st.session_state[key] is None or isinstance(st.session_state[key], dict) else ""
            st.session_state.analysis = ""
            st.session_state.characters = []
            st.session_state.scenes = []
            st.session_state.meanings = []
            st.session_state.meta = {}
            st.session_state.active_char = None
            st.session_state.messages = []
            st.session_state.used_images = set()
            st.session_state.book_title = ""
            st.session_state.quick_book = ""
            st.rerun()
    sidebar_status = st.empty()
    sidebar_progress = st.empty()
    st.divider()
    st.markdown("**Попробуй:**")
    if st.button("🔄 Обновить список", use_container_width=True):
        st.session_state.random_books = random.sample(books_list, 5)
        st.rerun()
    for book in st.session_state.random_books:
        if st.button(f"📖 {book}", use_container_width=True, key=f"quick_{book}"):
            st.session_state.quick_book = book
            st.rerun()
    if st.session_state.analysis:
        st.divider()
        st.markdown("### 📖 Содержание")
        st.markdown("🎬 Ключевые сцены")
        st.markdown("🎭 Персонажи")
        st.markdown("💡 Смыслы и идеи")
        st.markdown("💬 Чат с персонажем")
        if st.session_state.active_char:
            st.divider()
            st.markdown(f"**Чат с:** {st.session_state.active_char['name']}")
            if st.button("🔄 Сменить персонажа"):
                st.session_state.active_char = None
                st.session_state.messages = []
                st.rerun()


# ГЛАВНЫЙ ЭКРАН
if not st.session_state.analysis:
    st.markdown("""
    <div style="text-align:center;padding:60px 20px 20px;">
        <div style="font-size:42px;font-weight:700;color:#2D1B6B;margin-bottom:12px">🎬 Понимай книги как живой фильм</div>
        <div style="font-size:18px;color:#6C63FF;margin-bottom:40px">Общайся с героями, смотри сцены и понимай глубокие смыслы — просто и интересно</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        ("🎬", "Ключевые сцены", "Книга как фильм"),
        ("🎭", "Живые персонажи", "С эмоциями и целями"),
        ("💬", "Чат с героем", "От первого лица"),
        ("🧠", "Смыслы и идеи", "Просто о сложном"),
    ]
    for col, (emoji, title, sub) in zip([c1, c2, c3, c4], cards):
        with col:
            st.markdown(f'<div style="background:white;border-radius:12px;padding:20px;text-align:center;border:1px solid #E0D5F5"><div style="font-size:32px">{emoji}</div><div style="font-weight:600;margin-top:8px">{title}</div><div style="color:#888;font-size:13px;margin-top:4px">{sub}</div></div>', unsafe_allow_html=True)

    st.write("")
    st.markdown("""
    <div style="background:white;border-radius:16px;padding:30px;text-align:center;margin-top:20px;border:1px solid #E0D5F5">
        <div style="font-size:13px;letter-spacing:2px;color:#9B8EC4;margin-bottom:12px">🎬 СЦЕНА</div>
        <div style="font-size:18px;line-height:1.8;color:#2D1B6B;">Тёмная комната. Тишина.<br>Кто-то делает выбор, который изменит всё.</div>
        <div style="margin-top:16px;color:#6C63FF;font-size:14px">👉 Хочешь понять, что происходит? Введи книгу слева.</div>
    </div>
    """, unsafe_allow_html=True)


# АНАЛИЗ
if analyze_btn:
    if not book_title:
        st.warning("Введи название книги!")
    else:
        st.session_state.book_title = book_title
        st.session_state.active_char = None
        st.session_state.messages = []
        st.session_state.used_images = set()
        st.session_state.quick_book = ""

        def upd(pct, text):
            sidebar_status.caption(text)
            sidebar_progress.progress(pct)

        upd(5, "📖 Читаю произведение...")
        meta_r = client.chat.completions.create(model="gpt-4o-mini", messages=[
            {"role": "system", "content": "Отвечай ТОЛЬКО валидным JSON без markdown."},
            {"role": "user", "content": f"Книга: {book_title}\n\nВерни JSON: {{\"title\": \"Полное название\", \"author\": \"Автор\", \"year\": \"Год\"}}"}
        ])
        st.session_state.meta = json.loads(meta_r.choices[0].message.content)

        upd(20, "🔍 Анализирую сюжет...")
        analysis_r = client.chat.completions.create(model="gpt-4o-mini", messages=[
            {"role": "system", "content": "Ты литературный эксперт. Отвечай просто и понятно, без академичности."},
            {"role": "user", "content": f"Книга: {book_title}\n\nДай краткий анализ: о чём эта книга, главные темы и идеи. Максимум 3 абзаца."}
        ])
        st.session_state.analysis = analysis_r.choices[0].message.content

        upd(38, "🎬 Разбираю ключевые сцены...")
        scenes_r = client.chat.completions.create(model="gpt-4o-mini", messages=[
            {"role": "system", "content": f"Ты эксперт по книге '{book_title}'. Отвечай ТОЛЬКО валидным JSON без markdown. Используй ТОЛЬКО реальных персонажей этой книги."},
            {"role": "user", "content": f"Верни JSON массив с 4 ключевыми сценами книги '{book_title}'.\nФормат: [{{\"title\": \"Название\", \"description\": \"Описание 2-3 предложения\", \"mood\": \"Настроение по-русски\", \"mood_emoji\": \"Эмодзи\", \"characters\": \"Только реальные персонажи книги\"}}]"}
        ])
        st.session_state.scenes = json.loads(scenes_r.choices[0].message.content)

        upd(55, "🎭 Анализирую персонажей...")
        char_r = client.chat.completions.create(model="gpt-4o-mini", messages=[
            {"role": "system", "content": "Ты литературный эксперт. Отвечай ТОЛЬКО валидным JSON без markdown."},
            {"role": "user", "content": f"Книга: {book_title}\n\nВерни JSON массив с главными персонажами (максимум 4) на русском языке.\nФормат: [{{\"name\": \"Имя\", \"gender\": \"male или female\", \"age\": \"young или middle-aged или old\", \"era\": \"эпоха на английском\", \"role\": \"Главный герой / Главная героиня / Антагонист / Второстепенный\", \"emotion\": \"Эмоция по-русски\", \"emotion_en\": \"emotion in English\", \"goal\": \"Цель по-русски\", \"conflict\": \"Конфликт по-русски\"}}]"}
        ])
        st.session_state.characters = json.loads(char_r.choices[0].message.content)

        upd(72, "🖼 Ищу портреты персонажей...")
        for char in st.session_state.characters:
            char["img_url"] = get_character_image(char)

        upd(88, "💡 Нахожу смыслы...")
        meanings_r = client.chat.completions.create(model="gpt-4o-mini", messages=[
            {"role": "system", "content": "Ты мудрый друг. Отвечай ТОЛЬКО валидным JSON без markdown."},
            {"role": "user", "content": f"Книга: {book_title}\n\nВерни JSON массив с 4 главными смыслами книги на русском.\nФормат: [{{\"emoji\": \"Эмодзи\", \"title\": \"Название идеи\", \"simple\": \"Объяснение простым языком 2-3 предложения\", \"question\": \"Личный вопрос читателю\"}}]"}
        ])
        st.session_state.meanings = json.loads(meanings_r.choices[0].message.content)

        upd(100, "✅ Готово!")
        time.sleep(1)
        sidebar_progress.empty()
        sidebar_status.empty()
        st.rerun()


# РЕЗУЛЬТАТ
if st.session_state.analysis:
    meta = st.session_state.meta
    st.markdown(f"""
    <div style="text-align:center;padding:40px 20px 20px;">
        <div style="color:#9B8EC4;font-size:14px;letter-spacing:3px;text-transform:uppercase;margin-bottom:8px">Произведение</div>
        <div style="color:#2D1B6B;font-size:42px;font-weight:700;margin-bottom:8px">{meta.get('title','')}</div>
        <div style="color:#6C63FF;font-size:20px;margin-bottom:4px">{meta.get('author','')}</div>
        <div style="color:#9B8EC4;font-size:16px">{meta.get('year','')}</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.markdown(st.session_state.analysis)
    st.divider()

    st.subheader("🎬 Ключевые сцены")
    mood_colors = {
        "тревога": {"bg": "#FFF3E0", "border": "#FF9800"},
        "страх": {"bg": "#FCE4EC", "border": "#E91E63"},
        "любовь": {"bg": "#FCE4EC", "border": "#E91E63"},
        "радость": {"bg": "#E8F5E9", "border": "#4CAF50"},
        "грусть": {"bg": "#E3F2FD", "border": "#2196F3"},
        "напряжение": {"bg": "#FFF8E1", "border": "#FFC107"},
        "мистика": {"bg": "#EDE7F6", "border": "#673AB7"},
        "надежда": {"bg": "#E8F5E9", "border": "#4CAF50"},
        "конфликт": {"bg": "#FFEBEE", "border": "#F44336"},
        "печаль": {"bg": "#E3F2FD", "border": "#2196F3"},
        "ностальгия": {"bg": "#FFF8E1", "border": "#FFC107"},
    }
    for i, scene in enumerate(st.session_state.scenes):
        c = mood_colors.get(scene.get("mood", "").lower(), {"bg": "#F5F5F5", "border": "#9E9E9E"})
        st.markdown(f'<div style="background:{c["bg"]};border-radius:12px;padding:20px;margin-bottom:16px;border-left:4px solid {c["border"]};"><div style="color:#888;font-size:12px;margin-bottom:4px">СЦЕНА {i+1}</div><div style="font-size:20px;font-weight:600;margin-bottom:8px">{scene.get("mood_emoji","")} {scene.get("title","")}</div><div style="color:#555;font-size:14px;margin-bottom:12px">{scene.get("description","")}</div><div style="color:#888;font-size:12px">👥 {scene.get("characters","")} &nbsp;&nbsp; 🎭 {scene.get("mood","")}</div></div>', unsafe_allow_html=True)
    st.divider()

    st.subheader("🎭 Персонажи")
    for char in st.session_state.characters:
        colors = color_map.get(char["role"], {"bg": "#F1EFE8", "text": "#444441"})
        initials = "".join([w[0] for w in char["name"].split()][:2]).upper()
        with st.container(border=True):
            col_img, col_info = st.columns([1, 2])
            with col_img:
                show_image(char.get("img_url"), colors, initials)
            with col_info:
                st.markdown(f"### {char['name']}")
                st.markdown(f"<span style='background:{colors['bg']};color:{colors['text']};padding:2px 10px;border-radius:8px;font-size:12px'>{char['role']}</span>", unsafe_allow_html=True)
                st.markdown(f"**Эмоция:** {char.get('emotion','')}")
                st.markdown(f"**Цель:** {char.get('goal','')}")
                st.markdown(f"**Конфликт:** {char.get('conflict','')}")
                if st.button(f"💬 Поговорить с {char['name']}", key=f"chat_{char['name']}"):
                    st.session_state.active_char = char
                    st.session_state.messages = []
                    st.rerun()
    st.divider()

    st.subheader("💡 Смыслы и идеи")
    for meaning in st.session_state.meanings:
        with st.container(border=True):
            st.markdown(f"### {meaning.get('emoji','')} {meaning.get('title','')}")
            st.markdown(meaning.get("simple", ""))
            st.info(f"🤔 {meaning.get('question','')}")
    st.divider()

    if st.session_state.active_char:
        char = st.session_state.active_char
        st.subheader(f"💬 Чат с {char['name']}")
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        col_chat, col_btn = st.columns([3, 1])
        with col_btn:
            if st.button("😏 Дерзкий вопрос", use_container_width=True):
                st.session_state.daring_q = random.choice([
                    "Ты жалеешь о своих поступках?",
                    "Ты счастлив на самом деле?",
                    "Ты врёшь себе?",
                    "Чего ты боишься больше всего?",
                    "Если бы можно было всё изменить — ты бы изменил?"
                ])
                st.rerun()

        user_input = st.chat_input(f"Напиши {char['name']}...")
        if st.session_state.daring_q:
            user_input = st.session_state.daring_q
            st.session_state.daring_q = ""

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            system_prompt = f"""Ты {char['name']} из книги "{st.session_state.book_title}".
Роль: {char['role']}. Эмоция: {char.get('emotion','')}. Цель: {char.get('goal','')}. Конфликт: {char.get('conflict','')}.
Отвечай от первого лица в характере персонажа на русском языке. Максимум 3-4 предложения.
Если пользователь уже спрашивал тебя — можешь сослаться на это."""
            chat_r = client.chat.completions.create(model="gpt-4o-mini", messages=[
                {"role": "system", "content": system_prompt},
                *st.session_state.messages
            ])
            st.session_state.messages.append({"role": "assistant", "content": chat_r.choices[0].message.content})
            st.rerun()
