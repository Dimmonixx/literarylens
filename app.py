import streamlit as st
from openai import OpenAI
import json

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(
    page_title="LiteraryLens",
    page_icon="📚",
    layout="centered"
)

st.title("📚 LiteraryLens")
st.subheader("Понимай книги через живой опыт")

st.divider()

book_title = st.text_input("Название книги:", placeholder="Например: Мастер и Маргарита")

if st.button("Анализировать", type="primary", use_container_width=True):
    if not book_title:
        st.warning("Введи название книги!")
    else:
        # Блок 1: Анализ книги
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

        # Блок 2: Персонажи
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
            
            characters_text = char_response.choices[0].message.content
            characters = json.loads(characters_text)

        for char in characters:
            with st.container(border=True):
                st.markdown(f"### {char['name']}")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Роль:** {char['role']}")
                    st.markdown(f"**Эмоция:** {char['emotion']}")
                with col2:
                    st.markdown(f"**Цель:** {char['goal']}")
                    st.markdown(f"**Конфликт:** {char['conflict']}")
