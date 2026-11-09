"""Drukpa Chat: a Dzongkha-first assistant with a live Streamlit dashboard."""
from __future__ import annotations

import logging
from pathlib import Path

import requests
import streamlit as st

from dzongkha_bot.config import load_settings
from dzongkha_bot import engine as engine_module, strings

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
st.set_page_config(page_title="Drukpa Chat", page_icon="🐉", layout="wide")

settings = load_settings()
css_path = Path(__file__).parent / "assets" / "custom.css"
st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if st.session_state.dark_mode:
    st.markdown(
        """<style>
        .stApp { background-image:linear-gradient(rgba(10,18,22,.79),rgba(10,18,22,.86)),url('/app/static/bhutan_background.jpg'); color:#edf3f0; }
        .stApp, .stMain, [data-testid="stAppViewContainer"] { color:#edf3f0; }
        [data-testid="stSidebar"] { background:#132226; border-right-color:#33494a; }
        [data-testid="stSidebar"] * { color:#e5eeea; }
        [data-testid="stSidebar"] [data-testid="stMetric"] { background:#213638; border-color:#445b59; }
        .topbar { background:#122226; border:1px solid #3b5550; }
        .welcome, [data-testid="stChatMessage"] { background:#19282b; border-color:#425655; }
        .welcome-dz, [data-testid="stChatMessage"] p, .stMarkdown p, h1, h2, h3, label { color:#edf3f0 !important; }
        .welcome p, .eyebrow { color:#e3bd6c !important; }
        .footer-note { color:#d1dbd8; }
        .stButton button, [data-testid="stDownloadButton"] button { background:#203b3d; color:#f5f7f4; border-color:#526b65; }
        [data-testid="stChatInput"] textarea { background:#1a2d30; color:#f5f7f4; }
        [data-testid="stAlert"] { background:#20383a; color:#f5f7f4; }
        [data-testid="stAlert"] * { color:#f5f7f4 !important; }
        </style>""",
        unsafe_allow_html=True,
    )


@st.cache_resource
def get_engine():
    # Load models on the first message, so the dashboard opens before downloads.
    return engine_module.build_engine()


def model_history(messages):
    """Drop failed exchanges; use saved English text for the translation pipeline."""
    result = []
    for message in messages:
        if message.get("error"):
            if result and result[-1]["role"] == "user":
                result.pop()
            continue
        item = {"role": message["role"], "content": message.get("en") or message["content"]}
        result.append(item)
    return result


def ollama_status():
    """Return a quick local health check without blocking the page for long."""
    if "ollama" not in settings.provider_order:
        return None
    try:
        response = requests.get(f"{settings.ollama_host.rstrip('/')}/api/tags", timeout=1.5)
        response.raise_for_status()
        models = response.json().get("models", [])
        found = any(m.get("name", "").split(":")[0] == settings.ollama_model.split(":")[0] for m in models)
        return found
    except (requests.RequestException, ValueError, AttributeError):
        return False


with st.sidebar:
    st.markdown("# Drukpa Chat")
    st.caption("Dzongkha · English · རྫོང་ཁ")
    st.toggle("Dark mode", key="dark_mode")
    st.divider()
    if st.button("＋  New conversation", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.rerun()
    turns = sum(m["role"] == "user" for m in st.session_state.messages)
    st.metric("Messages sent", turns)
    st.divider()
    st.markdown("#### Your setup")
    st.caption(f"Chat provider: {', '.join(settings.provider_order) or 'not configured'}")
    st.caption("Translation: Dzongkha ↔ English · one shared checkpoint")
    st.caption("Conversation is kept in this browser session.")

st.markdown(
    '<div class="topbar"><img class="brand-logo" src="/app/static/drukpa_logo.png" alt="Drukpa Chat dragon logo">'
    '<div class="brand-copy"><div class="eyebrow">BHUTAN · DZONGKHA FIRST</div>'
    '<h1>Drukpa Chat</h1><p>Talk, learn, and explore in Dzongkha or English.</p></div></div>',
    unsafe_allow_html=True,
)

health = ollama_status()
if health is None:
    st.info("Using configured cloud or compatible providers. Check your .env settings if replies are unavailable.")
elif health:
    st.success(f"Ollama is online · {settings.ollama_model}")
else:
    st.warning(f"Ollama is offline or {settings.ollama_model} is missing. Start Ollama and pull the model to chat locally.")

if not st.session_state.messages:
    st.markdown(
        f'<div class="welcome"><span class="welcome-label">KUZUZANGPO LA</span>'
        f'<div class="welcome-dz">{strings.WELCOME}</div>'
        '<p>Start with a question below, or write your own message.</p></div>',
        unsafe_allow_html=True,
    )
    prompts = [
        "What is the capital of Bhutan?",
        "Tell me about Bhutanese culture.",
        "Help me practice Dzongkha.",
    ]
    columns = st.columns(3)
    for column, suggestion in zip(columns, prompts):
        if column.button(suggestion, use_container_width=True):
            st.session_state.quick_prompt = suggestion
            st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("ཁྱོད་ཀྱི་དྲི་བ་འདིར་འབྲི།  Ask Drukpa Chat…")
prompt = prompt or st.session_state.pop("quick_prompt", None)
if prompt and prompt.strip():
    clean_prompt = prompt.strip()
    st.session_state.messages.append({"role": "user", "content": clean_prompt})
    with st.chat_message("user"):
        st.markdown(clean_prompt)
    with st.chat_message("assistant"):
        try:
            with st.spinner("ལན་བཏབ་བཞིན་པ…  Working on your answer"):
                engine = get_engine()
                reply = engine.reply(model_history(st.session_state.messages))
            english_requested = "english" in clean_prompt.lower()
            answer = reply.text if english_requested else f"Kuzuzangpo la · {reply.text}"
            st.markdown(answer)
            st.session_state.messages.append(
                {"role": "assistant", "content": answer, "en": reply.en, "error": reply.error is not None}
            )
            if reply.user_en is not None:
                st.session_state.messages[-2]["en"] = reply.user_en
        except Exception as error:  # Keep the page usable after dependency/model failures.
            logging.exception("Chat request failed")
            safe_message = (
                "Kuzuzangpo la · I couldn't get a reply just now. Check that your chat provider is running "
                "and that the translation models are installed, then try again."
            )
            st.error(safe_message)
            st.session_state.messages.append({"role": "assistant", "content": safe_message, "error": True})

if st.session_state.messages:
    transcript = "\n\n".join(f"{m['role'].title()}: {m['content']}" for m in st.session_state.messages)
    st.download_button("↓  Download conversation", transcript, file_name="drukpa-chat.txt", mime="text/plain")
st.markdown('<div class="footer-note">Answers and translations can contain mistakes. Verify important details.</div>', unsafe_allow_html=True)
