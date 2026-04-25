import streamlit as st
from openai import OpenAI
import json
import requests

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

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

def get_unsplash_image(char_name, book_name, emotion):
    try:
        unsplash_key = st.secrets["UNSPLASH_ACCESS_KEY"]
        query = f"{char_name} {book_name} portrait"
        url = f"https://api.unsplash.com/search/photos?query={query}&per_page=1&client_id={unsplash_key}"
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get("results"):
            return data["results"][0]["urls"]["regular"]
    except:
        pass
    return None

book_title = st.text_input("Название книги:", placeholder="Например: Мастер и Маргарита")

if st.button("Анализировать", type="primary", use_container_width=True):
    if not book_title:
        st.warning("Введи название книги!")
    else:
        with st.spinner("Анализирую книгу..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Ты литературный эксперт. Отвечай просто и понятно, без академичности."
                    },
                    {
                        "role": "user",
                        "content": f"Книга: {book_title}\n\nДай краткий анализ: о чём эта книга, главные темы и идеи. Максимум 3 абзаца."
                    }
                ]
            )
            analysis = response.choices[0].message.content

        st.success("Готово!")
        st.markdown(analysis)
        st.divider()
        st.subheader("🎭 Персонажи")

        with st.spinner("Анализирую персонажей..."):
            char_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Ты литературный эксперт. Отвечай ТОЛЬКО валидным JSON без markdown и без пояснений."
                    },
                    {
                        "role": "user",
                        "content": f"""Книга: {book_title}

Верни JSON массив с главными персонажами (максимум 4).
Формат каждого персонажа:
{{
  "name": "Имя персонажа",
  "role": "Главный герой / Главная героиня / Антагонист / Второстепенный",
  "emotion": "Основная эмоция",
  "goal": "Главная цель в одном предложении",
  "conflict": "Главный конфликт в одном предложении"
}}"""
                    }
                ]
            )
            characters = json.loads(char_response.choices[0].message.content)

        for char in characters:
            colors = color_map.get(char['role'], {"bg": "#F1EFE8", "text": "#444441"})
            initials = "".join([w[0] for w in char['name'].split()][:2]).upper()

            with st.container(border=True):
                col_img, col_info = st.columns([1, 2])
                with col_img:
                    img_url = get_unsplash_image(char['name'], book_title, char['emotion'])
                    if img_url:
                        st.image(img_url, use_container_width=True)
                    else:
                        st.markdown(f"""
                        <div style="background:{colors['bg']};color:{colors['text']};width:100%;aspect-ratio:1;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:48px;font-weight:500;">
                        {initials}
                        </div>
                        """, unsafe_allow_html=True)
                with col_info:
                    st.markdown(f"### {char['name']}")
                    st.markdown(f"<span style='background:{colors['bg']};color:{colors['text']};padding:2px 10px;border-radius:8px;font-size:12px'>{char['role']}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Эмоция:** {char['emotion']}")
                    st.markdown(f"**Цель:** {char['goal']}")
                    st.markdown(f"**Конфликт:** {char['conflict']}")
