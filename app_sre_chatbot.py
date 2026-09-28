"""Streamlit chatbot UI for SRE Log Intelligence Agent."""

import sys
from pathlib import Path

import streamlit as st


# ============================================================================
# Add SRE agent to Python path
# ============================================================================

SRE_AGENT_PATH = (
    Path(__file__).parent
    / "sre-agent"
    / "app"
)

sys.path.insert(0, str(SRE_AGENT_PATH))

from sre_agent import SRELogAgent


# ============================================================================
# Page configuration
# ============================================================================

st.set_page_config(
    page_title="SRE Log Intelligence",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================================
# CSS
# ============================================================================

CSS = """
<style>

    :root {
        --bg: #ffffff;
        --bg-subtle: #f8fafc;
        --card: #ffffff;
        --border: #e2e8f0;
        --text: #0f172a;
        --text-muted: #64748b;
        --accent: #2563eb;
        --accent-dark: #1d4ed8;
    }

    /* ================================================================== */
    /* Main application                                                   */
    /* ================================================================== */

    [data-testid="stAppViewContainer"] {
        background-color: var(--bg);
    }

    [data-testid="stMain"] {
        padding-bottom: 100px;
    }

    /* Hide Streamlit chrome */
    header[data-testid="stHeader"],
    #MainMenu,
    footer,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    .stDeployButton {
        display: none !important;
    }


    /* ================================================================== */
    /* Header                                                             */
    /* ================================================================== */

    .app-subtitle {
        color: var(--text-muted);
        font-size: 14px;
        line-height: 1.5;
        margin-top: -8px;
        margin-bottom: 10px;
    }

    .status-pill {
        display: inline-block;
        padding: 5px 11px;
        border-radius: 999px;
        background-color: #f0fdf4;
        color: #15803d;
        border: 1px solid #bbf7d0;
        font-size: 12px;
        font-weight: 600;
    }


    /* ================================================================== */
    /* Chat area                                                          */
    /* ================================================================== */

    .chat-wrapper {
        max-width: 900px;
        margin: 0 auto;
    }

    .empty-state {
        text-align: center;
        padding: 55px 20px 40px 20px;
    }

    .empty-icon {
        font-size: 44px;
        margin-bottom: 8px;
    }

    .empty-description {
        color: var(--text-muted);
        font-size: 14px;
        line-height: 1.6;
        max-width: 650px;
        margin: 0 auto;
    }


    /* ================================================================== */
    /* Chat messages                                                      */
    /* ================================================================== */

    [data-testid="stChatMessage"] {
        margin-bottom: 12px;
    }

    [data-testid="stChatMessageContent"] {
        font-size: 14px;
        line-height: 1.6;
    }


    /* ================================================================== */
    /* Evidence                                                           */
    /* ================================================================== */

    .log-evidence {
        background-color: #f8fafc;
        border: 1px solid var(--border);
        border-left: 3px solid var(--accent);
        padding: 11px 13px;
        border-radius: 7px;
        font-family: "Courier New", monospace;
        font-size: 12px;
        line-height: 1.5;
        overflow-x: auto;
        white-space: pre-wrap;
        word-break: break-word;
        margin: 5px 0 12px 0;
    }


    /* ================================================================== */
    /* Input area                                                         */
    /* ================================================================== */

    .input-label {
        font-size: 14px;
        font-weight: 600;
        color: var(--text);
        margin-bottom: 6px;
    }

    [data-testid="stTextArea"] textarea {
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        padding: 12px !important;
        font-size: 14px !important;
        background-color: white !important;
        resize: none !important;
    }

    [data-testid="stTextArea"] textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 1px var(--accent) !important;
    }


    /* ================================================================== */
    /* Buttons                                                            */
    /* ================================================================== */

    .stButton button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        min-height: 40px !important;
    }

    .send-button button {
        background-color: var(--accent) !important;
        color: white !important;
        border: none !important;
    }

    .send-button button:hover {
        background-color: var(--accent-dark) !important;
    }


    /* ================================================================== */
    /* Sidebar                                                            */
    /* ================================================================== */

    section[data-testid="stSidebar"] {
        background-color: var(--bg-subtle);
        border-right: 1px solid var(--border);
    }

    section[data-testid="stSidebar"] h2 {
        color: var(--text);
    }

    .sidebar-section {
        color: var(--text-muted);
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 8px;
    }


    /* ================================================================== */
    /* Divider                                                            */
    /* ================================================================== */

    hr {
        border-color: var(--border) !important;
    }

</style>
"""

st.markdown(
    CSS,
    unsafe_allow_html=True,
)


# ============================================================================
# Session state
# ============================================================================

if "agent" not in st.session_state:

    with st.spinner("Initializing SRE Log Agent..."):

        st.session_state.agent = SRELogAgent()

        # Build/update the local Chroma index.
        st.session_state.agent.index_logs()


if "messages" not in st.session_state:
    st.session_state.messages = []


if "top_k" not in st.session_state:
    st.session_state.top_k = 5


# ============================================================================
# Helper functions
# ============================================================================

def process_question(question: str) -> None:
    """Process a question and add user/assistant messages to history."""

    question = question.strip()

    if not question:
        return

    # ------------------------------------------------------------------------
    # Add user message
    # ------------------------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )   

    # ------------------------------------------------------------------------
    # Run SRE agent
    # ------------------------------------------------------------------------

    with st.spinner("🔎 Analyzing operational logs..."):

        result = st.session_state.agent.answer_with_evidence(
            question,
            top_k=st.session_state.top_k,
        )

    # ------------------------------------------------------------------------
    # Add assistant response
    # ------------------------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["answer"],
            "evidence": result.get(
                "evidence",
                [],
            ),
        }
    )


