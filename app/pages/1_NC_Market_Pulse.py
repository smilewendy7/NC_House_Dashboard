from __future__ import annotations

import sys
from pathlib import Path
from html import escape
import math
import re

import altair as alt
import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.append(str(APP_DIR))

from shared_ui import (
    inject_base_css,
    render_global_sidebar,
    get_locale,
    get_budget_k,
)

st.set_page_config(
    page_title="NC Market Pulse / 北卡市场总览",
    page_icon="📈",
    layout="wide",
)

DATA_PATH = Path("data/analytics/monthly_metrics.csv")
alt.data_transformers.disable_max_rows()


# =========================================================
# i18n
# =========================================================
TEXT = {
    "en": {
        "title": "NC Market Pulse",
        "subtitle": "Statewide market analytics for buyers, investors, and advisors to assess inventory pressure, demand shifts, and pricing conditions more efficiently.",
        "hero_chip": "North Carolina Macro Market Analytics",

        "sidebar_preferences": "Preferences",
        "language": "Language",
        "budget_global": "Budget (USD, in $1,000s)",
        "budget_note": "This budget setting is shared across pages and can be adjusted anytime.",
        "selected_budget": "Selected Budget",

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

        "missing_file": "Missing `data/analytics/monthly_metrics.csv`.\n\nRun:\n\n`python run_full_pipeline.py --workers 4`",
        "missing_cols": "Missing required columns in monthly_metrics.csv:",
        "no_data_range": "No data is available in the selected month range.",

        "latest_month": "Latest Month",
        "inventory_months": "Inventory (MOI)",
        "listings": "Listings",
        "sales": "Sales",
        "median_price": "Median Price",

        "headline_title": "North Carolina Housing Snapshot",
        "headline_caption": "A statewide view of inventory pressure, demand conditions, and pricing direction.",

        "section_charts": "Market Structure",
        "section_charts_sub": "Use statewide signals to understand inventory, supply-demand balance, and pricing conditions before moving into local market and property-level analysis.",

        "inventory_chart_title": "Inventory Pressure Trend",
        "inventory_chart_caption": "Use Months of Inventory (MOI) to assess current choice and competition in the market. In general, higher MOI means more buyer choice and less competition, while lower MOI usually signals a tighter environment.",

        "ls_title": "Supply vs Demand Trend",
        "ls_caption": "By rebasing listings and sales to the same starting point (=100), this chart makes directional comparison easier. It helps users see whether supply is expanding faster than demand, or whether demand is recovering more quickly than supply.",
        "indexed_note": "Indexed View (Start = 100)",

        "price_title": "Median Price Trend",
        "price_caption": "Use the statewide median price trend to quickly understand the current pricing environment. This helps buyers, investors, and advisors judge whether price pressure is still building, stabilizing, or softening before moving into more detailed market comparisons.",
        "price_spotlight": "Price Context",
        "price_spotlight_sub": "Start with the statewide price trend to understand the broader pricing backdrop, then evaluate cities, neighborhoods, and individual properties with better context.",

        "market_signal": "NC Market Signal",
        "signal_summary": "Signal Summary",

        "current_moi_zone": "Current MOI Position",
        "demand_signal": "Demand Signal",
        "price_signal": "Price Signal",
        "supply_signal": "Supply Signal",
        "moi_trend_3m": "MOI Trend (3M)",
        "overall_market": "Overall Market Position",

        "how_to_read": "How to Read This Page",
        "how_to_read_text": (
            "This is a statewide macro market dashboard designed to help users understand the broader market environment before moving into city, neighborhood, and property-level analysis. "
            "Current MOI Position shows where the market stands now based on the latest inventory level. "
            "Demand Signal uses Sales YoY, Price Signal uses Price YoY, and Supply Signal uses Listings YoY. "
            "The 3-month MOI trend compares the latest 3-month rolling average with the prior 3-month rolling average to show short-term inventory direction. "
            "Overall Market Position combines current MOI, YoY signals, and short-term inventory trend into one higher-level market read. "
            "This page is useful for framing market conditions, improving communication, and supporting decision-making, but it should not replace local submarket, neighborhood, or property-level analysis."
        ),
        "show_latest_rows": "Show Latest Rows",

        "market_zone_table_title": "MOI Interpretation Guide",
        "moi_range": "MOI Range",
        "market_interpretation": "Interpretation",
        "seller_zone": "More Competitive",
        "balanced_zone": "Relatively Balanced",
        "buyer_zone": "More Buyer Room",

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

        "Buyer-Leaning": "More Buyer Room",
        "Seller-Leaning": "More Competitive",
        "Balanced": "Relatively Balanced",

        "market_zone": "Market Zone",
        "source_note": "Methodology",
        "source_note_text": (
            "Months of Inventory (MOI) = current listings divided by recent monthly sales pace. "
            "The MOI interpretation on this page is aligned with the Price Band Opportunities page: "
            "< 4 = more competitive, 4–6 = relatively balanced, > 6 = more buyer room. "
            "This is a market-structure metric, not a guarantee of negotiability for any individual property."
        ),
        "value": "Value",
        "series": "Series",
        "selected_data_points": "Selected Data Points",

        "as_of": "As of",
        "sales_yoy": "Sales YoY",
        "price_yoy": "Price YoY",
        "listings_yoy": "Listings YoY",

        "macro_note_title": "What this page is most useful for",
        "macro_note_body": (
            "- Understanding statewide market direction\n"
            "- Framing whether inventory pressure is easing or tightening\n"
            "- Giving buyers, investors, and clients a clearer macro context before discussing local choices\n\n"
            "**Not best used for directly answering:**\n"
            "- Whether a specific home is priced correctly\n"
            "- Whether one property can definitely be negotiated down\n"
            "- What one neighborhood will do next month"
        ),

        "section_signal": "Macro Market Read",
        "section_signal_sub": "Convert statewide data into a clearer market interpretation that is easier to use in decisions, comparisons, and client conversations.",

        "metric_latest_month": "Latest Month",
        "metric_data_span": "Data Window",
        "metric_market_bias": "Market Position",
        "metric_moi_trend": "Short-Term MOI Trend",
        "metric_price_signal": "Price Direction",

        "guide_title": "How to Read the Market",
        "guide_main": "Start at the statewide level to understand the broader market environment, then move into cities, neighborhoods, and specific properties with a stronger decision framework.",
        "guide_sub": "This page helps buyers, investors, and advisors build a shared view of market conditions before discussing area selection, home search priorities, pricing, or negotiation strategy.",

        "signal_card_1_sub": "Based on latest MOI",
        "signal_card_2_sub": "Based on Sales YoY",
        "signal_card_3_sub": "Based on Price YoY",
        "signal_card_4_sub": "Based on Listings YoY",
        "signal_card_5_sub": "Combined market interpretation",

        "narrative_title": "Current Market Read",
        "detail_title": "Key Indicators",
        "signal_table_title": "Signal Breakdown",

        "inventory_pressure_axis": "Months of Inventory",
        "price_axis": "Median Price",
        "indexed_axis": "Indexed Trend (Start = 100)",

        "table_metric": "Metric",
        "table_value": "Value",
        "table_signal": "Signal",
        "table_basis": "Basis",

        "price_up_mild": "Mild Upward Pressure",
        "price_up_clear": "Clear Upward Pressure",
        "price_flat": "Largely Stable",
        "price_down_mild": "Mild Softening",
        "price_down_clear": "Clear Softening",

        "increase": "Up",
        "decrease": "Down",
        "flat_move": "Flat",
    },
    "zh": {
        "title": "北卡市场总览",
        "subtitle": "面向买家、投资人和房产顾问的州级市场分析页面，用于更高效地判断库存压力、供需变化与价格环境。",
        "hero_chip": "北卡宏观市场分析",

        "sidebar_preferences": "偏好设置",
        "language": "语言",
        "budget_global": "预算（美元，单位：千）",
        "budget_note": "这个预算设置会在不同页面之间共享，也可以随时手动调整。",
        "selected_budget": "当前预算",

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

        "missing_file": "缺少 `data/analytics/monthly_metrics.csv` 文件。\n\n请运行：\n\n`python run_full_pipeline.py --workers 4`",
        "missing_cols": "monthly_metrics.csv 缺少必要字段：",
        "no_data_range": "当前选择的月份范围内没有数据。",

        "latest_month": "最新月份",
        "inventory_months": "库存（MOI）",
        "listings": "挂牌量",
        "sales": "成交量",
        "median_price": "中位价",

        "headline_title": "北卡房地产市场概览",
        "headline_caption": "从全州维度观察库存压力、供需关系与价格方向。",

        "section_charts": "市场结构",
        "section_charts_sub": "先从州级层面把握库存、供需与价格环境，再进入城市、社区和具体房源层面的比较与判断。",

        "inventory_chart_title": "库存压力趋势",
        "inventory_chart_caption": "用库存月数观察当前市场的选择空间与竞争强弱。一般来说，MOI 越高，买方可选房源越多，市场竞争压力越小；MOI 越低，通常意味着竞争更强。",

        "ls_title": "供需趋势对比",
        "ls_caption": "这张图把挂牌量和成交量统一换算到同一个起点（=100），更适合直接比较趋势方向。它可以帮助用户更快判断当前市场是供给扩张快于需求，还是需求恢复快于供给。",
        "indexed_note": "指数化视图（起点 = 100）",

        "price_title": "中位价趋势",
        "price_caption": "通过州级中位价趋势快速把握当前市场的价格环境，帮助买家、投资人和房产顾问判断价格压力是在延续、趋稳还是放缓，再进入更具体的区域与房源比较。",
        "price_spotlight": "价格环境判断",
        "price_spotlight_sub": "先从州级价格趋势判断当前市场价格环境，再结合城市、社区和具体房源做进一步比较，有助于更快区分整体价格背景与个别房源定价差异。",

        "market_signal": "北卡市场信号",
        "signal_summary": "信号总结",

        "current_moi_zone": "当前 MOI 位置",
        "demand_signal": "需求信号",
        "price_signal": "价格信号",
        "supply_signal": "供给信号",
        "moi_trend_3m": "MOI 趋势（3个月）",
        "overall_market": "整体市场位置",

        "how_to_read": "这页怎么读",
        "how_to_read_text": (
            "这是一页州级宏观市场分析页面，适合在进入城市、社区和具体房源分析之前，先帮助用户建立对当前市场环境的整体判断。"
            "“当前 MOI 位置”用于判断市场此刻所处的位置。"
            "“需求信号”使用成交同比，“价格信号”使用价格同比，“供给信号”使用挂牌同比。"
            "“3个月 MOI 趋势”通过比较最近一个3个月滚动均值与前一个3个月滚动均值来判断短期库存方向。"
            "“整体市场位置”会综合当前 MOI、同比信号与短期库存趋势，形成一个更适合用于判断与沟通的宏观结论。"
            "这页适合用于建立市场框架、提升沟通效率与辅助决策，但不能替代具体城市、具体社区与具体房源层面的分析。"
        ),
        "show_latest_rows": "查看最近数据",

        "market_zone_table_title": "MOI 市场区间说明",
        "moi_range": "MOI 区间",
        "market_interpretation": "解读",
        "seller_zone": "竞争偏强",
        "balanced_zone": "相对平衡",
        "buyer_zone": "买方空间较大",

        "report_month": "报告月份",
        "months_inventory": "MOI",
        "mom_inventory_pct": "库存环比 %",
        "mom_sales_pct": "成交环比 %",
        "mom_price_pct": "价格环比 %",
        "yoy_listings_pct": "挂牌同比 %",
        "yoy_sales_pct": "成交同比 %",
        "yoy_price_pct": "价格同比 %",

        "Rising": "上升",
        "Falling": "下降",
        "Stable": "稳定",

        "Improving": "改善",
        "Weakening": "走弱",
        "Softening": "走软",
        "Expanding": "扩张",
        "Tightening": "收紧",

        "Buyer-Leaning": "买方空间较大",
        "Seller-Leaning": "竞争偏强",
        "Balanced": "相对平衡",

        "market_zone": "市场区间",
        "source_note": "方法说明",
        "source_note_text": (
            "MOI（库存月数）= 当前挂牌量 ÷ 近期平均月成交速度。"
            "本页对 MOI 的解读与 Price Band Opportunities 页面保持一致："
            "< 4 = 竞争偏强，4–6 = 相对平衡，> 6 = 买方空间较大。"
            "它反映的是市场结构，不代表某一套房一定能谈价。"
        ),
        "value": "数值",
        "series": "系列",
        "selected_data_points": "当前数据点数",

        "as_of": "截至",
        "sales_yoy": "成交同比",
        "price_yoy": "价格同比",
        "listings_yoy": "挂牌同比",

        "macro_note_title": "这页最适合帮助回答什么问题",
        "macro_note_body": (
            "- 理解北卡全州市场方向\n"
            "- 判断库存压力是在缓解还是收紧\n"
            "- 在讨论局部区域之前，先建立对当前市场环境的整体认识\n\n"
            "**不适合直接回答：**\n"
            "- 某一套房是否定价正确\n"
            "- 某套房是否一定能谈下来\n"
            "- 某个社区下个月一定会怎么走"
        ),

        "section_signal": "宏观市场解读",
        "section_signal_sub": "把州级市场数据转化为更容易理解、也更方便用于判断、比较与沟通的市场结论。",

        "metric_latest_month": "最新月份",
        "metric_data_span": "数据区间",
        "metric_market_bias": "市场位置",
        "metric_moi_trend": "短期 MOI 趋势",
        "metric_price_signal": "价格方向",

        "guide_title": "宏观市场阅读方式",
        "guide_main": "先从州级层面判断当前市场环境，再进入城市、社区和具体房源层面的比较，更有助于理解价格、库存和竞争强弱之间的关系。",
        "guide_sub": "这页适合帮助买家、投资人和房产顾问先建立统一的市场认知，再进一步讨论区域选择、看房优先级、定价判断和交易策略。",

        "signal_card_1_sub": "基于最新 MOI",
        "signal_card_2_sub": "基于成交同比",
        "signal_card_3_sub": "基于价格同比",
        "signal_card_4_sub": "基于挂牌同比",
        "signal_card_5_sub": "综合后的市场判断",

        "narrative_title": "当前市场结论",
        "detail_title": "关键指标",
        "signal_table_title": "信号拆解",

        "inventory_pressure_axis": "库存月数",
        "price_axis": "中位价",
        "indexed_axis": "指数化趋势（起点 = 100）",

        "table_metric": "指标",
        "table_value": "当前值",
        "table_signal": "判断",
        "table_basis": "依据",

        "price_up_mild": "温和上行",
        "price_up_clear": "明显上行",
        "price_flat": "大致稳定",
        "price_down_mild": "温和走软",
        "price_down_clear": "明显走软",

        "increase": "增加",
        "decrease": "减少",
        "flat_move": "持平",
    },
}


