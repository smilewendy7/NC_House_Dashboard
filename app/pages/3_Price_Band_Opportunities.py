from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Optional
import re

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Price Band Opportunities / 价格带机会",
    page_icon="🎯",
    layout="wide",
)

PRICE_BAND_PATH = Path("data/analytics/price_ranges_enriched.csv")
alt.data_transformers.disable_max_rows()


# =========================================================
# i18n
# =========================================================
I18N = {
    "zh": {
        "title": "价格带机会",
        "subtitle": "基于价格带比较库存压力、成交吸收速度与买方相对谈判环境。",
        "page_note": "本页用于帮助客户快速理解不同预算区间的市场竞争强弱，识别更值得优先比较的价格带，并辅助看房、报价与沟通顺序安排。该页面反映的是价格带层面的市场结构，不替代具体房源、具体社区和具体定价判断。",
        "missing_file": "缺少 `data/analytics/price_ranges_enriched.csv`。\n\n请先运行：\n\n`python run_full_pipeline.py --workers 4`",
        "missing_cols": "缺少必要字段：",
        "filters": "筛选条件",
        "month": "报告月份",
        "budget": "预算（美元，千）",
        "methodology": "指标说明",
        "methodology_text": """
**库存月数（MOI / Months of Inventory）**  
当前挂牌 ÷ 过去12个月平均月成交。  
用于衡量：按照近期成交速度，当前库存大约需要多少个月消化完。  

常见理解：
- **< 4**：竞争偏强
- **4–6**：相对平衡
- **> 6**：库存压力更高，买方通常更有选择空间

**每月吸收率（Monthly Sell-Through）**  
过去12个月平均月成交 ÷ 当前挂牌。  
用于衡量：当前库存每个月大约能被市场消化多少比例。  
- 越高：成交更快，竞争更强
- 越低：去化更慢，买家可选空间通常更多

**买方杠杆分（Buyer Leverage Score）**  
这是同一个月份内，各价格带之间的相对比较分数：
- 库存压力越高，分数越高
- 吸收越慢，分数越高

分数范围为 0–100，但属于**当月内部相对分**：
- **100**：该月内相对最有利于买方的价格带
- **0**：该月内相对竞争最强的价格带
""",
        "score_explain": "买方杠杆分 = 60% 库存压力 + 40% 慢吸收",
        "market_read_title": "市场解读",
        "market_read_sub": "先看整体环境，再判断你的预算带在当月处于更紧还是更松的位置。",
        "metric_band_count": "价格带数量",
        "metric_best_band": "优势价格带",
        "metric_budget_match": "你的预算带",
        "metric_market_bias": "整体市场状态",
        "metric_best_score": "最高买方杠杆分",
        "metric_nearby_best": "预算附近更优带",
        "seller_leaning": "竞争偏强",
        "balanced": "相对平衡",
        "buyer_leaning": "买方空间较大",
        "regime_title": "整体市场状态",
        "regime_sub": "基于当月价格带中位库存压力判断",
        "position_title": "预算带位置",
        "position_sub": "你的预算带在本月大致处于什么位置",
        "best_title": "邻近优先比较带",
        "best_sub": "预算附近更值得优先比较的价格带",
        "section_market_map": "市场结构",
        "section_market_map_sub": "用库存压力、去化速度与买方相对谈判环境比较不同价格带。",
        "section_ranking": "价格带排序",
        "section_ranking_sub": "从更有利于买方到竞争更强，查看本月价格带相对位置。",
        "section_budget": "预算带建议",
        "section_budget_sub": "将预算映射到当前价格带，并输出更适合客户理解和沟通的判断。",
        "chart1_title": "各价格带库存压力",
        "chart1_caption": "库存月数越高，通常表示该价格带库存压力越大。",
        "chart2_title": "各价格带每月吸收率",
        "chart2_caption": "吸收率越低，通常表示当前库存去化更慢，竞争相对更弱。",
        "chart3_title": "机会矩阵",
        "chart3_caption": "通常左上区域更值得买方优先比较：高库存压力 + 低吸收率。",
        "chart4_title": "买方杠杆分排序",
        "chart4_caption": "该分数用于比较同月不同价格带的相对买方环境，不代表单套房源的绝对议价空间。",
        "top3": "优先关注的价格带",
        "matched_band": "匹配价格带",
        "inv_level": "库存月数",
        "sell_through": "每月吸收率",
        "competition": "竞争强度",
        "leverage": "买方空间",
        "temperature": "市场状态",
        "opportunity_score": "买方杠杆分",
        "tactics": "建议动作",
        "details": "查看匹配价格带明细",
        "unknown": "未知",
        "hot": "竞争偏强",
        "balanced_market": "相对平衡",
        "buyer_friendly": "买方空间较大",
        "comp_high": "高",
        "comp_mid": "中",
        "comp_low": "低",
        "lev_strong": "较大",
        "lev_mid": "中等",
        "lev_weak": "有限",
        "tip1": "如果目标房源在市时间较长，可优先测试更审慎的报价与条款谈判空间。",
        "tip2": "除了价格，也可同步关注 seller credit、维修责任和 closing cost 支持等条件。",
        "tip3": "优先横向比较降价房、重新挂牌房和 DOM 较长房源。",
        "tip4": "即使该价格带整体偏软，优质房源仍可能存在明显竞争。",
        "tip5": "最终判断仍需回到具体地区、街区、学区、房况与定价质量。",
        "tip6": "建议在同一价格带内至少比较 3–5 套相似房源后，再形成报价判断。",
        "tip7": "若预算允许，可把比较范围向上下相邻价格带各扩展一档。",
        "tip8": "本页适合做价格带方向判断，不适合替代单套房决策。",
        "no_valid_month": "没有可用的 report_month。",
        "no_rows_for_month": "所选月份没有数据。",
        "budget_label": "预算",
        "why_this_band": "这个价格带意味着什么",
        "why_line1": "它反映的是该价格带当前的库存压力与成交吸收速度。",
        "why_line2": "它帮助客户判断不同预算区间之间的相对竞争环境。",
        "why_line3": "它不能替代房源层面、社区层面和定价层面的专业判断。",
        "signal_title": "预算带判断",
        "signal_good": "更适合优先比较，并保留谈判空间",
        "signal_mid": "可以纳入比较，但仍需回到具体房源判断",
        "signal_hot": "该预算带竞争仍较明显",
        "signal_note": "这是价格带层面的市场信号，不是单套房源结论。",
        "rank_col_band": "价格带",
        "rank_col_moi": "库存月数",
        "rank_col_sell": "吸收率",
        "rank_col_score": "买方杠杆分",
        "rank_col_signal": "判断",
        "market_zone": "市场区间",
        "zone_seller": "竞争偏强",
        "zone_balanced": "相对平衡",
        "zone_buyer": "买方空间较大",
        "chart_empty": "当前月份数据不足，无法绘图。",
        "matrix_x": "每月吸收率",
        "matrix_y": "库存月数",
        "matrix_note1": "左上：库存压力更高、去化更慢，通常更值得买方优先比较。",
        "matrix_note2": "右下：库存压力更低、去化更快，通常竞争更强。",
        "matrix_spotlight": "矩阵说明",
        "matrix_spotlight_sub": "用这张图观察本月不同价格带的相对位置。",
        "matrix_top3": "本月相对更偏买方的 3 个区间",
        "matrix_best_zone": "优先比较区域",
        "matrix_best_zone_text": "高库存压力 + 低吸收率",
        "matrix_watchout": "使用边界",
        "matrix_watchout_text": "价格带级别的市场数据不能直接回答哪一套房最值得买，但可以帮助决定应先把时间投入到哪些价格区间。",
        "matrix_q1": "优先比较区",
        "matrix_q2": "库存较高但仍有成交",
        "matrix_q3": "竞争较强区",
        "matrix_q4": "观察区",
        "signal_summary_title": "预算带结论",
        "signal_summary_good": "该预算带在本月相对更偏买方，适合优先比较并保留更好的谈判预期。",
        "signal_summary_mid": "该预算带整体较中性，是否存在空间仍需结合具体房源条件判断。",
        "signal_summary_hot": "该预算带整体竞争仍偏强，不建议仅凭价格带信号判断可谈空间。",
        "offer_posture": "建议操作姿态",
        "offer_posture_soft": "先广泛比较，再有选择地谈判",
        "offer_posture_balanced": "以横向比较和房源筛选为主",
        "offer_posture_strong": "优先筛选优质房源，并做好竞争准备",
        "listings_label": "挂牌数",
        "avg_monthly_sales_label": "平均月成交",
        "limitations_title": "本页适合回答什么问题",
        "limitations_body": """
- 比较不同价格带之间的相对竞争环境  
- 判断你的预算带位于更强还是更弱的位置  
- 决定应优先把看房与分析重点放在哪些价格区间  
- 帮助经纪人与客户快速建立市场框架

**不适合直接回答：**
- 某一套房到底值不值得买  
- 某套房是否一定能压价  
- 某个具体社区的短期成交结论
""",
        "relative_score_note": "0–100（当月相对分）",
        "nearby_comparison_note": "预算附近优先比较带",
        "median_moi_note": "中位库存月数",
        "inventory_pressure_axis": "库存月数",
        "score_axis": "买方杠杆分（0–100）",
        "advisory_conclusion": "客户结论",
        "evidence_title": "关键依据",
        "action_title": "建议动作",
        "hero_chip": "北卡价格带分析",
    },
    "en": {
        "title": "Price Band Opportunities",
        "subtitle": "Compare budget tiers by inventory pressure, absorption pace, and relative buyer leverage.",
        "page_note": "This page helps clients understand which price segments are relatively tighter or softer in the current market, so they can prioritize where to compare, tour, and negotiate first. It is designed for price-band strategy and client communication, not as a substitute for property-level, neighborhood-level, or pricing-level analysis.",
        "missing_file": "Missing `data/analytics/price_ranges_enriched.csv`.\n\nRun:\n\n`python run_full_pipeline.py --workers 4`",
        "missing_cols": "Missing required columns:",
        "filters": "Filters",
        "month": "Report Month",
        "budget": "Budget (USD, thousands)",
        "methodology": "Methodology",
        "methodology_text": """
**Months of Inventory (MOI)**  
Active listings ÷ average monthly sales over the last 12 months.  
It estimates how many months the current inventory would take to clear at the recent sales pace.

Common interpretation:
- **< 4**: more competitive
- **4–6**: relatively balanced
- **> 6**: higher inventory pressure, often more room for buyers

**Monthly Sell-Through**  
Average monthly sales over the last 12 months ÷ active listings.  
It shows what share of current inventory is being absorbed each month.
- Higher: faster movement, stronger competition
- Lower: slower movement, usually more buyer choice

**Buyer Leverage Score**  
A monthly **relative** score across price bands:
- Higher inventory pressure → higher score
- Slower absorption → higher score

The score ranges from 0 to 100, but it is an **in-month relative measure**:
- **100**: the most buyer-favorable band in the selected month
- **0**: the most competitive band in the selected month
""",
        "score_explain": "Buyer Leverage Score = 60% inventory pressure + 40% slow absorption",
        "market_read_title": "Market Read",
        "market_read_sub": "Start with the broader environment, then evaluate whether your budget sits in a tighter or softer segment this month.",
        "metric_band_count": "Price Bands",
        "metric_best_band": "Most Buyer-Favorable Band",
        "metric_budget_match": "Your Budget Band",
        "metric_market_bias": "Overall Market Position",
        "metric_best_score": "Highest Buyer Leverage Score",
        "metric_nearby_best": "Best Nearby Band",
        "seller_leaning": "More Competitive",
        "balanced": "Relatively Balanced",
        "buyer_leaning": "More Buyer Room",
        "regime_title": "Overall Market Position",
        "regime_sub": "Based on median inventory pressure across current price bands",
        "position_title": "Budget Band Position",
        "position_sub": "Where your budget band broadly sits this month",
        "best_title": "Nearby Priority Band",
        "best_sub": "A nearby price band worth comparing first",
        "section_market_map": "Market Structure",
        "section_market_map_sub": "Compare price bands using inventory pressure, absorption pace, and relative buyer leverage.",
        "section_ranking": "Price Band Ranking",
        "section_ranking_sub": "Review the relative order of price bands, from more buyer-favorable to more competitive.",
        "section_budget": "Budget Advisory",
        "section_budget_sub": "Map your budget to the current market structure and turn it into a clearer, client-facing conclusion.",
        "chart1_title": "Inventory Pressure by Price Band",
        "chart1_caption": "Higher MOI usually indicates greater inventory pressure in that segment.",
        "chart2_title": "Monthly Sell-Through by Price Band",
        "chart2_caption": "Lower sell-through usually indicates slower absorption and softer competition.",
        "chart3_title": "Opportunity Matrix",
        "chart3_caption": "The upper-left area is usually where buyers should compare first: higher inventory pressure and lower absorption.",
        "chart4_title": "Buyer Leverage Ranking",
        "chart4_caption": "This score compares price bands within the selected month. It does not guarantee negotiability for any single property.",
        "top3": "Priority Price Bands",
        "matched_band": "Matched Price Band",
        "inv_level": "Months of Inventory",
        "sell_through": "Monthly Sell-Through",
        "competition": "Competition",
        "leverage": "Buyer Room",
        "temperature": "Market Position",
        "opportunity_score": "Buyer Leverage Score",
        "tactics": "Recommended Actions",
        "details": "Show Matched Band Details",
        "unknown": "Unknown",
        "hot": "More Competitive",
        "balanced_market": "Relatively Balanced",
        "buyer_friendly": "More Buyer Room",
        "comp_high": "High",
        "comp_mid": "Moderate",
        "comp_low": "Low",
        "lev_strong": "Greater",
        "lev_mid": "Moderate",
        "lev_weak": "Limited",
        "tip1": "If listings in this segment are sitting longer, consider testing more measured pricing and term negotiations.",
        "tip2": "Look beyond price alone: seller credits, repair responsibility, and closing-cost support may matter here.",
        "tip3": "Prioritize price-reduced, relisted, or longer-DOM homes for side-by-side comparison.",
        "tip4": "Even in a softer band, stronger homes may still attract meaningful competition.",
        "tip5": "Final decisions should still return to location, neighborhood, school assignment, condition, and pricing quality.",
        "tip6": "Compare at least 3–5 similar homes within the same price band before forming an offer view.",
        "tip7": "If budget allows, widen comparison one band above and one band below your target range.",
        "tip8": "This page is best used for price-band direction, not as a substitute for single-property decisions.",
        "no_valid_month": "No valid report_month found.",
        "no_rows_for_month": "No rows available for the selected month.",
        "budget_label": "Budget",
        "why_this_band": "What this price band tells you",
        "why_line1": "It reflects current inventory pressure and absorption pace within that budget tier.",
        "why_line2": "It helps clients compare relative competition across budget segments.",
        "why_line3": "It does not replace property-level, neighborhood-level, or pricing-level judgment.",
        "signal_title": "Budget Band Read",
        "signal_good": "A stronger segment to prioritize and negotiate within",
        "signal_mid": "Reasonable to compare, but still requires property-level review",
        "signal_hot": "This segment still appears meaningfully competitive",
        "signal_note": "This is a price-band market signal, not a property-specific conclusion.",
        "rank_col_band": "Price Band",
        "rank_col_moi": "MOI",
        "rank_col_sell": "Sell-Through",
        "rank_col_score": "Buyer Leverage Score",
        "rank_col_signal": "Read",
        "market_zone": "Market Zone",
        "zone_seller": "More Competitive",
        "zone_balanced": "Relatively Balanced",
        "zone_buyer": "More Buyer Room",
        "chart_empty": "Not enough data to render charts for the selected month.",
        "matrix_x": "Monthly Sell-Through",
        "matrix_y": "Months of Inventory",
        "matrix_note1": "Upper-left: higher inventory pressure and slower absorption, often worth a buyer’s attention first.",
        "matrix_note2": "Lower-right: lower inventory pressure and faster absorption, usually more competitive.",
        "matrix_spotlight": "Matrix Notes",
        "matrix_spotlight_sub": "Use this chart to see the relative position of each price band this month.",
        "matrix_top3": "Three more buyer-favorable bands this month",
        "matrix_best_zone": "Priority compare zone",
        "matrix_best_zone_text": "Higher inventory pressure + lower absorption",
        "matrix_watchout": "Use boundary",
        "matrix_watchout_text": "Price-band market data will not identify the single best home to buy, but it can clarify where buyers should focus first.",
        "matrix_q1": "Priority compare zone",
        "matrix_q2": "Higher supply, still moving",
        "matrix_q3": "More competitive zone",
        "matrix_q4": "Watch zone",
        "signal_summary_title": "Budget Band Summary",
        "signal_summary_good": "This budget band looks relatively more favorable for buyers this month and is worth prioritizing.",
        "signal_summary_mid": "This budget band appears more neutral overall. Real leverage still depends heavily on the specific property.",
        "signal_summary_hot": "This budget band still appears competitive overall, so the price-band signal alone should not drive expectations.",
        "offer_posture": "Suggested Approach",
        "offer_posture_soft": "Compare broadly, then negotiate selectively",
        "offer_posture_balanced": "Rely on disciplined comparison and screening",
        "offer_posture_strong": "Prioritize stronger filtering and stay competition-ready",
        "listings_label": "Listings",
        "avg_monthly_sales_label": "Avg Monthly Sales",
        "limitations_title": "What this page is best used for",
        "limitations_body": """
- Comparing relative competition across price bands  
- Understanding whether your budget sits in a tighter or softer segment  
- Deciding where to focus tours and analysis first  
- Giving agents and clients a clearer market framework

**Not best used for directly answering:**
- Whether one specific property is worth buying  
- Whether one home can definitely be negotiated down  
- A short-term conclusion about one specific neighborhood
""",
        "relative_score_note": "0–100 (in-month relative)",
        "nearby_comparison_note": "Best nearby band to compare",
        "median_moi_note": "Median inventory pressure",
        "inventory_pressure_axis": "Months of Inventory",
        "score_axis": "Buyer Leverage Score (0–100)",
        "advisory_conclusion": "Client Conclusion",
        "evidence_title": "Key Evidence",
        "action_title": "Recommended Actions",
        "hero_chip": "NC Price Band Analytics",
    },
}


