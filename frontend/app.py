import os

import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Customer Support Copilot", page_icon="🤖")
st.title("🤖 Customer Support Copilot")
st.caption("Ask support questions about shipping, returns, payments, or orders.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask your question...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        try:
            response = requests.post(
                f"{API_BASE_URL}/chat",
                json={"message": user_input, "top_k": 3},
                timeout=20,
            )
            response.raise_for_status()
            payload = response.json()

            content = payload["answer"]
            if payload["sources"]:
                sources = "\n".join(
                    [f"- {s['question']} (score={s['score']})" for s in payload["sources"]]
                )
                content += f"\n\n**Retrieved FAQs**\n{sources}"

            content += f"\n\nConfidence: `{payload['confidence']}`"
            if payload["fallback"]:
                content += "\n\n⚠️ Fallback response used."
        except requests.RequestException as exc:
            content = f"Could not reach backend API: {exc}"

        st.markdown(content)
        st.session_state.messages.append({"role": "assistant", "content": content})
