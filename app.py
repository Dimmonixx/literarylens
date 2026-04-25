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
st.subheader("понимай книги через живой опыт")

st.divider()

def get_character_image(character_name, emotion):
    keywords = {
        "Любовь": "romantic portrait painting",
        "Тоска": "melancholy portrait painting",
        "Игривость": "mysterious dark portrait",
        "Безразличие": "cold distant portrait",
        "Страдание": "suffering portrait painting",
        "Страх": "fearful portrait painting",
        "Гордость": "proud noble portrait",
        "Ненависть": "dark villain portrait"
    }
    keyword = keywords.get(emotion, "classical portrait painting")
    return f"https://source.unsplash.com/300x400/?{keyword.replace(' ', ',')}"

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
  "role": "Главный герой / Антагонист / Второстепенный",
  "emotion": "Основная эмоция",
  "goal": "Главная цель в одном предложении",
  "conflict": "Главный конфликт в одном предложении"
}}"""
                    }
                ]
            )
            characters = json.loads(char_response.choices[0].message.content)

        for char in characters:
            with st.container(border=True):
                col_img, col_info = st.columns([1, 2])
                with col_img:
                    img_url = get_character_image(char['name'], char['emotion'])
                    if img_url:
                        st.image(img_url, use_container_width=True)
                    else:
                        st.markdown("<div style='background:#f0f0f0;height:150px;display:flex;align-items:center;justify-content:center;border-radius:10px;font-size:48px'>👤</div>", unsafe_allow_html=True)
                with col_info:
                    st.markdown(f"### {char['name']}")
                    st.markdown(f"**Роль:** {char['role']}")
                    st.markdown(f"**Эмоция:** {char['emotion']}")
                    st.markdown(f"**Цель:** {char['goal']}")
                    st.markdown(f"**Конфликт:** {char['conflict']}")
