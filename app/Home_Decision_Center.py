# Home_Decision_Center.py
# Streamlit Page 1: Home / Decision Center
# Bilingual: English / 中文
# Styled version with cleaner layout + CSS polish

from __future__ import annotations

import math
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd
import streamlit as st


# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="NC Housing Decision Center",
    page_icon="🏠",
    layout="wide",
)


# -----------------------------
# Config
# -----------------------------
MONTHLY_PATH = Path("data/analytics/monthly_metrics.csv")
PRICE_BAND_PATH = Path("data/analytics/price_ranges_enriched.csv")


# -----------------------------
# CSS Styling
# -----------------------------
def inject_css() -> None:
    st.markdown(
        """
        <style>
        /* ===== Global ===== */
        .main {
            background-color: #f7f8fa;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 1200px;
        }

        /* ===== Typography ===== */
        .page-title {
            font-size: 2.2rem;
            font-weight: 800;
            line-height: 1.2;
            margin-bottom: 0.3rem;
            color: #111827;
        }

        .page-subtitle {
            font-size: 1rem;
            color: #6b7280;
            margin-bottom: 1.2rem;
        }

        .section-title {
            font-size: 1.18rem;
            font-weight: 700;
            color: #111827;
            margin-bottom: 0.8rem;
        }

        .small-muted {
            color: #6b7280;
            font-size: 0.92rem;
        }

        /* ===== Cards ===== */
        .app-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 18px;
            padding: 1.2rem 1.2rem;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
            margin-bottom: 1rem;
        }

        .result-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 20px;
            padding: 1.35rem 1.35rem;
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.05);
            margin-bottom: 1rem;
        }

        /* ===== KPI / badges ===== */
        .signal-badge {
            display: inline-block;
            padding: 0.35rem 0.75rem;
            border-radius: 999px;
            font-size: 0.84rem;
            font-weight: 700;
            margin-right: 0.4rem;
            margin-bottom: 0.35rem;
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

        /* ===== Metric rows ===== */
        .metric-label {
            color: #6b7280;
            font-size: 0.92rem;
            margin-bottom: 0.12rem;
        }

        .metric-value {
            font-size: 1.45rem;
            font-weight: 800;
            color: #111827;
            margin-bottom: 0.7rem;
        }

        /* ===== Strategy box ===== */
        .strategy-box {
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 0.9rem 1rem;
            margin-top: 0.8rem;
        }

        /* ===== Form area ===== */
        div[data-testid="stForm"] {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 20px;
            padding: 1rem 1rem 0.65rem 1rem;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
        }

        /* ===== Buttons ===== */
        div.stButton > button,
        div[data-testid="stFormSubmitButton"] > button {
            border-radius: 12px;
            font-weight: 700;
            padding: 0.6rem 1rem;
            border: 1px solid #111827;
        }

        /* ===== Sidebar ===== */
        section[data-testid="stSidebar"] {
            background-color: #fcfcfd;
            border-right: 1px solid #eceef2;
        }

        /* ===== Divider tweaks ===== */
        hr {
            margin-top: 0.8rem;
            margin-bottom: 0.8rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------
# Language packs
# -----------------------------
TEXT = {
    "English": {
        "lang_label": "Language / 语言",
        "title": "Home / Decision Center",
        "caption": "Input your profile and get a practical buyer/seller strategy from the latest NC market data.",
        "profile": "Your Profile",
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
        "market_condition": "Market Condition",
        "inventory_trend": "Inventory Trend",
        "competition": "Competition",
        "action_suggestion": "Action Suggestion",
        "suggested_strategy": "Suggested Strategy",
        "budget_temp": "Your Budget Market Temperature",
        "timing_suggestion": "Timing Suggestion",
        "latest_data": "Latest data month",
        "profile_summary": "Profile",
        "reason": "Reason",
        "state_median_inventory": "State latest inventory",
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
        "strategy_credit": "✓ Request seller credit",
        "strategy_repair": "✓ Negotiate inspection repair",
        "strategy_below_list": "✓ Consider offers below list if DOM > 20",
        "strategy_clean": "✓ Use a clean offer structure",
        "strategy_financing": "✓ Keep financing contingency strong",
        "band_label": "Band",
        "months_inventory_label": "Months Inventory",
    },
    "中文": {
        "lang_label": "Language / 语言",
        "title": "首页 / 决策中心",
        "caption": "输入你的条件，获得基于最新北卡房地产市场数据的买家/卖家实用策略建议。",
        "profile": "你的资料",
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
        "market_condition": "市场状态",
        "inventory_trend": "库存趋势",
        "competition": "竞争强度",
        "action_suggestion": "行动建议",
        "suggested_strategy": "建议策略",
        "budget_temp": "你的预算段市场温度",
        "timing_suggestion": "时机建议",
        "latest_data": "最新数据月份",
        "profile_summary": "用户条件",
        "reason": "原因",
        "state_median_inventory": "全州最新库存值",
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
        "strategy_credit": "✓ 争取 seller credit（卖家补贴）",
        "strategy_repair": "✓ 谈 inspection repair（验房维修）",
        "strategy_below_list": "✓ 如果 DOM > 20，可考虑低于挂牌价出价",
        "strategy_clean": "✓ 保持报价结构清晰干净",
        "strategy_financing": "✓ 保持融资条款稳健",
        "band_label": "价格区间",
        "months_inventory_label": "库存月数",
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


# -----------------------------
# Helpers
# -----------------------------
def tr(label_key: str, t: dict) -> str:
    return t.get(label_key, label_key)


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


# -----------------------------
# Data loaders
# -----------------------------
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


# -----------------------------
# Signals / scoring
# -----------------------------
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


def buyer_opportunity_score(
    inv_growth: float,
    sales_decline: float,
    price_growth_slowdown: float,
) -> float:
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


# -----------------------------
# Language selector
# -----------------------------
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


# -----------------------------
# Page header
# -----------------------------
st.markdown(
    f"""
    <div class="page-title">🏠 {t['title']}</div>
    <div class="page-subtitle">{t['caption']}</div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Load data
# -----------------------------
monthly_df = load_monthly_metrics(MONTHLY_PATH)
band_df = load_price_bands(PRICE_BAND_PATH)

if monthly_df.empty or band_df.empty:
    st.error(t["missing_data"])
    st.stop()

latest_month = monthly_df["report_month"].dropna().astype(str).max()
m_latest = monthly_df[monthly_df["report_month"] == latest_month]
b_latest = band_df[band_df["report_month"] == latest_month]


# -----------------------------
# Layout
# -----------------------------
left, right = st.columns([1, 2])


# -----------------------------
# Left panel: Form
# -----------------------------
with left:
    st.markdown(
        f'<div class="section-title">{t["profile"]}</div>',
        unsafe_allow_html=True,
    )

    with st.form("decision_form", clear_on_submit=False):
        identity = st.selectbox(t["identity"], opt["identity"])

        budget_k = st.slider(
            t["budget"],
            min_value=200,
            max_value=1500,
            value=550,
            step=10,
        )

        timeline = st.selectbox(t["timeline"], opt["timeline"])
        goal = st.selectbox(t["goal"], opt["goal"])
        down_payment = st.selectbox(t["down_payment"], opt["down_payment"])

        rate_assumption = st.slider(
            t["rate"],
            min_value=5.0,
            max_value=7.5,
            value=6.25,
            step=0.05,
        )

        submitted = st.form_submit_button(t["submit"])

if not submitted:
    st.info(t["fill_form"])
    st.stop()


# -----------------------------
# Core calculations
# -----------------------------
budget_usd = float(budget_k) * 1000.0

inv_trend = trend_label(monthly_df["months_inventory"])
sales_tr = trend_label(monthly_df["sales"])
price_tr = trend_label(monthly_df["median_price"])
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

inv_growth = (
    float(monthly_df["mom_inventory_pct"].dropna().tail(1).mean())
    if "mom_inventory_pct" in monthly_df.columns
    else 0.0
)
sales_decline = (
    -float(monthly_df["mom_sales_pct"].dropna().tail(1).mean())
    if "mom_sales_pct" in monthly_df.columns
    else 0.0
)
price_slowdown = (
    -float(monthly_df["mom_price_pct"].dropna().tail(1).mean())
    if "mom_price_pct" in monthly_df.columns
    else 0.0
)
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

strategy = []

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
display_price_tr = show_label(price_tr, labels)


# -----------------------------
# Right panel: Styled results
# -----------------------------
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
        f"""
        <div class="result-card">
            <div class="small-muted">{t['market_signal']}</div>
            <div style="margin-top: 0.5rem;">
                <span class="signal-badge {badge_class}">{display_overall}</span>
                <span class="signal-badge badge-blue">{t['inventory_trend']}: {display_inv_trend}</span>
                <span class="signal-badge badge-yellow">{t['competition']}: {display_comp}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="result-card">
            <div class="section-title" style="margin-bottom: 0.45rem;">{t['action_suggestion']}</div>
            <div class="small-muted" style="margin-bottom: 0.9rem;">
                {t['target_budget']}: <strong>{band_name}</strong>, {fmt_money(budget_usd)}
            </div>

            <div class="metric-label">{t['band_inventory']}</div>
            <div class="metric-value">{fmt_num(band_inv)} months</div>

            <div class="metric-label">{t['state_median_inventory']}</div>
            <div class="metric-value">{fmt_num(state_inv_latest)} months</div>

            <div class="metric-label">{t['opportunity_score']}</div>
            <div class="metric-value">{fmt_num(opp_score)}</div>

            <div class="strategy-box">
                <div style="font-weight: 700; margin-bottom: 0.45rem;">{t['suggested_strategy']}</div>
        """,
        unsafe_allow_html=True,
    )

    for item in strategy:
        st.write(item)

    st.markdown(
        """
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="result-card">
            <div class="section-title">{t['budget_temp']}</div>
            <div style="font-size: 1.5rem; font-weight: 800; margin-top: 0.45rem;">
                {temp_icon} {display_temp_label}
            </div>
            <div class="small-muted" style="margin-top: 0.45rem;">
                {t['band_label']}: {band_name} | {t['months_inventory_label']}: {fmt_num(band_inv)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="result-card">
            <div class="section-title">{t['timing_suggestion']}</div>
            <div style="font-size: 1.05rem; font-weight: 700; color: #111827; margin-top: 0.35rem;">
                {timing_title}
            </div>
            <div class="small-muted" style="margin-top: 0.45rem;">
                {t['reason']}: {timing_reason}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        f"{t['latest_month_caption']}: {latest_month} | "
        f"{t['profile_summary']}: {identity}, {timeline}, {goal}, "
        f"{down_payment}, Rate={rate_assumption:.2f}%"
    )