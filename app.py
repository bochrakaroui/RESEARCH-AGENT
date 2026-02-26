import requests
import streamlit as st

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Research Agent",
    page_icon="◈",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background: linear-gradient(160deg, #0d0f14 0%, #0f1420 100%);
    background-attachment: fixed;
    color: #e8e6e1;
}

.stApp {
    background: linear-gradient(160deg, #0d0f14 0%, #0f1420 100%);
    background-attachment: fixed;
    min-height: 100vh;
}

.block-container {
    max-width: 780px;
    padding: 0 1.5rem 6rem 1.5rem;
    margin: 0 auto;
    background: transparent;
}

header[data-testid="stHeader"] {
    background: transparent;
    border-bottom: none;
}

.app-header {
    padding: 2.5rem 0 1.5rem 0;
    border-bottom: 1px solid #1e2230;
    margin-bottom: 2rem;
}

.app-title {
    font-family: 'DM Mono', monospace;
    font-size: 1.15rem;
    font-weight: 500;
    color: #e8e6e1;
    letter-spacing: 0.04em;
    margin: 0;
}

.app-subtitle {
    font-size: 0.82rem;
    color: #5a5a6a;
    margin-top: 0.3rem;
    font-weight: 300;
    letter-spacing: 0.01em;
}

[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0.25rem 0;
}

[data-testid="stChatMessageContent"] {
    background: transparent !important;
}

[data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageContent"],
.user-bubble {
    background: #161b28 !important;
    border-radius: 16px 16px 4px 16px;
    padding: 0.85rem 1.1rem;
    border: 1px solid #1e2a3a;
}

[data-testid="stChatMessage"][data-testid*="assistant"] [data-testid="stChatMessageContent"],
.assistant-bubble {
    background: transparent !important;
    padding: 0.5rem 0;
}

.stChatMessage:has([data-testid="stChatMessageAvatarUser"]) {
    flex-direction: row-reverse;
}

[data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessageAvatarAssistant"] {
    width: 28px !important;
    height: 28px !important;
    background: #161b28 !important;
    border: 1px solid #1e2a3a !important;
    border-radius: 8px !important;
    font-size: 0.7rem !important;
    color: #4a5a7a !important;
}

[data-testid="stChatInput"] {
    background: #12161f !important;
    border: 1px solid #1e2a3a !important;
    border-radius: 14px !important;
    color: #e8e6e1 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    box-shadow: 0 -1px 0 #0d0f14 !important;
}

[data-testid="stChatInputSubmitButton"] {
    color: #e8e6e1 !important;
}

.source-meta {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #5a5a6a;
    margin-bottom: 1rem;
    letter-spacing: 0.02em;
}

.answer-text {
    font-size: 0.92rem;
    line-height: 1.75;
    color: #d4d2cd;
}

.stExpander {
    background: #10141e !important;
    border: 1px solid #1e2230 !important;
    border-radius: 10px !important;
    margin-bottom: 0.4rem !important;
}

.stExpander summary {
    font-size: 0.78rem !important;
    color: #5a5a6a !important;
    font-family: 'DM Mono', monospace !important;
}

.stExpander p {
    font-size: 0.84rem !important;
    color: #7a7a8a !important;
    line-height: 1.65 !important;
}

.stSpinner {
    color: #5a5a6a !important;
}

.empty-state {
    text-align: center;
    padding: 5rem 0 3rem 0;
    color: #1e2a3a;
}

.empty-state-icon {
    font-size: 2rem;
    margin-bottom: 0.75rem;
    display: block;
}

.empty-state-text {
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    letter-spacing: 0.06em;
}

.stAlert {
    background: #1a1016 !important;
    border: 1px solid #3a1e24 !important;
    border-radius: 10px !important;
    color: #a06070 !important;
    font-size: 0.85rem !important;
}

div[data-stale="false"] .stSpinner > div {
    border-top-color: #4a4a5a !important;
}
</style>
""", unsafe_allow_html=True)


def get_research_response(user_input: str) -> dict:
    response = requests.post(
        f"{API_URL}/research",
        json={"query": user_input},
        timeout=300,
    )
    return response.json()


def initialize_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "is_processing" not in st.session_state:
        st.session_state.is_processing = False


def render_header():
    st.markdown("""
    <div class="app-header">
        <p class="app-title">◈ Research Agent</p>
        <p class="app-subtitle">Searches the web and synthesizes answers in real time</p>
    </div>
    """, unsafe_allow_html=True)


def render_message(message: dict):
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(message["content"])
        else:
            st.markdown(f'<div class="answer-text">{message["content"]}</div>', unsafe_allow_html=True)

            if message.get("passages"):
                sources = message["passages"]
                st.markdown(
                    f'<div class="source-meta">{len(sources)} sources · {message.get("time", "—")}s</div>',
                    unsafe_allow_html=True,
                )
                for passage in sources:
                    score = round(passage["score"] * 100)
                    domain = passage["url"].split("/")[2] if "//" in passage["url"] else passage["url"]
                    with st.expander(f"{score}% — {domain}"):
                        st.write(passage["passage"])


def render_empty_state():
    st.markdown("""
    <div class="empty-state">
        <span class="empty-state-icon">◈</span>
        <p class="empty-state-text">ASK ANYTHING</p>
    </div>
    """, unsafe_allow_html=True)


def handle_user_input(user_query: str):
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.session_state.is_processing = True

    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Searching…"):
            result = get_research_response(user_query)

        if "error" in result:
            st.error(result["error"])
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Error: {result['error']}",
                "passages": [],
                "time": None,
            })
        else:
            answer = result["answer"]
            passages = result.get("passages", [])
            elapsed = result.get("time")

            st.markdown(f'<div class="answer-text">{answer}</div>', unsafe_allow_html=True)

            if passages:
                st.markdown(
                    f'<div class="source-meta">{len(passages)} sources · {elapsed}s</div>',
                    unsafe_allow_html=True,
                )
                for passage in passages:
                    score = round(passage["score"] * 100)
                    domain = passage["url"].split("/")[2] if "//" in passage["url"] else passage["url"]
                    with st.expander(f"{score}% — {domain}"):
                        st.write(passage["passage"])

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "passages": passages,
                "time": elapsed,
            })

    st.session_state.is_processing = False


def main():
    initialize_state()
    render_header()

    if not st.session_state.messages:
        render_empty_state()
    else:
        for message in st.session_state.messages:
            render_message(message)

    user_query = st.chat_input(
        "Ask a research question…",
        disabled=st.session_state.is_processing,
    )

    if user_query and user_query.strip():
        handle_user_input(user_query.strip())


if __name__ == "__main__":
    main()