def submit_question() -> None:
    """Process the current question and clear the input box."""

    question = st.session_state.get(
        "chat_input",
        "",
    ).strip()

    if not question:
        return

    process_question(question)

    # IMPORTANT:
    # This is executed from the button callback, before the widget
    # is instantiated again during the next Streamlit run.
    st.session_state.chat_input = ""


def submit_example(example: str) -> None:
    """Process a predefined example question."""

    process_question(example)


def clear_conversation() -> None:
    """Clear the conversation history."""

    st.session_state.messages = []


# ============================================================================
# Header
# ============================================================================

header_col1, header_col2 = st.columns(
    [5, 1],
    vertical_alignment="center",
)


with header_col1:

    st.title(
        "🔍 SRE Log Intelligence"
    )

    st.markdown(
        """
        <div class="app-subtitle">
            Query operational logs using natural language.
            Retrieve relevant evidence and investigate incidents
            with an AI-powered SRE log assistant.
        </div>
        """,
        unsafe_allow_html=True,
    )


with header_col2:

    st.markdown(
        """
        <div style="
            text-align: right;
            padding-top: 12px;
        ">
            <span class="status-pill">
                ● Agent Ready
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.divider()


# ============================================================================
# Main chat area
# ============================================================================

st.markdown(
    '<div class="chat-wrapper">',
    unsafe_allow_html=True,
)


# ============================================================================
# Empty state
# ============================================================================

if not st.session_state.messages:

    st.markdown(
        """
        <div class="empty-state">
            <div class="empty-icon">
                🔎
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Native Streamlit rendering - avoids HTML being displayed as text.
    st.markdown(
        "### 🔎 Investigate your operational logs"
    )

    st.markdown(
        """
        <div class="empty-description">
            Ask about deployments, outages, pods, databases,
            readiness probes, memory issues, rollbacks,
            or other operational incidents.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================================
# Conversation
# ============================================================================

for message in st.session_state.messages:

    # ------------------------------------------------------------------------
    # User message
    # ------------------------------------------------------------------------

    if message["role"] == "user":

        with st.chat_message(
            "user",
            avatar="👤",
        ):

            st.markdown(
                message["content"]
            )

    # ------------------------------------------------------------------------
    # Assistant message
    # ------------------------------------------------------------------------

    else:

        with st.chat_message(
            "assistant",
            avatar="🔍",
        ):

            st.markdown(
                message["content"]
            )

            evidence = message.get(
                "evidence",
                [],
            )

            if evidence:

                with st.expander(
                    f"📋 Retrieved Evidence · {len(evidence)} logs",
                    expanded=False,
                ):

                    for index, log in enumerate(
                        evidence,
                        start=1,
                    ):

                        st.markdown(
                            f"**Log {index}**"
                        )

                        st.markdown(
                            (
                                '<div class="log-evidence">'
                                f"{log}"
                                "</div>"
                            ),
                            unsafe_allow_html=True,
                        )


st.markdown(
    "</div>",
    unsafe_allow_html=True,
)


# ============================================================================
# Input area
# ============================================================================

st.divider()

st.markdown(
    '<div class="input-label">Ask a question</div>',
    unsafe_allow_html=True,
)


input_col, button_col = st.columns(
    [6, 1],
    vertical_alignment="bottom",
)


# ============================================================================
# Question input
# ============================================================================

with input_col:

    st.text_area(
        "Question",
        placeholder=(
            "e.g. Why did the last deployment fail?"
        ),
        height=70,
        key="chat_input",
        label_visibility="collapsed",
    )


# ============================================================================
# Send button
# ============================================================================

with button_col:

    st.markdown(
        '<div class="send-button">',
        unsafe_allow_html=True,
    )

    st.button(
        "📤 Send",
        key="send_button",
        use_container_width=True,
        type="primary",
        on_click=submit_question,
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# ============================================================================
# Sidebar
# ============================================================================

with st.sidebar:

    st.markdown(
        "## ⚙️ Settings"
    )


    # ------------------------------------------------------------------------
    # Retrieval configuration
    # ------------------------------------------------------------------------

    st.session_state.top_k = st.slider(
        "Retrieved logs per query",
        min_value=1,
        max_value=10,
        value=st.session_state.top_k,
        help=(
            "Number of relevant logs retrieved for each question."
        ),
    )


    st.divider()


    # ------------------------------------------------------------------------
    # Example queries
    # ------------------------------------------------------------------------

    st.markdown(
        '<div class="sidebar-section">Example Queries</div>',
        unsafe_allow_html=True,
    )

    examples = [
        "How to connect to the database?",
        "Why did the last deployment fail?",
        "Which pod exceeded its memory limit?",
        "What caused the readiness probe to fail?",
        "Was there a rollback recently?",
    ]

    for index, example in enumerate(examples):

        st.button(
            f"📌 {example}",
            key=f"example_{index}",
            use_container_width=True,
            on_click=submit_example,
            args=(example,),
        )


    st.divider()


    # ------------------------------------------------------------------------
    # Clear conversation
    # ------------------------------------------------------------------------

    st.button(
        "🗑️ Clear Conversation",
        key="clear_conversation",
        use_container_width=True,
        on_click=clear_conversation,
    )


    st.divider()


    # ------------------------------------------------------------------------
    # Footer
    # ------------------------------------------------------------------------

    st.caption(
        "SRE Log Agent v1.0\n\n"
        "Local RAG · Chroma · Sentence Transformers"
    )
