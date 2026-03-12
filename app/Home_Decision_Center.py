from __future__ import annotations

import math
from pathlib import Path
from typing import Optional, Tuple
from textwrap import dedent

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="NC Housing Decision Center",
    page_icon="🏠",
    layout="wide",
)

MONTHLY_PATH = Path("data/analytics/monthly_metrics.csv")
PRICE_BAND_PATH = Path("data/analytics/price_ranges_enriched.csv")


def inject_css() -> None:
    st.markdown(
        dedent(
            """
            <style>
            .main {
                background: #f7f8fa;
            }

            .block-container {
                padding-top: 4.2rem;
                padding-bottom: 2rem;
                padding-left: 2rem;
                padding-right: 2rem;
                max-width: 1240px;
            }

            section[data-testid="stSidebar"] {
                background-color: #fcfcfd;
                border-right: 1px solid #eceef2;
            }

            .page-title {
                font-size: 2.25rem;
                font-weight: 800;
                line-height: 1.2;
                margin-bottom: 0.25rem;
                color: #0f172a;
                letter-spacing: -0.02em;
            }

            .page-subtitle {
                font-size: 1rem;
                color: #64748b;
                margin-bottom: 1.4rem;
            }

            .section-title {
                font-size: 1.12rem;
                font-weight: 800;
                color: #0f172a;
                margin-bottom: 0.85rem;
            }

            .small-muted {
                color: #64748b;
                font-size: 0.92rem;
                line-height: 1.55;
            }

            .footer-line {
                color: #94a3b8;
                font-size: 0.84rem;
                margin-top: 0.3rem;
            }

            .control-panel {
                background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%);
                border: 1px solid #e5e7eb;
                border-radius: 22px;
                padding: 1.15rem 1.1rem 0.8rem 1.1rem;
                box-shadow: 0 10px 28px rgba(15, 23, 42, 0.05);
                margin-bottom: 1rem;
            }

            .control-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 0.9rem;
            }

            .control-title {
                font-size: 1.05rem;
                font-weight: 800;
                color: #0f172a;
            }

            .control-chip {
                display: inline-block;
                padding: 0.28rem 0.6rem;
                border-radius: 999px;
                font-size: 0.78rem;
                font-weight: 700;
                background: #eff6ff;
                color: #1d4ed8;
                border: 1px solid #dbeafe;
            }

            .control-note {
                font-size: 0.88rem;
                color: #64748b;
                margin-bottom: 0.75rem;
            }

            .mini-tip {
                background: #f8fafc;
                border: 1px dashed #dbeafe;
                color: #475569;
                border-radius: 14px;
                padding: 0.8rem 0.85rem;
                font-size: 0.88rem;
                line-height: 1.5;
                margin-top: 0.8rem;
            }

            .result-card {
                background: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 20px;
                padding: 1.25rem 1.25rem;
                box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
                margin-bottom: 1rem;
            }

            .hero-card {
                background: linear-gradient(135deg, #ffffff 0%, #f8fbff 100%);
                border: 1px solid #dbeafe;
                border-radius: 20px;
                padding: 1.25rem 1.25rem;
                box-shadow: 0 8px 24px rgba(29, 78, 216, 0.06);
                margin-bottom: 1rem;
            }

            .signal-badge {
                display: inline-block;
                padding: 0.38rem 0.78rem;
                border-radius: 999px;
                font-size: 0.84rem;
                font-weight: 800;
                margin-right: 0.45rem;
                margin-bottom: 0.4rem;
            }

            .badge-green {
                background-color: #dcfce7;
                color: #166534;
            }

            .badge-red {
                background-color: #fee2e2;
                color: #991b1b;
            }

            .badge-yellow {
                background-color: #fef3c7;
                color: #92400e;
            }

            .badge-blue {
                background-color: #dbeafe;
                color: #1d4ed8;
            }

            .metric-grid {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 0.85rem;
                margin-top: 0.95rem;
                margin-bottom: 0.95rem;
            }

            .metric-box {
                background: #f8fafc;
                border: 1px solid #e5e7eb;
                border-radius: 16px;
                padding: 0.9rem 0.95rem;
            }

            .metric-label {
                color: #64748b;
                font-size: 0.86rem;
                margin-bottom: 0.22rem;
            }

            .metric-value {
                font-size: 1.32rem;
                font-weight: 800;
                color: #0f172a;
                line-height: 1.2;
            }

            .strategy-box {
                background: #f8fafc;
                border: 1px solid #e5e7eb;
                border-radius: 16px;
                padding: 0.95rem 1rem;
                margin-top: 0.7rem;
            }

            .strategy-title {
                font-size: 0.98rem;
                font-weight: 800;
                color: #0f172a;
                margin-bottom: 0.7rem;
            }

            .strategy-item {
                display: flex;
                align-items: flex-start;
                gap: 0.65rem;
                margin-bottom: 0.65rem;
                font-size: 0.96rem;
                color: #0f172a;
                line-height: 1.55;
            }

            .strategy-check {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: 1.3rem;
                height: 1.3rem;
                border-radius: 999px;
                background: #dcfce7;
                color: #15803d;
                font-size: 0.84rem;
                font-weight: 900;
                flex-shrink: 0;
                margin-top: 0.08rem;
                border: 1px solid #86efac;
            }

            .highlight-line {
                font-size: 1.04rem;
                font-weight: 800;
                color: #0f172a;
                margin-top: 0.35rem;
                margin-bottom: 0.35rem;
            }

            .temp-line {
                font-size: 1.5rem;
                font-weight: 800;
                color: #0f172a;
                margin-top: 0.4rem;
                margin-bottom: 0.35rem;
            }

            div[data-testid="stForm"] {
                background: transparent;
                border: none;
                padding: 0;
                box-shadow: none;
            }

            div[data-baseweb="select"] > div {
                border-radius: 12px !important;
                border: 1px solid #e5e7eb !important;
                background-color: #f8fafc !important;
            }

            div[data-testid="stSlider"] {
                padding-top: 0.25rem;
                padding-bottom: 0.45rem;
            }

            div.stButton > button,
            div[data-testid="stFormSubmitButton"] > button {
                border-radius: 12px;
                font-weight: 700;
                padding: 0.68rem 1rem;
                border: 1px solid #0f172a;
                background: white;
                transition: all 0.18s ease;
            }

            div.stButton > button:hover,
            div[data-testid="stFormSubmitButton"] > button:hover {
                background: #0f172a;
                color: white;
                border-color: #0f172a;
            }

            label, .stSelectbox label, .stSlider label {
                font-weight: 600 !important;
                color: #334155 !important;
            }
            </style>
            """
        ),
        unsafe_allow_html=True,
    )


