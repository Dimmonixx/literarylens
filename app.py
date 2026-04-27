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
    layout="wide"
)

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #F0EBF8; }
    [data-testid="stSidebar"] { background-color: #E8E0F5; }
    .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

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
if "meta" not in st.session_state:
    st.session_state.meta = {}
if "scenes" not in st.session_state:
    st.session_state.scenes = []
if "meanings" not in st.session_state:
    st.session_state.meanings = []
if "quick_book" not in st.session_state:
    st.session_state.quick_book = ""

color_map = {
    "Главный герой":   {"bg": "#EEEDFE", "text": "#3C3489"},
    "Главная героиня": {"bg": "#FBEAF0", "text": "#72243E"},
    "Антагонист":      {"bg": "#FAECE7", "text": "#712B13"},
    "Второстепенный":  {"bg": "#E1F5EE", "text": "#085041"}
}

def build_query(char):
    gender = char.get("gender", "")
    emotion = char.get("emotion_en", "")
    age = char.get("age", "")
    era = char.get("era", "")
    return f"{age} {gender} {era} {emotion} portrait face cinematic lighting -group -crowd"

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

# SIDEBAR
with st.sidebar:
    st.title("📚 LiteraryLens")
    st.caption("Понимай книги так, будто ты внутри истории")
    st.divider()
    st.markdown("🎬 Смотри сцены")
    st.markdown("🎭 Общайся с героями")
    st.markdown("🧠 Понимай глубинные смыслы")
    st.divider()
    st.markdown("**Попробуй:**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Мастер и Маргарита", use_container_width=True):
            st.session_state.quick_book = "Мастер и Маргарита"
            st.rerun()
        if st.button("1984", use_container_width=True):
            st.session_state.quick_book = "1984"
            st.rerun()
    with col2:
        if st.button("Гарри Поттер", use_container_width=True):
            st.session_state.quick_book = "Гарри Поттер"
            st.rerun()
        if st.button("Алхимик", use_container_width=True):
            st.session_state.quick_book = "Алхимик"
            st.rerun()
    st.divider()
    book_title = st.text_input("Или введи свою книгу:", value=st.session_state.quick_book, placeholder="Например: Преступление и наказание")
    analyze_btn = st.button("Анализировать", type="primary", use_container_width=True)

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

# ГЛАВНЫЙ ЭКРАН (если книга ещё не введена)
if not st.session_state.analysis:
    st.markdown("""
    <div style="text-align:center;padding:60px 20px 20px;">
        <div style="font-size:42px;font-weight:700;color:#2D1B6B;margin-bottom:12px">
            🎬 Понимай книги как живой фильм
        </div>
        <div style="font-size:18px;color:#6C63FF;margin-bottom:40px">
            Общайся с героями, смотри сцены и понимай глубокие смыслы — просто и интересно
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""
        <div style="background:white;border-radius:12px;padding:20px;text-align:center;border:1px solid #E0D5F5">
            <div style="font-size:32px">🎬</div>
            <div style="font-weight:600;margin-top:8px">Ключевые сцены</div>
            <div style="color:#888;font-size:13px;margin-top:4px">Книга как фильм</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div style="background:white;border-radius:12px;padding:20px;text-align:center;border:1px solid #E0D5F5">
            <div style="font-size:32px">🎭</div>
            <div style="font-weight:600;margin-top:8px">Живые персонажи</div>
            <div style="color:#888;font-size:13px;margin-top:4px">С эмоциями и целями</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div style="background:white;border-radius:12px;padding:20px;text-align:center;border:1px solid #E0D5F5">
            <div style="font-size:32px">💬</div>
            <div style="font-weight:600;margin-top:8px">Чат с героем</div>
            <div style="color:#888;font-size:13px;margin-top:4px">От первого лица</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown("""
        <div style="background:white;border-radius:12px;padding:20px;text-align:center;border:1px solid #E0D5F5">
            <div style="font-size:32px">🧠</div>
            <div style="font-weight:600;margin-top:8px">Смыслы и идеи</div>
            <div style="color:#888;font-size:13px;margin-top:4px">Просто о сложном</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.write("")
    st.markdown("""
    <div style="background:#2D1B6B;border-radius:16px;padding:30px;text-align:center;color:white;margin-top:20px">
        <div style="font-size:13px;letter-spacing:2px;opacity:0.6;margin-bottom:12px">🎬 СЦЕНА</div>
        <div style="font-size:18px;line-height:1.8;opacity:0.9">
            Тёмная комната. Тишина.<br>
            Кто-то делает выбор, который изменит всё.
        </div>
        <div style="margin-top:16px;opacity:0.6;font-size:14px">
            👉 Хочешь понять, что происходит? Введи книгу слева.
        </div>
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

        meta_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Отвечай ТОЛЬКО валидным JSON без markdown."},
                {"role": "user", "content": f"Книга: {book_title}\n\nВерни JSON:\n{{\"title\": \"Полное название\", \"author\": \"Автор\", \"year\": \"Год издания\"}}"}
            ]
        )
        st.session_state.meta = json.loads(meta_response.choices[0].message.content)

        analysis_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты литературный эксперт. Отвечай просто и понятно, без академичности."},
                {"role": "user", "content": f"Книга: {book_title}\n\nДай краткий анализ: о чём эта книга, главные темы и идеи. Максимум 3 абзаца."}
            ]
        )
        st.session_state.analysis = analysis_response.choices[0].message.content

        scenes_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты литературный эксперт. Отвечай ТОЛЬКО валидным JSON без markdown."},
                {"role": "user", "content": "Книга: " + book_title + """

Верни JSON массив с 4 ключевыми сценами книги на русском языке.
Формат:
{
  "title": "Название сцены",
  "description": "Описание 2-3 предложения",
  "mood": "Настроение одним словом на русском",
  "mood_emoji": "Один эмодзи",
  "characters": "Персонажи через запятую"
}"""}
            ]
        )
        st.session_state.scenes = json.loads(scenes_response.choices[0].message.content)

        char_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты литературный эксперт. Отвечай ТОЛЬКО валидным JSON без markdown."},
                {"role": "user", "content": "Книга: " + book_title + """

Верни JSON массив с главными персонажами (максимум 4) на русском языке.
Формат:
{
  "name": "Имя на русском",
  "gender": "male или female",
  "age": "young или middle-aged или old",
  "era": "например: 1920s или medieval или modern",
  "role": "Главный герой / Главная героиня / Антагонист / Второстепенный",
  "emotion": "Эмоция на русском",
  "emotion_en": "emotion in English",
  "goal": "Цель на русском",
  "conflict": "Конфликт на русском"
}"""}
            ]
        )
        st.session_state.characters = json.loads(char_response.choices[0].message.content)
        for char in st.session_state.characters:
            char["img_url"] = get_character_image(char)

        meanings_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты мудрый друг. Отвечай ТОЛЬКО валидным JSON без markdown."},
                {"role": "user", "content": "Книга: " + book_title + """

Верни JSON массив с 4 главными смыслами книги на русском языке.
Формат:
{
  "title": "Название идеи",
  "simple": "Объяснение простым языком 2-3 предложения",
  "question": "Личный вопрос читателю",
  "emoji": "Один эмодзи"
}"""}
            ]
        )
        st.session_state.meanings = json.loads(meanings_response.choices[0].message.content)
        st.rerun()

# ПОКАЗЫВАЕМ РЕЗУЛЬТАТ
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

    # СЦЕНЫ
    st.subheader("🎬 Ключевые сцены")
    mood_colors = {
        "тревога":     {"bg": "#FFF3E0", "border": "#FF9800"},
        "страх":       {"bg": "#FCE4EC", "border": "#E91E63"},
        "любовь":      {"bg": "#FCE4EC", "border": "#E91E63"},
        "радость":     {"bg": "#E8F5E9", "border": "#4CAF50"},
        "грусть":      {"bg": "#E3F2FD", "border": "#2196F3"},
        "напряжение":  {"bg": "#FFF8E1", "border": "#FFC107"},
        "мистика":     {"bg": "#EDE7F6", "border": "#673AB7"},
        "надежда":     {"bg": "#E8F5E9", "border": "#4CAF50"},
        "конфликт":    {"bg": "#FFEBEE", "border": "#F44336"},
        "тайна":       {"bg": "#EDE7F6", "border": "#9C27B0"}
    }
    for i, scene in enumerate(st.session_state.scenes):
        colors = mood_colors.get(scene['mood'].lower(), {"bg": "#F5F5F5", "border": "#9E9E9E"})
        st.markdown(f"""
        <div style="background:{colors['bg']};border-radius:12px;padding:20px;margin-bottom:16px;border-left:4px solid {colors['border']};">
            <div style="color:#888;font-size:12px;margin-bottom:4px">СЦЕНА {i+1}</div>
            <div style="font-size:20px;font-weight:600;margin-bottom:8px">{scene['mood_emoji']} {scene['title']}</div>
            <div style="color:#555;font-size:14px;margin-bottom:12px">{scene['description']}</div>
            <div style="color:#888;font-size:12px">👥 {scene['characters']} &nbsp;&nbsp; 🎭 {scene['mood']}</div>
        </div>
        """, unsafe_allow_html=True)
    st.divider()

    # ПЕРСОНАЖИ
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
    st.divider()

    # СМЫСЛЫ
    st.subheader("💡 Смыслы и идеи")
    for meaning in st.session_state.meanings:
        with st.container(border=True):
            st.markdown(f"### {meaning['emoji']} {meaning['title']}")
            st.markdown(meaning['simple'])
            st.info(f"🤔 {meaning['question']}")
    st.divider()

    # ЧАТ
    if st.session_state.active_char:
        char = st.session_state.active_char
        st.subheader(f"💬 Чат с {char['name']}")

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        col_input, col_btn = st.columns([3, 1])
        with col_btn:
            if st.button("😏 Дерзкий вопрос", use_container_width=True):
                daring_questions = [
                    "Ты жалеешь о своих поступках?",
                    "Ты счастлив на самом деле?",
                    "Ты врёшь себе?",
                    "Чего ты боишься больше всего?",
                    "Если бы можно было всё изменить — ты бы изменил?"
                ]
                import random
                st.session_state.daring_q = random.choice(daring_questions)
                st.rerun()

        user_input = st.chat_input(f"Напиши {char['name']}...")

        if "daring_q" in st.session_state and st.session_state.daring_q:
            user_input = st.session_state.daring_q
            st.session_state.daring_q = ""

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            system_prompt = f"""Ты {char['name']} из книги "{st.session_state.book_title}".
Роль: {char['role']}. Эмоция: {char['emotion']}. Цель: {char['goal']}. Конфликт: {char['conflict']}.
Отвечай от первого лица в характере персонажа на русском языке. Максимум 3-4 предложения.
Если пользователь уже спрашивал тебя раньше — можешь сослаться на это."""

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
