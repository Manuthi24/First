import os
from datetime import datetime

import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Customer Support Copilot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main .block-container {
        max-width: 1100px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    .hero-card {
        background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%);
        border-radius: 20px;
        padding: 1.25rem 1.5rem;
        color: white;
        box-shadow: 0 12px 30px rgba(79, 70, 229, 0.2);
        margin-bottom: 1rem;
    }
    .hero-subtext {
        color: rgba(255,255,255,0.9);
        margin-top: .35rem;
        font-size: .95rem;
    }
    .kpi-card {
        background: #ffffff;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 0.8rem 1rem;
        min-height: 84px;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.04);
    }
    .kpi-title {
        color: #64748B;
        font-size: .8rem;
        margin-bottom: .2rem;
    }
    .kpi-value {
        color: #0F172A;
        font-size: 1.05rem;
        font-weight: 700;
    }
    .stChatMessage {
        border-radius: 16px;
        border: 1px solid #E2E8F0;
        padding: 0.25rem 0.65rem;
        background: #FFFFFF;
    }
    .footer-note {
        color: #64748B;
        font-size: .8rem;
        margin-top: .5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hi! I’m your support copilot. I can help with shipping, returns, refunds, "
                "order tracking, cancellations, and payment questions."
            ),
        }
    ]

if "active_prompt" not in st.session_state:
    st.session_state.active_prompt = None

if "last_confidence" not in st.session_state:
    st.session_state.last_confidence = "-"

if "api_status" not in st.session_state:
    st.session_state.api_status = "Checking..."


def check_api_health() -> str:
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return "Online"
        return "Degraded"
    except requests.RequestException:
        return "Offline"


def render_kpi(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class='kpi-card'>
            <div class='kpi-title'>{label}</div>
            <div class='kpi-value'>{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.session_state.api_status = check_api_health()

with st.sidebar:
    st.markdown("## ⚙️ Copilot Controls")
    st.caption("Use quick actions and monitor runtime status.")

    if st.button("🧹 Clear conversation", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Conversation cleared. How can I help you today?",
            }
        ]
        st.session_state.last_confidence = "-"

    st.markdown("### Suggested questions")
    for suggestion in [
        "How can I track my order?",
        "What is your return policy?",
        "Can I cancel my order after placing it?",
        "Which payment methods are accepted?",
    ]:
        if st.button(f"💬 {suggestion}", use_container_width=True):
            st.session_state.active_prompt = suggestion

    st.markdown("---")
    st.markdown("### Service Status")
    st.write(f"Backend API: **{st.session_state.api_status}**")
    st.write(f"Last answer confidence: **{st.session_state.last_confidence}**")

st.markdown(
    """
    <div class='hero-card'>
        <h2 style='margin:0;'>🤖 Customer Support Copilot</h2>
        <div class='hero-subtext'>Production-style support assistant for e-commerce FAQ automation.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

k1, k2, k3 = st.columns(3)
with k1:
    render_kpi("Average Response Time", "< 2s (local)")
with k2:
    render_kpi("Coverage", "Shipping • Returns • Orders")
with k3:
    render_kpi("Updated", datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"))

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

chat_input = st.chat_input("Ask your support question...")
if st.session_state.active_prompt and not chat_input:
    chat_input = st.session_state.active_prompt
    st.session_state.active_prompt = None

if chat_input:
    st.session_state.messages.append({"role": "user", "content": chat_input})
    with st.chat_message("user"):
        st.markdown(chat_input)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing support knowledge base..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/chat",
                    json={"message": chat_input, "top_k": 3},
                    timeout=20,
                )
                response.raise_for_status()
                payload = response.json()

                content = payload["answer"]
                if payload["sources"]:
                    sources = "\n".join(
                        [f"- {s['question']} · category={s['category']} · score={s['score']}" for s in payload["sources"]]
                    )
                    content += f"\n\n**Retrieved Sources**\n{sources}"

                st.session_state.last_confidence = str(payload["confidence"])
                content += f"\n\nConfidence: `{payload['confidence']}`"

                if payload["fallback"]:
                    content += "\n\n⚠️ I used fallback mode. A human support agent can help for complex cases."
            except requests.RequestException as exc:
                content = f"❌ Could not reach backend API: {exc}"

        st.markdown(content)
        st.session_state.messages.append({"role": "assistant", "content": content})

st.markdown("<div class='footer-note'>Built for deployment demos: health checks, confidence-aware responses, and support-safe fallback.</div>", unsafe_allow_html=True)
