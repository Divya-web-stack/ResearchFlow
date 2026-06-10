import streamlit as st
import requests
import pandas as pd

API_BASE = "https://researchflow-0rqd.onrender.com"

st.set_page_config(
    page_title="ResearchFlow AI",
    page_icon="🧠",
    layout="wide"
)

# ─── GLOBAL CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --bg:          #0d0f14;
    --surface:     #13161f;
    --surface-2:   #1a1e2a;
    --border:      #252938;
    --accent:      #4f7cff;
    --accent-2:    #7c3aed;
    --accent-glow: rgba(79,124,255,0.15);
    --text:        #e8eaf2;
    --muted:       #6b7280;
    --success:     #10b981;
    --warning:     #f59e0b;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* Sidebar brand */
.brand-block {
    padding: 24px 20px 18px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 6px;
}
.brand-title {
    font-family: 'Syne', sans-serif;
    font-size: 22px; font-weight: 800;
    background: linear-gradient(135deg, #4f7cff, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}
.brand-sub {
    font-size: 11px; color: var(--muted);
    letter-spacing: 1.5px; text-transform: uppercase; margin-top: 2px;
}

/* Page header */
.page-header {
    padding: 28px 0 20px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 28px;
}
.page-title {
    font-family: 'Syne', sans-serif;
    font-size: 26px; font-weight: 700;
    color: var(--text); margin: 0; letter-spacing: -0.5px;
}
.page-subtitle { font-size: 13px; color: var(--muted); margin-top: 4px; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), var(--accent-2)) !important;
    color: #fff !important; border: none !important;
    border-radius: 10px !important; padding: 10px 22px !important;
    font-family: 'DM Sans', sans-serif !important; font-weight: 500 !important;
    font-size: 14px !important;
    box-shadow: 0 4px 14px rgba(79,124,255,0.25) !important;
    transition: opacity 0.18s, transform 0.12s !important;
}
.stButton > button:hover { opacity: 0.88 !important; transform: translateY(-1px) !important; }

/* Chat */
[data-testid="stChatMessage"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 16px !important;
    margin-bottom: 10px !important;
}
[data-testid="stChatInput"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    color: var(--text) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 20px 24px !important;
}
[data-testid="stMetricLabel"] {
    font-size: 11px !important; letter-spacing: 1px !important;
    text-transform: uppercase !important; color: var(--muted) !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 34px !important; font-weight: 700 !important;
    color: var(--accent) !important;
}

/* Expanders */
[data-testid="stExpander"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    margin-bottom: 10px !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] summary {
    font-weight: 500 !important; font-size: 14px !important;
    padding: 14px 18px !important; color: var(--text) !important;
}
[data-testid="stExpander"] summary:hover { background: var(--surface-2) !important; }

/* File uploader */
[data-testid="stFileUploader"] {
    background: var(--surface) !important;
    border: 2px dashed var(--border) !important;
    border-radius: 14px !important;
}
[data-testid="stFileUploader"]:hover { border-color: var(--accent) !important; }

/* Text input */
[data-testid="stTextInput"] input {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 12px !important; overflow: hidden !important;
}

/* Divider */
hr { border-color: var(--border) !important; }

/* Info/Success/Warning */
[data-testid="stInfo"] {
    background: rgba(79,124,255,0.08) !important;
    border-left: 3px solid var(--accent) !important;
    border-radius: 10px !important; color: var(--text) !important;
}
[data-testid="stSuccess"] {
    background: rgba(16,185,129,0.08) !important;
    border-left: 3px solid var(--success) !important;
    border-radius: 10px !important;
}
[data-testid="stWarning"] {
    background: rgba(245,158,11,0.08) !important;
    border-left: 3px solid var(--warning) !important;
    border-radius: 10px !important;
}

/* Link button */
.stLinkButton a {
    background: transparent !important;
    border: 1px solid var(--border) !important;
    color: var(--accent) !important;
    border-radius: 8px !important; font-size: 13px !important;
}
.stLinkButton a:hover {
    border-color: var(--accent) !important;
    background: var(--accent-glow) !important;
}

/* Sidebar radio — hide default labels, we inject HTML headings */
[data-testid="stSidebar"] .stRadio label {
    display: flex; align-items: center;
    padding: 10px 14px; border-radius: 10px;
    font-size: 14px; font-weight: 500;
    color: var(--muted); cursor: pointer;
    transition: background 0.15s, color 0.15s;
    margin: 2px 4px;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: var(--surface-2); color: var(--text);
}
[data-testid="stSidebar"] .stRadio [aria-checked="true"] + label,
[data-testid="stSidebar"] .stRadio input:checked + div label {
    background: var(--accent-glow) !important;
    color: var(--accent) !important;
}
[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
    color: inherit !important; font-size: 14px !important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
    gap: 2px !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

/* Main padding */
.block-container {
    padding-top: 0 !important;
    padding-left: 36px !important;
    padding-right: 36px !important;
    max-width: 1200px !important;
}

/* Status dot */
.status-dot {
    display: inline-block; width: 8px; height: 8px;
    border-radius: 50%; background: var(--success);
    box-shadow: 0 0 6px var(--success); margin-right: 6px;
    animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.35} }

