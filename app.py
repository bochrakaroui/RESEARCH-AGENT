import requests
import streamlit as st
from datetime import datetime

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Research Agent",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0f0f13 !important;
    font-family: 'Inter', sans-serif;
    color: #e2e2e8;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #16161d !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
}

/* ── MAIN CONTENT ── */
[data-testid="stMain"] { background: #0f0f13 !important; }
[data-testid="stMainBlockContainer"] {
    max-width: 820px !important;
    padding: 0 2rem 6rem !important;
    margin: 0 auto !important;
}

/* ── ALL BUTTONS BASE ── */
[data-testid="stButton"] > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    transition: all 0.15s ease !important;
    cursor: pointer !important;
    border-radius: 8px !important;
}

/* New Chat */
.new-chat-btn [data-testid="stButton"] > button {
    background: #ede0c4 !important;
    color: #1a1208 !important;
    border: none !important;
    width: 100% !important;
    font-size: 0.83rem !important;
    padding: 0.55rem 1rem !important;
    justify-content: flex-start !important;
    gap: 0.4rem !important;
}
.new-chat-btn [data-testid="stButton"] > button:hover {
    background: #e2d4b5 !important;
}

/* History items */
.hist-item [data-testid="stButton"] > button {
    background: transparent !important;
    color: rgba(255,255,255,0.42) !important;
    border: none !important;
    width: 100% !important;
    font-size: 0.79rem !important;
    font-weight: 400 !important;
    padding: 0.42rem 0.6rem !important;
    justify-content: flex-start !important;
    text-align: left !important;
    border-radius: 6px !important;
}
.hist-item [data-testid="stButton"] > button:hover {
    background: rgba(255,255,255,0.05) !important;
    color: rgba(255,255,255,0.7) !important;
}

/* Send button */
.send-btn [data-testid="stButton"] > button {
    background: #5c5cf5 !important;
    color: white !important;
    border: none !important;
    width: 42px !important;
    height: 42px !important;
    min-height: 0 !important;
    border-radius: 10px !important;
    padding: 0 !important;
    font-size: 1.1rem !important;
    line-height: 1 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
.send-btn [data-testid="stButton"] > button:hover {
    background: #4a4ae0 !important;
    transform: translateY(-1px) !important;
}

/* Clear button */
.clear-btn [data-testid="stButton"] > button {
    background: transparent !important;
    color: rgba(255,255,255,0.25) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    font-size: 0.73rem !important;
    font-weight: 400 !important;
    padding: 0.3rem 0.75rem !important;
}
.clear-btn [data-testid="stButton"] > button:hover {
    color: rgba(255,255,255,0.5) !important;
    border-color: rgba(255,255,255,0.14) !important;
}

/* ── TEXT INPUT ── */
[data-testid="stTextInput"] label { display: none !important; }
[data-testid="stTextInput"] > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 12px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stTextInput"] > div > div:focus-within {
    border-color: rgba(92,92,245,0.5) !important;
    box-shadow: 0 0 0 3px rgba(92,92,245,0.08) !important;
}
[data-testid="stTextInput"] input {
    background: transparent !important;
    color: rgba(255,255,255,0.88) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
    padding: 0.72rem 1rem !important;
    caret-color: #5c5cf5 !important;
}
[data-testid="stTextInput"] input::placeholder {
    color: rgba(255,255,255,0.2) !important;
}

/* ── SPINNER ── */
[data-testid="stSpinner"] p {
    color: rgba(255,255,255,0.35) !important;
    font-size: 0.8rem !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── ALERT ── */
[data-testid="stAlert"] {
    background: rgba(239,68,68,0.07) !important;
    border: 1px solid rgba(239,68,68,0.18) !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.09); border-radius: 3px; }

