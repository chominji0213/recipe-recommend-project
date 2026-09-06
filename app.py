"""
Streamlit UI. 기존 챗봇들(영화/도서 추천봇)의 app.py 구조를 그대로 재사용.

TODO(4일차): llm_client.ask()가 구현되면 연결
"""

import uuid

import streamlit as st

import llm_client

st.set_page_config(page_title="레시피 추천봇", page_icon="🍳")
st.title("🍳 레시피 추천봇")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    if st.button("새 대화 시작"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

for role, content in st.session_state.messages:
    with st.chat_message(role):
        st.write(content)

user_input = st.chat_input("어떤 재료로 뭘 만들고 싶으세요? (예: 계란이랑 감자로 비건 요리 추천해줘)")
if user_input:
    st.session_state.messages.append(("user", user_input))
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        # TODO: llm_client.ask()가 구현되면 아래 placeholder를 교체
        answer = llm_client.ask(thread_id=st.session_state.thread_id, user_message=user_input)
        st.write(answer)
    st.session_state.messages.append(("assistant", answer))
