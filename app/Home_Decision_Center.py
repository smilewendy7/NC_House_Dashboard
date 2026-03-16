from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional
from textwrap import dedent

import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.append(str(APP_DIR))

from shared_ui import (
    inject_base_css,
    render_global_sidebar,
    get_lang,
    get_budget_k,
)

st.set_page_config(
    page_title="NC Housing Decision Center",
    page_icon="🏠",
    layout="wide",
)

MONTHLY_PATH = Path("data/analytics/monthly_metrics.csv")
PRICE_BAND_PATH = Path("data/analytics/price_ranges_enriched.csv")


# =========================================================
# CSS
# =========================================================
def inject_css() -> None:
    st.markdown(
        dedent(
            """
            <style>
            .main {
                background: #f6f8fb;
            }

            .block-container {
                padding-top: 1.1rem;
                padding-bottom: 2.4rem;
                padding-left: 2rem;
                padding-right: 2rem;
                max-width: 1420px;
            }

            section[data-testid="stSidebar"] {
                background: linear-gradient(180deg, #fcfdff 0%, #ffffff 100%);
                border-right: 1px solid #e7edf5;
            }

            .hero {
                position: relative;
                overflow: hidden;
                background:
                    radial-gradient(circle at top right, rgba(96,165,250,0.16), transparent 24%),
                    radial-gradient(circle at bottom left, rgba(56,189,248,0.10), transparent 22%),
                    linear-gradient(135deg, #08111f 0%, #0f172a 38%, #172554 100%);
                border-radius: 28px;
                padding: 1.55rem 1.6rem 1.45rem 1.6rem;
                border: 1px solid rgba(255,255,255,0.08);
                box-shadow: 0 18px 48px rgba(15, 23, 42, 0.16);
                margin-bottom: 1rem;
                color: white;
            }

            .hero-chip {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 0.38rem 0.74rem;
                border-radius: 999px;
                background: rgba(255,255,255,0.12);
                color: rgba(255,255,255,0.95);
                font-size: 0.76rem;
                font-weight: 800;
                letter-spacing: 0.04em;
                margin-bottom: 0.85rem;
                text-transform: uppercase;
            }

            .hero-title {
                font-size: 2.05rem;
                font-weight: 900;
                line-height: 1.08;
                letter-spacing: -0.02em;
                margin-bottom: 0.34rem;
            }

            .hero-subtitle {
                font-size: 0.98rem;
                line-height: 1.66;
                color: rgba(255,255,255,0.88);
                max-width: 1060px;
            }

            .panel-card,
            .signal-hero,
            .summary-card,
            .insight-card,
            .strategy-card,
            .memo-card {
                background: #ffffff;
                border: 1px solid #e6ebf2;
                border-radius: 22px;
                box-shadow: 0 10px 28px rgba(15, 23, 42, 0.05);
                min-width: 0;
                overflow: hidden;
            }

            .panel-card {
                padding: 1.12rem 1.12rem 0.92rem 1.12rem;
                margin-bottom: 1rem;
                background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
            }

            .panel-title {
                font-size: 1.02rem;
                font-weight: 900;
                color: #0f172a;
                margin-bottom: 0.24rem;
                letter-spacing: -0.01em;
            }

            .panel-sub {
                font-size: 0.91rem;
                line-height: 1.58;
                color: #64748b;
                margin-bottom: 0.1rem;
            }

            .mini-note {
                margin-top: 0.88rem;
                padding: 0.84rem 0.9rem;
                border-radius: 16px;
                background: #f8fafc;
                border: 1px dashed #cbd5e1;
                color: #475569;
                font-size: 0.88rem;
                line-height: 1.55;
            }

            .section-title {
                font-size: 1.08rem;
                font-weight: 900;
                color: #0f172a;
                margin-bottom: 0.78rem;
                letter-spacing: -0.01em;
            }

            .signal-hero {
                padding: 1.22rem 1.24rem 1.18rem 1.24rem;
                margin-bottom: 1rem;
                background: linear-gradient(135deg, #ffffff 0%, #f8fbff 100%);
                border: 1px solid #dbeafe;
                box-shadow: 0 10px 28px rgba(29,78,216,0.06);
            }

            .signal-kicker {
                color: #64748b;
                font-size: 0.76rem;
                font-weight: 800;
                margin-bottom: 0.42rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }

            .signal-main {
                font-size: 1.5rem;
                font-weight: 900;
                color: #0f172a;
                line-height: 1.16;
                margin-bottom: 0.56rem;
                letter-spacing: -0.02em;
            }

            .signal-sub {
                font-size: 0.95rem;
                color: #475569;
                line-height: 1.68;
                margin-top: 0.76rem;
            }

            .badge {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 0.42rem 0.8rem;
                border-radius: 999px;
                font-size: 0.82rem;
                font-weight: 800;
                margin-right: 0.44rem;
                margin-top: 0.35rem;
                border: 1px solid transparent;
                white-space: normal;
                flex-wrap: wrap;
                max-width: 100%;
                overflow-wrap: anywhere;
                word-break: break-word;
                box-sizing: border-box;
            }

            .badge-green {
                background: #dcfce7;
                color: #166534;
                border-color: #bbf7d0;
            }

            .badge-red {
                background: #fee2e2;
                color: #991b1b;
                border-color: #fecaca;
            }

            .badge-yellow {
                background: #fef3c7;
                color: #92400e;
                border-color: #fde68a;
            }

            .badge-blue {
                background: #dbeafe;
                color: #1d4ed8;
                border-color: #bfdbfe;
            }

            .metric-grid {
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 12px;
                margin-top: 0.18rem;
                margin-bottom: 1rem;
            }

            .metric-box {
                background: #ffffff;
                border: 1px solid #e6ebf2;
                border-radius: 18px;
                padding: 0.94rem 1rem;
                box-shadow: 0 8px 22px rgba(15, 23, 42, 0.04);
                min-width: 0;
                overflow: hidden;
            }

            .metric-label {
                color: #64748b;
                font-size: 0.74rem;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 0.04em;
                margin-bottom: 0.26rem;
            }

            .metric-value {
                font-size: 1.12rem;
                font-weight: 900;
                color: #0f172a;
                line-height: 1.2;
                letter-spacing: -0.01em;
                min-width: 0;
                overflow-wrap: anywhere;
                word-break: break-word;
            }

            .summary-card {
                padding: 1rem 1rem;
                min-height: 136px;
                margin-bottom: 0.82rem;
                background: linear-gradient(180deg, #ffffff 0%, #fcfdff 100%);
            }

            .summary-label {
                font-size: 0.73rem;
                font-weight: 800;
                color: #64748b;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 0.28rem;
            }

            .summary-value {
                font-size: 1.13rem;
                font-weight: 900;
                color: #0f172a;
                line-height: 1.22;
                margin-bottom: 0.24rem;
                min-width: 0;
                overflow-wrap: anywhere;
                word-break: break-word;
            }

            .summary-sub {
                font-size: 0.89rem;
                color: #64748b;
                line-height: 1.55;
                min-width: 0;
                overflow-wrap: anywhere;
                word-break: break-word;
            }

            .insight-card,
            .strategy-card,
            .memo-card {
                padding: 1.12rem 1.14rem;
                margin-bottom: 1rem;
            }

            .card-kicker {
                color: #64748b;
                font-size: 0.73rem;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 0.33rem;
            }

            .card-title {
                font-size: 1rem;
                font-weight: 900;
                color: #0f172a;
                margin-bottom: 0.56rem;
                letter-spacing: -0.01em;
                min-width: 0;
                overflow-wrap: anywhere;
                word-break: break-word;
            }

            .card-body {
                color: #475569;
                font-size: 0.95rem;
                line-height: 1.68;
                min-width: 0;
                overflow-wrap: anywhere;
                word-break: break-word;
            }

            .action-list {
                list-style: none;
                margin: 0.36rem 0 0 0;
                padding-left: 0;
            }

            .action-list li {
                position: relative;
                padding-left: 1.9rem;
                margin-bottom: 0.66rem;
                color: #0f172a;
                line-height: 1.62;
            }

            .action-list li::before {
                content: "✓";
                position: absolute;
                left: 0;
                top: 0.08rem;
                width: 1.18rem;
                height: 1.18rem;
                border-radius: 999px;
                background: #dcfce7;
                color: #15803d;
                border: 1px solid #86efac;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 0.78rem;
                font-weight: 900;
            }

            .memo-quote {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
                padding: 0.95rem 1rem;
                color: #0f172a;
                font-size: 0.95rem;
                line-height: 1.74;
                white-space: pre-wrap;
            }

            .copy-tip {
                color: #64748b;
                font-size: 0.86rem;
                margin-top: 0.6rem;
                line-height: 1.5;
            }

            .footer-line {
                color: #94a3b8;
                font-size: 0.84rem;
                margin-top: 0.18rem;
            }

            div[data-baseweb="select"] > div {
                border-radius: 12px !important;
                border: 1px solid #e5e7eb !important;
                background-color: #f8fafc !important;
            }

            div[data-testid="stRadio"] > div {
                gap: 0.5rem;
            }

            div[data-testid="stRadio"] label {
                background: #f8fafc;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 0.45rem 0.85rem;
            }

            div.stButton > button,
            div[data-testid="stFormSubmitButton"] > button {
                border-radius: 14px;
                font-weight: 800;
                padding: 0.78rem 1rem;
                border: 1px solid #0f172a;
                background: #ffffff;
                transition: all 0.18s ease;
                width: 100%;
            }

            div.stButton > button:hover,
            div[data-testid="stFormSubmitButton"] > button:hover {
                background: #0f172a;
                color: white;
                border-color: #0f172a;
            }

            label, .stSelectbox label, .stSlider label, .stRadio label {
                font-weight: 700 !important;
                color: #334155 !important;
            }

            @media (max-width: 1240px) {
                .metric-grid {
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                }
            }
            </style>
            """
        ),
        unsafe_allow_html=True,
    )