TEXT = {
    "English": {
        "title": "Home / Decision Center",
        "caption": "Input your profile and get a practical buyer/seller strategy from the latest NC market data.",
        "profile": "Your Profile",
        "profile_chip": "Interactive Input",
        "profile_note": "Adjust your budget, timeline, and goal to generate a personalized market recommendation.",
        "mini_tip": "Tip: this page helps buyers, sellers, and agents quickly understand whether the current market environment is favorable and what action to take next.",
        "identity": "Identity",
        "budget": "Budget (USD, in $1,000s)",
        "timeline": "Timeline",
        "goal": "Goal",
        "down_payment": "Down Payment",
        "rate": "Rate Assumption (%)",
        "submit": "Generate Decision",
        "fill_form": "Fill the form and click **Generate Decision**.",
        "missing_data": (
            "Missing analytics files. Please run:\n\n"
            "`python run_full_pipeline.py --workers 4`\n\n"
            "This should generate analytics outputs first."
        ),
        "decision_card": "Decision Card",
        "market_signal": "Buyer Market Signal",
        "inventory_trend": "Inventory Trend",
        "competition": "Competition",
        "action_suggestion": "Action Suggestion",
        "suggested_strategy": "Suggested Strategy",
        "budget_temp": "Your Budget Market Temperature",
        "timing_suggestion": "Timing Suggestion",
        "profile_summary": "Profile",
        "reason": "Reason",
        "state_inventory": "State latest inventory",
        "band_inventory": "Inventory in band",
        "opportunity_score": "Opportunity score (quick)",
        "target_budget": "Target budget",
        "could_not_map": "Could not map budget to a price band for latest month.",
        "latest_month_caption": "Latest data month",
        "recommend_watch": "Recommendation: Monitor for 1–2 more reports",
        "recommend_fast": "Recommendation: Prepare to act faster",
        "recommend_selective": "Recommendation: Watch and act selectively",
        "reason_watch": "Inventory rising + sales slowing. Buyer leverage likely improving.",
        "reason_fast": "Inventory tightening + sales strengthening. Competition may increase.",
        "reason_selective": "Signals are mixed. Keep pre-approval ready and negotiate case-by-case.",
        "strategy_credit": "Request seller credit",
        "strategy_repair": "Negotiate inspection repair",
        "strategy_below_list": "Consider offers below list if DOM > 20",
        "strategy_clean": "Use a clean offer structure",
        "strategy_financing": "Keep financing contingency strong",
        "band_label": "Band",
        "months_inventory_label": "Months Inventory",
        "months_unit": "months",
    },
    "中文": {
        "title": "首页 / 决策中心",
        "caption": "输入你的条件，获得基于最新北卡房地产市场数据的买家/卖家实用策略建议。",
        "profile": "你的资料",
        "profile_chip": "互动输入",
        "profile_note": "调整你的预算、时间窗口和目标，生成更个性化的市场建议。",
        "mini_tip": "提示：这个页面用于帮助买家、卖家和经纪人快速判断当前市场环境是否更有利，以及下一步如何行动。",
        "identity": "身份",
        "budget": "预算（美元，单位：千）",
        "timeline": "时间窗口",
        "goal": "目标",
        "down_payment": "首付比例",
        "rate": "利率假设 (%)",
        "submit": "生成决策建议",
        "fill_form": "请填写表单，然后点击 **生成决策建议**。",
        "missing_data": (
            "缺少 analytics 文件。请先运行：\n\n"
            "`python run_full_pipeline.py --workers 4`\n\n"
            "需要先生成 analytics 输出文件。"
        ),
        "decision_card": "决策卡片",
        "market_signal": "买家市场信号",
        "inventory_trend": "库存趋势",
        "competition": "竞争强度",
        "action_suggestion": "行动建议",
        "suggested_strategy": "建议策略",
        "budget_temp": "你的预算段市场温度",
        "timing_suggestion": "时机建议",
        "profile_summary": "用户条件",
        "reason": "原因",
        "state_inventory": "全州最新库存值",
        "band_inventory": "该预算段库存",
        "opportunity_score": "机会分数（快速）",
        "target_budget": "目标预算",
        "could_not_map": "无法把该预算匹配到最新月份的价格区间。",
        "latest_month_caption": "最新数据月份",
        "recommend_watch": "建议：再观察 1–2 期报告",
        "recommend_fast": "建议：准备更快出手",
        "recommend_selective": "建议：边观察边选择性行动",
        "reason_watch": "库存上升 + 成交放缓，买方议价能力可能继续改善。",
        "reason_fast": "库存收紧 + 成交增强，竞争可能上升。",
        "reason_selective": "信号较混合。保持贷款预批，具体房源具体谈判。",
        "strategy_credit": "争取 seller credit（卖家补贴）",
        "strategy_repair": "谈 inspection repair（验房维修）",
        "strategy_below_list": "如果 DOM > 20，可考虑低于挂牌价出价",
        "strategy_clean": "保持报价结构清晰干净",
        "strategy_financing": "保持融资条款稳健",
        "band_label": "价格区间",
        "months_inventory_label": "库存月数",
        "months_unit": "个月",
    },
}