# =========================================================
# CSS
# =========================================================
def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root{
            --bg:#f3f6fb;
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
            --shadow:0 10px 26px rgba(15, 23, 42, 0.06);
            --shadow-strong:0 18px 50px rgba(15, 23, 42, 0.12);
        }

        html, body, [class*="css"] {
            font-family: Inter, "Segoe UI", "PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(37,99,235,0.04), transparent 20%),
                radial-gradient(circle at top right, rgba(14,165,233,0.03), transparent 18%),
                linear-gradient(180deg, #f8fafc 0%, #f3f6fb 100%);
        }

        .block-container {
            max-width: 1460px;
            padding-top: 0.8rem;
            padding-bottom: 2.2rem;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
            border-right: 1px solid #e5e7eb;
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
            margin-bottom: 1.1rem;
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
            font-size: 2.04rem;
            font-weight: 900;
            line-height: 1.05;
            letter-spacing: -0.02em;
            margin-bottom: 0.38rem;
        }

        .hero-subtitle {
            font-size: 1rem;
            color: rgba(255,255,255,0.92);
            margin-bottom: 0.45rem;
        }

        .hero-note {
            max-width: 1120px;
            font-size: 0.92rem;
            line-height: 1.64;
            color: rgba(255,255,255,0.80);
        }

        .summary-card,
        .executive-card,
        .top-op-card,
        .statement-card,
        .evidence-card,
        .action-card,
        .spotlight-card,
        .limit-card {
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 22px;
            box-shadow: var(--shadow);
        }

        .summary-card {
            min-height: 136px;
            padding: 16px 18px;
            position: relative;
            overflow: hidden;
            background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
        }

        .summary-card::after {
            content:"";
            position:absolute;
            top:0;
            right:0;
            width:86px;
            height:86px;
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
            font-size: 1.16rem;
            font-weight: 900;
            line-height: 1.25;
            color: var(--text);
            margin-bottom: 0.30rem;
            word-break: break-word;
            white-space: normal;
        }

        .summary-sub {
            font-size: 0.88rem;
            color: var(--muted);
            line-height: 1.45;
            margin-top: 0.42rem;
        }

        .summary-sub:empty {
            display:none;
        }

        .section-head {
            margin-top: 0.15rem;
            margin-bottom: 0.8rem;
        }

        .section-title {
            font-size: 1.16rem;
            font-weight: 900;
            color: var(--text);
            letter-spacing: -0.01em;
            margin-bottom: 0.08rem;
        }

        .section-subtitle {
            font-size: 0.92rem;
            color: var(--muted);
            line-height: 1.56;
        }

        .executive-card {
            min-height: 162px;
            padding: 18px 20px;
            background: linear-gradient(180deg, #ffffff 0%, #fcfdff 100%);
        }

        .executive-kicker {
            font-size: 0.72rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--muted);
            margin-bottom: 0.35rem;
        }

        .executive-title {
            font-size: 0.95rem;
            font-weight: 800;
            color: var(--text);
            margin-bottom: 0.2rem;
        }

        .executive-main {
            font-size: 1.30rem;
            font-weight: 900;
            line-height: 1.18;
            color: var(--text);
            margin-bottom: 0.34rem;
        }

        .executive-sub {
            font-size: 0.90rem;
            color: var(--muted);
            line-height: 1.56;
            margin-top: 0.42rem;
        }

        .chart-title {
            font-size: 0.98rem;
            font-weight: 860;
            color: var(--text);
            margin-bottom: 0.16rem;
        }

        .chart-caption {
            font-size: 0.88rem;
            color: var(--muted);
            line-height: 1.52;
            margin-bottom: 0.55rem;
        }

        .signal-chip {
            display:inline-flex;
            align-items:center;
            gap:8px;
            padding: 0.38rem 0.70rem;
            border-radius: 999px;
            font-size: 0.76rem;
            font-weight: 860;
            line-height: 1;
            white-space: nowrap;
            margin-top: 2px;
            border: 1px solid transparent;
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

        .spotlight-card {
            height: 100%;
            padding: 18px;
            background:
                radial-gradient(circle at top right, rgba(56,189,248,0.10), transparent 24%),
                linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        }

        .spotlight-title {
            font-size: 0.74rem;
            font-weight: 900;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            color: var(--muted);
            margin-bottom: 0.38rem;
        }

        .spotlight-main {
            font-size: 1.01rem;
            font-weight: 900;
            color: var(--text);
            line-height: 1.3;
            margin-bottom: 0.28rem;
        }

        .spotlight-sub {
            font-size: 0.9rem;
            color: var(--muted);
            line-height: 1.6;
            margin-bottom: 0.78rem;
        }

        .spotlight-pill {
            display: inline-flex;
            align-items: center;
            padding: 0.36rem 0.66rem;
            border-radius: 999px;
            font-size: 0.74rem;
            font-weight: 820;
            color: var(--text);
            background: #e2e8f0;
            margin: 0 0.36rem 0.45rem 0;
        }

        .spotlight-rank {
            display:flex;
            align-items:flex-start;
            gap:10px;
            padding:10px 0;
            border-bottom:1px solid var(--line-soft);
        }

        .spotlight-rank:last-child {
            border-bottom:none;
        }

        .spotlight-badge {
            min-width:36px;
            height:36px;
            border-radius:12px;
            display:flex;
            align-items:center;
            justify-content:center;
            background:#0f172a;
            color:#fff;
            font-size:0.78rem;
            font-weight:900;
        }

        .spotlight-band {
            font-size: 0.93rem;
            font-weight: 860;
            color: var(--text);
            line-height: 1.24;
            margin-bottom: 0.24rem;
        }

        .spotlight-meta {
            font-size: 0.84rem;
            color: var(--muted);
            margin-top: 0.2rem;
            line-height: 1.48;
        }

        .matrix-legend-note {
            margin-top: 0.42rem;
            font-size: 0.84rem;
            line-height: 1.58;
            color: var(--muted);
        }

        .top-op-card {
            padding: 15px 16px;
            min-height: 120px;
            background: linear-gradient(180deg, #ffffff 0%, #fafcff 100%);
        }

        .top-op-rank {
            font-size: 0.72rem;
            font-weight: 900;
            color: var(--muted);
            margin-bottom: 0.34rem;
            letter-spacing: 0.04em;
        }

        .top-op-band {
            font-size: 1.02rem;
            font-weight: 900;
            color: var(--text);
            line-height: 1.22;
            margin-bottom: 0.24rem;
        }

        .top-op-meta {
            font-size: 0.87rem;
            color: var(--muted);
            line-height: 1.46;
            margin-top: 0.35rem;
        }

        .statement-card {
            padding: 22px 24px;
            border-radius: 24px;
            background: linear-gradient(135deg, #fff8f1 0%, #fffdf7 100%);
            border-color: #fed7aa;
        }

        .statement-kicker {
            font-size: 0.74rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #9a3412;
            margin-bottom: 0.42rem;
        }

        .statement-main {
            font-size: 1.56rem;
            font-weight: 900;
            line-height: 1.18;
            color: var(--text);
            margin-bottom: 0.22rem;
        }

        .statement-sub {
            font-size: 0.95rem;
            color: #7c2d12;
            line-height: 1.58;
            margin-top: 0.28rem;
        }

        .metric-strip {
            display:grid;
            grid-template-columns: repeat(6, minmax(0,1fr));
            gap: 12px;
            margin-top: 12px;
            margin-bottom: 12px;
        }

        .metric-box {
            background: #ffffff;
            border: 1px solid var(--line);
            border-radius: 16px;
            padding: 13px 14px;
            box-shadow: var(--shadow);
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
        }

        .evidence-card, .action-card, .limit-card {
            padding: 18px 20px;
            border-radius: 20px;
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
            line-height: 1.34;
        }

        .card-body {
            margin-top: 0.40rem;
            font-size: 0.92rem;
            color: var(--muted);
            line-height: 1.68;
        }

        .card-body strong {
            color: var(--text);
        }

        .action-list {
            list-style: none;
            padding-left: 0;
            margin: 0.3rem 0 0 0;
        }

        .action-list li {
            position: relative;
            padding-left: 1.9rem;
            margin-bottom: 0.62rem;
            color: var(--muted);
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
            background: #22c55e;
            color: #ffffff;
            font-size: 0.78rem;
            font-weight: 900;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 6px 14px rgba(34,197,94,0.22);
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
        }

        @media (max-width: 1280px) {
            .metric-strip {
                grid-template-columns: repeat(3, minmax(0,1fr));
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
    """
    Extra-safe text sanitizer for HTML rendering.
    Prevents accidental raw HTML from showing inside cards.
    """
    text = plain_text(value)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def fmt_num(value, decimals: int = 1) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    try:
        return f"{float(value):,.{decimals}f}"
    except Exception:
        return "N/A"


def fmt_pct(value, decimals: int = 1) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    try:
        return f"{float(value):.{decimals}%}"
    except Exception:
        return "N/A"


def fmt_money(value) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    try:
        return f"${float(value):,.0f}"
    except Exception:
        return "N/A"


def safe_minmax_scale(series: pd.Series, reverse: bool = False) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    valid = s.dropna()
    if valid.empty:
        return pd.Series(np.nan, index=series.index)
    s_min = valid.min()
    s_max = valid.max()
    if s_max == s_min:
        out = pd.Series(50.0, index=series.index)
    else:
        out = (s - s_min) / (s_max - s_min) * 100.0
    if reverse:
        out = 100 - out
    return out.clip(0, 100)


def localize_market_zone(series_or_value, t: dict):
    mapping = {
        "More Competitive": t["zone_seller"],
        "Balanced": t["zone_balanced"],
        "More Buyer Room": t["zone_buyer"],
    }
    if isinstance(series_or_value, pd.Series):
        return series_or_value.map(lambda x: mapping.get(x, x))
    return mapping.get(series_or_value, series_or_value)


def market_bias_label(median_moi: float, t: dict) -> str:
    if pd.isna(median_moi):
        return t["unknown"]
    if median_moi < 4:
        return t["seller_leaning"]
    if median_moi <= 6:
        return t["balanced"]
    return t["buyer_leaning"]


def get_signal_state(moi: float, sell_through: float) -> str:
    if pd.notna(moi):
        if moi > 6:
            return "soft"
        if moi < 4:
            return "hot"
        return "balanced"

    if pd.notna(sell_through):
        if sell_through < 0.17:
            return "soft"
        if sell_through > 0.25:
            return "hot"
        return "balanced"

    return "balanced"


def get_signal_badge_meta(state: str, t: dict):
    if state == "soft":
        return "🟢", t["buyer_friendly"]
    if state == "hot":
        return "🔴", t["hot"]
    return "🟡", t["balanced_market"]


def signal_chip_html(state: str, label: str) -> str:
    icon, _ = get_signal_badge_meta(
        state,
        {
            "buyer_friendly": label,
            "hot": label,
            "balanced_market": label,
        },
    )
    state = state if state in {"soft", "balanced", "hot"} else "balanced"
    safe_label = escape(sanitize_text(label))
    safe_icon = escape(plain_text(icon))
    return (
        f'<span class="signal-chip {state}">'
        f'<span class="signal-chip-icon">{safe_icon}</span>'
        f'<span>{safe_label}</span>'
        f"</span>"
    )


def competition_label(moi: float, t: dict) -> str:
    if pd.isna(moi):
        return t["unknown"]
    if moi < 4:
        return t["comp_high"]
    if moi <= 6:
        return t["comp_mid"]
    return t["comp_low"]


def leverage_label(moi: float, sell_through: float, t: dict) -> str:
    state = get_signal_state(moi, sell_through)
    if state == "soft":
        return t["lev_strong"]
    if state == "hot":
        return t["lev_weak"]
    return t["lev_mid"]


def temperature_label(moi: float, t: dict) -> str:
    if pd.isna(moi):
        return t["unknown"]
    if moi < 4:
        return t["hot"]
    if moi <= 6:
        return t["balanced_market"]
    return t["buyer_friendly"]


def interpret_band(moi: float, sell_through: float, score: float, t: dict) -> str:
    state = get_signal_state(moi, sell_through)
    if state == "soft":
        return t["buyer_friendly"]
    if state == "hot":
        return t["hot"]
    return t["balanced_market"]


def offer_posture(moi: float, sell_through: float, t: dict) -> str:
    state = get_signal_state(moi, sell_through)
    if state == "soft":
        return t["offer_posture_soft"]
    if state == "hot":
        return t["offer_posture_strong"]
    return t["offer_posture_balanced"]


def signal_summary(moi: float, sell_through: float, t: dict) -> str:
    state = get_signal_state(moi, sell_through)
    if state == "soft":
        return t["signal_summary_good"]
    if state == "hot":
        return t["signal_summary_hot"]
    return t["signal_summary_mid"]


def get_signal_text(moi: float, sell_through: float, t: dict) -> str:
    state = get_signal_state(moi, sell_through)
    if state == "soft":
        return t["signal_good"]
    if state == "hot":
        return t["signal_hot"]
    return t["signal_mid"]


def build_tactics(moi: float, sell_through: float, t: dict) -> list[str]:
    state = get_signal_state(moi, sell_through)
    if state == "soft":
        return [t["tip1"], t["tip2"], t["tip3"], t["tip5"], t["tip7"]]
    if state == "hot":
        return [t["tip4"], t["tip5"], t["tip6"], t["tip8"]]
    return [t["tip2"], t["tip5"], t["tip6"], t["tip7"], t["tip8"]]


def pick_budget_band(df_m: pd.DataFrame, budget_usd: float) -> Optional[pd.Series]:
    if df_m.empty:
        return None

    if {"range_min", "range_max"}.issubset(df_m.columns):
        matched = df_m[
            df_m["range_min"].notna()
            & df_m["range_max"].notna()
            & (df_m["range_min"] <= budget_usd)
            & (df_m["range_max"] >= budget_usd)
        ]
        if not matched.empty:
            return matched.sort_values(["range_rank", "range_min"], na_position="last").iloc[0]

    tmp = df_m.copy()
    tmp["midpoint"] = np.where(
        tmp["range_min"].notna() & tmp["range_max"].notna(),
        (tmp["range_min"] + tmp["range_max"]) / 2.0,
        tmp["range_min"],
    )
    tmp["dist"] = (tmp["midpoint"] - budget_usd).abs()
    tmp = tmp.sort_values(["dist", "range_rank", "range_min"], na_position="last")
    if tmp.empty:
        return None
    return tmp.iloc[0]


def pick_nearby_best_band(df_m: pd.DataFrame, budget_row: Optional[pd.Series]) -> Optional[pd.Series]:
    if budget_row is None or df_m.empty:
        return None

    rank_val = budget_row.get("range_rank")
    if pd.notna(rank_val):
        nearby = df_m[
            df_m["range_rank"].notna()
            & (df_m["range_rank"] >= float(rank_val) - 1)
            & (df_m["range_rank"] <= float(rank_val) + 1)
        ].copy()
    else:
        nearby = df_m.copy()

    nearby = nearby.dropna(subset=["buyer_leverage_score"])
    if nearby.empty:
        return None

    nearby = nearby.sort_values("buyer_leverage_score", ascending=False, na_position="last")
    return nearby.iloc[0]


def prepare_top3(df_m: pd.DataFrame) -> pd.DataFrame:
    top3 = (
        df_m.dropna(subset=["buyer_leverage_score"])
        .sort_values("buyer_leverage_score", ascending=False, na_position="last")
        .head(3)
        .copy()
        .reset_index(drop=True)
    )
    if top3.empty:
        return top3

    top3["rank_label"] = [f"#{i}" for i in range(1, len(top3) + 1)]
    top3["short_label"] = top3["price_range"].astype(str)
    return top3


# =========================================================
# Professional metrics
# =========================================================
def add_professional_metrics(df_m: pd.DataFrame) -> pd.DataFrame:
    out = df_m.copy()

    for col in ["listings", "sales_prev_12mo", "months_inventory", "range_min", "range_max", "range_rank"]:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    out["avg_monthly_sales"] = out["sales_prev_12mo"] / 12.0

    calc_moi = np.where(
        (out["avg_monthly_sales"] > 0) & out["listings"].notna(),
        out["listings"] / out["avg_monthly_sales"],
        np.nan,
    )
    if "months_inventory" not in out.columns:
        out["months_inventory"] = calc_moi
    else:
        out["months_inventory"] = out["months_inventory"].where(out["months_inventory"].notna(), calc_moi)

    out["monthly_sell_through"] = np.where(
        (out["listings"] > 0) & out["avg_monthly_sales"].notna(),
        out["avg_monthly_sales"] / out["listings"],
        np.nan,
    )

    out["market_zone_en"] = np.select(
        [
            out["months_inventory"] < 4,
            out["months_inventory"].between(4, 6, inclusive="both"),
            out["months_inventory"] > 6,
        ],
        [
            "More Competitive",
            "Balanced",
            "More Buyer Room",
        ],
        default="Balanced",
    )

    moi_score = safe_minmax_scale(out["months_inventory"], reverse=False)
    slow_absorption_score = safe_minmax_scale(out["monthly_sell_through"], reverse=True)
    out["buyer_leverage_score"] = (moi_score * 0.60 + slow_absorption_score * 0.40).round(1)

    return out


# =========================================================
# Data loader
# =========================================================
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
    ]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    sort_cols = [c for c in ["report_month", "range_rank", "range_min"] if c in df.columns]
    if sort_cols:
        df = df.sort_values(sort_cols, na_position="last")

    return df


# =========================================================
# Render helpers
# =========================================================
def render_html(html: str) -> None:
    st.markdown(html, unsafe_allow_html=True)


def render_hero(t: dict) -> None:
    render_html(
        "".join(
            [
                '<div class="hero">',
                f'<div class="hero-chip">{escape(sanitize_text(t["hero_chip"]))}</div>',
                f'<div class="hero-title">{escape(sanitize_text(t["title"]))}</div>',
                f'<div class="hero-subtitle">{escape(sanitize_text(t["subtitle"]))}</div>',
                f'<div class="hero-note">{escape(sanitize_text(t["page_note"]))}</div>',
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
    badge_html = signal_chip_html(state, badge_label) if (state in {"hot", "balanced", "soft"} and badge_label) else ""
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


def render_executive_card(
    kicker: str,
    title: str,
    main: str,
    sub: str,
    state: str | None = None,
    badge_label: str | None = None,
) -> None:
    badge_html = signal_chip_html(state, badge_label) if (state in {"hot", "balanced", "soft"} and badge_label) else ""
    html = "".join(
        [
            '<div class="executive-card">',
            f'<div class="executive-kicker">{escape(sanitize_text(kicker))}</div>',
            f'<div class="executive-title">{escape(sanitize_text(title))}</div>',
            f'<div class="executive-main">{escape(sanitize_text(main))}</div>',
            badge_html,
            f'<div class="executive-sub">{escape(sanitize_text(sub))}</div>',
            "</div>",
        ]
    )
    render_html(html)


def render_matrix_spotlight(top3_df: pd.DataFrame, t: dict) -> None:
    parts = [
        '<div class="spotlight-card">',
        f'<div class="spotlight-title">{escape(sanitize_text(t["matrix_spotlight"]))}</div>',
        f'<div class="spotlight-main">{escape(sanitize_text(t["matrix_spotlight_sub"]))}</div>',
        f'<div class="spotlight-sub">{escape(sanitize_text(t["matrix_note1"]))}</div>',
        f'<span class="spotlight-pill">{escape(sanitize_text(t["matrix_best_zone"]))}: {escape(sanitize_text(t["matrix_best_zone_text"]))}</span>',
        f'<div class="spotlight-title" style="margin-top:0.9rem;">{escape(sanitize_text(t["matrix_top3"]))}</div>',
    ]

    if top3_df.empty:
        parts.append(f'<div class="spotlight-sub">{escape(sanitize_text(t["chart_empty"]))}</div>')
    else:
        for _, row in top3_df.iterrows():
            state = get_signal_state(row.get("months_inventory", np.nan), row.get("monthly_sell_through", np.nan))
            _, label = get_signal_badge_meta(state, t)
            parts.extend(
                [
                    '<div class="spotlight-rank">',
                    f'<div class="spotlight-badge">{escape(sanitize_text(row["rank_label"]))}</div>',
                    "<div>",
                    f'<div class="spotlight-band">{escape(sanitize_text(row["price_range"]))}</div>',
                    signal_chip_html(state, label),
                    (
                        f'<div class="spotlight-meta">'
                        f'MOI {fmt_num(row.get("months_inventory", np.nan), 1)} · '
                        f'{escape(sanitize_text(t["sell_through"]))} {fmt_pct(row.get("monthly_sell_through", np.nan))} · '
                        f'{escape(sanitize_text(t["opportunity_score"]))} {fmt_num(row.get("buyer_leverage_score", np.nan), 1)}'
                        f"</div>"
                    ),
                    "</div>",
                    "</div>",
                ]
            )

    parts.extend(
        [
            f'<div class="spotlight-title" style="margin-top:0.95rem;">{escape(sanitize_text(t["matrix_watchout"]))}</div>',
            f'<div class="spotlight-sub" style="margin-bottom:0;">{escape(sanitize_text(t["matrix_watchout_text"]))}</div>',
            "</div>",
        ]
    )
    render_html("".join(parts))


def render_top_op_card(rank: int, band: str, moi: float, score: float, sell: float, t: dict) -> None:
    state = get_signal_state(moi, sell)
    _, label = get_signal_badge_meta(state, t)

    html = "".join(
        [
            '<div class="top-op-card">',
            f'<div class="top-op-rank">#{rank}</div>',
            f'<div class="top-op-band">{escape(sanitize_text(band))}</div>',
            signal_chip_html(state, label),
            f'<div class="top-op-meta">MOI {fmt_num(moi, 1)} · {escape(sanitize_text(t["opportunity_score"]))} {fmt_num(score, 1)}</div>',
            "</div>",
        ]
    )
    render_html(html)


# =========================================================
# Charts
# =========================================================
def build_moi_chart(df_m: pd.DataFrame, t: dict) -> alt.Chart:
    plot_df = (
        df_m.dropna(subset=["price_range", "months_inventory"])
        .sort_values("months_inventory", ascending=True)
        .copy()
    )
    if plot_df.empty:
        return alt.Chart(pd.DataFrame({"x": [], "y": []})).mark_bar()

    plot_df["market_zone"] = localize_market_zone(plot_df["market_zone_en"], t)
    zone_domain = [t["zone_seller"], t["zone_balanced"], t["zone_buyer"]]
    color_scale = alt.Scale(domain=zone_domain, range=["#ef4444", "#f59e0b", "#22c55e"])

    base = alt.Chart(plot_df).encode(
        y=alt.Y("price_range:N", sort=list(plot_df["price_range"]), title=None),
        x=alt.X(
            "months_inventory:Q",
            title=t["inventory_pressure_axis"],
            axis=alt.Axis(format=".1f", grid=True, tickCount=6),
        ),
        color=alt.Color("market_zone:N", scale=color_scale, legend=alt.Legend(title=t["market_zone"])),
        tooltip=[
            alt.Tooltip("price_range:N", title=t["matched_band"]),
            alt.Tooltip("months_inventory:Q", title="MOI", format=".2f"),
            alt.Tooltip("listings:Q", title=t["listings_label"], format=".0f"),
            alt.Tooltip("avg_monthly_sales:Q", title=t["avg_monthly_sales_label"], format=".1f"),
            alt.Tooltip("market_zone:N", title=t["market_zone"]),
        ],
    )

    bars = base.mark_bar(cornerRadiusEnd=7, size=22)
    labels = base.mark_text(
        align="left",
        baseline="middle",
        dx=6,
        fontSize=11,
        color="#0f172a",
    ).encode(text=alt.Text("months_inventory:Q", format=".1f"))

    rule4 = alt.Chart(pd.DataFrame({"x": [4]})).mark_rule(color="#94a3b8", strokeDash=[6, 6]).encode(x="x:Q")
    rule6 = alt.Chart(pd.DataFrame({"x": [6]})).mark_rule(color="#cbd5e1", strokeDash=[6, 6]).encode(x="x:Q")

    return (bars + labels + rule4 + rule6).properties(height=400)


def build_sellthrough_chart(df_m: pd.DataFrame, t: dict) -> alt.Chart:
    plot_df = (
        df_m.dropna(subset=["price_range", "monthly_sell_through"])
        .sort_values("monthly_sell_through", ascending=True)
        .copy()
    )
    if plot_df.empty:
        return alt.Chart(pd.DataFrame({"x": [], "y": []})).mark_bar()

    base = alt.Chart(plot_df).encode(
        y=alt.Y("price_range:N", sort=list(plot_df["price_range"]), title=None),
        x=alt.X(
            "monthly_sell_through:Q",
            title=t["sell_through"],
            axis=alt.Axis(format=".0%", grid=True, tickCount=6),
        ),
        tooltip=[
            alt.Tooltip("price_range:N", title=t["matched_band"]),
            alt.Tooltip("monthly_sell_through:Q", title=t["sell_through"], format=".1%"),
            alt.Tooltip("listings:Q", title=t["listings_label"], format=".0f"),
            alt.Tooltip("avg_monthly_sales:Q", title=t["avg_monthly_sales_label"], format=".1f"),
        ],
    )

    bars = base.mark_bar(cornerRadiusEnd=7, size=22, color="#2563eb")
    labels = base.mark_text(
        align="left",
        baseline="middle",
        dx=6,
        fontSize=11,
        color="#0f172a",
    ).encode(text=alt.Text("monthly_sell_through:Q", format=".0%"))

    return (bars + labels).properties(height=400)


def build_matrix_chart(df_m: pd.DataFrame, top3_df: pd.DataFrame, t: dict) -> alt.Chart:
    plot_df = df_m.dropna(subset=["price_range", "months_inventory", "monthly_sell_through", "buyer_leverage_score"]).copy()
    if plot_df.empty:
        return alt.Chart(pd.DataFrame({"x": [], "y": []})).mark_circle()

    plot_df["market_zone"] = localize_market_zone(plot_df["market_zone_en"], t)

    top3_names = top3_df["price_range"].tolist() if not top3_df.empty else []
    rank_map = dict(zip(top3_df["price_range"], top3_df["rank_label"])) if not top3_df.empty else {}
    short_map = dict(zip(top3_df["price_range"], top3_df["short_label"])) if not top3_df.empty else {}

    plot_df["is_top3"] = plot_df["price_range"].isin(top3_names)
    plot_df["rank_label"] = plot_df["price_range"].map(rank_map)
    plot_df["top3_label"] = plot_df["price_range"].map(short_map)

    zone_domain = [t["zone_seller"], t["zone_balanced"], t["zone_buyer"]]
    color_scale = alt.Scale(domain=zone_domain, range=["#ef4444", "#f59e0b", "#22c55e"])

    x_valid = plot_df["monthly_sell_through"].dropna()
    y_valid = plot_df["months_inventory"].dropna()

    x_min = max(0.0, float(x_valid.min()) - 0.03) if not x_valid.empty else 0.0
    x_max = float(x_valid.max()) + 0.03 if not x_valid.empty else 0.5
    y_min = max(0.0, float(y_valid.min()) - 0.8) if not y_valid.empty else 0.0
    y_max = float(y_valid.max()) + 0.8 if not y_valid.empty else 10.0

    x_mid = float(plot_df["monthly_sell_through"].median()) if not plot_df["monthly_sell_through"].dropna().empty else (x_min + x_max) / 2
    y_mid = 4.0

    quadrant_df = pd.DataFrame(
        [
            {"x0": x_min, "x1": x_mid, "y0": y_mid, "y1": y_max, "label": t["matrix_q1"], "fill": "#dcfce7"},
            {"x0": x_mid, "x1": x_max, "y0": y_mid, "y1": y_max, "label": t["matrix_q2"], "fill": "#fef3c7"},
            {"x0": x_min, "x1": x_mid, "y0": y_min, "y1": y_mid, "label": t["matrix_q4"], "fill": "#e0f2fe"},
            {"x0": x_mid, "x1": x_max, "y0": y_min, "y1": y_mid, "label": t["matrix_q3"], "fill": "#fee2e2"},
        ]
    )

    quadrant_rect = alt.Chart(quadrant_df).mark_rect(opacity=0.16).encode(
        x=alt.X("x0:Q", scale=alt.Scale(domain=[x_min, x_max], nice=False)),
        x2="x1:Q",
        y=alt.Y("y0:Q", scale=alt.Scale(domain=[y_min, y_max], nice=False)),
        y2="y1:Q",
        color=alt.Color("fill:N", scale=None, legend=None),
    )

    quadrant_text_df = pd.DataFrame(
        [
            {"x": (x_min + x_mid) / 2, "y": y_max - 0.35, "label": t["matrix_q1"]},
            {"x": (x_mid + x_max) / 2, "y": y_max - 0.35, "label": t["matrix_q2"]},
            {"x": (x_min + x_mid) / 2, "y": y_min + 0.45, "label": t["matrix_q4"]},
            {"x": (x_mid + x_max) / 2, "y": y_min + 0.45, "label": t["matrix_q3"]},
        ]
    )

    quadrant_text = alt.Chart(quadrant_text_df).mark_text(
        fontSize=11,
        fontWeight="bold",
        color="#475569",
        opacity=0.70,
    ).encode(
        x=alt.X("x:Q", scale=alt.Scale(domain=[x_min, x_max], nice=False)),
        y=alt.Y("y:Q", scale=alt.Scale(domain=[y_min, y_max], nice=False)),
        text="label:N",
    )

    base = alt.Chart(plot_df).encode(
        x=alt.X(
            "monthly_sell_through:Q",
            title=t["matrix_x"],
            scale=alt.Scale(domain=[x_min, x_max], nice=False),
            axis=alt.Axis(format=".0%", tickCount=6, grid=True),
        ),
        y=alt.Y(
            "months_inventory:Q",
            title=t["matrix_y"],
            scale=alt.Scale(domain=[y_min, y_max], nice=False),
            axis=alt.Axis(tickCount=6, grid=True),
        ),
        tooltip=[
            alt.Tooltip("price_range:N", title=t["matched_band"]),
            alt.Tooltip("months_inventory:Q", title="MOI", format=".2f"),
            alt.Tooltip("monthly_sell_through:Q", title=t["sell_through"], format=".1%"),
            alt.Tooltip("buyer_leverage_score:Q", title=t["opportunity_score"], format=".1f"),
            alt.Tooltip("listings:Q", title=t["listings_label"], format=".0f"),
            alt.Tooltip("avg_monthly_sales:Q", title=t["avg_monthly_sales_label"], format=".1f"),
        ],
    )

    background_points = (
        base.transform_filter(alt.datum.is_top3 == False)
        .mark_circle(size=110, opacity=0.92, stroke="white", strokeWidth=1.2)
        .encode(color=alt.Color("market_zone:N", scale=color_scale, legend=alt.Legend(title=t["market_zone"])))
    )

    top3_points = (
        base.transform_filter(alt.datum.is_top3 == True)
        .mark_circle(size=240, opacity=1.0, stroke="#0f172a", strokeWidth=2.0)
        .encode(color=alt.Color("market_zone:N", scale=color_scale, legend=None))
    )

    top3_rank = (
        alt.Chart(plot_df[plot_df["is_top3"]])
        .mark_text(fontSize=11, fontWeight="bold", color="#0f172a", dy=-15)
        .encode(
            x=alt.X("monthly_sell_through:Q", scale=alt.Scale(domain=[x_min, x_max], nice=False)),
            y=alt.Y("months_inventory:Q", scale=alt.Scale(domain=[y_min, y_max], nice=False)),
            text="rank_label:N",
        )
    )

    top3_short = (
        alt.Chart(plot_df[plot_df["is_top3"]])
        .mark_text(fontSize=10, color="#0f172a", dy=15)
        .encode(
            x=alt.X("monthly_sell_through:Q", scale=alt.Scale(domain=[x_min, x_max], nice=False)),
            y=alt.Y("months_inventory:Q", scale=alt.Scale(domain=[y_min, y_max], nice=False)),
            text="top3_label:N",
        )
    )

    h_rule4 = alt.Chart(pd.DataFrame({"y": [4]})).mark_rule(color="#94a3b8", strokeDash=[5, 5], opacity=0.8).encode(y="y:Q")
    h_rule6 = alt.Chart(pd.DataFrame({"y": [6]})).mark_rule(color="#cbd5e1", strokeDash=[4, 4], opacity=0.65).encode(y="y:Q")
    v_rule = alt.Chart(pd.DataFrame({"x": [x_mid]})).mark_rule(color="#94a3b8", strokeDash=[5, 5], opacity=0.6).encode(x="x:Q")

    return (
        quadrant_rect
        + quadrant_text
        + background_points
        + top3_points
        + top3_rank
        + top3_short
        + h_rule4
        + h_rule6
        + v_rule
    ).properties(height=455)


def build_score_chart(df_m: pd.DataFrame, t: dict) -> alt.Chart:
    plot_df = (
        df_m.dropna(subset=["price_range", "buyer_leverage_score"])
        .sort_values("buyer_leverage_score", ascending=False)
        .copy()
    )
    if plot_df.empty:
        return alt.Chart(pd.DataFrame({"x": [], "y": []})).mark_bar()

    base = alt.Chart(plot_df).encode(
        y=alt.Y("price_range:N", sort=list(plot_df["price_range"]), title=None),
        x=alt.X(
            "buyer_leverage_score:Q",
            title=t["score_axis"],
            scale=alt.Scale(domain=[0, 100]),
            axis=alt.Axis(format=".0f", grid=True, tickCount=6),
        ),
        tooltip=[
            alt.Tooltip("price_range:N", title=t["matched_band"]),
            alt.Tooltip("buyer_leverage_score:Q", title=t["opportunity_score"], format=".1f"),
            alt.Tooltip("months_inventory:Q", title="MOI", format=".2f"),
            alt.Tooltip("monthly_sell_through:Q", title=t["sell_through"], format=".1%"),
        ],
    )

    bars = base.mark_bar(cornerRadiusEnd=7, size=20, color="#0ea5e9")
    labels = base.mark_text(
        align="left",
        baseline="middle",
        dx=6,
        fontSize=11,
        color="#0f172a",
    ).encode(text=alt.Text("buyer_leverage_score:Q", format=".1f"))

    return (bars + labels).properties(height=370)


# =========================================================
# Ranking styling
# =========================================================
def style_ranking(df: pd.DataFrame, t: dict):
    score_col = t["rank_col_score"]
    signal_col = t["rank_col_signal"]

    def row_style(row):
        signal = str(row.get(signal_col, ""))
        if "🟢" in signal:
            return ["background-color:#f0fdf4; color:#14532d;"] * len(row)
        if "🟡" in signal:
            return ["background-color:#fffbeb; color:#92400e;"] * len(row)
        if "🔴" in signal:
            return ["background-color:#fef2f2; color:#991b1b;"] * len(row)
        return [""] * len(row)

    def emphasize_score(val):
        if pd.isna(val):
            return ""
        try:
            v = float(val)
        except Exception:
            return ""
        if v >= 70:
            return "font-weight:800; color:#166534;"
        if v >= 40:
            return "font-weight:800; color:#9a3412;"
        return "font-weight:800; color:#991b1b;"

    styler = (
        df.style
        .format(
            {
                t["rank_col_moi"]: "{:.2f}",
                t["rank_col_sell"]: "{:.1%}",
                t["rank_col_score"]: "{:.1f}",
            },
            na_rep="N/A",
        )
        .apply(row_style, axis=1)
        .applymap(emphasize_score, subset=[score_col])
        .set_properties(**{
            "border-color": "#e5e7eb",
            "font-size": "0.92rem",
        })
    )
    return styler


# =========================================================
# Main
# =========================================================
def main() -> None:
    inject_css()

    lang = st.sidebar.radio("Language / 语言", options=["中文", "English"], index=0, horizontal=True)
    locale = "zh" if lang == "中文" else "en"
    t = I18N[locale]

    df = load_price_bands(PRICE_BAND_PATH)
    if df.empty:
        st.error(t["missing_file"])
        st.stop()

    required = {
        "report_month",
        "price_range",
        "range_min",
        "range_max",
        "range_rank",
        "listings",
        "sales_prev_12mo",
    }
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(f"{t['missing_cols']} {missing}")
        st.stop()

    months = sorted(df["report_month"].dropna().unique().tolist())
    if not months:
        st.warning(t["no_valid_month"])
        st.stop()

    st.sidebar.header(t["filters"])
    month = st.sidebar.selectbox(t["month"], months, index=len(months) - 1)
    budget_k = st.sidebar.slider(t["budget"], min_value=200, max_value=1500, value=550, step=10)
    budget_usd = float(budget_k) * 1000

    df_m = df[df["report_month"] == month].copy()
    if df_m.empty:
        st.warning(t["no_rows_for_month"])
        st.stop()

    df_m = add_professional_metrics(df_m)
    df_m = df_m.sort_values(["range_rank", "range_min"], na_position="last").reset_index(drop=True)

    render_hero(t)

    best_candidates = df_m.dropna(subset=["buyer_leverage_score"])
    best_row = best_candidates.sort_values("buyer_leverage_score", ascending=False).iloc[0] if not best_candidates.empty else df_m.iloc[0]
    budget_row = pick_budget_band(df_m, budget_usd)
    nearby_best_row = pick_nearby_best_band(df_m, budget_row)
    median_moi = df_m["months_inventory"].median()
    market_bias = market_bias_label(median_moi, t)
    best_score = best_candidates["buyer_leverage_score"].max() if not best_candidates.empty else np.nan
    top3_df = prepare_top3(df_m)

    market_state = "soft" if market_bias == t["buyer_leaning"] else ("balanced" if market_bias == t["balanced"] else "hot")
    _, market_label = get_signal_badge_meta(market_state, t)

    best_state = get_signal_state(
        float(best_row.get("months_inventory", np.nan)) if pd.notna(best_row.get("months_inventory", np.nan)) else np.nan,
        float(best_row.get("monthly_sell_through", np.nan)) if pd.notna(best_row.get("monthly_sell_through", np.nan)) else np.nan,
    )
    _, best_label = get_signal_badge_meta(best_state, t)

    s1, s2, s3, s4, s5, s6 = st.columns(6)
    with s1:
        render_summary_card(t["metric_band_count"], str(len(df_m)), month)
    with s2:
        render_summary_card(
            t["metric_best_band"],
            str(best_row["price_range"]),
            f'{t["opportunity_score"]}: {fmt_num(best_row.get("buyer_leverage_score", np.nan))}',
            state=best_state,
            badge_label=best_label,
        )
    with s3:
        render_summary_card(t["metric_best_score"], fmt_num(best_score), t["relative_score_note"])
    with s4:
        render_summary_card(
            t["metric_budget_match"],
            str(budget_row["price_range"]) if budget_row is not None else "N/A",
            fmt_money(budget_usd),
        )
    with s5:
        if nearby_best_row is not None:
            nearby_state = get_signal_state(
                float(nearby_best_row["months_inventory"]) if pd.notna(nearby_best_row["months_inventory"]) else np.nan,
                float(nearby_best_row["monthly_sell_through"]) if pd.notna(nearby_best_row["monthly_sell_through"]) else np.nan,
            )
            _, nearby_label = get_signal_badge_meta(nearby_state, t)
        else:
            nearby_state, nearby_label = None, None

        render_summary_card(
            t["metric_nearby_best"],
            str(nearby_best_row["price_range"]) if nearby_best_row is not None else "N/A",
            t["nearby_comparison_note"],
            state=nearby_state,
            badge_label=nearby_label,
        )
    with s6:
        render_summary_card(
            t["metric_market_bias"],
            market_bias,
            f'{t["median_moi_note"]}: {fmt_num(median_moi)}',
            state=market_state,
            badge_label=market_label,
        )

    with st.expander(t["methodology"], expanded=False):
        st.markdown(t["methodology_text"])
        st.caption(t["score_explain"])

    render_section_head(t["market_read_title"], t["market_read_sub"])

    if budget_row is not None:
        budget_position = interpret_band(
            float(budget_row["months_inventory"]) if pd.notna(budget_row["months_inventory"]) else np.nan,
            float(budget_row["monthly_sell_through"]) if pd.notna(budget_row["monthly_sell_through"]) else np.nan,
            float(budget_row["buyer_leverage_score"]) if pd.notna(budget_row["buyer_leverage_score"]) else np.nan,
            t,
        )
        budget_state = get_signal_state(
            float(budget_row["months_inventory"]) if pd.notna(budget_row["months_inventory"]) else np.nan,
            float(budget_row["monthly_sell_through"]) if pd.notna(budget_row["monthly_sell_through"]) else np.nan,
        )
        _, budget_position_label = get_signal_badge_meta(budget_state, t)
    else:
        budget_position = t["unknown"]
        budget_state = None
        budget_position_label = None

    e1, e2, e3 = st.columns(3)
    with e1:
        render_executive_card("01", t["regime_title"], market_bias, t["regime_sub"], market_state, market_label)
    with e2:
        render_executive_card("02", t["position_title"], budget_position, t["position_sub"], budget_state, budget_position_label)
    with e3:
        if nearby_best_row is not None:
            nearby_state_exec = get_signal_state(
                float(nearby_best_row["months_inventory"]) if pd.notna(nearby_best_row["months_inventory"]) else np.nan,
                float(nearby_best_row["monthly_sell_through"]) if pd.notna(nearby_best_row["monthly_sell_through"]) else np.nan,
            )
            _, nearby_label_exec = get_signal_badge_meta(nearby_state_exec, t)
        else:
            nearby_state_exec, nearby_label_exec = None, None

        render_executive_card(
            "03",
            t["best_title"],
            str(nearby_best_row["price_range"]) if nearby_best_row is not None else "N/A",
            t["best_sub"],
            nearby_state_exec,
            nearby_label_exec,
        )

    render_section_head(t["section_market_map"], t["section_market_map_sub"])

    c1, c2 = st.columns(2, gap="large")
    with c1:
        render_html(f'<div class="chart-title">{escape(sanitize_text(t["chart1_title"]))}</div>')
        render_html(f'<div class="chart-caption">{escape(sanitize_text(t["chart1_caption"]))}</div>')
        if df_m.dropna(subset=["price_range", "months_inventory"]).empty:
            st.info(t["chart_empty"])
        else:
            st.altair_chart(build_moi_chart(df_m, t), use_container_width=True)

    with c2:
        render_html(f'<div class="chart-title">{escape(sanitize_text(t["chart2_title"]))}</div>')
        render_html(f'<div class="chart-caption">{escape(sanitize_text(t["chart2_caption"]))}</div>')
        if df_m.dropna(subset=["price_range", "monthly_sell_through"]).empty:
            st.info(t["chart_empty"])
        else:
            st.altair_chart(build_sellthrough_chart(df_m, t), use_container_width=True)

    m1, m2 = st.columns([1.58, 0.82], gap="large")
    with m1:
        render_html(f'<div class="chart-title">{escape(sanitize_text(t["chart3_title"]))}</div>')
        render_html(f'<div class="chart-caption">{escape(sanitize_text(t["chart3_caption"]))}</div>')
        if df_m.dropna(subset=["price_range", "months_inventory", "monthly_sell_through", "buyer_leverage_score"]).empty:
            st.info(t["chart_empty"])
        else:
            st.altair_chart(build_matrix_chart(df_m, top3_df, t), use_container_width=True)

        render_html(
            f'<div class="matrix-legend-note">• {escape(sanitize_text(t["matrix_note1"]))}<br>• {escape(sanitize_text(t["matrix_note2"]))}</div>'
        )

    with m2:
        render_matrix_spotlight(top3_df, t)

    render_section_head(t["section_ranking"], t["section_ranking_sub"])
    render_html(f'<div class="chart-title">{escape(sanitize_text(t["chart4_title"]))}</div>')
    render_html(f'<div class="chart-caption">{escape(sanitize_text(t["chart4_caption"]))}</div>')

    if df_m.dropna(subset=["price_range", "buyer_leverage_score"]).empty:
        st.info(t["chart_empty"])
    else:
        st.altair_chart(build_score_chart(df_m, t), use_container_width=True)

    rank_df = df_m.copy()
    rank_df["signal_read_internal"] = rank_df.apply(
        lambda r: interpret_band(
            float(r["months_inventory"]) if pd.notna(r["months_inventory"]) else np.nan,
            float(r["monthly_sell_through"]) if pd.notna(r["monthly_sell_through"]) else np.nan,
            float(r["buyer_leverage_score"]) if pd.notna(r["buyer_leverage_score"]) else np.nan,
            t,
        ),
        axis=1,
    )

    if locale == "zh":
        signal_map = {
            t["buyer_friendly"]: "🟢 买方空间较大",
            t["balanced_market"]: "🟡 相对平衡",
            t["hot"]: "🔴 竞争偏强",
            t["unknown"]: "🟡 未知",
        }
    else:
        signal_map = {
            t["buyer_friendly"]: "🟢 More Buyer Room",
            t["balanced_market"]: "🟡 Relatively Balanced",
            t["hot"]: "🔴 More Competitive",
            t["unknown"]: "🟡 Unknown",
        }

    rank_df[t["rank_col_signal"]] = rank_df["signal_read_internal"].map(signal_map).fillna(rank_df["signal_read_internal"])

    rank_df = (
        rank_df[["price_range", "months_inventory", "monthly_sell_through", "buyer_leverage_score", t["rank_col_signal"]]]
        .sort_values("buyer_leverage_score", ascending=False, na_position="last")
        .rename(
            columns={
                "price_range": t["rank_col_band"],
                "months_inventory": t["rank_col_moi"],
                "monthly_sell_through": t["rank_col_sell"],
                "buyer_leverage_score": t["rank_col_score"],
            }
        )
        .reset_index(drop=True)
    )
    rank_df.index = rank_df.index + 1

    st.dataframe(
        style_ranking(rank_df, t),
        use_container_width=True,
        height=335,
    )

    st.markdown(f"## {escape(sanitize_text(t['top3']))}")
    top3_cols = st.columns(3)
    top3_list = (
        df_m.dropna(subset=["buyer_leverage_score"])
        .sort_values("buyer_leverage_score", ascending=False, na_position="last")
        .head(3)
        .reset_index(drop=True)
    )

    for i in range(3):
        with top3_cols[i]:
            if i < len(top3_list):
                row = top3_list.iloc[i]
                render_top_op_card(
                    i + 1,
                    str(row["price_range"]),
                    float(row["months_inventory"]) if pd.notna(row["months_inventory"]) else np.nan,
                    float(row["buyer_leverage_score"]) if pd.notna(row["buyer_leverage_score"]) else np.nan,
                    float(row["monthly_sell_through"]) if pd.notna(row["monthly_sell_through"]) else np.nan,
                    t,
                )
            else:
                st.empty()

    render_section_head(t["section_budget"], t["section_budget_sub"])

    if budget_row is None:
        st.warning("Could not map budget to a price band.")
        st.stop()

    inv = float(budget_row["months_inventory"]) if pd.notna(budget_row["months_inventory"]) else np.nan
    sell_through = float(budget_row["monthly_sell_through"]) if pd.notna(budget_row["monthly_sell_through"]) else np.nan
    score = float(budget_row["buyer_leverage_score"]) if pd.notna(budget_row["buyer_leverage_score"]) else np.nan

    comp = competition_label(inv, t)
    lev = leverage_label(inv, sell_through, t)
    temp = temperature_label(inv, t)
    tips = build_tactics(inv, sell_through, t)
    posture = offer_posture(inv, sell_through, t)
    band_summary = signal_summary(inv, sell_through, t)
    signal_text = get_signal_text(inv, sell_through, t)

    budget_state = get_signal_state(inv, sell_through)
    _, budget_chip_label = get_signal_badge_meta(budget_state, t)
    budget_badge = signal_chip_html(budget_state, budget_chip_label)

    statement_html = "".join(
        [
            '<div class="statement-card">',
            f'<div class="statement-kicker">{escape(sanitize_text(t["advisory_conclusion"]))}</div>',
            f'<div class="statement-main">{escape(sanitize_text(signal_text))}</div>',
            budget_badge,
            f'<div class="statement-sub">{escape(sanitize_text(band_summary))}</div>',
            "</div>",
        ]
    )
    render_html(statement_html)

    render_html(
        "".join(
            [
                '<div class="metric-strip">',
                f'<div class="metric-box"><div class="metric-box-label">{escape(sanitize_text(t["budget_label"]))}</div><div class="metric-box-value">{fmt_money(budget_usd)}</div></div>',
                f'<div class="metric-box"><div class="metric-box-label">{escape(sanitize_text(t["matched_band"]))}</div><div class="metric-box-value">{escape(sanitize_text(budget_row["price_range"]))}</div></div>',
                f'<div class="metric-box"><div class="metric-box-label">{escape(sanitize_text(t["opportunity_score"]))}</div><div class="metric-box-value">{fmt_num(score)}</div></div>',
                f'<div class="metric-box"><div class="metric-box-label">{escape(sanitize_text(t["inv_level"]))}</div><div class="metric-box-value">{fmt_num(inv, 2)}</div></div>',
                f'<div class="metric-box"><div class="metric-box-label">{escape(sanitize_text(t["sell_through"]))}</div><div class="metric-box-value">{fmt_pct(sell_through)}</div></div>',
                f'<div class="metric-box"><div class="metric-box-label">{escape(sanitize_text(t["leverage"]))}</div><div class="metric-box-value">{escape(sanitize_text(lev))}</div></div>',
                "</div>",
            ]
        )
    )

    b1, b2 = st.columns([1.05, 1.25], gap="large")

    with b1:
        evidence_html = "".join(
            [
                '<div class="evidence-card">',
                f'<div class="card-kicker">{escape(sanitize_text(t["evidence_title"]))}</div>',
                f'<div class="card-main">{escape(sanitize_text(budget_row["price_range"]))}</div>',
                budget_badge,
                '<div class="card-body">',
                f'<strong>{escape(sanitize_text(t["competition"]))}:</strong> {escape(sanitize_text(comp))}<br><br>',
                f'<strong>{escape(sanitize_text(t["temperature"]))}:</strong> {escape(sanitize_text(temp))}<br><br>',
                f'<strong>{escape(sanitize_text(t["offer_posture"]))}:</strong> {escape(sanitize_text(posture))}<br><br>',
                f'<strong>{escape(sanitize_text(t["why_this_band"]))}:</strong><br>',
                f'• {escape(sanitize_text(t["why_line1"]))}<br>',
                f'• {escape(sanitize_text(t["why_line2"]))}<br>',
                f'• {escape(sanitize_text(t["why_line3"]))}',
                "</div>",
                "</div>",
            ]
        )
        render_html(evidence_html)

    with b2:
        action_items = "".join([f"<li>{escape(sanitize_text(tip))}</li>" for tip in tips])

        action_html = "".join(
            [
                '<div class="action-card">',
                f'<div class="card-kicker">{escape(sanitize_text(t["action_title"]))}</div>',
                f'<div class="card-main">{escape(sanitize_text(t["offer_posture"]))}: {escape(sanitize_text(posture))}</div>',
                '<div class="card-body">',
                f'<ul class="action-list">{action_items}</ul>',
                "</div>",
                "</div>",
            ]
        )
        render_html(action_html)

        limit_body = "<br>".join([escape(sanitize_text(line)) for line in str(t["limitations_body"]).splitlines()])

        limit_html = "".join(
            [
                '<div class="limit-card" style="margin-top:12px;">',
                f'<div class="card-kicker">{escape(sanitize_text(t["limitations_title"]))}</div>',
                f'<div class="card-body">{limit_body}</div>',
                "</div>",
            ]
        )
        render_html(limit_html)

    with st.expander(t["details"]):
        detail_zone = budget_row.get("market_zone_en")
        if isinstance(detail_zone, str):
            detail_zone = localize_market_zone(detail_zone, t)

        details = {
            "report_month": budget_row.get("report_month"),
            "price_range": budget_row.get("price_range"),
            "range_min": budget_row.get("range_min"),
            "range_max": budget_row.get("range_max"),
            "listings": budget_row.get("listings"),
            "sales_prev_12mo": budget_row.get("sales_prev_12mo"),
            "avg_monthly_sales": budget_row.get("avg_monthly_sales"),
            "months_inventory": budget_row.get("months_inventory"),
            "monthly_sell_through": budget_row.get("monthly_sell_through"),
            "buyer_leverage_score": budget_row.get("buyer_leverage_score"),
            "market_zone": detail_zone,
        }
        st.json(details)


if __name__ == "__main__":
    main()