/* Remove extra padding from columns */
[data-testid="column"] { padding: 0 0.25rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────
if "messages"    not in st.session_state: st.session_state.messages    = []
if "history"     not in st.session_state: st.session_state.history     = []
if "query_count" not in st.session_state: st.session_state.query_count = 0

# ── API ───────────────────────────────────────────────────────────
def call_api(query):
    r = requests.post(f"{API_URL}/research", json={"query": query}, timeout=90)
    return r.json()

# ════════════════════════════════════════════════════════════════
#  SIDEBAR
# ════════════════════════════════════════════════════════════════
with st.sidebar:

    # Logo row
    st.markdown("""
    <div style="padding:1.3rem 1.1rem 0.9rem; display:flex;
                align-items:center; gap:0.5rem;">
        <span style="color:#5c5cf5; font-size:1rem;">◈</span>
        <span style="font-family:'Inter',sans-serif; font-size:0.92rem;
                     font-weight:600; color:rgba(255,255,255,0.88);
                     letter-spacing:0.01em;">ResearchAgent</span>
    </div>
    """, unsafe_allow_html=True)

    # New chat
    st.markdown('<div class="new-chat-btn">', unsafe_allow_html=True)
    if st.button("＋  New chat", key="new_chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:0.9rem;"></div>', unsafe_allow_html=True)

    # Stats card
    st.markdown(f"""
    <div style="margin:0 0.9rem 1rem; background:rgba(255,255,255,0.03);
                border:1px solid rgba(255,255,255,0.06); border-radius:10px;
                padding:0.75rem 1rem;">
        <div style="font-size:0.58rem; letter-spacing:0.12em; text-transform:uppercase;
                    color:rgba(255,255,255,0.25); font-family:'Inter',sans-serif;
                    margin-bottom:0.2rem;">Queries this session</div>
        <div style="font-size:1.6rem; font-weight:600; color:rgba(255,255,255,0.82);
                    font-family:'Inter',sans-serif; line-height:1.1;">
            {st.session_state.query_count}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # History
    if st.session_state.history:
        st.markdown("""
        <div style="padding:0 1rem 0.5rem; font-size:0.65rem; letter-spacing:0.09em;
                    text-transform:uppercase; color:rgba(255,255,255,0.22);
                    font-family:'Inter',sans-serif;">Your conversations</div>
        """, unsafe_allow_html=True)

        for i, item in enumerate(reversed(st.session_state.history[-8:])):
            label = (item["query"][:34] + "…") if len(item["query"]) > 34 else item["query"]
            st.markdown('<div class="hist-item">', unsafe_allow_html=True)
            st.button(f"◯  {label}", key=f"h{i}", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Bottom strip
    st.markdown("""
    <div style="position:absolute; bottom:0; left:0; right:0;
                padding:0.9rem 1.1rem;
                border-top:1px solid rgba(255,255,255,0.05);
                display:flex; align-items:center; gap:0.6rem;
                background:#16161d;">
        <div style="width:26px; height:26px; border-radius:50%; flex-shrink:0;
                    background:linear-gradient(135deg,#5c5cf5,#a78bfa);
                    display:flex; align-items:center; justify-content:center;
                    font-size:0.68rem; color:white; font-weight:600;
                    font-family:'Inter',sans-serif;">R</div>
        <div>
            <div style="font-size:0.77rem; font-weight:500;
                        color:rgba(255,255,255,0.75);
                        font-family:'Inter',sans-serif;">Research Agent</div>
            <div style="font-size:0.65rem; color:rgba(255,255,255,0.28);
                        font-family:'Inter',sans-serif;">localhost:8000</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
#  MAIN — CHAT AREA
# ════════════════════════════════════════════════════════════════

# Empty state
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align:center; padding:5rem 1rem 2rem;">
        <div style="font-size:1.9rem; opacity:0.12; margin-bottom:1rem;">◈</div>
        <div style="font-size:1.45rem; font-weight:600;
                    color:rgba(255,255,255,0.7); font-family:'Inter',sans-serif;
                    margin-bottom:0.45rem;">
            How can I help you research today?
        </div>
        <div style="font-size:0.84rem; color:rgba(255,255,255,0.28);
                    font-family:'Inter',sans-serif;">
            Ask any question — I search the web and generate a grounded answer with sources.
        </div>
    </div>
    <div style="display:flex; flex-wrap:wrap; gap:0.5rem;
                justify-content:center; padding-bottom:2rem;">
        <div style="background:rgba(255,255,255,0.04);
                    border:1px solid rgba(255,255,255,0.07);
                    border-radius:8px; padding:0.45rem 0.85rem;
                    font-size:0.78rem; color:rgba(255,255,255,0.35);
                    font-family:'Inter',sans-serif; cursor:default;">
            What causes urban heat islands?
        </div>
        <div style="background:rgba(255,255,255,0.04);
                    border:1px solid rgba(255,255,255,0.07);
                    border-radius:8px; padding:0.45rem 0.85rem;
                    font-size:0.78rem; color:rgba(255,255,255,0.35);
                    font-family:'Inter',sans-serif; cursor:default;">
            How does CRISPR gene editing work?
        </div>
        <div style="background:rgba(255,255,255,0.04);
                    border:1px solid rgba(255,255,255,0.07);
                    border-radius:8px; padding:0.45rem 0.85rem;
                    font-size:0.78rem; color:rgba(255,255,255,0.35);
                    font-family:'Inter',sans-serif; cursor:default;">
            Latest advances in quantum computing
        </div>
    </div>
    """, unsafe_allow_html=True)

# Messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div style="display:flex; gap:0.75rem; margin-bottom:2rem;
                    align-items:flex-start;">
            <div style="width:28px; height:28px; border-radius:50%; flex-shrink:0;
                        background:linear-gradient(135deg,#5c5cf5,#a78bfa);
                        display:flex; align-items:center; justify-content:center;
                        font-size:0.68rem; font-weight:600; color:white;
                        font-family:'Inter',sans-serif; margin-top:1px;">U</div>
            <div style="flex:1; padding-top:2px;">
                <div style="font-family:'Inter',sans-serif; font-size:0.76rem;
                            font-weight:600; color:rgba(255,255,255,0.88);
                            margin-bottom:0.28rem;">
                    You
                    <span style="font-weight:400; font-size:0.7rem;
                                 color:rgba(255,255,255,0.22);
                                 margin-left:0.45rem;">{msg["ts"]}</span>
                </div>
                <div style="font-family:'Inter',sans-serif; font-size:0.88rem;
                            color:rgba(255,255,255,0.82); line-height:1.65;">
                    {msg["content"]}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        # Sources block
        src_html = ""
        if msg.get("passages"):
            src_html = """
            <div style="margin-top:1rem; padding-top:0.9rem;
                        border-top:1px solid rgba(255,255,255,0.05);">
                <div style="font-size:0.63rem; letter-spacing:0.1em;
                            text-transform:uppercase; color:rgba(255,255,255,0.22);
                            font-family:'Inter',sans-serif; margin-bottom:0.5rem;">
                    Sources
                </div>"""
            for p in msg["passages"]:
                score  = round(p["score"] * 100)
                url    = p["url"]
                domain = url.replace("https://","").replace("http://","").split("/")[0]
                src_html += f"""
                <div style="display:flex; align-items:center; gap:0.65rem;
                            padding:0.42rem 0.7rem; margin-bottom:0.28rem;
                            background:rgba(255,255,255,0.03);
                            border:1px solid rgba(255,255,255,0.055);
                            border-radius:7px;">
                    <span style="font-size:0.68rem; font-weight:600;
                                 color:rgba(92,92,245,0.85);
                                 font-family:'Inter',sans-serif;
                                 min-width:30px;">{score}%</span>
                    <a href="{url}" target="_blank"
                       style="font-size:0.74rem; color:rgba(255,255,255,0.38);
                              font-family:'Inter',sans-serif; text-decoration:none;
                              overflow:hidden; text-overflow:ellipsis;
                              white-space:nowrap; flex:1;">
                        {domain}
                    </a>
                </div>"""
            src_html += "</div>"

        elapsed_html = ""
        if msg.get("elapsed"):
            elapsed_html = f"""<span style="font-size:0.68rem; font-weight:400;
                                color:rgba(255,255,255,0.18); margin-left:0.5rem;">
                                ⚡ {msg['elapsed']}s</span>"""

        st.markdown(f"""
        <div style="display:flex; gap:0.75rem; margin-bottom:2rem;
                    align-items:flex-start;">
            <div style="width:28px; height:28px; border-radius:50%; flex-shrink:0;
                        background:rgba(92,92,245,0.12);
                        border:1px solid rgba(92,92,245,0.28);
                        display:flex; align-items:center; justify-content:center;
                        font-size:0.8rem; margin-top:1px;">◈</div>
            <div style="flex:1; padding-top:2px;">
                <div style="font-family:'Inter',sans-serif; font-size:0.76rem;
                            font-weight:600; color:rgba(255,255,255,0.88);
                            margin-bottom:0.28rem;">
                    Research Agent
                    <span style="font-weight:400; font-size:0.7rem;
                                 color:rgba(255,255,255,0.22);
                                 margin-left:0.45rem;">{msg["ts"]}</span>
                    {elapsed_html}
                </div>
                <div style="font-family:'Inter',sans-serif; font-size:0.88rem;
                            color:rgba(255,255,255,0.78); line-height:1.7;">
                    {msg["content"]}
                </div>
                {src_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Input bar (sticky bottom) ─────────────────────────────────────
st.markdown("""
<div style="position:fixed; bottom:0; left:260px; right:0;
            background:linear-gradient(to top, #0f0f13 75%, transparent);
            padding:1.2rem 0 1rem; z-index:100;">
<div style="max-width:820px; margin:0 auto; padding:0 2rem;">
""", unsafe_allow_html=True)

c1, c2 = st.columns([11, 1])
with c1:
    question = st.text_input("msg", placeholder="Send a message…",
                             label_visibility="collapsed", key="msg_input")
with c2:
    st.markdown('<div class="send-btn">', unsafe_allow_html=True)
    send = st.button("↑", key="send_btn")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; margin-top:0.5rem; font-size:0.66rem;
            color:rgba(255,255,255,0.15); font-family:'Inter',sans-serif;">
    Research Agent may produce inaccurate information — always verify sources
</div>
</div></div>
""", unsafe_allow_html=True)

# Clear button
if st.session_state.messages:
    _, ccol = st.columns([5, 1])
    with ccol:
        st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
        if st.button("Clear chat", key="clear"):
            st.session_state.messages = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ── Submit logic ──────────────────────────────────────────────────
if send and question.strip():
    ts = datetime.now().strftime("%I:%M %p")

    st.session_state.messages.append({
        "role": "user", "content": question.strip(), "ts": ts
    })
    st.session_state.query_count += 1

    with st.spinner("Researching…"):
        try:
            data = call_api(question.strip())

            if "error" in data:
                st.session_state.messages.append({
                    "role": "bot",
                    "content": f"Error: {data['error']}",
                    "ts": datetime.now().strftime("%I:%M %p"),
                    "passages": [], "elapsed": None
                })
            else:
                st.session_state.messages.append({
                    "role":     "bot",
                    "content":  data["answer"],
                    "ts":       datetime.now().strftime("%I:%M %p"),
                    "passages": data["passages"],
                    "elapsed":  data["time"]
                })
                st.session_state.history.append({"query": question.strip()})

        except requests.exceptions.ConnectionError:
            st.error("Cannot reach backend — is FastAPI running on port 8000?")
        except requests.exceptions.Timeout:
            st.error("Request timed out — Ollama may be slow. Try again.")
        except Exception as e:
            st.error(f"Error: {str(e)}")

    st.rerun()

elif send and not question.strip():
    st.warning("Please type a question first.")