OPTIONS = {
    "English": {
        "identity": ["Buyer", "Seller", "Agent"],
        "timeline": ["30 days", "3 months", "6 months", "Not urgent"],
        "goal": ["Save money", "Higher success rate", "Faster purchase", "Lower risk"],
        "down_payment": ["5%", "10%", "20%", "30%"],
    },
    "中文": {
        "identity": ["买家", "卖家", "经纪人"],
        "timeline": ["30天内", "3个月内", "6个月内", "不着急"],
        "goal": ["省钱", "提高成功率", "更快买到", "降低风险"],
        "down_payment": ["5%", "10%", "20%", "30%"],
    },
}

LABELS = {
    "English": {
        "Buyer-Leaning": "Buyer-Leaning",
        "Seller-Leaning": "Seller-Leaning",
        "Balanced": "Balanced",
        "Rising": "Rising",
        "Falling": "Falling",
        "Stable": "Stable",
        "Unknown": "Unknown",
        "High": "High",
        "Moderate": "Moderate",
        "Low": "Low",
        "Hot Market": "Hot Market",
        "Buyer Friendly": "Buyer Friendly",
    },
    "中文": {
        "Buyer-Leaning": "偏买方市场",
        "Seller-Leaning": "偏卖方市场",
        "Balanced": "平衡市场",
        "Rising": "上升",
        "Falling": "下降",
        "Stable": "稳定",
        "Unknown": "未知",
        "High": "高",
        "Moderate": "中等",
        "Low": "低",
        "Hot Market": "竞争激烈",
        "Buyer Friendly": "对买家友好",
    },
}