# =========================================================
# TEXT
# =========================================================
TEXT = {
    "English": {
        "hero_chip": "Decision Advisory",
        "title": "NC Housing Decision Center",
        "caption": "Turn current market analytics into a user-friendly decision, timing, and negotiation plan tailored to the person making the move.",
        "profile": "Decision Profile",
        "profile_note": "This page is built for action, not just market reading. It turns the latest statewide and price-band data into a recommendation users can actually follow.",
        "mini_tip": "Best use: buyer consultation, agent prep, investor screening, and pre-offer strategy discussions.",
        "identity": "Identity",
        "budget": "Budget (USD, in $1,000s)",
        "shared_budget": "Shared Budget",
        "timeline": "Timeline",
        "goal": "Primary Goal",
        "down_payment": "Down Payment",
        "rate": "Rate Assumption (%)",
        "risk": "Risk Preference",
        "submit_buyer": "Generate Buyer Advisory",
        "submit_agent": "Generate Agent Advisory",
        "submit_investor": "Generate Investor Advisory",
        "fill_form": "Fill the form and click the advisory button.",
        "missing_data": (
            "Missing analytics files. Please run:\n\n"
            "`python run_full_pipeline.py --workers 4`\n\n"
            "The analytics outputs need to exist first."
        ),
        "latest_month": "Latest Data Month",
        "advisory_section": "Decision Output",
        "decision_title_buyer": "Current Buyer Recommendation",
        "decision_title_agent": "Current Agent Recommendation",
        "decision_title_investor": "Current Investor Recommendation",
        "market_position": "Market Position",
        "budget_position": "Budget Band Position",
        "readiness": "Readiness",
        "leverage": "Negotiation Leverage",
        "offer_posture": "Offer Posture",
        "timing": "Timing",
        "next_steps": "Recommended Next Steps",
        "client_memo": "Client-Ready Summary",
        "memo_title": "Copyable Client Language",
        "profile_summary": "Decision Profile",
        "target_budget": "Target Budget",
        "matched_band": "Matched Price Band",
        "state_inventory": "Statewide Inventory",
        "band_inventory": "Band Inventory",
        "band_score": "Band Leverage Score",
        "competition": "Competition",
        "buyer_friendly": "More Buyer Room",
        "balanced": "Balanced",
        "competitive": "More Competitive",
        "readiness_ready": "Ready",
        "readiness_almost": "Nearly Ready",
        "readiness_build": "Needs Preparation",
        "leverage_high": "Higher",
        "leverage_mid": "Moderate",
        "leverage_low": "Limited",
        "offer_aggressive": "Can negotiate assertively",
        "offer_balanced": "Negotiate selectively",
        "offer_competitive": "Keep offer structure strong",
        "timing_watch": "Watch closely over the next 1–2 reports",
        "timing_fast": "Be ready to move quickly on stronger homes",
        "timing_selective": "Use selective action rather than broad urgency",
        "risk_low": "Conservative",
        "risk_mid": "Balanced",
        "risk_high": "Opportunistic",
        "not_mapped": "Could not map budget to a price band for the latest month.",
        "footer_prefix": "Generated from current statewide and price-band analytics.",
        "buyer_recommend_now": "Actively pursue opportunities in this segment",
        "buyer_recommend_selective": "Stay selective and move on the right homes",
        "buyer_recommend_prepare": "Prepare carefully before moving aggressively",
        "agent_recommend_now": "Guide the client toward active comparison and negotiation",
        "agent_recommend_selective": "Keep the client selective and ready for the right listing",
        "agent_recommend_prepare": "Strengthen client readiness before encouraging aggressive action",
        "investor_recommend_now": "Screen this segment more actively for favorable entries",
        "investor_recommend_selective": "Underwrite selectively and avoid broad assumptions",
        "investor_recommend_prepare": "Improve assumptions and discipline before expanding activity",
        "reason_title": "Why this recommendation",
        "strategy_title": "Suggested Action Plan",
        "copy_tip": "This section is intentionally written so an agent can copy it directly into a client message or consultation recap.",
        "agent_client_section": "Client Communication",
        "button_copy_label": "Copyable summary below",
        "signal_good": "More favorable setup",
        "signal_mid": "Mixed / workable setup",
        "signal_hot": "Stay disciplined",
    },
    "中文": {
        "hero_chip": "决策建议页",
        "title": "北卡房产决策中心",
        "caption": "把当前市场分析结果，转成真正用户需要的决策结论、时机判断和谈判行动建议。",
        "profile": "决策画像",
        "profile_note": "这个页面重点不是重复展示市场结构，而是把最新全州与价格带数据转成用户下一步该怎么做。",
        "mini_tip": "最佳用途：买家咨询、经纪人准备、投资者初筛、出价前策略讨论。",
        "identity": "身份",
        "budget": "预算（美元，单位：千）",
        "shared_budget": "共享预算",
        "timeline": "时间窗口",
        "goal": "主要目标",
        "down_payment": "首付比例",
        "rate": "利率假设 (%)",
        "risk": "风险偏好",
        "submit_buyer": "生成买家建议",
        "submit_agent": "生成经纪人建议",
        "submit_investor": "生成投资建议",
        "fill_form": "请填写表单，然后点击生成建议。",
        "missing_data": (
            "缺少 analytics 文件。请先运行：\n\n"
            "`python run_full_pipeline.py --workers 4`\n\n"
            "需要先生成 analytics 输出文件。"
        ),
        "latest_month": "最新数据月份",
        "advisory_section": "决策输出",
        "decision_title_buyer": "当前买家建议",
        "decision_title_agent": "当前经纪人建议",
        "decision_title_investor": "当前投资建议",
        "market_position": "市场位置",
        "budget_position": "预算带位置",
        "readiness": "准备度",
        "leverage": "谈判空间",
        "offer_posture": "出价姿态",
        "timing": "时机判断",
        "next_steps": "建议下一步",
        "client_memo": "客户可用总结",
        "memo_title": "可直接复制给客户的话术",
        "profile_summary": "决策画像",
        "target_budget": "目标预算",
        "matched_band": "匹配价格带",
        "state_inventory": "全州库存月数",
        "band_inventory": "该价格带库存月数",
        "band_score": "该带谈判分",
        "competition": "竞争强度",
        "buyer_friendly": "买方空间较大",
        "balanced": "相对平衡",
        "competitive": "竞争偏强",
        "readiness_ready": "准备度较高",
        "readiness_almost": "接近可出手",
        "readiness_build": "还需补强准备",
        "leverage_high": "较大",
        "leverage_mid": "中等",
        "leverage_low": "有限",
        "offer_aggressive": "可更主动谈判",
        "offer_balanced": "选择性谈判",
        "offer_competitive": "保持较强报价结构",
        "timing_watch": "建议继续观察未来 1–2 期报告",
        "timing_fast": "优质房源出现时要准备更快推进",
        "timing_selective": "不需要全面着急，但要有选择地行动",
        "risk_low": "保守型",
        "risk_mid": "平衡型",
        "risk_high": "机会型",
        "not_mapped": "无法把该预算匹配到最新月份的价格区间。",
        "footer_prefix": "基于当前全州与价格带 analytics 自动生成。",
        "buyer_recommend_now": "可以主动寻找并推进这一预算段的机会",
        "buyer_recommend_selective": "保持选择性，遇到合适房源再快速推进",
        "buyer_recommend_prepare": "先把准备工作做扎实，再更积极出手",
        "agent_recommend_now": "可引导客户主动比较并争取更好的谈判条件",
        "agent_recommend_selective": "保持客户选择性，并为合适房源提前准备",
        "agent_recommend_prepare": "先补强客户准备度，再推动更积极行动",
        "investor_recommend_now": "可更积极筛选这一价格带的入场机会",
        "investor_recommend_selective": "选择性测算，不要对整体市场做过度泛化",
        "investor_recommend_prepare": "先把假设和纪律收紧，再扩大动作",
        "reason_title": "为什么这样判断",
        "strategy_title": "建议行动方案",
        "copy_tip": "这段文案刻意写成可以直接发给客户或放进沟通纪要里的表达。",
        "agent_client_section": "客户沟通输出",
        "button_copy_label": "下方内容可直接复制",
        "signal_good": "相对更有利",
        "signal_mid": "信号中性 / 可操作",
        "signal_hot": "保持纪律",
    },
}