def tr(key: str, lang: str) -> str:
    return TEXT[lang].get(key, key)


# =========================================================
# CSS
# =========================================================
def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root{
            --bg:#f4f7fb;
            --card:#ffffff;
            --text:#0f172a;
            --muted:#64748b;
            --line:#dbe3ee;
            --line-soft:#edf2f7;
            --green:#16a34a;
            --green-bg:#ecfdf3;
            --amber:#d97706;
            --amber-bg:#fff7ed;
            --red:#dc2626;
            --red-bg:#fef2f2;
            --blue:#2563eb;
            --blue-soft:#eff6ff;
            --shadow:0 10px 28px rgba(15, 23, 42, 0.06);
            --shadow-strong:0 18px 50px rgba(15, 23, 42, 0.12);
        }

        html, body, [class*="css"] {
            font-family: Inter, "Segoe UI", "PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif;
            color: var(--text);
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(37,99,235,0.04), transparent 20%),
                radial-gradient(circle at top right, rgba(14,165,233,0.03), transparent 18%),
                linear-gradient(180deg, #f8fafc 0%, #f4f7fb 100%);
        }

        .block-container {
            max-width: 1460px;
            padding-top: 0.8rem;
            padding-bottom: 2.6rem;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
            border-right: 1px solid #e5e7eb;
        }

        section[data-testid="stSidebar"] .stSelectbox label,
        section[data-testid="stSidebar"] .stSlider label,
        section[data-testid="stSidebar"] .stRadio label {
            font-weight: 700 !important;
            color: #334155 !important;
        }

        .hero {
            position: relative;
            overflow: hidden;
            background:
                radial-gradient(circle at top right, rgba(56,189,248,0.16), transparent 22%),
                linear-gradient(135deg, #08111f 0%, #0f172a 35%, #172554 100%);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 28px;
            padding: 30px 32px 28px 32px;
            box-shadow: var(--shadow-strong);
            color: #ffffff;
            margin-bottom: 1.25rem;
        }

        .hero-chip {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 0.42rem 0.78rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.12);
            color: rgba(255,255,255,0.94);
            font-size: 0.74rem;
            font-weight: 800;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin-bottom: 0.9rem;
        }

        .hero-title {
            font-size: 2.05rem;
            font-weight: 900;
            line-height: 1.06;
            letter-spacing: -0.02em;
            margin-bottom: 0.38rem;
        }

        .hero-subtitle {
            font-size: 1rem;
            color: rgba(255,255,255,0.92);
            margin-bottom: 0.45rem;
            line-height: 1.68;
            max-width: 1120px;
        }

        .summary-card,
        .signal-card,
        .narrative-card,
        .guide-card,
        .spotlight-card,
        .metric-box,
        .table-card,
        .chart-card {
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 22px;
            box-shadow: var(--shadow);
            min-width: 0;
            overflow: hidden;
        }

        .summary-card {
            min-height: 142px;
            padding: 16px 18px;
            position: relative;
            overflow: hidden;
            background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
            margin-bottom: 0.4rem;
        }

        .summary-card::after {
            content:"";
            position:absolute;
            top:0;
            right:0;
            width:88px;
            height:88px;
            background: radial-gradient(circle, rgba(37,99,235,0.06) 0%, rgba(37,99,235,0) 68%);
            pointer-events:none;
        }

        .summary-hot { border-left: 4px solid var(--red); }
        .summary-balanced { border-left: 4px solid #f59e0b; }
        .summary-soft { border-left: 4px solid var(--green); }

        .summary-label {
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            color: var(--muted);
            margin-bottom: 0.38rem;
        }

        .summary-value {
            font-size: 1.12rem;
            font-weight: 900;
            line-height: 1.28;
            color: var(--text);
            margin-bottom: 0.30rem;
            word-break: break-word;
            white-space: normal;
            min-width: 0;
            overflow-wrap: anywhere;
        }

        .summary-sub {
            font-size: 0.88rem;
            color: var(--muted);
            line-height: 1.5;
            margin-top: 0.42rem;
            min-width: 0;
            overflow-wrap: anywhere;
        }

        .summary-sub:empty {
            display:none;
        }

        .section-head {
            margin-top: 1.15rem;
            margin-bottom: 0.95rem;
        }

        .section-title {
            font-size: 1.16rem;
            font-weight: 900;
            color: var(--text);
            letter-spacing: -0.01em;
            margin-bottom: 0.10rem;
        }

        .section-subtitle {
            font-size: 0.94rem;
            color: var(--muted);
            line-height: 1.6;
        }

        .chart-card {
            padding: 18px 18px 14px 18px;
            background: linear-gradient(180deg, #ffffff 0%, #fcfdff 100%);
            margin-top: 0.45rem;
            margin-bottom: 1.5rem;
        }

        .chart-title {
            font-size: 1.02rem;
            font-weight: 860;
            color: var(--text);
            margin-bottom: 0.18rem;
        }

        .chart-caption {
            font-size: 0.91rem;
            color: var(--muted);
            line-height: 1.58;
            margin-bottom: 0.88rem;
            max-width: 1120px;
        }

        .signal-card {
            min-height: 168px;
            padding: 18px 20px;
            background: linear-gradient(180deg, #ffffff 0%, #fcfdff 100%);
            margin-bottom: 0.95rem;
        }

        .signal-kicker {
            font-size: 0.72rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--muted);
            margin-bottom: 0.35rem;
        }

        .signal-main {
            font-size: 1.08rem;
            font-weight: 900;
            line-height: 1.2;
            color: var(--text);
            margin-bottom: 0.34rem;
            min-width: 0;
            overflow-wrap: anywhere;
        }

        .signal-sub {
            font-size: 0.90rem;
            color: var(--muted);
            line-height: 1.58;
            margin-top: 0.42rem;
            min-width: 0;
            overflow-wrap: anywhere;
        }

        .signal-chip {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 0.42rem 0.72rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 860;
            line-height: 1.25;
            white-space: normal;
            flex-wrap: wrap;
            max-width: 100%;
            word-break: break-word;
            overflow-wrap: anywhere;
            margin-top: 4px;
            border: 1px solid transparent;
            box-sizing: border-box;
        }

        .summary-card .signal-chip {
            font-size: 0.72rem;
            padding: 0.34rem 0.62rem;
            line-height: 1.2;
        }

        .signal-chip-icon {
            width: auto;
            height: auto;
            border-radius: 0;
            display:flex;
            align-items:center;
            justify-content:center;
            font-size: 0.90rem;
            font-weight: 900;
            flex: 0 0 auto;
            background: transparent !important;
            color: inherit !important;
        }

        .signal-chip.soft {
            background: var(--green-bg);
            color: #166534;
            border-color: rgba(22,163,74,0.18);
        }

        .signal-chip.balanced {
            background: #fff7ed;
            color: #9a3412;
            border-color: rgba(217,119,6,0.18);
        }

        .signal-chip.hot {
            background: var(--red-bg);
            color: #991b1b;
            border-color: rgba(220,38,38,0.18);
        }

        .narrative-card,
        .guide-card,
        .spotlight-card,
        .table-card {
            padding: 18px 20px;
            border-radius: 20px;
            margin-bottom: 1rem;
        }

        .spotlight-card {
            background:
                radial-gradient(circle at top right, rgba(56,189,248,0.10), transparent 24%),
                linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        }

        .card-kicker {
            font-size: 0.73rem;
            font-weight: 860;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 0.32rem;
        }

        .card-main {
            font-size: 1rem;
            font-weight: 850;
            color: var(--text);
            line-height: 1.36;
            min-width: 0;
            overflow-wrap: anywhere;
        }

        .card-body {
            margin-top: 0.40rem;
            font-size: 0.92rem;
            color: var(--muted);
            line-height: 1.7;
            min-width: 0;
            overflow-wrap: anywhere;
        }

        .card-body strong {
            color: var(--text);
        }

        .metric-strip {
            display:grid;
            grid-template-columns: repeat(4, minmax(0,1fr));
            gap: 12px;
            margin-top: 0.65rem;
            margin-bottom: 0.15rem;
        }

        .metric-box {
            padding: 13px 14px;
            border-radius: 16px;
        }

        .metric-box-label {
            font-size: 0.71rem;
            font-weight: 800;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 0.28rem;
        }

        .metric-box-value {
            font-size: 1rem;
            font-weight: 860;
            color: var(--text);
            line-height: 1.16;
            min-width: 0;
            overflow-wrap: anywhere;
        }

        .signal-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            overflow: hidden;
            border: 1px solid var(--line);
            border-radius: 16px;
            margin-top: 0.5rem;
            table-layout: auto;
        }

        .signal-table col.metric-col { width: 23%; }
        .signal-table col.value-col  { width: 22%; }
        .signal-table col.signal-col { width: 23%; }
        .signal-table col.basis-col  { width: 32%; }

        .signal-table th {
            background: #f8fafc;
            color: var(--muted);
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            text-align: left;
            padding: 12px 14px;
            border-bottom: 1px solid var(--line);
        }

        .signal-table td {
            padding: 13px 14px;
            border-bottom: 1px solid var(--line-soft);
            vertical-align: middle;
            font-size: 0.93rem;
            color: var(--text);
        }

        .signal-table tr:last-child td {
            border-bottom: none;
        }

        .table-metric {
            font-weight: 820;
            color: var(--text);
        }

        .signal-cell {
            min-width: 150px;
        }

        .basis-cell {
            min-width: 170px;
        }

        div[data-testid="stDataFrame"], .stDataFrame {
            border-radius: 18px;
            overflow: hidden;
            border: 1px solid var(--line);
            box-shadow: var(--shadow);
        }

        .stExpander {
            border: 1px solid var(--line);
            border-radius: 16px;
            overflow: hidden;
            box-shadow: var(--shadow);
            margin-top: 0.75rem;
        }

        @media (max-width: 1200px) {
            .metric-strip {
                grid-template-columns: repeat(2, minmax(0,1fr));
            }

            .signal-table col.metric-col,
            .signal-table col.value-col,
            .signal-table col.signal-col,
            .signal-table col.basis-col {
                width: auto;
            }

            .signal-cell,
            .basis-cell {
                min-width: 0;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# Helpers
# =========================================================
def plain_text(value) -> str:
    if value is None:
        return ""
    return str(value)


def sanitize_text(value) -> str:
    text = plain_text(value)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def render_html(html: str) -> None:
    st.markdown(html, unsafe_allow_html=True)


def fmt_int(x) -> str:
    if x is None or pd.isna(x):
        return "N/A"
    return f"{int(round(float(x))):,}"


def fmt_float(x, digits: int = 2) -> str:
    if x is None or pd.isna(x):
        return "N/A"
    return f"{float(x):.{digits}f}"


def fmt_pct(x, digits: int = 1) -> str:
    if x is None or pd.isna(x):
        return "N/A"
    return f"{float(x):.{digits}f}%"


def fmt_money(x) -> str:
    if x is None or pd.isna(x):
        return "N/A"
    return f"${float(x):,.0f}"


def latest_value(df: pd.DataFrame, col: str):
    if col not in df.columns:
        return None
    s = df[col].dropna()
    return s.iloc[-1] if len(s) else None


def localized_label(raw_key: str, lang: str) -> str:
    return tr(raw_key, lang)


def price_direction_phrase(yoy_price: float | None, lang: str) -> str:
    if yoy_price is None or pd.isna(yoy_price):
        return tr("price_flat", lang)

    x = float(yoy_price)
    if x >= 5:
        return tr("price_up_clear", lang)
    if x >= 1:
        return tr("price_up_mild", lang)
    if x <= -5:
        return tr("price_down_clear", lang)
    if x <= -1:
        return tr("price_down_mild", lang)
    return tr("price_flat", lang)


def movement_text(x, lang: str, digits: int = 1) -> str:
    if x is None or pd.isna(x):
        return "N/A"
    x = float(x)
    if x > 0:
        return f'{tr("increase", lang)} {abs(x):.{digits}f}%'
    if x < 0:
        return f'{tr("decrease", lang)} {abs(x):.{digits}f}%'
    return f'{tr("flat_move", lang)} 0.0%'


def nice_axis_domain(
    series: pd.Series,
    *,
    zero_floor: bool = False,
    pad_ratio: float = 0.12,
    min_span: float = 1.0,
    min_upper: float | None = None,
) -> list[float] | None:
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return None

    y_min = float(s.min())
    y_max = float(s.max())

    if math.isclose(y_min, y_max):
        pad = max(abs(y_min) * 0.15, min_span / 2)
        low = y_min - pad
        high = y_max + pad
    else:
        span = max(y_max - y_min, min_span)
        pad = span * pad_ratio
        low = y_min - pad
        high = y_max + pad

    if zero_floor:
        low = 0

    span2 = max(high - low, min_span)
    rough_step = span2 / 6 if span2 > 0 else 1

    mag = 10 ** math.floor(math.log10(rough_step)) if rough_step > 0 else 1
    normalized = rough_step / mag

    if normalized <= 1:
        nice_step = 1 * mag
    elif normalized <= 2:
        nice_step = 2 * mag
    elif normalized <= 2.5:
        nice_step = 2.5 * mag
    elif normalized <= 5:
        nice_step = 5 * mag
    else:
        nice_step = 10 * mag

    nice_low = math.floor(low / nice_step) * nice_step
    nice_high = math.ceil(high / nice_step) * nice_step

    if zero_floor:
        nice_low = 0

    if min_upper is not None:
        nice_high = max(nice_high, float(min_upper))

    if nice_high <= nice_low:
        nice_high = nice_low + max(min_span, 1)

    return [float(nice_low), float(nice_high)]


# =========================================================
# CSS-aligned UI helpers
# =========================================================
def get_signal_badge_meta(state: str, lang: str):
    if state == "soft":
        label = tr("Buyer-Leaning", lang)
        return "🟢", label
    if state == "hot":
        label = tr("Seller-Leaning", lang)
        return "🔴", label
    label = tr("Balanced", lang)
    return "🟡", label


def signal_chip_html(label: str, state: str) -> str:
    state = state if state in {"soft", "balanced", "hot"} else "balanced"
    icon, _ = get_signal_badge_meta(state, "en")
    safe_label = escape(sanitize_text(label))
    safe_icon = escape(plain_text(icon))
    return (
        f'<span class="signal-chip {state}">'
        f'<span class="signal-chip-icon">{safe_icon}</span>'
        f'<span>{safe_label}</span>'
        f"</span>"
    )


def render_hero(lang: str) -> None:
    render_html(
        "".join(
            [
                '<div class="hero">',
                f'<div class="hero-chip">{escape(sanitize_text(tr("hero_chip", lang)))}</div>',
                f'<div class="hero-title">{escape(sanitize_text(tr("title", lang)))}</div>',
                f'<div class="hero-subtitle">{escape(sanitize_text(tr("subtitle", lang)))}</div>',
                "</div>",
            ]
        )
    )


def render_summary_card(
    label: str,
    value: str,
    sub: str = "",
    state: str | None = None,
    badge_label: str | None = None,
) -> None:
    state_cls = f"summary-{state}" if state in {"hot", "balanced", "soft"} else ""
    badge_html = signal_chip_html(badge_label, state) if (state in {"hot", "balanced", "soft"} and badge_label) else ""
    sub_html = f'<div class="summary-sub">{escape(sanitize_text(sub))}</div>' if sanitize_text(sub) else ""

    html = "".join(
        [
            f'<div class="summary-card {state_cls}">',
            f'<div class="summary-label">{escape(sanitize_text(label))}</div>',
            f'<div class="summary-value">{escape(sanitize_text(value))}</div>',
            badge_html,
            sub_html,
            "</div>",
        ]
    )
    render_html(html)


def render_section_head(title: str, subtitle: str) -> None:
    render_html(
        "".join(
            [
                '<div class="section-head">',
                f'<div class="section-title">{escape(sanitize_text(title))}</div>',
                f'<div class="section-subtitle">{escape(sanitize_text(subtitle))}</div>',
                "</div>",
            ]
        )
    )


def render_chart_header(title: str, caption: str) -> None:
    render_html(
        f"""
        <div class="chart-card">
            <div class="chart-title">{escape(sanitize_text(title))}</div>
            <div class="chart-caption">{escape(sanitize_text(caption))}</div>
        </div>
        """
    )


def render_signal_card(
    kicker: str,
    main: str,
    chip_label: str,
    chip_state: str,
    sub: str,
) -> None:
    html = "".join(
        [
            '<div class="signal-card">',
            f'<div class="signal-kicker">{escape(sanitize_text(kicker))}</div>',
            f'<div class="signal-main">{escape(sanitize_text(main))}</div>',
            signal_chip_html(chip_label, chip_state),
            f'<div class="signal-sub">{escape(sanitize_text(sub))}</div>',
            "</div>",
        ]
    )
    render_html(html)


def render_metric_strip(items: list[tuple[str, str]]) -> None:
    parts = ['<div class="metric-strip">']
    for label, value in items:
        parts.append(
            f'<div class="metric-box">'
            f'<div class="metric-box-label">{escape(sanitize_text(label))}</div>'
            f'<div class="metric-box-value">{escape(sanitize_text(value))}</div>'
            f'</div>'
        )
    parts.append("</div>")
    render_html("".join(parts))


# =========================================================
# Data loading
# =========================================================
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


# =========================================================
# Signal logic
# =========================================================
def moi_zone(moi: float | None) -> str:
    if moi is None or pd.isna(moi):
        return "Balanced"
    if moi < 4:
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
    if "months_inventory" not in view.columns:
        return "Stable"

    s = view.sort_values("report_month_dt")["months_inventory"].dropna().reset_index(drop=True)
    if len(s) < 6:
        return "Stable"

    rolling = s.rolling(window=3).mean().dropna().reset_index(drop=True)
    if len(rolling) < 2:
        return "Stable"

    latest_roll = rolling.iloc[-1]
    prev_roll = rolling.iloc[-2]
    delta = latest_roll - prev_roll

    if delta > 0.05:
        return "Rising"
    if delta < -0.05:
        return "Falling"
    return "Stable"


def overall_market(current_zone: str, demand: str, price: str, supply: str, moi_trend: str) -> str:
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


def zone_state(zone_raw: str) -> str:
    if zone_raw == "Buyer-Leaning":
        return "soft"
    if zone_raw == "Seller-Leaning":
        return "hot"
    return "balanced"


def generic_state(val_raw: str) -> str:
    if val_raw in {"Improving", "Rising", "Tightening"}:
        return "hot"
    if val_raw in {"Weakening", "Softening", "Expanding"}:
        return "soft"
    return "balanced"


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
    sales_yoy_text = movement_text(yoy_sales, lang, 1)
    price_yoy_text = movement_text(yoy_price, lang, 1)
    listings_yoy_text = movement_text(yoy_listings, lang, 1)
    price_phrase = price_direction_phrase(yoy_price, lang)

    if lang == "zh":
        return (
            f"截至 {latest_month}，北卡房地产市场当前 MOI 为 {moi_text}，处于“{localized_label(current_zone, lang)}”区间。"
            f"从同比信号看，成交同比为 {sales_yoy_text}，需求表现为“{localized_label(demand, lang)}”；"
            f"价格同比为 {price_yoy_text}，价格表现为“{localized_label(price, lang)}”，当前更接近“{price_phrase}”；"
            f"挂牌同比为 {listings_yoy_text}，供给表现为“{localized_label(supply, lang)}”。"
            f"短期库存趋势（3个月滚动）为“{localized_label(moi_trend, lang)}”。"
            f"综合来看，当前市场整体更接近“{localized_label(overall, lang)}”。"
        )

    return (
        f"As of {latest_month}, North Carolina's MOI is {moi_text}, placing the market in a "
        f"“{localized_label(current_zone, lang)}” position. "
        f"Sales YoY is {sales_yoy_text}, so demand is “{localized_label(demand, lang)}”. "
        f"Price YoY is {price_yoy_text}, so pricing is “{localized_label(price, lang)}”, which reads as "
        f"“{price_phrase}”. "
        f"Listings YoY is {listings_yoy_text}, so supply is “{localized_label(supply, lang)}”. "
        f"The short-term inventory trend based on the 3-month rolling MOI is “{localized_label(moi_trend, lang)}”. "
        f"Overall, the market is best described as “{localized_label(overall, lang)}”."
    )


# =========================================================
# Filtering helpers
# =========================================================
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
        return alt.Axis(
            format="%Y",
            labelAngle=0,
            labelOverlap=True,
            grid=False,
            title=tr("report_month", lang),
            tickCount=8,
        )

    if num_points > 18:
        return alt.Axis(
            format="%Y-%m",
            labelAngle=-35,
            labelOverlap=False,
            grid=False,
            title=tr("report_month", lang),
            tickCount=12,
        )

    return alt.Axis(
        format="%Y-%m",
        labelAngle=-35,
        labelOverlap=False,
        grid=False,
        title=tr("report_month", lang),
        tickCount=max(num_points, 2),
    )


# =========================================================
# Chart builders
# =========================================================
def build_interactive_line_chart(
    chart_df: pd.DataFrame,
    x_col: str,
    y_col: str,
    lang: str,
    y_title: str,
    color_value: str | None = None,
    tooltip_fields: list | None = None,
    y_scale_domain: list[float] | None = None,
    height: int = 420,
    add_last_label: bool = True,
    y_format: str | None = None,
):
    num_points = len(chart_df)
    base = alt.Chart(chart_df)

    nearest = alt.selection_point(
        nearest=True,
        on="mouseover",
        fields=[x_col],
        empty="none",
    )

    y_encoding = alt.Y(
        f"{y_col}:Q",
        title=y_title,
        scale=alt.Scale(domain=y_scale_domain) if y_scale_domain else alt.Undefined,
        axis=alt.Axis(format=y_format) if y_format else alt.Axis(),
    )

    x_encoding = alt.X(
        f"{x_col}:T",
        axis=axis_config_for_span(num_points, lang),
    )

    point_size = 32 if num_points > 36 else 44 if num_points > 24 else 54

    line = base.mark_line(strokeWidth=3.2).encode(
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
    rule = base.mark_rule(color="#94a3b8").encode(x=x_encoding).transform_filter(nearest)

    default_tooltips = [
        alt.Tooltip("report_month:N", title=tr("report_month", lang)),
        alt.Tooltip(f"{y_col}:Q", title=y_title, format=",.2f"),
    ]
    tooltips = tooltip_fields if tooltip_fields else default_tooltips

    hover_points = base.mark_point(size=100, filled=True).encode(
        x=x_encoding,
        y=y_encoding,
        opacity=alt.condition(nearest, alt.value(1), alt.value(0)),
        tooltip=tooltips,
        color=alt.value(color_value) if color_value else alt.Undefined,
    )

    chart = alt.layer(line, points, selectors, rule, hover_points).properties(height=height)

    if add_last_label and not chart_df.empty:
        last_df = chart_df.tail(1)
        text_format = ".2f" if y_col == "months_inventory" else ",.0f"
        last_point = alt.Chart(last_df).mark_point(size=100, filled=True).encode(
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
            color="#0f172a",
        ).encode(
            x=x_encoding,
            y=y_encoding,
            text=alt.Text(f"{y_col}:Q", format=text_format),
        )
        chart = alt.layer(chart, last_point, last_label).properties(height=height)

    return chart


def build_indexed_supply_demand_chart(view: pd.DataFrame, lang: str) -> alt.Chart:
    plot_df = view[["report_month_dt", "report_month", "listings", "sales"]].dropna(subset=["report_month_dt"]).copy()
    plot_df = plot_df.dropna(subset=["listings", "sales"])
    if plot_df.empty:
        return alt.Chart(pd.DataFrame({"x": [], "y": []})).mark_line()

    base_listings = plot_df["listings"].replace(0, pd.NA).dropna()
    base_sales = plot_df["sales"].replace(0, pd.NA).dropna()
    if base_listings.empty or base_sales.empty:
        return alt.Chart(pd.DataFrame({"x": [], "y": []})).mark_line()

    listings_base = float(base_listings.iloc[0])
    sales_base = float(base_sales.iloc[0])

    plot_df["listings_index"] = plot_df["listings"] / listings_base * 100
    plot_df["sales_index"] = plot_df["sales"] / sales_base * 100

    long_df = plot_df.melt(
        id_vars=["report_month_dt", "report_month", "listings", "sales"],
        value_vars=["listings_index", "sales_index"],
        var_name="series_raw",
        value_name="index_value",
    )

    label_map = {
        "listings_index": tr("listings", lang),
        "sales_index": tr("sales", lang),
    }
    color_domain = [tr("listings", lang), tr("sales", lang)]
    color_range = ["#7cc0f7", "#1565c0"]

    long_df["series"] = long_df["series_raw"].map(label_map)
    long_df["raw_value"] = long_df.apply(
        lambda r: r["listings"] if r["series_raw"] == "listings_index" else r["sales"],
        axis=1,
    )

    num_points = long_df["report_month"].nunique()
    x_encoding = alt.X("report_month_dt:T", axis=axis_config_for_span(num_points, lang))

    y_domain = nice_axis_domain(long_df["index_value"], zero_floor=False, pad_ratio=0.10, min_span=12)
    if y_domain is None:
        y_domain = [80, 120]

    y_encoding = alt.Y(
        "index_value:Q",
        title=tr("indexed_axis", lang),
        axis=alt.Axis(format=".0f"),
        scale=alt.Scale(domain=y_domain),
    )

    color_encoding = alt.Color(
        "series:N",
        scale=alt.Scale(domain=color_domain, range=color_range),
        legend=alt.Legend(title=""),
    )

    base = alt.Chart(long_df)
    nearest = alt.selection_point(nearest=True, on="mouseover", fields=["report_month_dt"], empty="none")

    ref_line = alt.Chart(pd.DataFrame({"y": [100]})).mark_rule(
        color="#cbd5e1",
        strokeDash=[6, 6],
    ).encode(y="y:Q")

    line = base.mark_line(strokeWidth=3).encode(
        x=x_encoding,
        y=y_encoding,
        color=color_encoding,
    )

    points = base.mark_point(filled=True, size=42).encode(
        x=x_encoding,
        y=y_encoding,
        color=color_encoding,
    )

    selectors = alt.Chart(long_df[["report_month_dt"]].drop_duplicates()).mark_point(opacity=0).encode(
        x=x_encoding
    ).add_params(nearest)

    rule = alt.Chart(long_df[["report_month_dt"]].drop_duplicates()).mark_rule(color="#94a3b8").encode(
        x=x_encoding
    ).transform_filter(nearest)

    hover = base.mark_point(size=110, filled=True).encode(
        x=x_encoding,
        y=y_encoding,
        color=color_encoding,
        opacity=alt.condition(nearest, alt.value(1), alt.value(0)),
        tooltip=[
            alt.Tooltip("report_month:N", title=tr("report_month", lang)),
            alt.Tooltip("series:N", title=tr("series", lang)),
            alt.Tooltip("index_value:Q", title=tr("indexed_note", lang), format=".1f"),
            alt.Tooltip("raw_value:Q", title=tr("value", lang), format=",.0f"),
        ],
    )

    last_points = long_df.sort_values(["series", "report_month_dt"]).groupby("series", as_index=False).tail(1)
    last_marks = alt.Chart(last_points).mark_point(size=100, filled=True).encode(
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
        text=alt.Text("index_value:Q", format=".0f"),
    )

    return alt.layer(ref_line, line, points, selectors, rule, hover, last_marks, last_labels).properties(height=420)


# =========================================================
# Render sections
# =========================================================
def render_inventory_chart(view: pd.DataFrame, lang: str) -> None:
    render_chart_header(tr("inventory_chart_title", lang), tr("inventory_chart_caption", lang))

    inv_chart_df = view[["report_month_dt", "report_month", "months_inventory"]].dropna().copy()
    if not inv_chart_df.empty:
        inv_chart_df["market_zone"] = inv_chart_df["months_inventory"].apply(moi_zone)
        inv_chart_df["market_zone_display"] = inv_chart_df["market_zone"].map(lambda x: localized_label(x, lang))

        y_domain = nice_axis_domain(
            inv_chart_df["months_inventory"],
            zero_floor=True,
            pad_ratio=0.16,
            min_span=2.0,
            min_upper=7.0,
        )
        if y_domain is None:
            y_domain = [0, 7]

        balanced_band = alt.Chart(pd.DataFrame({"ymin": [4.0], "ymax": [6.0]})).mark_rect(
            opacity=0.12, color="#f59e0b"
        ).encode(
            y=alt.Y(
                "ymin:Q",
                scale=alt.Scale(domain=y_domain),
                title=tr("inventory_pressure_axis", lang),
            ),
            y2="ymax:Q",
        )

        line_4 = alt.Chart(pd.DataFrame({"y": [4.0]})).mark_rule(
            strokeDash=[6, 4], size=1.5, color="#94a3b8"
        ).encode(y=alt.Y("y:Q", scale=alt.Scale(domain=y_domain)))

        line_6 = alt.Chart(pd.DataFrame({"y": [6.0]})).mark_rule(
            strokeDash=[6, 4], size=1.5, color="#cbd5e1"
        ).encode(y=alt.Y("y:Q", scale=alt.Scale(domain=y_domain)))

        main_chart = build_interactive_line_chart(
            chart_df=inv_chart_df,
            x_col="report_month_dt",
            y_col="months_inventory",
            lang=lang,
            y_title=tr("inventory_pressure_axis", lang),
            color_value="#2563eb",
            tooltip_fields=[
                alt.Tooltip("report_month:N", title=tr("report_month", lang)),
                alt.Tooltip("months_inventory:Q", title="MOI", format=".2f"),
                alt.Tooltip("market_zone_display:N", title=tr("market_zone", lang)),
            ],
            y_scale_domain=y_domain,
            height=420,
            add_last_label=True,
            y_format=".1f",
        )

        st.altair_chart(
            alt.layer(balanced_band, line_4, line_6, main_chart).resolve_scale(y="shared").properties(height=420),
            width="stretch",
        )

        zone_df = pd.DataFrame(
            {
                tr("moi_range", lang): ["< 4.0", "4.0 – 6.0", "> 6.0"],
                tr("market_interpretation", lang): [
                    tr("seller_zone", lang),
                    tr("balanced_zone", lang),
                    tr("buyer_zone", lang),
                ],
            }
        )
        st.dataframe(zone_df, width="content", hide_index=True)


def render_supply_demand_chart(view: pd.DataFrame, lang: str) -> None:
    render_chart_header(tr("ls_title", lang), tr("ls_caption", lang))

    chart = build_indexed_supply_demand_chart(view, lang)
    st.altair_chart(chart, width="stretch")

    latest_listings = latest_value(view, "listings")
    latest_sales = latest_value(view, "sales")
    latest_yoy_listings = latest_value(view, "yoy_listings_pct")
    latest_yoy_sales = latest_value(view, "yoy_sales_pct")

    render_metric_strip(
        [
            (tr("listings", lang), fmt_int(latest_listings)),
            (tr("sales", lang), fmt_int(latest_sales)),
            (tr("listings_yoy", lang), movement_text(latest_yoy_listings, lang, 1)),
            (tr("sales_yoy", lang), movement_text(latest_yoy_sales, lang, 1)),
        ]
    )


def render_price_focus_chart(view: pd.DataFrame, lang: str, price_signal_display: str, price_signal_raw: str, latest_yoy_price) -> None:
    render_chart_header(tr("price_title", lang), tr("price_caption", lang))

    price_phrase = price_direction_phrase(latest_yoy_price, lang)

    render_html(
        f"""
        <div class="spotlight-card">
            <div class="card-kicker">{escape(sanitize_text(tr("price_spotlight", lang)))}</div>
            <div class="card-main">{escape(sanitize_text(price_signal_display))} · {escape(sanitize_text(price_phrase))}</div>
            {signal_chip_html(f'{tr("price_yoy", lang)} {movement_text(latest_yoy_price, lang, 1)}', generic_state(price_signal_raw))}
            <div class="card-body">{escape(sanitize_text(tr("price_spotlight_sub", lang)))}</div>
        </div>
        """
    )

    price_df = view[["report_month_dt", "report_month", "median_price"]].dropna().copy()
    if not price_df.empty:
        y_domain = nice_axis_domain(price_df["median_price"], zero_floor=False, pad_ratio=0.10, min_span=20000)
        chart = build_interactive_line_chart(
            chart_df=price_df,
            x_col="report_month_dt",
            y_col="median_price",
            lang=lang,
            y_title=tr("price_axis", lang),
            color_value="#0ea5e9",
            tooltip_fields=[
                alt.Tooltip("report_month:N", title=tr("report_month", lang)),
                alt.Tooltip("median_price:Q", title=tr("median_price", lang), format=",.0f"),
            ],
            y_scale_domain=y_domain,
            height=460,
            add_last_label=True,
            y_format=",.0f",
        )
        st.altair_chart(chart, width="stretch")


def render_signal_table(rows: list[dict], lang: str) -> None:
    parts = [
        '<div class="table-card">',
        f'<div class="card-kicker">{escape(sanitize_text(tr("signal_table_title", lang)))}</div>',
        '<table class="signal-table">',
        '<colgroup>',
        '<col class="metric-col">',
        '<col class="value-col">',
        '<col class="signal-col">',
        '<col class="basis-col">',
        '</colgroup>',
        "<thead><tr>",
        f'<th>{escape(sanitize_text(tr("table_metric", lang)))}</th>',
        f'<th>{escape(sanitize_text(tr("table_value", lang)))}</th>',
        f'<th>{escape(sanitize_text(tr("table_signal", lang)))}</th>',
        f'<th>{escape(sanitize_text(tr("table_basis", lang)))}</th>',
        "</tr></thead><tbody>",
    ]

    for row in rows:
        parts.append(
            "<tr>"
            f'<td class="table-metric">{escape(sanitize_text(row["metric"]))}</td>'
            f'<td>{escape(sanitize_text(row["value"]))}</td>'
            f'<td class="signal-cell">{signal_chip_html(row["signal"], row["state"])}</td>'
            f'<td class="basis-cell">{escape(sanitize_text(row["basis"]))}</td>'
            "</tr>"
        )

    parts.append("</tbody></table></div>")
    render_html("".join(parts))


# =========================================================
# App
# =========================================================
def main() -> None:
    inject_base_css()
    inject_css()

    render_global_sidebar()
    locale = get_locale()
    budget_k = get_budget_k()
    budget_usd = budget_k * 1000

    st.sidebar.divider()
    st.sidebar.header(tr("filters", locale))
    st.sidebar.caption(tr("budget_note", locale))

    df = load_monthly_metrics(DATA_PATH)
    if df.empty:
        st.error(tr("missing_file", locale))
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
        st.error(f"{tr('missing_cols', locale)} {missing}")
        st.stop()

    render_hero(locale)

    time_range_map = {
        tr("last_12m", locale): "12M",
        tr("last_24m", locale): "24M",
        tr("last_36m", locale): "36M",
        tr("ytd", locale): "YTD",
        tr("all_data", locale): "ALL",
    }

    selected_time_range_label = st.sidebar.radio(
        tr("time_range", locale),
        options=list(time_range_map.keys()),
        index=1 if tr("last_24m", locale) in time_range_map else 0,
    )
    selected_time_range = time_range_map[selected_time_range_label]

    years = sorted([int(y) for y in df["report_year"].dropna().unique().tolist()])
    year_options = [tr("all_years", locale)] + [str(y) for y in years]

    selected_year = st.sidebar.selectbox(
        tr("year_filter", locale),
        options=year_options,
        index=0,
    )

    filtered = df.copy()

    if selected_year != tr("all_years", locale):
        filtered = filtered[filtered["report_year"] == int(selected_year)].copy()

    filtered = apply_time_range(filtered, selected_time_range)

    if filtered.empty:
        st.warning(tr("no_data_range", locale))
        st.stop()

    month_options = filtered["report_month"].dropna().astype(str).tolist()
    min_m = min(month_options)
    max_m = max(month_options)

    month_window = st.sidebar.select_slider(
        tr("month_window", locale),
        options=month_options,
        value=(min_m, max_m),
    )

    start_month, end_month = month_window
    mask = (filtered["report_month"] >= start_month) & (filtered["report_month"] <= end_month)
    view = filtered.loc[mask].copy()

    if view.empty:
        st.warning(tr("no_data_range", locale))
        st.stop()

    view = view.sort_values("report_month_dt").copy()

    latest_month = str(view["report_month"].iloc[-1])
    first_month = str(view["report_month"].iloc[0])
    inventory_val = latest_value(view, "months_inventory")
    latest_yoy_sales = latest_value(view, "yoy_sales_pct")
    latest_yoy_price = latest_value(view, "yoy_price_pct")
    latest_yoy_listings = latest_value(view, "yoy_listings_pct")

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

    current_moi_zone_display = localized_label(current_moi_zone_raw, locale)
    demand_signal_display = localized_label(demand_signal_raw, locale)
    price_signal_display = localized_label(price_signal_raw, locale)
    supply_signal_display = localized_label(supply_signal_raw, locale)
    moi_trend_display = localized_label(moi_trend_raw, locale)
    overall_display = localized_label(overall_raw, locale)

    overall_state = zone_state(overall_raw)
    price_state = generic_state(price_signal_raw)
    price_phrase = price_direction_phrase(latest_yoy_price, locale)

    s1, s2, s3, s4, s5, s6 = st.columns(6)
    with s1:
        render_summary_card(
            tr("metric_latest_month", locale),
            latest_month,
            f"{tr('selected_data_points', locale)}: {len(view)}",
        )
    with s2:
        render_summary_card(
            tr("inventory_months", locale),
            fmt_float(inventory_val, 2),
            tr("headline_caption", locale),
            state=zone_state(current_moi_zone_raw),
            badge_label=current_moi_zone_display,
        )
    with s3:
        render_summary_card(
            tr("metric_data_span", locale),
            f"{first_month} → {latest_month}",
            tr("time_range", locale),
        )
    with s4:
        render_summary_card(
            tr("metric_market_bias", locale),
            overall_display,
            tr("signal_summary", locale),
            state=overall_state,
            badge_label=overall_display,
        )
    with s5:
        render_summary_card(
            tr("metric_price_signal", locale),
            f"{price_signal_display} · {price_phrase}",
            f'{tr("price_yoy", locale)}: {movement_text(latest_yoy_price, locale, 1)}',
            state=price_state,
            badge_label=price_signal_display,
        )
    with s6:
        render_summary_card(
            tr("selected_budget", locale),
            fmt_money(budget_usd),
            tr("budget_note", locale),
        )

    render_section_head(tr("section_charts", locale), tr("section_charts_sub", locale))
    render_inventory_chart(view, locale)
    render_supply_demand_chart(view, locale)
    render_price_focus_chart(view, locale, price_signal_display, price_signal_raw, latest_yoy_price)

    render_section_head(tr("section_signal", locale), tr("section_signal_sub", locale))

    sig1, sig2, sig3, sig4, sig5 = st.columns(5)
    with sig1:
        render_signal_card(
            tr("current_moi_zone", locale),
            current_moi_zone_display,
            f"MOI {fmt_float(inventory_val, 2)}",
            zone_state(current_moi_zone_raw),
            tr("signal_card_1_sub", locale),
        )

    with sig2:
        render_signal_card(
            tr("demand_signal", locale),
            demand_signal_display,
            f'{tr("sales_yoy", locale)} {movement_text(latest_yoy_sales, locale, 1)}',
            generic_state(demand_signal_raw),
            tr("signal_card_2_sub", locale),
        )

    with sig3:
        render_signal_card(
            tr("price_signal", locale),
            price_signal_display,
            f'{tr("price_yoy", locale)} {movement_text(latest_yoy_price, locale, 1)} · {price_phrase}',
            generic_state(price_signal_raw),
            tr("signal_card_3_sub", locale),
        )

    with sig4:
        render_signal_card(
            tr("supply_signal", locale),
            supply_signal_display,
            f'{tr("listings_yoy", locale)} {movement_text(latest_yoy_listings, locale, 1)}',
            generic_state(supply_signal_raw),
            tr("signal_card_4_sub", locale),
        )

    with sig5:
        render_signal_card(
            tr("overall_market", locale),
            overall_display,
            moi_trend_display,
            zone_state(overall_raw),
            tr("signal_card_5_sub", locale),
        )

    # 左边更宽，右边更窄
    left_col, right_col = st.columns([1.28, 0.92], gap="large")

    with left_col:
        signal_rows = [
            {
                "metric": tr("current_moi_zone", locale),
                "value": f"MOI {fmt_float(inventory_val, 2)}",
                "signal": current_moi_zone_display,
                "state": zone_state(current_moi_zone_raw),
                "basis": tr("signal_card_1_sub", locale),
            },
            {
                "metric": tr("demand_signal", locale),
                "value": movement_text(latest_yoy_sales, locale, 1),
                "signal": demand_signal_display,
                "state": generic_state(demand_signal_raw),
                "basis": tr("signal_card_2_sub", locale),
            },
            {
                "metric": tr("price_signal", locale),
                "value": f"{movement_text(latest_yoy_price, locale, 1)} · {price_phrase}",
                "signal": price_signal_display,
                "state": generic_state(price_signal_raw),
                "basis": tr("signal_card_3_sub", locale),
            },
            {
                "metric": tr("supply_signal", locale),
                "value": movement_text(latest_yoy_listings, locale, 1),
                "signal": supply_signal_display,
                "state": generic_state(supply_signal_raw),
                "basis": tr("signal_card_4_sub", locale),
            },
            {
                "metric": tr("moi_trend_3m", locale),
                "value": moi_trend_display,
                "signal": moi_trend_display,
                "state": generic_state(moi_trend_raw),
                "basis": tr("metric_moi_trend", locale),
            },
            {
                "metric": tr("overall_market", locale),
                "value": overall_display,
                "signal": overall_display,
                "state": zone_state(overall_raw),
                "basis": tr("signal_card_5_sub", locale),
            },
        ]

        render_signal_table(signal_rows, locale)

    with right_col:
        render_html(
            f"""
            <div class="spotlight-card">
                <div class="card-kicker">{escape(sanitize_text(tr("guide_title", locale)))}</div>
                <div class="card-main">{escape(sanitize_text(tr("guide_main", locale)))}</div>
                <div class="card-body">{escape(sanitize_text(tr("guide_sub", locale)))}</div>
            </div>
            """
        )

        render_html(
            f"""
            <div class="narrative-card">
                <div class="card-kicker">{escape(sanitize_text(tr("narrative_title", locale)))}</div>
                <div class="card-main">{escape(sanitize_text(tr("as_of", locale)))} {escape(sanitize_text(latest_month))}</div>
                <div class="card-body">
                    {escape(sanitize_text(build_signal_summary(
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
                        lang=locale,
                    )))}
                </div>
            </div>
            """
        )

        render_html(
            f"""
            <div class="guide-card">
                <div class="card-kicker">{escape(sanitize_text(tr("source_note", locale)))}</div>
                <div class="card-main">{escape(sanitize_text(tr("overall_market", locale)))}: {escape(sanitize_text(overall_display))}</div>
                <div class="card-body">{escape(sanitize_text(tr("source_note_text", locale)))}</div>
            </div>
            """
        )

    with st.expander(tr("how_to_read", locale)):
        st.write(tr("how_to_read_text", locale))

    with st.expander(tr("source_note", locale)):
        st.write(tr("source_note_text", locale))

    with st.expander(tr("macro_note_title", locale)):
        st.markdown(tr("macro_note_body", locale))

    with st.expander(tr("show_latest_rows", locale)):
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
        ].copy()

        latest_rows = latest_rows.sort_values("report_month", ascending=False).head(24)

        latest_rows = latest_rows.rename(
            columns={
                "report_month": tr("report_month", locale),
                "months_inventory": tr("months_inventory", locale),
                "listings": tr("listings", locale),
                "sales": tr("sales", locale),
                "median_price": tr("median_price", locale),
                "yoy_listings_pct": tr("yoy_listings_pct", locale),
                "yoy_sales_pct": tr("yoy_sales_pct", locale),
                "yoy_price_pct": tr("yoy_price_pct", locale),
                "mom_inventory_pct": tr("mom_inventory_pct", locale),
                "mom_sales_pct": tr("mom_sales_pct", locale),
                "mom_price_pct": tr("mom_price_pct", locale),
            }
        )

        st.dataframe(latest_rows, width="stretch", hide_index=True)


if __name__ == "__main__":
    main()