def show_label(value: str, labels: dict) -> str:
    return labels.get(value, value)


def fmt_money(x: float) -> str:
    if pd.isna(x):
        return "N/A"
    return f"${x:,.0f}"


def fmt_num(x: float, digits: int = 2) -> str:
    if pd.isna(x):
        return "N/A"
    return f"{x:.{digits}f}"


def build_strategy_html(strategy_items: list[str]) -> str:
    blocks = []
    for item in strategy_items:
        blocks.append(
            dedent(
                f"""
                <div class="strategy-item">
                    <span class="strategy-check">✓</span>
                    <span>{item}</span>
                </div>
                """
            )
        )
    return "".join(blocks)


@st.cache_data(ttl=60)
def load_monthly_metrics(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()

    df = pd.read_csv(path)

    if "report_month" in df.columns:
        df["report_month"] = df["report_month"].astype(str)
        df = df.sort_values("report_month")

    for c in [
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
    ]:
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
        sort_cols = ["report_month"]
        if "range_rank" in df.columns:
            sort_cols.append("range_rank")
        df = df.sort_values(sort_cols, na_position="last")

    for c in [
        "range_min",
        "range_max",
        "listings",
        "sales_prev_12mo",
        "months_inventory",
        "range_rank",
    ]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    return df


def trend_label(series: pd.Series) -> str:
    s = series.dropna()
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


def competition_from_inventory(inv: float) -> str:
    if math.isnan(inv):
        return "Unknown"
    if inv < 3.5:
        return "High"
    if inv < 5.5:
        return "Moderate"
    return "Low"


def budget_temp(inv: float) -> Tuple[str, str]:
    if math.isnan(inv):
        return "⚪", "Unknown"
    if inv < 3.5:
        return "🔥", "Hot Market"
    if inv < 5.5:
        return "🟡", "Balanced"
    return "🟢", "Buyer Friendly"


def buyer_opportunity_score(inv_growth: float, sales_decline: float, price_growth_slowdown: float) -> float:
    vals = [inv_growth, sales_decline, price_growth_slowdown]
    vals = [v for v in vals if pd.notna(v)]
    return float(sum(vals)) if vals else 0.0


def pick_budget_band(latest_band_df: pd.DataFrame, budget_usd: float) -> Optional[pd.Series]:
    if latest_band_df.empty:
        return None

    numeric = latest_band_df.dropna(subset=["range_min"]).copy()

    if not numeric.empty:
        in_range = numeric[
            (numeric["range_min"] <= budget_usd)
            & ((numeric["range_max"].isna()) | (numeric["range_max"] >= budget_usd))
        ]
        if not in_range.empty:
            sort_cols = [c for c in ["range_rank", "range_min"] if c in in_range.columns]
            if sort_cols:
                return in_range.sort_values(sort_cols).iloc[0]
            return in_range.iloc[0]

    if not numeric.empty:
        numeric["dist"] = (numeric["range_min"] - budget_usd).abs()
        sort_cols = [c for c in ["dist", "range_rank"] if c in numeric.columns]
        if sort_cols:
            return numeric.sort_values(sort_cols).iloc[0]
        return numeric.iloc[0]

    return latest_band_df.iloc[0]


if "lang" not in st.session_state:
    st.session_state.lang = "English"

lang = st.sidebar.selectbox(
    "Language / 语言",
    ["English", "中文"],
    key="lang",
)

t = TEXT[lang]
opt = OPTIONS[lang]
labels = LABELS[lang]

inject_css()

st.markdown(
    dedent(
        f"""
        <div class="page-title">🏠 {t['title']}</div>
        <div class="page-subtitle">{t['caption']}</div>
        """
    ),
    unsafe_allow_html=True,
)

monthly_df = load_monthly_metrics(MONTHLY_PATH)
band_df = load_price_bands(PRICE_BAND_PATH)

if monthly_df.empty or band_df.empty:
    st.error(t["missing_data"])
    st.stop()

latest_month = monthly_df["report_month"].dropna().astype(str).max()
m_latest = monthly_df[monthly_df["report_month"] == latest_month]
b_latest = band_df[band_df["report_month"] == latest_month]

left, right = st.columns([1, 2])

with left:
    st.markdown(
        dedent(
            f"""
            <div class="control-panel">
                <div class="control-header">
                    <div class="control-title">{t["profile"]}</div>
                    <div class="control-chip">{t["profile_chip"]}</div>
                </div>
                <div class="control-note">{t["profile_note"]}</div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    with st.form("decision_form", clear_on_submit=False):
        identity = st.selectbox(t["identity"], opt["identity"])
        budget_k = st.slider(t["budget"], min_value=200, max_value=1500, value=550, step=10)
        timeline = st.selectbox(t["timeline"], opt["timeline"])
        goal = st.selectbox(t["goal"], opt["goal"])
        down_payment = st.selectbox(t["down_payment"], opt["down_payment"])
        rate_assumption = st.slider(t["rate"], min_value=5.0, max_value=7.5, value=6.25, step=0.05)
        submitted = st.form_submit_button(t["submit"])

    st.markdown(
        dedent(
            f"""
            <div class="mini-tip">
                {t["mini_tip"]}
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

if not submitted:
    st.info(t["fill_form"])
    st.stop()

budget_usd = float(budget_k) * 1000.0

inv_trend = trend_label(monthly_df["months_inventory"])
sales_tr = trend_label(monthly_df["sales"])
overall = market_condition(inv_trend, sales_tr)

band_row = pick_budget_band(b_latest, budget_usd)
if band_row is None:
    st.error(t["could_not_map"])
    st.stop()

band_inv = float(band_row.get("months_inventory", float("nan")))
band_listings = float(band_row.get("listings", float("nan")))
band_sales_12m = float(band_row.get("sales_prev_12mo", float("nan")))
band_name = str(band_row.get("price_range", "Unknown Band"))

comp = competition_from_inventory(band_inv)
temp_icon, temp_label = budget_temp(band_inv)

state_inv_latest = (
    float(m_latest["months_inventory"].iloc[0])
    if not m_latest.empty and "months_inventory" in m_latest.columns
    else float("nan")
)

inv_growth = float(monthly_df["mom_inventory_pct"].dropna().tail(1).mean()) if "mom_inventory_pct" in monthly_df.columns else 0.0
sales_decline = -float(monthly_df["mom_sales_pct"].dropna().tail(1).mean()) if "mom_sales_pct" in monthly_df.columns else 0.0
price_slowdown = -float(monthly_df["mom_price_pct"].dropna().tail(1).mean()) if "mom_price_pct" in monthly_df.columns else 0.0
opp_score = buyer_opportunity_score(inv_growth, sales_decline, price_slowdown)

if inv_trend == "Rising" and sales_tr == "Falling":
    timing_title = t["recommend_watch"]
    timing_reason = t["reason_watch"]
elif inv_trend == "Falling" and sales_tr == "Rising":
    timing_title = t["recommend_fast"]
    timing_reason = t["reason_fast"]
else:
    timing_title = t["recommend_selective"]
    timing_reason = t["reason_selective"]

strategy: list[str] = []

if pd.notna(band_inv) and pd.notna(state_inv_latest) and band_inv > state_inv_latest:
    strategy.append(t["strategy_credit"])

if (
    sales_tr == "Falling"
    or (
        pd.notna(band_sales_12m)
        and band_sales_12m > 0
        and pd.notna(band_listings)
        and (band_listings / band_sales_12m) > 0.12
    )
):
    strategy.append(t["strategy_repair"])

if comp in {"Moderate", "Low"}:
    strategy.append(t["strategy_below_list"])

if not strategy:
    strategy = [t["strategy_clean"], t["strategy_financing"]]

display_overall = show_label(overall, labels)
display_inv_trend = show_label(inv_trend, labels)
display_comp = show_label(comp, labels)
display_temp_label = show_label(temp_label, labels)

with right:
    st.markdown(
        f'<div class="section-title">{t["decision_card"]}</div>',
        unsafe_allow_html=True,
    )

    badge_class = "badge-yellow"
    if overall == "Buyer-Leaning":
        badge_class = "badge-green"
    elif overall == "Seller-Leaning":
        badge_class = "badge-red"

    st.markdown(
        dedent(
            f"""
            <div class="hero-card">
                <div class="small-muted">{t['market_signal']}</div>
                <div style="margin-top: 0.55rem;">
                    <span class="signal-badge {badge_class}">{display_overall}</span>
                    <span class="signal-badge badge-blue">{t['inventory_trend']}: {display_inv_trend}</span>
                    <span class="signal-badge badge-yellow">{t['competition']}: {display_comp}</span>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    strategy_html = build_strategy_html(strategy)

    # 行动建议卡（不用 HTML，直接用 Streamlit 原生组件）
    with st.container(border=True):
        st.markdown(f"### {t['action_suggestion']}")
        st.caption(f"{t['target_budget']}: {band_name}, {fmt_money(budget_usd)}")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(
                label=t["band_inventory"],
                value=f"{fmt_num(band_inv)} {t['months_unit']}",
            )
        with c2:
            st.metric(
                label=t["state_inventory"],
                value=f"{fmt_num(state_inv_latest)} {t['months_unit']}",
            )
        with c3:
            st.metric(
                label=t["opportunity_score"],
                value=fmt_num(opp_score),
            )

        st.markdown(f"**{t['suggested_strategy']}**")

        for item in strategy:
            st.markdown(
                f"""
                <div style="
                    display:flex;
                    align-items:flex-start;
                    gap:10px;
                    margin:10px 0;
                    font-size:16px;
                    line-height:1.5;
                ">
                    <div style="
                        width:22px;
                        height:22px;
                        min-width:22px;
                        border-radius:999px;
                        background:#dcfce7;
                        color:#15803d;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        font-weight:800;
                        border:1px solid #86efac;
                        margin-top:2px;
                    ">✓</div>
                    <div>{item}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        dedent(
            f"""
            <div class="result-card">
                <div class="section-title">{t['budget_temp']}</div>
                <div class="temp-line">{temp_icon} {display_temp_label}</div>
                <div class="small-muted">
                    {t['band_label']}: {band_name} | {t['months_inventory_label']}: {fmt_num(band_inv)}
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        dedent(
            f"""
            <div class="result-card">
                <div class="section-title">{t['timing_suggestion']}</div>
                <div class="highlight-line">{timing_title}</div>
                <div class="small-muted">{t['reason']}: {timing_reason}</div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        dedent(
            f"""
            <div class="footer-line">
                {t['latest_month_caption']}: {latest_month} |
                {t['profile_summary']}: {identity}, {timeline}, {goal}, {down_payment}, Rate={rate_assumption:.2f}%
            </div>
            """
        ),
        unsafe_allow_html=True,
    )
    # st.caption(
    #     f"{t['latest_month_caption']}: {latest_month} | "
    #     f"{t['profile_summary']}: {identity}, {timeline}, {goal}, "
    #     f"{down_payment}, Rate={rate_assumption:.2f}%"
    # )