import streamlit as st

st.set_page_config(
    page_title="119 Assistant",
    page_icon="🚒",
    layout="wide"
)

st.markdown("""
# 🚒 119 Assistant
### 충남소방 행정·복무 AI

안녕하세요.
무엇이 궁금하신가요?
""")

question = st.text_input(
    "",
    placeholder="예) 병가 신청 어떻게 하지?"
)

st.markdown("---")

st.write("🔥 자주 찾는 업무")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.button("병가")

with col2:
    st.button("공가")

with col3:
    st.button("e사람")

with col4:
    st.button("온나라")

with col5:
    st.button("e호조")

if question:
    st.success(f"질문: {question}")
