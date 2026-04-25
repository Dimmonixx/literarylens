import streamlit as st
from openai import OpenAI

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
        st.warning("Введите название книги!")
    else:
        with st.spinner("Анализирую..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Ты литературный эксперт. Анализируй книги просто и понятно, без академичности."
                    },
                    {
                        "role": "user",
                        "content": f"Книга: {book_title}\n\nДай краткий анализ: о чём эта книга, главные темы, идеи и эмоции которые она вызывает."
                    }
                ]
            )
            result = response.choices[0].message.content
            st.success("Готово!")
            st.markdown(result)