OPTIONS = {
    "English": {
        "identity": ["Buyer", "Agent", "Investor"],
        "timeline": ["30 days", "3 months", "6 months", "Not urgent"],
        "goal": ["Save money", "Higher success rate", "Buy quickly", "Lower risk"],
        "down_payment": ["5%", "10%", "20%", "30%"],
        "risk": ["Conservative", "Balanced", "Opportunistic"],
    },
    "中文": {
        "identity": ["买家", "经纪人", "投资者"],
        "timeline": ["30天内", "3个月内", "6个月内", "不着急"],
        "goal": ["省钱", "提高成功率", "更快买到", "降低风险"],
        "down_payment": ["5%", "10%", "20%", "30%"],
        "risk": ["保守型", "平衡型", "机会型"],
    },
}


# =========================================================
# HELPERS
# =========================================================
def fmt_money(x: float) -> str:
    if pd.isna(x):
        return "N/A"
    return f"${x:,.0f}"


def fmt_num(x: float, digits: int = 1) -> str:
    if pd.isna(x):
        return "N/A"
    return f"{x:.{digits}f}"


def html_block(html: str) -> None:
    st.markdown(html, unsafe_allow_html=True)


@st.cache_data(ttl=60)
def load_monthly_metrics(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()

    df = pd.read_csv(path)

    if "report_month" in df.columns:
        df["report_month"] = df["report_month"].astype(str)
        df = df.sort_values("report_month")

    numeric_cols = [
        "listings",
        "sales",
        "median_price",
        "months_inventory",
        "yoy_listings_pct",
        "yoy_sales_pct",
        "yoy_price_pct",
        "yoy_inventory_pct",
        "mom_listings_pct",
        "mom_sales_pct",
        "mom_price_pct",
        "mom_inventory_pct",
    ]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    return df


@st.cache_data(ttl=60)
def load_price_bands(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()

    df = pd.read_csv(path)

    if "report_month" in df.columns:
        df["report_month"] = df["report_month"].astype(str)

    numeric_cols = [
        "range_min",
        "range_max",
        "range_rank",
        "listings",
        "sales_prev_12mo",
        "months_inventory",
        "buyer_leverage_score",
    ]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    sort_cols = [c for c in ["report_month", "range_rank", "range_min"] if c in df.columns]
    if sort_cols:
        df = df.sort_values(sort_cols, na_position="last")

    return df


def trend_label(series: pd.Series) -> str:
    s = pd.to_numeric(series, errors="coerce").dropna()
    if len(s) < 2:
        return "Stable"

    recent = s.tail(3).reset_index(drop=True)
    if len(recent) < 2:
        return "Stable"

    delta = recent.iloc[-1] - recent.iloc[0]
    if delta > 0:
        return "Rising"
    if delta < 0:
        return "Falling"
    return "Stable"


def market_condition(inventory_trend: str, sales_trend: str) -> str:
    if inventory_trend == "Rising" and sales_trend == "Falling":
        return "Buyer-Leaning"
    if inventory_trend == "Falling" and sales_trend == "Rising":
        return "Seller-Leaning"
    return "Balanced"


def pick_budget_band(latest_band_df: pd.DataFrame, budget_usd: float) -> Optional[pd.Series]:
    if latest_band_df.empty:
        return None

    numeric = latest_band_df.copy()
    for c in ["range_min", "range_max", "range_rank"]:
        if c in numeric.columns:
            numeric[c] = pd.to_numeric(numeric[c], errors="coerce")

    in_range = numeric[
        numeric["range_min"].notna()
        & (numeric["range_min"] <= budget_usd)
        & (numeric["range_max"].isna() | (numeric["range_max"] >= budget_usd))
    ]
    if not in_range.empty:
        return in_range.sort_values(["range_rank", "range_min"], na_position="last").iloc[0]

    numeric = numeric.copy()
    midpoint = numeric["range_min"].fillna(0)
    if "range_max" in numeric.columns:
        midpoint = (
            numeric["range_min"].fillna(0) + numeric["range_max"].fillna(numeric["range_min"])
        ) / 2
    numeric["dist"] = (midpoint - budget_usd).abs()

    numeric = numeric.sort_values(["dist", "range_rank", "range_min"], na_position="last")
    if not numeric.empty:
        return numeric.iloc[0]

    return None


def inventory_position(inv: float, t: dict) -> str:
    if pd.isna(inv):
        return t["balanced"]
    if inv < 4:
        return t["competitive"]
    if inv <= 6:
        return t["balanced"]
    return t["buyer_friendly"]


def leverage_label(score: float, inv: float, t: dict) -> str:
    if pd.notna(score):
        if score >= 70:
            return t["leverage_high"]
        if score >= 40:
            return t["leverage_mid"]
        return t["leverage_low"]

    if pd.isna(inv):
        return t["leverage_mid"]
    if inv > 6:
        return t["leverage_high"]
    if inv >= 4:
        return t["leverage_mid"]
    return t["leverage_low"]


def readiness_label(down_payment: str, timeline: str, rate_assumption: float, t: dict) -> str:
    score = 0

    if down_payment in {"20%", "30%"}:
        score += 2
    elif down_payment == "10%":
        score += 1

    if timeline in {"30 days", "30天内", "3 months", "3个月内"}:
        score += 2
    elif timeline in {"6 months", "6个月内"}:
        score += 1

    if rate_assumption <= 6.5:
        score += 1

    if score >= 4:
        return t["readiness_ready"]
    if score >= 2:
        return t["readiness_almost"]
    return t["readiness_build"]


def offer_posture(leverage: str, risk_pref: str, t: dict) -> str:
    conservative = risk_pref in {"Conservative", "保守型"}
    opportunistic = risk_pref in {"Opportunistic", "机会型"}

    if leverage == t["leverage_high"]:
        return t["offer_aggressive"] if opportunistic or not conservative else t["offer_balanced"]
    if leverage == t["leverage_low"]:
        return t["offer_competitive"]
    return t["offer_balanced"]


def timing_suggestion(inv_trend: str, sales_trend: str, timeline: str, t: dict) -> str:
    if inv_trend == "Rising" and sales_trend == "Falling":
        return t["timing_watch"]
    if inv_trend == "Falling" and sales_trend == "Rising":
        return t["timing_fast"]
    if timeline in {"30 days", "30天内"}:
        return t["timing_fast"]
    return t["timing_selective"]


def identity_key(identity: str) -> str:
    if identity in {"Buyer", "买家"}:
        return "buyer"
    if identity in {"Agent", "经纪人"}:
        return "agent"
    return "investor"


def main_recommendation(identity: str, leverage: str, readiness: str, timeline: str, t: dict) -> str:
    who = identity_key(identity)
    urgent = timeline in {"30 days", "30天内"}

    if who == "buyer":
        if leverage == t["leverage_high"] and readiness != t["readiness_build"]:
            return t["buyer_recommend_now"]
        if urgent or readiness == t["readiness_ready"]:
            return t["buyer_recommend_selective"]
        return t["buyer_recommend_prepare"]

    if who == "agent":
        if leverage == t["leverage_high"] and readiness != t["readiness_build"]:
            return t["agent_recommend_now"]
        if urgent or readiness == t["readiness_ready"]:
            return t["agent_recommend_selective"]
        return t["agent_recommend_prepare"]

    if leverage == t["leverage_high"] and readiness != t["readiness_build"]:
        return t["investor_recommend_now"]
    if urgent or readiness == t["readiness_ready"]:
        return t["investor_recommend_selective"]
    return t["investor_recommend_prepare"]


def decision_title(identity: str, t: dict) -> str:
    who = identity_key(identity)
    if who == "buyer":
        return t["decision_title_buyer"]
    if who == "agent":
        return t["decision_title_agent"]
    return t["decision_title_investor"]


def submit_label(identity: str, t: dict) -> str:
    who = identity_key(identity)
    if who == "buyer":
        return t["submit_buyer"]
    if who == "agent":
        return t["submit_agent"]
    return t["submit_investor"]


def signal_meta(leverage: str, t: dict) -> tuple[str, str, str]:
    if leverage == t["leverage_high"]:
        return "🟢", t["signal_good"], "badge-green"
    if leverage == t["leverage_mid"]:
        return "🟡", t["signal_mid"], "badge-yellow"
    return "🔴", t["signal_hot"], "badge-red"


def build_reason_lines(
    market_pos: str,
    budget_pos: str,
    leverage: str,
    readiness: str,
    timing_msg: str,
    identity: str,
    lang: str,
) -> list[str]:
    who = identity_key(identity)

    if lang == "English":
        if who == "agent":
            return [
                f"The broader market currently reads as **{market_pos}**.",
                f"The client’s matched budget band appears **{budget_pos.lower()}**.",
                f"Client leverage is **{leverage.lower()}**, and readiness is **{readiness.lower()}**.",
                f"From a timing standpoint: **{timing_msg}**.",
            ]
        if who == "investor":
            return [
                f"The broader market currently reads as **{market_pos}**.",
                f"This matched budget band appears **{budget_pos.lower()}**.",
                f"Negotiation leverage looks **{leverage.lower()}**, while current readiness is **{readiness.lower()}**.",
                f"From a timing standpoint: **{timing_msg}**.",
            ]
        return [
            f"The broader market currently reads as **{market_pos}**.",
            f"Your matched budget band appears **{budget_pos.lower()}**.",
            f"Your negotiation leverage is **{leverage.lower()}**, and readiness is **{readiness.lower()}**.",
            f"From a timing standpoint: **{timing_msg}**.",
        ]

    if who == "agent":
        return [
            f"整体市场当前更接近 **{market_pos}**。",
            f"客户匹配到的预算带目前属于 **{budget_pos}**。",
            f"客户当前谈判空间为 **{leverage}**，准备度为 **{readiness}**。",
            f"从时机上看：**{timing_msg}**。",
        ]
    if who == "investor":
        return [
            f"整体市场当前更接近 **{market_pos}**。",
            f"该预算带目前属于 **{budget_pos}**。",
            f"当前谈判空间为 **{leverage}**，准备度为 **{readiness}**。",
            f"从时机上看：**{timing_msg}**。",
        ]
    return [
        f"整体市场当前更接近 **{market_pos}**。",
        f"你的匹配预算带目前属于 **{budget_pos}**。",
        f"你当前谈判空间为 **{leverage}**，准备度为 **{readiness}**。",
        f"从时机上看：**{timing_msg}**。",
    ]


def build_strategy(
    leverage: str,
    readiness: str,
    goal: str,
    timeline: str,
    identity: str,
    lang: str,
) -> list[str]:
    who = identity_key(identity)
    strategy: list[str] = []

    if lang == "English":
        if leverage == "Higher":
            strategy.append("Prioritize homes with longer DOM, price cuts, or relist history.")
            strategy.append("Test seller credit, repair responsibility, or closing-cost support before focusing only on price.")
        elif leverage == "Moderate":
            strategy.append("Compare at least 3–5 similar homes before finalizing the offer posture.")
            strategy.append("Use negotiation selectively rather than assuming every listing is soft.")
        else:
            strategy.append("Keep financing, timing, and offer structure strong for better homes.")
            strategy.append("Do not assume broad market softness automatically applies to every listing.")

        if readiness != "Ready":
            strategy.append("Tighten financing readiness and internal decision steps before moving aggressively.")

        if goal == "Save money":
            strategy.append("Expand comparison one band above and one band below to find better value pockets.")
        elif goal == "Higher success rate":
            strategy.append("Focus first on better-fit homes rather than stretching toward the most competitive listings.")
        elif goal == "Buy quickly":
            strategy.append("Shorten comparison cycles and pre-decide your acceptable offer posture.")
        else:
            strategy.append("Screen condition, pricing discipline, and resale defensiveness before pursuing aggressively.")

        if who == "agent":
            strategy.insert(0, "Use this band read to frame the client conversation before touring or writing.")
        elif who == "investor":
            strategy.insert(0, "Underwrite this segment with discipline instead of relying on a broad statewide headline.")
    else:
        if leverage == "较大":
            strategy.append("优先看 DOM 较长、降价过、重新挂牌过的房源。")
            strategy.append("不要只盯价格，可同步争取 seller credit、维修责任或 closing cost 支持。")
        elif leverage == "中等":
            strategy.append("在最终决定前，先横向比较至少 3–5 套相似房源。")
            strategy.append("不要默认每套房都能谈，要选择性谈判。")
        else:
            strategy.append("对于更强势的房源，保持融资、时机和报价结构的完整性。")
            strategy.append("不要因为宏观市场偏软，就低估个别优质房源的竞争。")

        if readiness != "准备度较高":
            strategy.append("先把融资准备、内部决策和出手节奏再收紧一些。")

        if goal == "省钱":
            strategy.append("可把比较范围向上下相邻价格带各扩展一档，寻找性价比更高的区间。")
        elif goal == "提高成功率":
            strategy.append("优先聚焦匹配度高的房源，而不是一开始就追最热门的房子。")
        elif goal == "更快买到":
            strategy.append("缩短横向比较周期，并提前想清楚自己可接受的出价姿态。")
        else:
            strategy.append("更重视房屋条件、定价纪律和未来转手安全边际。")

        if who == "agent":
            strategy.insert(0, "先用这个预算带判断，帮助客户建立正确预期，再进入带看或出价。")
        elif who == "investor":
            strategy.insert(0, "先按这个价格带单独测算，不要只用全州大盘结论替代项目判断。")

    return strategy[:5]


def build_copyable_memo(
    budget_usd: float,
    band_name: str,
    market_pos: str,
    budget_pos: str,
    leverage: str,
    recommendation: str,
    timing_msg: str,
    lang: str,
) -> str:
    if lang == "English":
        return (
            f"Based on the latest North Carolina market data, your target budget of {fmt_money(budget_usd)} "
            f"currently maps to the {band_name} price band. The broader market reads as {market_pos.lower()}, "
            f"and your budget band appears {budget_pos.lower()}, which suggests {leverage.lower()} negotiation room "
            f"relative to tighter segments. At this stage, the best approach is to {recommendation.lower()}. "
            f"In practical terms, {timing_msg.lower()}."
        )

    return (
        f"根据最新北卡市场数据，你的目标预算 {fmt_money(budget_usd)} 目前对应到 {band_name} 这个价格带。"
        f"整体市场更接近 {market_pos}，而你的预算带处于 {budget_pos} 状态，说明相较更紧的区间，"
        f"当前仍存在 {leverage} 的谈判空间。现阶段更建议你：{recommendation}。"
        f"落到执行上，就是：{timing_msg}。"
    )


def build_investor_memo(
    budget_usd: float,
    band_name: str,
    market_pos: str,
    budget_pos: str,
    leverage: str,
    recommendation: str,
    timing_msg: str,
    lang: str,
) -> str:
    if lang == "English":
        return (
            f"For a target budget around {fmt_money(budget_usd)}, the current match is the {band_name} band. "
            f"The broader market reads as {market_pos.lower()}, while this band appears {budget_pos.lower()}. "
            f"That implies {leverage.lower()} entry flexibility relative to tighter segments. "
            f"The better posture here is to {recommendation.lower()}. In execution terms, {timing_msg.lower()}."
        )

    return (
        f"以 {fmt_money(budget_usd)} 左右预算来看，目前对应的是 {band_name} 价格带。"
        f"整体市场更接近 {market_pos}，而该价格带处于 {budget_pos} 状态，"
        f"说明相较更紧的区间，目前仍有 {leverage} 的入场灵活度。"
        f"现阶段更适合：{recommendation}。执行层面建议：{timing_msg}。"
    )


def badge_class_for_market(text_value: str, t: dict) -> str:
    if text_value == t["buyer_friendly"]:
        return "badge-green"
    if text_value == t["competitive"]:
        return "badge-red"
    return "badge-yellow"


# =========================================================
# MAIN
# =========================================================
def main() -> None:
    inject_base_css()
    inject_css()

    render_global_sidebar()
    lang = get_lang()
    t = TEXT[lang]
    opt = OPTIONS[lang]

    html_block(
        dedent(
            f"""
            <div class="hero">
                <div class="hero-chip">{t["hero_chip"]}</div>
                <div class="hero-title">{t["title"]}</div>
                <div class="hero-subtitle">{t["caption"]}</div>
            </div>
            """
        )
    )

    monthly_df = load_monthly_metrics(MONTHLY_PATH)
    band_df = load_price_bands(PRICE_BAND_PATH)

    if monthly_df.empty or band_df.empty:
        st.error(t["missing_data"])
        st.stop()

    latest_month = monthly_df["report_month"].dropna().astype(str).max()
    m_latest = monthly_df[monthly_df["report_month"] == latest_month].copy()
    b_latest = band_df[band_df["report_month"] == latest_month].copy()

    st.sidebar.divider()
    st.sidebar.header(t["profile"])

    budget_k = get_budget_k()
    budget_usd = float(budget_k) * 1000.0

    left, right = st.columns([0.96, 1.72], gap="large")

    with left:
        html_block(
            dedent(
                f"""
                <div class="panel-card">
                    <div class="panel-title">{t["profile"]}</div>
                    <div class="panel-sub">{t["profile_note"]}</div>
                </div>
                """
            )
        )

        identity = st.radio(
            t["identity"],
            opt["identity"],
            horizontal=True,
            key="decision_identity",
        )

        with st.form("decision_form", clear_on_submit=False):
            st.caption(f'{t["shared_budget"]}: {fmt_money(budget_usd)}')
            timeline = st.selectbox(t["timeline"], opt["timeline"])
            goal = st.selectbox(t["goal"], opt["goal"])
            down_payment = st.selectbox(t["down_payment"], opt["down_payment"])
            rate_assumption = st.slider(t["rate"], min_value=5.0, max_value=7.5, value=6.25, step=0.05)
            risk_pref = st.selectbox(t["risk"], opt["risk"])
            submitted = st.form_submit_button(submit_label(identity, t))

        html_block(f'<div class="mini-note">{t["mini_tip"]}</div>')

    if not submitted:
        st.info(t["fill_form"])
        st.stop()

    inv_trend = trend_label(monthly_df["months_inventory"]) if "months_inventory" in monthly_df.columns else "Stable"
    sales_trend = trend_label(monthly_df["sales"]) if "sales" in monthly_df.columns else "Stable"
    overall_raw = market_condition(inv_trend, sales_trend)

    overall_label = {
        "Buyer-Leaning": t["buyer_friendly"],
        "Seller-Leaning": t["competitive"],
        "Balanced": t["balanced"],
    }.get(overall_raw, t["balanced"])

    band_row = pick_budget_band(b_latest, budget_usd)
    if band_row is None:
        st.error(t["not_mapped"])
        st.stop()

    band_name = str(band_row.get("price_range", "N/A"))
    band_inv = pd.to_numeric(band_row.get("months_inventory"), errors="coerce")
    band_score = pd.to_numeric(band_row.get("buyer_leverage_score"), errors="coerce")

    state_inv_latest = (
        pd.to_numeric(m_latest["months_inventory"].iloc[0], errors="coerce")
        if not m_latest.empty and "months_inventory" in m_latest.columns
        else float("nan")
    )

    budget_pos = inventory_position(band_inv, t)
    readiness = readiness_label(down_payment, timeline, rate_assumption, t)
    leverage = leverage_label(band_score, band_inv, t)
    timing_msg = timing_suggestion(inv_trend, sales_trend, timeline, t)
    posture = offer_posture(leverage, risk_pref, t)
    recommendation = main_recommendation(identity, leverage, readiness, timeline, t)
    signal_icon, signal_text, signal_css = signal_meta(leverage, t)

    reason_lines = build_reason_lines(
        market_pos=overall_label,
        budget_pos=budget_pos,
        leverage=leverage,
        readiness=readiness,
        timing_msg=timing_msg,
        identity=identity,
        lang=lang,
    )
    strategy = build_strategy(
        leverage=leverage,
        readiness=readiness,
        goal=goal,
        timeline=timeline,
        identity=identity,
        lang=lang,
    )

    who = identity_key(identity)
    if who == "agent":
        memo = build_copyable_memo(
            budget_usd=budget_usd,
            band_name=band_name,
            market_pos=overall_label,
            budget_pos=budget_pos,
            leverage=leverage,
            recommendation=recommendation,
            timing_msg=timing_msg,
            lang=lang,
        )
    elif who == "investor":
        memo = build_investor_memo(
            budget_usd=budget_usd,
            band_name=band_name,
            market_pos=overall_label,
            budget_pos=budget_pos,
            leverage=leverage,
            recommendation=recommendation,
            timing_msg=timing_msg,
            lang=lang,
        )
    else:
        memo = ""

    signal_summary_text = (
        build_investor_memo(budget_usd, band_name, overall_label, budget_pos, leverage, recommendation, timing_msg, lang)
        if who == "investor"
        else build_copyable_memo(budget_usd, band_name, overall_label, budget_pos, leverage, recommendation, timing_msg, lang)
    )

    with right:
        html_block(f'<div class="section-title">{t["advisory_section"]}</div>')

        html_block(
            dedent(
                f"""
                <div class="signal-hero">
                    <div class="signal-kicker">{decision_title(identity, t)}</div>
                    <div class="signal-main">{recommendation}</div>
                    <div>
                        <span class="badge {signal_css}">{signal_icon} {signal_text}</span>
                        <span class="badge {badge_class_for_market(overall_label, t)}">{t["market_position"]}: {overall_label}</span>
                        <span class="badge {badge_class_for_market(budget_pos, t)}">{t["budget_position"]}: {budget_pos}</span>
                        <span class="badge badge-blue">{t["offer_posture"]}: {posture}</span>
                    </div>
                    <div class="signal-sub">{signal_summary_text}</div>
                </div>
                """
            )
        )

        html_block(
            dedent(
                f"""
                <div class="metric-grid">
                    <div class="metric-box">
                        <div class="metric-label">{t["target_budget"]}</div>
                        <div class="metric-value">{fmt_money(budget_usd)}</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">{t["matched_band"]}</div>
                        <div class="metric-value">{band_name}</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">{t["band_inventory"]}</div>
                        <div class="metric-value">{fmt_num(band_inv)} MOI</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">{t["state_inventory"]}</div>
                        <div class="metric-value">{fmt_num(state_inv_latest)} MOI</div>
                    </div>
                </div>
                """
            )
        )

        r1, r2, r3, r4 = st.columns(4)
        with r1:
            html_block(
                f"""
                <div class="summary-card">
                    <div class="summary-label">{t["readiness"]}</div>
                    <div class="summary-value">{readiness}</div>
                    <div class="summary-sub">{identity} · {down_payment} · Rate {rate_assumption:.2f}%</div>
                </div>
                """
            )
        with r2:
            html_block(
                f"""
                <div class="summary-card">
                    <div class="summary-label">{t["leverage"]}</div>
                    <div class="summary-value">{leverage}</div>
                    <div class="summary-sub">{t["band_score"]}: {fmt_num(band_score)}</div>
                </div>
                """
            )
        with r3:
            html_block(
                f"""
                <div class="summary-card">
                    <div class="summary-label">{t["offer_posture"]}</div>
                    <div class="summary-value">{posture}</div>
                    <div class="summary-sub">{goal}</div>
                </div>
                """
            )
        with r4:
            html_block(
                f"""
                <div class="summary-card">
                    <div class="summary-label">{t["timing"]}</div>
                    <div class="summary-value">{timing_msg}</div>
                    <div class="summary-sub">{timeline}</div>
                </div>
                """
            )

        reason_html = "".join([f"<li>{line}</li>" for line in reason_lines])
        strategy_html = "".join([f"<li>{item}</li>" for item in strategy])

        c1, c2 = st.columns([1.0, 1.08], gap="large")

        with c1:
            html_block(
                f"""
                <div class="insight-card">
                    <div class="card-kicker">{t["reason_title"]}</div>
                    <div class="card-title">{recommendation}</div>
                    <div class="card-body">
                        <ul class="action-list">{reason_html}</ul>
                    </div>
                </div>
                """
            )

        with c2:
            html_block(
                f"""
                <div class="strategy-card">
                    <div class="card-kicker">{t["next_steps"]}</div>
                    <div class="card-title">{t["strategy_title"]}</div>
                    <div class="card-body">
                        <ul class="action-list">{strategy_html}</ul>
                    </div>
                </div>
                """
            )

        if who == "agent":
            html_block(
                f"""
                <div class="memo-card">
                    <div class="card-kicker">{t["agent_client_section"]}</div>
                    <div class="card-title">{t["memo_title"]}</div>
                    <div class="memo-quote">{memo}</div>
                    <div class="copy-tip">{t["copy_tip"]}<br>{t["button_copy_label"]}</div>
                </div>
                """
            )
            st.code(memo, language=None)

        html_block(
            f"""
            <div class="footer-line">
                {t["footer_prefix"]} {t["latest_month"]}: {latest_month} |
                {t["profile_summary"]}: {identity}, {timeline}, {goal}, {down_payment}, {risk_pref}, Rate={rate_assumption:.2f}%
            </div>
            """
        )


if __name__ == "__main__":
    main()