/* Agent card */
.agent-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 14px; padding: 22px 24px; margin-bottom: 14px;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.agent-card:hover {
    border-color: rgba(79,124,255,0.35);
    box-shadow: 0 4px 20px rgba(79,124,255,0.08);
}
.agent-name {
    font-family: 'Syne', sans-serif; font-size: 17px;
    font-weight: 700; color: var(--text); margin-bottom: 6px;
}
.agent-role {
    display: inline-block; font-size: 11px; font-weight: 600;
    letter-spacing: 1px; text-transform: uppercase;
    color: var(--accent); background: var(--accent-glow);
    border: 1px solid rgba(79,124,255,0.2);
    border-radius: 6px; padding: 3px 10px; margin-bottom: 10px;
}
.agent-desc { font-size: 13px; color: var(--muted); line-height: 1.6; }
.agent-tools { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 14px; }
.tool-badge {
    font-size: 11px; font-weight: 500; color: #a78bfa;
    background: rgba(124,58,237,0.12);
    border: 1px solid rgba(124,58,237,0.2);
    border-radius: 6px; padding: 3px 10px;
}
</style>
""", unsafe_allow_html=True)

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="brand-block">
        <div class="brand-title">ResearchFlow AI</div>
        <div class="brand-sub">Multi-Agent Platform</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.sidebar.radio(
        "Navigation",
        [
            "🔬  Research",
            "📄  Document Analysis",
            "📚  Memory",
            "📊  Analytics",
            "🤖  Agents"
        ]
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="padding: 0 12px;">
        <div style="font-size:11px;color:var(--muted);letter-spacing:1px;
                    text-transform:uppercase;margin-bottom:8px;">System</div>
        <div style="font-size:13px;color:var(--text);">
            <span class="status-dot"></span>All agents online
        </div>
    </div>
    """, unsafe_allow_html=True)

# map back to plain names for comparisons
_page = page.split("  ", 1)[-1]

# ─── RESEARCH PAGE ────────────────────────────────────────────────────────────
if _page == "Research":

    st.markdown('<div class="page-header"><div class="page-title">🔬 Research Chat</div><div class="page-subtitle">Ask anything — your multi-agent team is standing by</div></div>', unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask anything...")

    if prompt:

        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):

            with st.spinner("Agents working..."):

                response = requests.post(
                    f"{API_BASE}/api/research",
                    json={
                        "query": prompt,
                        "limit": 5,
                        "chat_history": st.session_state.messages
                    }
                )

                result = response.json()

          
            answer = result["report"]["report"]



            st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})

# ─── DOCUMENT PAGE ────────────────────────────────────────────────────────────
elif _page == "Document Analysis":

    st.markdown('<div class="page-header"><div class="page-title">📄 Document Analysis</div><div class="page-subtitle">Upload a file and let the agents extract insights</div></div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload PDF/DOCX/TXT",
        type=["pdf", "docx", "txt"]
    )

    if uploaded_file:

        files = {"file": uploaded_file}

        if st.button("Analyze Document"):

            with st.spinner("Analyzing document..."):

                response = requests.post(
                    f"{API_BASE}/upload",
                    files=files
                )

                st.json(response.json())

# ─── MEMORY PAGE ──────────────────────────────────────────────────────────────
elif _page == "Memory":

    st.markdown('<div class="page-header"><div class="page-title">📚 Research History</div><div class="page-subtitle">Browse and search all past research reports</div></div>', unsafe_allow_html=True)

    response = requests.get(f"{API_BASE}/memory")

    memories = response.json()

    if len(memories) == 0:

        st.info("No research history found.")

    else:

        search_term = st.text_input("🔍 Search Research History")

        st.write(f"Total Reports: {len(memories)}")

        for memory in reversed(memories):

            if (
                search_term
                and search_term.lower()
                not in memory["title"].lower()
            ):
                continue

            with st.expander(f"📄 {memory['title']}"):

                st.caption(f"Created: {memory.get('created_at', 'Unknown')}")

                st.markdown("---")

                st.markdown(memory.get("content", ""))

                st.markdown("---")

                pdf_url = f"{API_BASE}/pdf/{memory['id']}"

                st.link_button("📥 Download PDF Report", pdf_url)

                st.code(memory["id"], language="text")

# ─── ANALYTICS PAGE ───────────────────────────────────────────────────────────
elif _page == "Analytics":

    st.markdown('<div class="page-header"><div class="page-title">📊 Research Analytics</div><div class="page-subtitle">Usage, volume and topic insights</div></div>', unsafe_allow_html=True)

    response = requests.get(f"{API_BASE}/analytics")

    data = response.json()

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Research Queries", data["total_queries"])

    with col2:
        st.metric("Reports Generated", data["total_reports"])

    st.subheader("🔥 Most Researched Topics")

    import pandas as pd

    df = pd.DataFrame(data["top_topics"], columns=["Topic", "Count"])

    st.dataframe(df, use_container_width=True)

    if len(df) > 0:

        st.bar_chart(df.set_index("Topic"))

# ─── AGENTS PAGE ──────────────────────────────────────────────────────────────
elif _page == "Agents":

    st.markdown('<div class="page-header"><div class="page-title">🤖 Agent Registry</div><div class="page-subtitle">All registered AI agents and their capabilities</div></div>', unsafe_allow_html=True)

    response = requests.get(f"{API_BASE}/agents")

    agents = response.json()

    if len(agents) == 0:

        st.warning("No agents registered.")

    else:

        st.success(f"{len(agents)} Agents Active")

        for agent in agents:

            tools = agent.get("tools", [])
            tools_html = "".join(f'<span class="tool-badge">{t}</span>' for t in tools)

            st.markdown(f"""
            <div class="agent-card">
                <div class="agent-name">🤖 {agent.get('name')}</div>
                <div class="agent-role">{agent.get('role')}</div>
                <div class="agent-desc">{agent.get('description')}</div>
                {'<div class="agent-tools">' + tools_html + '</div>' if tools else ''}
            </div>
            """, unsafe_allow_html=True)