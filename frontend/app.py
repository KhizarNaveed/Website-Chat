import streamlit as st
import httpx
import uuid

API_URL = "http://localhost:8000"

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="WebChat · RAG Assistant",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════
# PREMIUM CHATBOT STYLES (Midnight & Rust Theme)
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    /* ═══ Typography ═══ */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        -webkit-font-smoothing: antialiased;
    }

    /* ═══ Hide Streamlit Chrome ═══ */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden;}
    
    /* Hide "Press Enter to apply" text */
    [data-testid="InputInstructions"] {
        display: none !important;
    }

    /* ═══ Disable Streamlit's "running" dim effect ═══ */
    .stApp > div:first-child,
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] > section,
    [data-testid="stVerticalBlock"],
    [data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stMainBlockContainer"] {
        opacity: 1 !important;
        transition: none !important;
    }
    [data-testid="stStatusWidget"] { display: none !important; }
    .stApp > div:first-child > div:first-child > div:first-child { display: none !important; }

    /* ═══ App Background & Colors ═══ */
    .stApp {
        background: #0e0e10; /* Deep midnight background */
    }

    /* ═══ Sidebar ═══ */
    [data-testid="stSidebar"] {
        background: #161618;
        border-right: 1px solid #27272a;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }

    /* ═══ Main Container ═══ */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 6rem;
        max-width: 860px;
    }

    /* ═══ Sidebar Brand ═══ */
    .brand {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0 0.25rem 1.5rem 0.25rem;
    }

    /* The Crown Logo */
    .brand-mark {
        width: 36px;
        height: 36px;
        border-radius: 8px;
        background: #7f1d1d; /* Deep rust red */
        border: 1px solid #991b1b;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        box-shadow: 0 4px 12px rgba(127, 29, 29, 0.3);
    }

    .brand-name {
        font-size: 1.05rem;
        font-weight: 700;
        color: #f4f4f5;
        letter-spacing: -0.02em;
    }

    .brand-sub {
        font-size: 0.75rem;
        color: #a1a1aa;
        margin-top: 1px;
    }

    /* ═══ Section Labels ═══ */
    .section-label {
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #a1a1aa;
        margin-bottom: 0.75rem;
        padding: 0 0.25rem;
    }

    /* ═══ Status Dot ═══ */
    .status {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.75rem;
        color: #a1a1aa;
        padding: 0.4rem 0.6rem;
        border-radius: 6px;
        background: #1f1f22;
        border: 1px solid #27272a;
    }

    .status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #10b981;
    }

    .status-dot.offline {
        background: #ef4444;
    }

    /* ═══ Text Input (Sidebar) ═══ */
    .stTextInput > div > div {
        background: #1f1f22 !important;
        border: 1px solid #3f3f46 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }

    .stTextInput > div > div:focus-within {
        border-color: #dc2626 !important;
        box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.15) !important;
    }

    .stTextInput > div > div > input {
        background: transparent !important;
        color: #f4f4f5 !important;
        padding: 0.6rem 0.85rem !important;
        font-size: 0.85rem !important;
        border: none !important;
        box-shadow: none !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: #71717a !important;
    }

    /* ═══ Buttons ═══ */
    .stButton > button {
        background: #7f1d1d;
        color: #ffffff;
        border: 1px solid #991b1b;
        border-radius: 8px;
        padding: 0.55rem 1rem;
        font-weight: 500;
        font-size: 0.85rem;
        transition: all 0.2s ease;
        width: 100%;
    }

    .stButton > button:hover {
        background: #991b1b;
        border-color: #b91c1c;
        color: #ffffff;
    }

    .stButton > button:active {
        transform: scale(0.98);
    }

    .stButton > button[kind="secondary"] {
        background: transparent;
        color: #a1a1aa;
        border: 1px solid #3f3f46;
    }

    .stButton > button[kind="secondary"]:hover {
        background: #27272a;
        color: #f4f4f5;
    }

    /* ═══ Chat Messages ═══ */
    [data-testid="stChatMessage"] {
        background: transparent;
        border: none;
        padding: 0.5rem 0;
        margin-bottom: 1rem;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: #1f1f22;
        border: 1px solid #27272a;
        border-radius: 12px;
        padding: 1rem 1.25rem;
    }

    [data-testid="stChatMessage"] p {
        color: #e4e4e7;
        line-height: 1.65;
        font-size: 0.95rem;
    }

    /* ═══ Chat Input Box (Now blends with background) ═══ */
    /* The container behind the input */
    [data-testid="stBottom"] > div {
        background-color: #0e0e10 !important;
    }

    [data-testid="stChatInput"] {
        background: #0e0e10 !important; /* Matches main background */
        border: 1px solid #27272a !important; /* Subtle border */
        border-radius: 12px !important;
        box-shadow: none !important; /* Removed shadow for a flat look */
        transition: all 0.2s ease;
    }

    [data-testid="stChatInput"]:focus-within {
        border-color: #dc2626 !important; /* Rust red glow on focus */
        box-shadow: 0 0 0 2px rgba(220, 38, 38, 0.15) !important;
    }

    /* Ensure the inner wrapper is transparent */
    [data-testid="stChatInput"] > div {
        background: transparent !important;
    }

    [data-testid="stChatInput"] textarea {
        background: transparent !important;
        color: #f4f4f5 !important;
        font-size: 0.95rem !important;
        padding: 1rem 1.15rem !important;
    }

    /* Fix placeholder text color in Chat Input */
    [data-testid="stChatInput"] textarea::placeholder {
        color: #71717a !important;
        opacity: 1 !important;
    }

    /* ═══ Source Cards ═══ */
    .source-item {
        display: flex;
        gap: 0.75rem;
        padding: 0.75rem 0;
        border-bottom: 1px solid #27272a;
    }

    .source-item:last-child {
        border-bottom: none;
    }

    .source-index {
        flex-shrink: 0;
        width: 22px;
        height: 22px;
        border-radius: 6px;
        background: #27272a;
        color: #a1a1aa;
        font-size: 0.7rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'JetBrains Mono', monospace;
    }

    .source-content {
        flex: 1;
        min-width: 0;
    }

    .source-meta {
        color: #71717a;
        font-size: 0.75rem;
        font-family: 'JetBrains Mono', monospace;
        margin-bottom: 0.35rem;
        word-break: break-all;
    }

    .source-text {
        color: #a1a1aa;
        font-size: 0.85rem;
        line-height: 1.55;
    }

    /* ═══ Expander ═══ */
    .streamlit-expanderHeader {
        background: transparent !important;
        border: none !important;
        color: #a1a1aa !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        padding: 0.5rem 0 !important;
    }

    .streamlit-expanderHeader:hover {
        color: #f4f4f5 !important;
    }

    .streamlit-expanderContent {
        background: #161618 !important;
        border: 1px solid #27272a !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
    }

    /* ═══ Empty State ═══ */
    .empty-state {
        padding: 6rem 2rem;
        text-align: center;
    }

    .empty-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: inline-block;
    }

    .empty-title {
        font-size: 2rem;
        font-weight: 700;
        color: #f4f4f5;
        letter-spacing: -0.03em;
        margin-bottom: 0.75rem;
    }

    .empty-desc {
        color: #a1a1aa;
        font-size: 1rem;
        line-height: 1.65;
        max-width: 500px;
        margin: 0 auto;
    }

    /* ═══ Divider ═══ */
    hr {
        border: none;
        border-top: 1px solid #27272a;
        margin: 1.25rem 0;
    }

    /* ═══ Active Doc Card ═══ */
    .doc-card {
        background: #1f1f22;
        border: 1px solid #27272a;
        border-radius: 8px;
        padding: 0.75rem 0.85rem;
        margin-bottom: 1rem;
    }

    .doc-label {
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #10b981;
        margin-bottom: 0.4rem;
    }

    .doc-url {
        color: #a1a1aa;
        font-size: 0.75rem;
        font-family: 'JetBrains Mono', monospace;
        word-break: break-all;
        line-height: 1.4;
    }

    /* ═══ Alerts ═══ */
    .stAlert {
        background: #1f1f22 !important;
        border: 1px solid #3f3f46 !important;
        border-radius: 8px !important;
        color: #e4e4e7 !important;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
if "indexed_url" not in st.session_state:
    st.session_state.indexed_url = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "backend_healthy" not in st.session_state:
    st.session_state.backend_healthy = False

# Health check
try:
    r = httpx.get(f"{API_URL}/health", timeout=3)
    st.session_state.backend_healthy = r.status_code == 200
except Exception:
    st.session_state.backend_healthy = False

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    # Brand & Logo
    st.markdown("""
    <div class="brand">
        <div class="brand-mark">👑</div>
        <div>
            <div class="brand-name">WebChat</div>
            <div class="brand-sub">RAG Assistant</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Status
    dot_class = "status-dot" if st.session_state.backend_healthy else "status-dot offline"
    status_text = "Connected" if st.session_state.backend_healthy else "Disconnected"
    st.markdown(f"""
    <div style="padding: 0 0.25rem 1.5rem 0.25rem;">
        <span class="status">
            <span class="{dot_class}"></span>
            {status_text}
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Index section
    st.markdown('<div class="section-label">Index Website</div>', unsafe_allow_html=True)

    url = st.text_input(
        "URL",
        placeholder="https://example.com",
        label_visibility="collapsed",
    )

    if st.button("Index", type="primary", use_container_width=True):
        if not url.strip():
            st.error("Please enter a URL")
        elif not url.startswith(("http://", "https://")):
            st.error("URL must start with http:// or https://")
        else:
            with st.spinner("Indexing..."):
                try:
                    httpx.post(f"{API_URL}/session/clear",
                               json={"session_id": st.session_state.session_id}, timeout=30)
                    r = httpx.post(f"{API_URL}/index", json={"url": url}, timeout=600)
                    if r.status_code == 200:
                        data = r.json()
                        st.session_state.indexed_url = url
                        st.session_state.messages = []
                        st.success(f"Indexed {data['chunks']} chunks")
                        st.rerun()
                    else:
                        st.error(f"{r.json().get('detail', 'Error')}")
                except httpx.ConnectError:
                    st.error("Backend not running")
                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown("---")

    # Active document
    if st.session_state.indexed_url:
        st.markdown('<div class="section-label">Active Document</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="doc-card">
            <div class="doc-label">● Indexed</div>
            <div class="doc-url">{st.session_state.indexed_url[:100]}{'…' if len(st.session_state.indexed_url) > 100 else ''}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Clear chat", use_container_width=True, type="secondary"):
            st.session_state.messages = []
            try:
                httpx.post(f"{API_URL}/session/clear",
                           json={"session_id": st.session_state.session_id}, timeout=30)
            except Exception:
                pass
            st.rerun()

    # Footer
    st.markdown(f"""
    <div style="position: fixed; bottom: 1rem; padding: 0.5rem 0.25rem; color: #52525b; font-size: 0.7rem;">
        Session · <code style="font-size: 0.7rem;">{st.session_state.session_id}</code>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# MAIN AREA
# ═══════════════════════════════════════════════════════════════

# Empty state
if not st.session_state.indexed_url:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">👑</div>
        <div class="empty-title">Chat with any website</div>
        <div class="empty-desc">
            Paste a URL in the sidebar and index it. Then ask questions about the page content — 
            get cited answers from a local language model.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ═══════════════════════════════════════════════════════════════
# CHAT HISTORY
# ═══════════════════════════════════════════════════════════════
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if msg.get("sources"):
            with st.expander(f"Sources · {len(msg['sources'])} chunks"):
                for i, src in enumerate(msg["sources"], 1):
                    st.markdown(f"""
                    <div class="source-item">
                        <div class="source-index">{i}</div>
                        <div class="source-content">
                            <div class="source-meta">{src['source']} · chunk #{src['chunk_id']}</div>
                            <div class="source-text">{src['snippet']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# CHAT INPUT
# ═══════════════════════════════════════════════════════════════
if question := st.chat_input("Ask a question about this page..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                r = httpx.post(f"{API_URL}/ask", json={
                    "question": question,
                    "session_id": st.session_state.session_id,
                }, timeout=180)

                if r.status_code == 200:
                    data = r.json()
                    st.markdown(data["answer"])

                    if data.get("sources"):
                        with st.expander(f"Sources · {len(data['sources'])} chunks"):
                            for i, src in enumerate(data["sources"], 1):
                                st.markdown(f"""
                                <div class="source-item">
                                    <div class="source-index">{i}</div>
                                    <div class="source-content">
                                        <div class="source-meta">{src['source']} · chunk #{src['chunk_id']}</div>
                                        <div class="source-text">{src['snippet']}</div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": data["answer"],
                        "sources": data["sources"],
                    })
                else:
                    st.error(f"{r.json().get('detail', 'Error')}")
            except httpx.ConnectError:
                st.error("Backend not running")
            except Exception as e:
                st.error(f"Error: {e}")