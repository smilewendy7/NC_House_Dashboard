from __future__ import annotations

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="NC Market Pulse",
    page_icon="📈",
    layout="wide",
)

DATA_PATH = Path("data/analytics/monthly_metrics.csv")

alt.data_transformers.disable_max_rows()


# -----------------------------
# global style
# -----------------------------
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2.4rem;
        max-width: 1400px;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #E5E7EB;
        padding: 14px 16px;
        border-radius: 16px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }

    .hero-box {
        background: linear-gradient(135deg, #F8FBFF 0%, #F9FAFB 45%, #EEF6FF 100%);
        border: 1px solid #E5E7EB;
        border-radius: 24px;
        padding: 26px 24px 22px 24px;
        margin-bottom: 18px;
    }

    .hero-title {
        font-size: 30px;
        font-weight: 800;
        line-height: 1.2;
        color: #111827;
        margin-bottom: 6px;
    }

    .hero-subtitle {
        font-size: 14px;
        color: #4B5563;
        line-height: 1.7;
        margin-bottom: 16px;
    }

    .chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }

    .chip {
        display: inline-block;
        padding: 7px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        color: #1F2937;
        background: rgba(255,255,255,0.88);
        border: 1px solid #D1D5DB;
    }

    .section-card {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 20px;
        padding: 18px 18px 14px 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        margin-bottom: 16px;
    }

    .section-title {
        font-size: 22px;
        font-weight: 800;
        color: #111827;
        margin-bottom: 4px;
    }

    .section-caption {
        font-size: 13px;
        color: #6B7280;
        margin-bottom: 14px;
        line-height: 1.6;
    }

    .signal-card {
        border-radius: 18px;
        padding: 16px 16px 14px 16px;
        min-height: 158px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        border: 1px solid #E5E7EB;
    }

    .signal-title {
        font-size: 13px;
        color: #6B7280;
        margin-bottom: 10px;
        font-weight: 700;
        letter-spacing: 0.2px;
    }

    .signal-main {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 10px;
    }

    .signal-icon {
        font-size: 24px;
    }

    .signal-value {
        font-size: 20px;
        font-weight: 800;
        line-height: 1.2;
    }

    .signal-badge {
        display: inline-block;
        font-size: 12px;
        font-weight: 700;
        border-radius: 999px;
        padding: 4px 10px;
        margin-bottom: 10px;
        background: rgba(255,255,255,0.66);
    }

    .signal-subtext {
        font-size: 13px;
        color: #4B5563;
        line-height: 1.55;
        margin-top: 4px;
    }

    .overall-card {
        border-radius: 20px;
        padding: 22px 18px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        border: 1.5px solid #D1D5DB;
    }

    .overall-label {
        font-size: 13px;
        font-weight: 700;
        color: #6B7280;
        margin-bottom: 8px;
    }

    .overall-main {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 10px;
    }

    .overall-icon {
        font-size: 30px;
    }

    .overall-value {
        font-size: 28px;
        font-weight: 900;
        line-height: 1.1;
    }

    .overall-badge {
        display: inline-block;
        font-size: 12px;
        font-weight: 700;
        border-radius: 999px;
        padding: 5px 10px;
        margin-bottom: 12px;
        background: rgba(255,255,255,0.72);
    }

    .overall-sub {
        font-size: 13px;
        color: #4B5563;
        line-height: 1.6;
    }

    .mini-note {
        font-size: 12px;
        color: #6B7280;
        margin-top: 3px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# i18n
# -----------------------------
TEXT = {
    "en": {
        "page_title": "📊 NC Market Pulse",
        "page_caption": "A professional dashboard for North Carolina housing market trends based on monthly analytics outputs.",
        "lang_en": "English",
        "lang_zh": "中文",
        "filters": "Filters",
        "month_window": "Month Window",
        "time_range": "Time Range",
        "year_filter": "Year Filter",
        "all_years": "All Years",
        "last_12m": "Last 12M",
        "last_24m": "Last 24M",
        "last_36m": "Last 36M",
        "ytd": "YTD",
        "all_data": "All",
        "missing_file": "Missing data/analytics/monthly_metrics.csv.\n\nRun:\n\npython run_full_pipeline.py --workers 4",
        "missing_cols": "Missing required columns in monthly_metrics.csv:",
        "no_data_range": "No data in selected month range.",
        "latest_month": "Latest Month",
        "inventory_months": "Inventory (months)",
        "listings": "Listings",
        "sales": "Sales",
        "median_price": "Median Price",
        "headline_title": "North Carolina Housing Snapshot",
        "headline_caption": "A macro view of inventory, demand, and pricing dynamics.",
        "inventory_chart_title": "NC Inventory Trend (MOI, Months of Inventory)",
        "inventory_chart_caption": "MOI is sourced from or derived from NC REALTORS monthly market reports. Higher values usually indicate stronger buyer leverage.",
        "ls_title": "Listings vs Sales",
        "ls_caption": "When listings rise faster than sales, buyer negotiation power usually increases.",
        "price_title": "Median Price Trend",
        "price_caption": "Price growth slowdown may indicate a cooling market.",
        "market_signal": "NC Market Signal",
        "signal_summary": "Signal Summary",
        "signal_framework_note": "This section combines current inventory position, year-over-year signals, and short-term trend confirmation.",
        "signal_details": "Signal Details",
        "signal_notes": "Signal Notes",
        "current_moi_zone": "Current MOI Zone",
        "demand_signal": "Demand Signal",
        "price_signal": "Price Signal",
        "supply_signal": "Supply Signal",
        "moi_trend_3m": "MOI Trend (3M Rolling)",
        "overall_market": "Overall Market",
        "how_to_read": "How to Read This Dashboard",
        "how_to_read_text": (
            "Current MOI Zone shows where the market stands right now based on the latest inventory level. "
            "Demand Signal uses Sales YoY, Price Signal uses Price YoY, and Supply Signal uses Listings YoY. "
            "MOI Trend compares the latest 3-month rolling average of inventory with the previous 3-month rolling average. "
            "Overall Market combines current MOI zone, YoY signals, and short-term inventory trend into one market interpretation."
        ),
        "show_latest_rows": "Show latest rows",
        "market_zone_table_title": "MOI Interpretation Guide",
        "moi_range": "MOI Range",
        "market_interpretation": "Market Interpretation",
        "seller_zone": "Seller-Leaning",
        "balanced_zone": "Balanced",
        "buyer_zone": "Buyer-Leaning",
        "report_month": "Report Month",
        "months_inventory": "MOI",
        "mom_inventory_pct": "MoM Inventory %",
        "mom_sales_pct": "MoM Sales %",
        "mom_price_pct": "MoM Price %",
        "yoy_listings_pct": "Listings YoY %",
        "yoy_sales_pct": "Sales YoY %",
        "yoy_price_pct": "Price YoY %",
        "Rising": "Rising",
        "Falling": "Falling",
        "Stable": "Stable",
        "Improving": "Improving",
        "Weakening": "Weakening",
        "Softening": "Softening",
        "Expanding": "Expanding",
        "Tightening": "Tightening",
        "Buyer-Leaning": "Buyer-Leaning",
        "Seller-Leaning": "Seller-Leaning",
        "Balanced": "Balanced",
        "market_zone": "Market Zone",
        "value": "Value",
        "series": "Series",
        "selected_data_points": "Selected data points",
        "sales_yoy": "Sales YoY",
        "price_yoy": "Price YoY",
        "listings_yoy": "Listings YoY",
        "hero_title": "North Carolina Market Pulse",
        "hero_subtitle": "Track inventory, supply, demand, pricing, and market balance using a cleaner signal framework built for market monitoring and real estate storytelling.",
        "hero_chip_1": "Current Market Position",
        "hero_chip_2": "YoY Signal Framework",
        "hero_chip_3": "3M Rolling Inventory Trend",
        "hero_chip_4": "Buyer vs Seller Balance",
        "kpi_note_latest_month": "Selected endpoint",
        "kpi_note_inventory": "Current inventory level",
        "kpi_note_listings": "Latest monthly supply",
        "kpi_note_sales": "Latest monthly demand",
        "kpi_note_price": "Latest monthly pricing",
    },
    "zh": {
        "page_title": "📊 北卡房地产市场脉搏",
        "page_caption": "基于月度分析结果构建的北卡房地产市场专业仪表盘。",
        "lang_en": "English",
        "lang_zh": "中文",
        "filters": "筛选条件",
        "month_window": "月份范围",
        "time_range": "时间范围",
        "year_filter": "年份筛选",
        "all_years": "全部年份",
        "last_12m": "最近12个月",
        "last_24m": "最近24个月",
        "last_36m": "最近36个月",
        "ytd": "今年至今",
        "all_data": "全部",
        "missing_file": "缺少 data/analytics/monthly_metrics.csv 文件。\n\n请运行：\n\npython run_full_pipeline.py --workers 4",
        "missing_cols": "monthly_metrics.csv 缺少必要字段：",
        "no_data_range": "当前选择的月份范围内没有数据。",
        "latest_month": "最新月份",
        "inventory_months": "库存（月）",
        "listings": "新挂牌",
        "sales": "成交量",
        "median_price": "中位价",
        "headline_title": "北卡房地产市场概览",
        "headline_caption": "从库存、需求和价格三个维度观察市场变化。",
        "inventory_chart_title": "北卡库存趋势（MOI, Months of Inventory）",
        "inventory_chart_caption": "MOI 由 NC REALTORS 月报直接提供或基于其字段整理。数值越高，通常意味着库存更充足、买方议价能力更强。",
        "ls_title": "新挂牌 vs 成交",
        "ls_caption": "当挂牌增长快于成交时，买方谈判能力通常增强。",
        "price_title": "中位价趋势",
        "price_caption": "价格涨幅放缓，可能意味着市场正在降温。",
        "market_signal": "北卡市场信号",
        "signal_summary": "信号总结",
        "signal_framework_note": "这一部分综合了当前库存位置、同比信号和短期趋势确认。",
        "signal_details": "信号明细",
        "signal_notes": "信号说明",
        "current_moi_zone": "当前 MOI 区间",
        "demand_signal": "需求信号",
        "price_signal": "价格信号",
        "supply_signal": "供给信号",
        "moi_trend_3m": "MOI 趋势（3个月滚动）",
        "overall_market": "整体市场",
        "how_to_read": "这块仪表盘怎么读",
        "how_to_read_text": (
            "当前 MOI 区间用于判断市场此刻所处的位置。"
            "需求信号使用 Sales YoY，价格信号使用 Price YoY，供给信号使用 Listings YoY。"
            "MOI 趋势通过比较“最近一个3个月滚动均值”和“前一个3个月滚动均值”来判断短期库存压力。"
            "整体市场会综合当前 MOI 区间、同比信号和短期库存趋势，给出最终市场定性。"
        ),
        "show_latest_rows": "查看最近数据",
        "market_zone_table_title": "MOI 市场区间说明",
        "moi_range": "MOI区间",
        "market_interpretation": "市场解读",
        "seller_zone": "偏卖方市场",
        "balanced_zone": "均衡市场",
        "buyer_zone": "偏买方市场",
        "report_month": "报告月份",
        "months_inventory": "MOI",
        "mom_inventory_pct": "库存环比%",
        "mom_sales_pct": "成交环比%",
        "mom_price_pct": "价格环比%",
        "yoy_listings_pct": "挂牌同比%",
        "yoy_sales_pct": "成交同比%",
        "yoy_price_pct": "价格同比%",
        "Rising": "上升",
        "Falling": "下降",
        "Stable": "稳定",
        "Improving": "改善",
        "Weakening": "走弱",
        "Softening": "走软",
        "Expanding": "扩张",
        "Tightening": "收紧",
        "Buyer-Leaning": "偏买方市场",
        "Seller-Leaning": "偏卖方市场",
        "Balanced": "均衡市场",
        "market_zone": "市场区间",
        "value": "数值",
        "series": "系列",
        "selected_data_points": "当前数据点数",
        "sales_yoy": "成交同比",
        "price_yoy": "价格同比",
        "listings_yoy": "挂牌同比",
        "hero_title": "北卡房地产市场脉搏",
        "hero_subtitle": "用更清晰的信号框架跟踪库存、供给、需求、价格和市场平衡，适合做市场监测，也适合对客户讲市场故事。",
        "hero_chip_1": "当前市场位置",
        "hero_chip_2": "同比信号框架",
        "hero_chip_3": "3个月滚动库存趋势",
        "hero_chip_4": "买卖方力量平衡",
        "kpi_note_latest_month": "当前筛选终点",
        "kpi_note_inventory": "当前库存水平",
        "kpi_note_listings": "最新月度供给",
        "kpi_note_sales": "最新月度需求",
        "kpi_note_price": "最新月度价格",
    },
}


def tr(key: str, lang: str) -> str:
    return TEXT[lang].get(key, key)


# -----------------------------
# data loading
# -----------------------------
@st.cache_data(ttl=60)
def load_monthly_metrics(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()

    df = pd.read_csv(path)

    if "report_month" in df.columns:
        df["report_month"] = df["report_month"].astype(str)
        df = df.sort_values("report_month")

    num_cols = [
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
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    if "report_month" in df.columns:
        df["report_month_dt"] = pd.to_datetime(df["report_month"] + "-01", errors="coerce")
        df["report_year"] = df["report_month_dt"].dt.year.astype("Int64")

    return df


# -----------------------------
# helpers
# -----------------------------
def fmt_int(x) -> str:
    if x is None or pd.isna(x):
        return "N/A"
    return f"{int(x):,}"


def fmt_float(x, digits: int = 2) -> str:
    if x is None or pd.isna(x):
        return "N/A"
    return f"{x:.{digits}f}"


def fmt_pct(x, digits: int = 1) -> str:
    if x is None or pd.isna(x):
        return "N/A"
    return f"{x:.{digits}f}%"


def latest_value(df: pd.DataFrame, col: str):
    if col not in df.columns:
        return None
    s = df[col].dropna()
    return s.iloc[-1] if len(s) else None


def localized_label(raw_key: str, lang: str) -> str:
    return tr(raw_key, lang)


# -----------------------------
# signal logic
# -----------------------------
def moi_zone(moi: float | None) -> str:
    if moi is None or pd.isna(moi):
        return "Balanced"
    if moi < 5:
        return "Seller-Leaning"
    if moi <= 6:
        return "Balanced"
    return "Buyer-Leaning"


def demand_signal(yoy_sales: float | None) -> str:
    if yoy_sales is None or pd.isna(yoy_sales):
        return "Stable"
    if yoy_sales > 5:
        return "Improving"
    if yoy_sales < -5:
        return "Weakening"
    return "Stable"


def price_signal(yoy_price: float | None) -> str:
    if yoy_price is None or pd.isna(yoy_price):
        return "Stable"
    if yoy_price > 3:
        return "Rising"
    if yoy_price < -3:
        return "Softening"
    return "Stable"


def supply_signal(yoy_listings: float | None) -> str:
    if yoy_listings is None or pd.isna(yoy_listings):
        return "Stable"
    if yoy_listings > 5:
        return "Expanding"
    if yoy_listings < -5:
        return "Tightening"
    return "Stable"


def moi_trend_3m(view: pd.DataFrame) -> str:
    s = view.sort_values("report_month_dt")["months_inventory"].dropna().reset_index(drop=True)
    if len(s) < 6:
        return "Stable"

    rolling = s.rolling(3).mean().dropna().reset_index(drop=True)
    if len(rolling) < 2:
        return "Stable"

    delta = rolling.iloc[-1] - rolling.iloc[-2]

    if delta > 0.05:
        return "Rising"
    if delta < -0.05:
        return "Falling"
    return "Stable"


def overall_market(
    current_zone: str,
    demand: str,
    price: str,
    supply: str,
    moi_trend: str,
) -> str:
    zone_score = {
        "Seller-Leaning": -1,
        "Balanced": 0,
        "Buyer-Leaning": 1,
    }

    score = zone_score.get(current_zone, 0)

    if demand == "Improving":
        score -= 1
    elif demand == "Weakening":
        score += 1

    if price == "Rising":
        score -= 1
    elif price == "Softening":
        score += 1

    if supply == "Expanding":
        score += 1
    elif supply == "Tightening":
        score -= 1

    if moi_trend == "Rising":
        score += 1
    elif moi_trend == "Falling":
        score -= 1

    if score <= -2:
        return "Seller-Leaning"
    if score >= 2:
        return "Buyer-Leaning"
    return "Balanced"


# -----------------------------
# signal UI
# -----------------------------
def signal_badge_config(signal_key: str) -> dict:
    mapping = {
        "Seller-Leaning": {"icon": "🔥", "bg": "#FEF2F2", "border": "#FCA5A5", "text": "#991B1B"},
        "Buyer-Leaning": {"icon": "🧊", "bg": "#EFF6FF", "border": "#93C5FD", "text": "#1D4ED8"},
        "Balanced": {"icon": "⚖️", "bg": "#F9FAFB", "border": "#D1D5DB", "text": "#374151"},
        "Improving": {"icon": "📈", "bg": "#ECFDF5", "border": "#86EFAC", "text": "#166534"},
        "Weakening": {"icon": "📉", "bg": "#FEF2F2", "border": "#FCA5A5", "text": "#991B1B"},
        "Rising": {"icon": "⬆️", "bg": "#FFF7ED", "border": "#FDBA74", "text": "#9A3412"},
        "Softening": {"icon": "⬇️", "bg": "#EFF6FF", "border": "#93C5FD", "text": "#1D4ED8"},
        "Expanding": {"icon": "🏗️", "bg": "#EFF6FF", "border": "#93C5FD", "text": "#1D4ED8"},
        "Tightening": {"icon": "🔒", "bg": "#FFF7ED", "border": "#FDBA74", "text": "#9A3412"},
        "Stable": {"icon": "➖", "bg": "#F9FAFB", "border": "#D1D5DB", "text": "#374151"},
        "Falling": {"icon": "📉", "bg": "#FEF2F2", "border": "#FCA5A5", "text": "#991B1B"},
    }
    return mapping.get(signal_key, {"icon": "•", "bg": "#F9FAFB", "border": "#D1D5DB", "text": "#374151"})


def render_signal_card(title: str, signal_raw: str, signal_display: str, subtext: str) -> None:
    cfg = signal_badge_config(signal_raw)

    st.markdown(
        f"""
        <div class="signal-card" style="background:{cfg['bg']}; border-color:{cfg['border']};">
            <div class="signal-title">{title}</div>
            <div class="signal-main">
                <div class="signal-icon">{cfg['icon']}</div>
                <div class="signal-value" style="color:{cfg['text']};">{signal_display}</div>
            </div>
            <div class="signal-badge" style="color:{cfg['text']}; border:1px solid {cfg['border']};">
                {signal_raw}
            </div>
            <div class="signal-subtext">{subtext}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_overall_market_box(overall_raw: str, overall_display: str, latest_month: str, lang: str) -> None:
    cfg = signal_badge_config(overall_raw)
    subtitle = (
        f"截至 {latest_month} 的综合市场判断"
        if lang == "zh"
        else f"Composite market read as of {latest_month}"
    )

    st.markdown(
        f"""
        <div class="overall-card" style="background:{cfg['bg']}; border-color:{cfg['border']};">
            <div class="overall-label">{tr("overall_market", lang)}</div>
            <div class="overall-main">
                <div class="overall-icon">{cfg['icon']}</div>
                <div class="overall-value" style="color:{cfg['text']};">{overall_display}</div>
            </div>
            <div class="overall-badge" style="color:{cfg['text']}; border:1px solid {cfg['border']};">
                {overall_raw}
            </div>
            <div class="overall-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def signal_explainer(signal_type: str, signal_raw: str, lang: str) -> str:
    if lang == "zh":
        mapping = {
            ("zone", "Seller-Leaning"): "当前库存偏低，卖方相对更有议价优势。",
            ("zone", "Balanced"): "当前库存处于相对均衡区间，买卖双方力量较接近。",
            ("zone", "Buyer-Leaning"): "当前库存偏高，买方通常有更多选择和谈判空间。",
            ("demand", "Improving"): "成交同比明显改善，说明需求比去年同期更强。",
            ("demand", "Stable"): "成交同比波动不大，需求整体相对平稳。",
            ("demand", "Weakening"): "成交同比走弱，说明需求较去年同期偏弱。",
            ("price", "Rising"): "价格同比上涨较明显，价格韧性仍在。",
            ("price", "Stable"): "价格同比变化有限，价格整体较稳。",
            ("price", "Softening"): "价格同比偏弱，价格有走软迹象。",
            ("supply", "Expanding"): "挂牌同比增加，市场供给正在扩张。",
            ("supply", "Stable"): "挂牌同比变化不大，供给整体稳定。",
            ("supply", "Tightening"): "挂牌同比下降，供给相对收紧。",
            ("trend", "Rising"): "3个月滚动 MOI 上升，短期库存压力在增加。",
            ("trend", "Stable"): "3个月滚动 MOI 变化不大，短期趋势相对平稳。",
            ("trend", "Falling"): "3个月滚动 MOI 下降，短期库存压力在缓解。",
        }
    else:
        mapping = {
            ("zone", "Seller-Leaning"): "Inventory is relatively tight, which usually favors sellers.",
            ("zone", "Balanced"): "Inventory is in a more balanced range, with neither side clearly dominating.",
            ("zone", "Buyer-Leaning"): "Inventory is relatively elevated, which usually gives buyers more leverage.",
            ("demand", "Improving"): "Sales are meaningfully stronger than a year ago, pointing to firmer demand.",
            ("demand", "Stable"): "Sales are close to last year's level, suggesting fairly stable demand.",
            ("demand", "Weakening"): "Sales are softer than a year ago, suggesting demand has weakened.",
            ("price", "Rising"): "Prices are showing solid year-over-year growth.",
            ("price", "Stable"): "Prices are relatively steady compared with a year ago.",
            ("price", "Softening"): "Price growth is weak or negative, suggesting softer pricing conditions.",
            ("supply", "Expanding"): "Listings are up from a year ago, so supply is expanding.",
            ("supply", "Stable"): "Listings are close to last year's level, so supply is fairly stable.",
            ("supply", "Tightening"): "Listings are down from a year ago, so supply is tightening.",
            ("trend", "Rising"): "The 3-month rolling MOI is rising, which points to increasing short-term inventory pressure.",
            ("trend", "Stable"): "The 3-month rolling MOI is relatively flat, suggesting a stable short-term trend.",
            ("trend", "Falling"): "The 3-month rolling MOI is falling, which points to easing short-term inventory pressure.",
        }
    return mapping.get((signal_type, signal_raw), "")


def build_signal_summary(
    latest_month: str,
    latest_moi: float | None,
    current_zone: str,
    yoy_sales: float | None,
    demand: str,
    yoy_price: float | None,
    price: str,
    yoy_listings: float | None,
    supply: str,
    moi_trend: str,
    overall: str,
    lang: str,
) -> str:
    moi_text = fmt_float(latest_moi, 2)
    sales_yoy_text = fmt_pct(yoy_sales, 1)
    price_yoy_text = fmt_pct(yoy_price, 1)
    listings_yoy_text = fmt_pct(yoy_listings, 1)

    if lang == "zh":
        return (
            f"截至 {latest_month}，北卡市场当前 MOI 为 {moi_text}，"
            f"处于“{localized_label(current_zone, lang)}”区间。"
            f"成交同比为 {sales_yoy_text}，对应“{localized_label(demand, lang)}”；"
            f"价格同比为 {price_yoy_text}，对应“{localized_label(price, lang)}”；"
            f"挂牌同比为 {listings_yoy_text}，对应“{localized_label(supply, lang)}”。"
            f"同时，3个月滚动 MOI 趋势为“{localized_label(moi_trend, lang)}”。"
            f"综合来看，当前市场更适合定义为“{localized_label(overall, lang)}”。"
        )

    return (
        f"As of {latest_month}, North Carolina's MOI is {moi_text}, placing the market in a "
        f"“{localized_label(current_zone, lang)}” zone. "
        f"Sales YoY is {sales_yoy_text}, which reads as “{localized_label(demand, lang)}”. "
        f"Price YoY is {price_yoy_text}, which reads as “{localized_label(price, lang)}”. "
        f"Listings YoY is {listings_yoy_text}, which reads as “{localized_label(supply, lang)}”. "
        f"The 3-month rolling MOI trend is “{localized_label(moi_trend, lang)}”. "
        f"Taken together, the market is best described as “{localized_label(overall, lang)}”."
    )


# -----------------------------
# filtering
# -----------------------------
def apply_time_range(df: pd.DataFrame, time_range: str) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    df = df.sort_values("report_month_dt").copy()

    if time_range == "12M":
        return df.tail(12).copy()
    if time_range == "24M":
        return df.tail(24).copy()
    if time_range == "36M":
        return df.tail(36).copy()
    if time_range == "YTD":
        latest_year = int(df["report_year"].dropna().max())
        return df[df["report_year"] == latest_year].copy()

    return df.copy()


def axis_config_for_span(num_points: int, lang: str) -> alt.Axis:
    if num_points > 36:
        return alt.Axis(format="%Y", labelAngle=0, labelOverlap=True, grid=False, title=tr("report_month", lang), tickCount=8)
    if num_points > 18:
        return alt.Axis(format="%Y-%m", labelAngle=-35, labelOverlap=False, grid=False, title=tr("report_month", lang), tickCount=12)
    return alt.Axis(format="%Y-%m", labelAngle=-35, labelOverlap=False, grid=False, title=tr("report_month", lang), tickCount=max(num_points, 2))


# -----------------------------
# charts
# -----------------------------
def build_interactive_line_chart(
    chart_df: pd.DataFrame,
    x_col: str,
    y_col: str,
    lang: str,
    y_title: str,
    color_value: str | None = None,
    tooltip_fields: list | None = None,
    y_scale_domain: list[float] | None = None,
    height: int = 360,
    add_last_label: bool = True,
):
    num_points = len(chart_df)
    base = alt.Chart(chart_df)

    nearest = alt.selection_point(nearest=True, on="mouseover", fields=[x_col], empty="none")

    y_encoding = alt.Y(
        f"{y_col}:Q",
        title=y_title,
        scale=alt.Scale(domain=y_scale_domain) if y_scale_domain else alt.Undefined,
    )

    x_encoding = alt.X(f"{x_col}:T", axis=axis_config_for_span(num_points, lang))

    point_size = 30 if num_points > 36 else 42 if num_points > 24 else 50

    line = base.mark_line(strokeWidth=3).encode(
        x=x_encoding,
        y=y_encoding,
        color=alt.value(color_value) if color_value else alt.Undefined,
    )

    points = base.mark_point(filled=True, size=point_size).encode(
        x=x_encoding,
        y=y_encoding,
        color=alt.value(color_value) if color_value else alt.Undefined,
    )

    selectors = base.mark_point(opacity=0).encode(x=x_encoding).add_params(nearest)
    rule = base.mark_rule(color="#9CA3AF").encode(x=x_encoding).transform_filter(nearest)

    default_tooltips = [
        alt.Tooltip("report_month:N", title=tr("report_month", lang)),
        alt.Tooltip(f"{y_col}:Q", title=y_title, format=",.2f"),
    ]
    tooltips = tooltip_fields if tooltip_fields else default_tooltips

    hover_points = base.mark_point(size=95, filled=True).encode(
        x=x_encoding,
        y=y_encoding,
        opacity=alt.condition(nearest, alt.value(1), alt.value(0)),
        tooltip=tooltips,
        color=alt.value(color_value) if color_value else alt.Undefined,
    )

    chart = alt.layer(line, points, selectors, rule, hover_points).properties(height=height)

    if add_last_label and not chart_df.empty:
        last_df = chart_df.tail(1)
        last_point = alt.Chart(last_df).mark_point(size=95, filled=True).encode(
            x=x_encoding,
            y=y_encoding,
            color=alt.value(color_value) if color_value else alt.Undefined,
        )
        last_label = alt.Chart(last_df).mark_text(
            align="left",
            dx=8,
            dy=-8,
            fontSize=12,
            fontWeight="bold",
        ).encode(
            x=x_encoding,
            y=y_encoding,
            text=alt.Text(f"{y_col}:Q", format=".2f"),
        )
        chart = alt.layer(chart, last_point, last_label).properties(height=height)

    return chart


def build_interactive_multi_line_chart(
    chart_df: pd.DataFrame,
    x_col: str,
    y_col: str,
    series_col: str,
    lang: str,
    y_title: str,
    height: int = 360,
):
    num_points = chart_df["report_month"].nunique()
    base = alt.Chart(chart_df)

    nearest = alt.selection_point(nearest=True, on="mouseover", fields=[x_col], empty="none")

    x_encoding = alt.X(f"{x_col}:T", axis=axis_config_for_span(num_points, lang))
    y_encoding = alt.Y(f"{y_col}:Q", title=y_title)
    color_encoding = alt.Color(f"{series_col}:N", title="", legend=alt.Legend(orient="right"))

    point_size = 28 if num_points > 36 else 38 if num_points > 24 else 45

    line = base.mark_line(strokeWidth=2.8).encode(x=x_encoding, y=y_encoding, color=color_encoding)
    points = base.mark_point(filled=True, size=point_size).encode(x=x_encoding, y=y_encoding, color=color_encoding)

    selectors = alt.Chart(chart_df[[x_col]].drop_duplicates()).mark_point(opacity=0).encode(x=x_encoding).add_params(nearest)
    rule = alt.Chart(chart_df[[x_col]].drop_duplicates()).mark_rule(color="#9CA3AF").encode(x=x_encoding).transform_filter(nearest)

    hover_points = base.mark_point(size=100, filled=True).encode(
        x=x_encoding,
        y=y_encoding,
        color=color_encoding,
        opacity=alt.condition(nearest, alt.value(1), alt.value(0)),
        tooltip=[
            alt.Tooltip("report_month:N", title=tr("report_month", lang)),
            alt.Tooltip(f"{series_col}:N", title=tr("series", lang)),
            alt.Tooltip(f"{y_col}:Q", title=tr("value", lang), format=",.2f"),
        ],
    )

    chart = alt.layer(line, points, selectors, rule, hover_points).properties(height=height)

    last_points = (
        chart_df.sort_values([series_col, x_col])
        .groupby(series_col, as_index=False)
        .tail(1)
        .copy()
    )

    if not last_points.empty:
        last_point_marks = alt.Chart(last_points).mark_point(size=100, filled=True).encode(
            x=x_encoding,
            y=y_encoding,
            color=color_encoding,
        )
        last_labels = alt.Chart(last_points).mark_text(
            align="left",
            dx=8,
            dy=0,
            fontSize=11,
            fontWeight="bold",
        ).encode(
            x=x_encoding,
            y=y_encoding,
            color=color_encoding,
            text=alt.Text(f"{y_col}:Q", format=",.0f"),
        )
        chart = alt.layer(chart, last_point_marks, last_labels).properties(height=height)

    return chart


def render_inventory_chart(view: pd.DataFrame, lang: str) -> None:
    with st.container():
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">{tr("inventory_chart_title", lang)}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="section-caption">{tr("inventory_chart_caption", lang)}</div>', unsafe_allow_html=True)

        inv_chart_df = view[["report_month_dt", "report_month", "months_inventory"]].dropna().copy()
        if not inv_chart_df.empty:
            inv_chart_df["market_zone"] = inv_chart_df["months_inventory"].apply(moi_zone)
            inv_chart_df["market_zone_display"] = inv_chart_df["market_zone"].map(lambda x: localized_label(x, lang))

            y_max = max(7.0, float(inv_chart_df["months_inventory"].max()) + 0.6)

            balanced_band = alt.Chart(pd.DataFrame({"ymin": [5.0], "ymax": [6.0]})).mark_rect(opacity=0.12).encode(
                y=alt.Y("ymin:Q", scale=alt.Scale(domain=[0, y_max]), title="MOI (Months of Inventory)" if lang == "en" else "MOI（库存月数）"),
                y2="ymax:Q",
            )

            line_5 = alt.Chart(pd.DataFrame({"y": [5.0]})).mark_rule(
                strokeDash=[6, 4], size=1.5, color="#111827"
            ).encode(y=alt.Y("y:Q", scale=alt.Scale(domain=[0, y_max])))

            line_6 = alt.Chart(pd.DataFrame({"y": [6.0]})).mark_rule(
                strokeDash=[6, 4], size=1.5, color="#111827"
            ).encode(y=alt.Y("y:Q", scale=alt.Scale(domain=[0, y_max])))

            main_chart = build_interactive_line_chart(
                chart_df=inv_chart_df,
                x_col="report_month_dt",
                y_col="months_inventory",
                lang=lang,
                y_title="MOI (Months of Inventory)" if lang == "en" else "MOI（库存月数）",
                color_value="#1565C0",
                tooltip_fields=[
                    alt.Tooltip("report_month:N", title=tr("report_month", lang)),
                    alt.Tooltip("months_inventory:Q", title="MOI", format=".2f"),
                    alt.Tooltip("market_zone_display:N", title=tr("market_zone", lang)),
                ],
                y_scale_domain=[0, y_max],
                height=390,
                add_last_label=True,
            )

            inventory_chart = alt.layer(balanced_band, line_5, line_6, main_chart).resolve_scale(y="shared").properties(height=390)
            st.altair_chart(inventory_chart, use_container_width=True)

            st.markdown(f"**{tr('market_zone_table_title', lang)}**")
            zone_df = pd.DataFrame(
                {
                    tr("moi_range", lang): ["< 5.0", "5.0 – 6.0", "> 6.0"],
                    tr("market_interpretation", lang): [
                        tr("seller_zone", lang),
                        tr("balanced_zone", lang),
                        tr("buyer_zone", lang),
                    ],
                }
            )
            st.dataframe(zone_df, use_container_width=False, hide_index=True)

        st.markdown("</div>", unsafe_allow_html=True)


def render_listings_sales_chart(view: pd.DataFrame, lang: str) -> None:
    with st.container():
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">{tr("ls_title", lang)}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="section-caption">{tr("ls_caption", lang)}</div>', unsafe_allow_html=True)

        chart_df = view[["report_month_dt", "report_month", "listings", "sales"]].dropna(subset=["report_month_dt"]).copy()
        if not chart_df.empty:
            chart_df = chart_df.melt(
                id_vars=["report_month_dt", "report_month"],
                value_vars=["listings", "sales"],
                var_name="series_raw",
                value_name="value",
            )
            chart_df["series_display"] = chart_df["series_raw"].map(
                {"listings": tr("listings", lang), "sales": tr("sales", lang)}
            )

            chart = build_interactive_multi_line_chart(
                chart_df=chart_df,
                x_col="report_month_dt",
                y_col="value",
                series_col="series_display",
                lang=lang,
                y_title=tr("value", lang),
                height=360,
            )
            st.altair_chart(chart, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)


def render_price_chart(view: pd.DataFrame, lang: str) -> None:
    with st.container():
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">{tr("price_title", lang)}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="section-caption">{tr("price_caption", lang)}</div>', unsafe_allow_html=True)

        price_df = view[["report_month_dt", "report_month", "median_price"]].dropna().copy()
        if not price_df.empty:
            chart = build_interactive_line_chart(
                chart_df=price_df,
                x_col="report_month_dt",
                y_col="median_price",
                lang=lang,
                y_title=tr("median_price", lang),
                color_value="#1E88E5",
                tooltip_fields=[
                    alt.Tooltip("report_month:N", title=tr("report_month", lang)),
                    alt.Tooltip("median_price:Q", title=tr("median_price", lang), format=",.0f"),
                ],
                height=360,
                add_last_label=True,
            )
            st.altair_chart(chart, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# language switch
# -----------------------------
if "lang" not in st.session_state:
    st.session_state.lang = "en"

lang_col1, lang_col2, _ = st.columns([1, 1, 8])
with lang_col1:
    if st.button("English", use_container_width=True):
        st.session_state.lang = "en"
with lang_col2:
    if st.button("中文", use_container_width=True):
        st.session_state.lang = "zh"

lang = st.session_state.lang


# -----------------------------
# load data
# -----------------------------
df = load_monthly_metrics(DATA_PATH)
if df.empty:
    st.error(tr("missing_file", lang))
    st.stop()

required = {
    "report_month",
    "report_month_dt",
    "report_year",
    "listings",
    "sales",
    "median_price",
    "months_inventory",
    "yoy_listings_pct",
    "yoy_sales_pct",
    "yoy_price_pct",
}
missing = [c for c in required if c not in df.columns]
if missing:
    st.error(f"{tr('missing_cols', lang)} {missing}")
    st.stop()


# -----------------------------
# sidebar filters
# -----------------------------
st.sidebar.header(tr("filters", lang))

time_range_map = {
    tr("last_12m", lang): "12M",
    tr("last_24m", lang): "24M",
    tr("last_36m", lang): "36M",
    tr("ytd", lang): "YTD",
    tr("all_data", lang): "ALL",
}

selected_time_range_label = st.sidebar.radio(
    tr("time_range", lang),
    options=list(time_range_map.keys()),
    index=1,
)

selected_time_range = time_range_map[selected_time_range_label]

years = sorted([int(y) for y in df["report_year"].dropna().unique().tolist()])
year_options = [tr("all_years", lang)] + [str(y) for y in years]

selected_year = st.sidebar.selectbox(
    tr("year_filter", lang),
    options=year_options,
    index=0,
)

filtered = df.copy()

if selected_year != tr("all_years", lang):
    filtered = filtered[filtered["report_year"] == int(selected_year)].copy()

filtered = apply_time_range(filtered, selected_time_range)

if filtered.empty:
    st.warning(tr("no_data_range", lang))
    st.stop()

month_options = filtered["report_month"].dropna().astype(str).tolist()
min_m = min(month_options)
max_m = max(month_options)

month_window = st.sidebar.select_slider(
    tr("month_window", lang),
    options=month_options,
    value=(min_m, max_m),
)

start_month, end_month = month_window
mask = (filtered["report_month"] >= start_month) & (filtered["report_month"] <= end_month)
view = filtered.loc[mask].copy().sort_values("report_month_dt")

if view.empty:
    st.warning(tr("no_data_range", lang))
    st.stop()


# -----------------------------
# latest values
# -----------------------------
latest_month = str(view["report_month"].iloc[-1])
inventory_val = latest_value(view, "months_inventory")
listings_val = latest_value(view, "listings")
sales_val = latest_value(view, "sales")
price_val = latest_value(view, "median_price")
latest_yoy_sales = latest_value(view, "yoy_sales_pct")
latest_yoy_price = latest_value(view, "yoy_price_pct")
latest_yoy_listings = latest_value(view, "yoy_listings_pct")


# -----------------------------
# hero
# -----------------------------
st.markdown(
    f"""
    <div class="hero-box">
        <div class="hero-title">{tr("hero_title", lang)}</div>
        <div class="hero-subtitle">{tr("hero_subtitle", lang)}</div>
        <div class="chip-row">
            <span class="chip">{tr("hero_chip_1", lang)}</span>
            <span class="chip">{tr("hero_chip_2", lang)}</span>
            <span class="chip">{tr("hero_chip_3", lang)}</span>
            <span class="chip">{tr("hero_chip_4", lang)}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# top KPIs
# -----------------------------
st.markdown(f'<div class="section-title">{tr("headline_title", lang)}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="section-caption">{tr("headline_caption", lang)}</div>', unsafe_allow_html=True)

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.metric(tr("latest_month", lang), latest_month)
    st.caption(tr("kpi_note_latest_month", lang))
with k2:
    st.metric(tr("inventory_months", lang), fmt_float(inventory_val, 2))
    st.caption(tr("kpi_note_inventory", lang))
with k3:
    st.metric(tr("listings", lang), fmt_int(listings_val))
    st.caption(tr("kpi_note_listings", lang))
with k4:
    st.metric(tr("sales", lang), fmt_int(sales_val))
    st.caption(tr("kpi_note_sales", lang))
with k5:
    st.metric(tr("median_price", lang), fmt_int(price_val))
    st.caption(tr("kpi_note_price", lang))

st.caption(f"{tr('selected_data_points', lang)}: {len(view)}")


# -----------------------------
# charts
# -----------------------------
render_inventory_chart(view, lang)
render_listings_sales_chart(view, lang)
render_price_chart(view, lang)


# -----------------------------
# signal calculation
# -----------------------------
current_moi_zone_raw = moi_zone(inventory_val)
demand_signal_raw = demand_signal(latest_yoy_sales)
price_signal_raw = price_signal(latest_yoy_price)
supply_signal_raw = supply_signal(latest_yoy_listings)
moi_trend_raw = moi_trend_3m(view)

overall_raw = overall_market(
    current_zone=current_moi_zone_raw,
    demand=demand_signal_raw,
    price=price_signal_raw,
    supply=supply_signal_raw,
    moi_trend=moi_trend_raw,
)

current_moi_zone_display = localized_label(current_moi_zone_raw, lang)
demand_signal_display = localized_label(demand_signal_raw, lang)
price_signal_display = localized_label(price_signal_raw, lang)
supply_signal_display = localized_label(supply_signal_raw, lang)
moi_trend_display = localized_label(moi_trend_raw, lang)
overall_display = localized_label(overall_raw, lang)


# -----------------------------
# market signal section
# -----------------------------
with st.container():
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{tr("market_signal", lang)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-caption">{tr("signal_framework_note", lang)}</div>', unsafe_allow_html=True)

    row1 = st.columns(3)
    row2 = st.columns(2)

    with row1[0]:
        render_signal_card(
            title=tr("current_moi_zone", lang),
            signal_raw=current_moi_zone_raw,
            signal_display=current_moi_zone_display,
            subtext=f"MOI: {fmt_float(inventory_val, 2)} · {signal_explainer('zone', current_moi_zone_raw, lang)}",
        )

    with row1[1]:
        render_signal_card(
            title=tr("demand_signal", lang),
            signal_raw=demand_signal_raw,
            signal_display=demand_signal_display,
            subtext=f"{tr('sales_yoy', lang)}: {fmt_pct(latest_yoy_sales, 1)} · {signal_explainer('demand', demand_signal_raw, lang)}",
        )

    with row1[2]:
        render_signal_card(
            title=tr("price_signal", lang),
            signal_raw=price_signal_raw,
            signal_display=price_signal_display,
            subtext=f"{tr('price_yoy', lang)}: {fmt_pct(latest_yoy_price, 1)} · {signal_explainer('price', price_signal_raw, lang)}",
        )

    with row2[0]:
        render_signal_card(
            title=tr("supply_signal", lang),
            signal_raw=supply_signal_raw,
            signal_display=supply_signal_display,
            subtext=f"{tr('listings_yoy', lang)}: {fmt_pct(latest_yoy_listings, 1)} · {signal_explainer('supply', supply_signal_raw, lang)}",
        )

    with row2[1]:
        render_signal_card(
            title=tr("moi_trend_3m", lang),
            signal_raw=moi_trend_raw,
            signal_display=moi_trend_display,
            subtext=signal_explainer("trend", moi_trend_raw, lang),
        )

    st.markdown("")

    left_col, right_col = st.columns([2, 3])

    with left_col:
        render_overall_market_box(
            overall_raw=overall_raw,
            overall_display=overall_display,
            latest_month=latest_month,
            lang=lang,
        )

        st.markdown(f"### {tr('signal_details', lang)}")
        detail_df = pd.DataFrame(
            {
                "Metric": [
                    tr("current_moi_zone", lang),
                    tr("demand_signal", lang),
                    tr("price_signal", lang),
                    tr("supply_signal", lang),
                    tr("moi_trend_3m", lang),
                ],
                "Value": [
                    f"{current_moi_zone_display} (MOI {fmt_float(inventory_val, 2)})",
                    f"{demand_signal_display} ({fmt_pct(latest_yoy_sales, 1)})",
                    f"{price_signal_display} ({fmt_pct(latest_yoy_price, 1)})",
                    f"{supply_signal_display} ({fmt_pct(latest_yoy_listings, 1)})",
                    moi_trend_display,
                ],
            }
        )
        st.dataframe(detail_df, use_container_width=True, hide_index=True)

    with right_col:
        st.markdown(f"### {tr('signal_summary', lang)}")
        st.info(
            build_signal_summary(
                latest_month=latest_month,
                latest_moi=inventory_val,
                current_zone=current_moi_zone_raw,
                yoy_sales=latest_yoy_sales,
                demand=demand_signal_raw,
                yoy_price=latest_yoy_price,
                price=price_signal_raw,
                yoy_listings=latest_yoy_listings,
                supply=supply_signal_raw,
                moi_trend=moi_trend_raw,
                overall=overall_raw,
                lang=lang,
            )
        )

        with st.expander(tr("signal_notes", lang)):
            if lang == "zh":
                st.write(
                    "Current MOI Zone 用来定义市场当前所处位置；"
                    "Demand / Price / Supply Signals 使用同比数据减少季节性误判；"
                    "MOI Trend (3M Rolling) 用于确认短期库存压力是上升、下降还是平稳；"
                    "Overall Market 则综合以上信息给出最终结论。"
                )
            else:
                st.write(
                    "Current MOI Zone defines where the market stands right now. "
                    "Demand / Price / Supply Signals use year-over-year comparisons to reduce seasonality noise. "
                    "MOI Trend (3M Rolling) confirms whether short-term inventory pressure is rising, falling, or stable. "
                    "Overall Market combines all of these into one market conclusion."
                )

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# bottom explainers
# -----------------------------
with st.container():
    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    with st.expander(tr("how_to_read", lang)):
        st.write(tr("how_to_read_text", lang))

    with st.expander(tr("show_latest_rows", lang)):
        latest_rows = view[
            [
                "report_month",
                "months_inventory",
                "listings",
                "sales",
                "median_price",
                "yoy_listings_pct",
                "yoy_sales_pct",
                "yoy_price_pct",
                "mom_inventory_pct",
                "mom_sales_pct",
                "mom_price_pct",
            ]
        ].tail(24).copy()

        latest_rows = latest_rows.rename(
            columns={
                "report_month": tr("report_month", lang),
                "months_inventory": tr("months_inventory", lang),
                "listings": tr("listings", lang),
                "sales": tr("sales", lang),
                "median_price": tr("median_price", lang),
                "yoy_listings_pct": tr("yoy_listings_pct", lang),
                "yoy_sales_pct": tr("yoy_sales_pct", lang),
                "yoy_price_pct": tr("yoy_price_pct", lang),
                "mom_inventory_pct": tr("mom_inventory_pct", lang),
                "mom_sales_pct": tr("mom_sales_pct", lang),
                "mom_price_pct": tr("mom_price_pct", lang),
            }
        )

        st.dataframe(latest_rows, use_container_width=True, hide_index=True)

    st.markdown("</div>", unsafe_allow_html=True)