from __future__ import annotations

from textwrap import dedent
import streamlit as st

GLOBAL_LANG_KEY = "global_lang"
GLOBAL_BUDGET_KEY = "global_budget_k"


def init_global_state() -> None:
    if GLOBAL_LANG_KEY not in st.session_state:
        st.session_state[GLOBAL_LANG_KEY] = "English"
    if GLOBAL_BUDGET_KEY not in st.session_state:
        st.session_state[GLOBAL_BUDGET_KEY] = 550


def get_lang() -> str:
    init_global_state()
    return st.session_state[GLOBAL_LANG_KEY]


def get_locale() -> str:
    return "en" if get_lang() == "English" else "zh"


def get_budget_k() -> int:
    init_global_state()
    return int(st.session_state[GLOBAL_BUDGET_KEY])


def inject_base_css() -> None:
    st.markdown(
        dedent(
            """
            <style>
            .sidebar-title {
                font-size: 0.82rem;
                font-weight: 900;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                color: #475569;
                margin-top: 0.2rem;
                margin-bottom: 0.5rem;
            }

            .sidebar-note {
                font-size: 0.84rem;
                line-height: 1.55;
                color: #64748b;
                margin-top: -0.15rem;
                margin-bottom: 0.9rem;
            }

            /* 只控制 sidebar 内部 */
            section[data-testid="stSidebar"] .stRadio > div {
                gap: 0.5rem;
            }

            section[data-testid="stSidebar"] div[data-testid="stRadio"] label {
                background: #f8fafc !important;
                border: 1px solid #e5e7eb !important;
                border-radius: 12px !important;
                padding: 0.45rem 0.85rem !important;
                min-height: 42px !important;
                transition: all 0.18s ease;
            }

            section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
                background: #f1f5f9 !important;
                border-color: #cbd5e1 !important;
            }

            section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-checked="true"] {
                background: #eff6ff !important;
                border-color: #93c5fd !important;
                box-shadow: inset 0 0 0 1px #bfdbfe;
            }

            section[data-testid="stSidebar"] div[data-testid="stRadio"] label p {
                font-weight: 700 !important;
                color: #334155 !important;
                margin: 0 !important;
            }

            section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-checked="true"] p {
                color: #1d4ed8 !important;
            }

            section[data-testid="stSidebar"] div[data-testid="stRadio"] input[type="radio"] {
                accent-color: #2563eb;
            }

            /* 修复 slider label 被挤乱 */
            section[data-testid="stSidebar"] .stSlider label,
            section[data-testid="stSidebar"] .stRadio label,
            section[data-testid="stSidebar"] .stSelectbox label {
                font-weight: 700 !important;
                color: #334155 !important;
            }

            section[data-testid="stSidebar"] .stSlider label p,
            section[data-testid="stSidebar"] .stRadio label p,
            section[data-testid="stSidebar"] .stSelectbox label p {
                white-space: normal !important;
                word-break: keep-all !important;
                overflow-wrap: break-word !important;
                line-height: 1.35 !important;
            }

            section[data-testid="stSidebar"] div[data-baseweb="slider"] {
                padding-top: 0.2rem;
            }

            section[data-testid="stSidebar"] div[data-baseweb="slider"] > div {
                min-width: 0;
            }
            </style>
            """
        ),
        unsafe_allow_html=True,
    )


def render_global_sidebar() -> tuple[str, int]:
    init_global_state()

    current_lang = get_lang()
    is_en = current_lang == "English"

    st.sidebar.markdown(
        f'<div class="sidebar-title">{"Workspace Settings" if is_en else "全局设置"}</div>',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        f'<div class="sidebar-note">{"These settings are shared across all pages in this session." if is_en else "这些设置会在当前会话中的所有页面共享。"}'
        f"</div>",
        unsafe_allow_html=True,
    )

    lang = st.sidebar.radio(
        "Language / 语言",
        options=["English", "中文"],
        key=GLOBAL_LANG_KEY,
        horizontal=True,
    )

    is_en = lang == "English"
    budget_label = "Budget (USD, in $1,000s)" if is_en else "预算（美元，单位：千）"

    budget_k = st.sidebar.slider(
        budget_label,
        min_value=200,
        max_value=1500,
        step=10,
        key=GLOBAL_BUDGET_KEY,
    )

    st.sidebar.caption(
        f'{"Shared budget:" if is_en else "共享预算："} ${int(budget_k):,}k'
    )

    return lang, int(budget_k)