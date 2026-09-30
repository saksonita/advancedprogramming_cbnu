"""Streamlit chat UI for the café agent. Only calls CafeAgent.run() and displays results."""
import streamlit as st

from src.agent import CafeAgent

st.set_page_config(page_title="Café CBNU Agent", page_icon="☕")
st.title("☕ Café CBNU Agent")

if "agent" not in st.session_state:
    st.session_state.agent = CafeAgent()
if "messages" not in st.session_state:
    st.session_state.messages = []


def _render_steps(steps):
    if not steps:
        return
    with st.expander("🔧 Tool calls"):
        for step in steps:
            st.markdown(f"**{step['tool']}**({step['arguments']}) → `{step['result']}`")


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        _render_steps(msg.get("steps"))

user_input = st.chat_input("Ask about the menu, stock, or sales...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    result = st.session_state.agent.run(user_input)
    st.session_state.messages.append(
        {"role": "assistant", "content": result["answer"], "steps": result["steps"]}
    )
    with st.chat_message("assistant"):
        st.markdown(result["answer"])
        _render_steps(result["steps"])
