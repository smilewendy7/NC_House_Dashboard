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

# Allow richer Altair charts
alt.data_transformers.disable_max_rows()


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

        "insight_title": "Auto Insight",
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
        "latest_value_label": "Latest Value",
        "source_note": "Source note",
        "source_note_text": "MOI is an industry-standard measure. In many MLS and REALTOR reports, it is sourced directly from the market report or derived from listing and sales fields.",
        "value": "Value",
        "series": "Series",
        "selected_data_points": "Selected data points",

        "as_of": "As of",
        "sales_yoy": "Sales YoY",
        "price_yoy": "Price YoY",
        "listings_yoy": "Listings YoY",
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

        "insight_title": "自动解读",
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
        "latest_value_label": "最新值",
        "source_note": "来源说明",
        "source_note_text": "MOI 是房地产行业常用指标。在很多 MLS / REALTOR 市场报告中，它要么直接由报告给出，要么基于挂牌与成交字段计算得到。",
        "value": "数值",
        "series": "系列",
        "selected_data_points": "当前数据点数",

        "as_of": "截至",
        "sales_yoy": "成交同比",
        "price_yoy": "价格同比",
        "listings_yoy": "挂牌同比",
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
# formatting helpers
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
    """
    Current market position based on latest MOI:
    - < 5 => Seller-Leaning
    - 5 to 6 => Balanced
    - > 6 => Buyer-Leaning
    """
    if moi is None or pd.isna(moi):
        return "Balanced"
    if moi < 5:
        return "Seller-Leaning"
    if moi <= 6:
        return "Balanced"
    return "Buyer-Leaning"


def demand_signal(yoy_sales: float | None) -> str:
    """
    Sales YoY:
    > +5  => Improving
    [-5, +5] => Stable
    < -5 => Weakening
    """
    if yoy_sales is None or pd.isna(yoy_sales):
        return "Stable"
    if yoy_sales > 5:
        return "Improving"
    if yoy_sales < -5:
        return "Weakening"
    return "Stable"


def price_signal(yoy_price: float | None) -> str:
    """
    Price YoY:
    > +3 => Rising
    [-3, +3] => Stable
    < -3 => Softening
    """
    if yoy_price is None or pd.isna(yoy_price):
        return "Stable"
    if yoy_price > 3:
        return "Rising"
    if yoy_price < -3:
        return "Softening"
    return "Stable"


def supply_signal(yoy_listings: float | None) -> str:
    """
    Listings YoY:
    > +5 => Expanding
    [-5, +5] => Stable
    < -5 => Tightening
    """
    if yoy_listings is None or pd.isna(yoy_listings):
        return "Stable"
    if yoy_listings > 5:
        return "Expanding"
    if yoy_listings < -5:
        return "Tightening"
    return "Stable"


def moi_trend_3m(view: pd.DataFrame) -> str:
    """
    Compare latest 3M rolling mean vs previous 3M rolling mean for MOI.
    """
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

    # small tolerance to avoid classifying tiny noise as trend
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
    """
    Overall logic:
    1. Start from current MOI zone.
    2. Use Demand / Price / Supply to nudge the result.
    3. Use MOI Trend (3M) as confirmation.

    Score map:
    Seller-Leaning = -1
    Balanced = 0
    Buyer-Leaning = +1
    """
    zone_score = {
        "Seller-Leaning": -1,
        "Balanced": 0,
        "Buyer-Leaning": 1,
    }

    score = zone_score.get(current_zone, 0)

    # Demand: strong demand pushes seller side, weak demand pushes buyer side
    if demand == "Improving":
        score -= 1
    elif demand == "Weakening":
        score += 1

    # Price: rising prices push seller side, softening prices push buyer side
    if price == "Rising":
        score -= 1
    elif price == "Softening":
        score += 1

    # Supply: expanding supply pushes buyer side, tightening pushes seller side
    if supply == "Expanding":
        score += 1
    elif supply == "Tightening":
        score -= 1

    # MOI rolling trend confirms short-term direction
    if moi_trend == "Rising":
        score += 1
    elif moi_trend == "Falling":
        score -= 1

    if score <= -2:
        return "Seller-Leaning"
    if score >= 2:
        return "Buyer-Leaning"
    return "Balanced"


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
            f"截至 {latest_month}，北卡房地产市场当前 MOI 为 {moi_text}，"
            f"属于“{localized_label(current_zone, lang)}”。"
            f"从同比信号看，成交同比为 {sales_yoy_text}，需求表现为“{localized_label(demand, lang)}”；"
            f"价格同比为 {price_yoy_text}，价格表现为“{localized_label(price, lang)}”；"
            f"挂牌同比为 {listings_yoy_text}，供给表现为“{localized_label(supply, lang)}”。"
            f"短期库存趋势（3个月滚动）为“{localized_label(moi_trend, lang)}”。"
            f"综合判断，目前市场整体为“{localized_label(overall, lang)}”。"
        )

    return (
        f"As of {latest_month}, North Carolina's MOI is {moi_text}, placing the market in a "
        f"“{localized_label(current_zone, lang)}” zone. "
        f"Sales YoY is {sales_yoy_text}, so demand is “{localized_label(demand, lang)}”. "
        f"Price YoY is {price_yoy_text}, so pricing is “{localized_label(price, lang)}”. "
        f"Listings YoY is {listings_yoy_text}, so supply is “{localized_label(supply, lang)}”. "
        f"The short-term inventory trend based on the 3-month rolling MOI is “{localized_label(moi_trend, lang)}”. "
        f"Overall, the market is best described as “{localized_label(overall, lang)}”."
    )


# -----------------------------
# filtering helpers
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


# -----------------------------
# chart helpers
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
    )

    x_encoding = alt.X(
        f"{x_col}:T",
        axis=axis_config_for_span(num_points, lang),
    )

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

    selectors = base.mark_point(opacity=0).encode(
        x=x_encoding
    ).add_params(nearest)

    rule = base.mark_rule(color="#9CA3AF").encode(
        x=x_encoding
    ).transform_filter(nearest)

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

    chart = alt.layer(
        line,
        points,
        selectors,
        rule,
        hover_points,
    ).properties(height=height)

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

    nearest = alt.selection_point(
        nearest=True,
        on="mouseover",
        fields=[x_col],
        empty="none",
    )

    x_encoding = alt.X(
        f"{x_col}:T",
        axis=axis_config_for_span(num_points, lang),
    )

    y_encoding = alt.Y(
        f"{y_col}:Q",
        title=y_title,
    )

    color_encoding = alt.Color(
        f"{series_col}:N",
        title="",
        legend=alt.Legend(orient="right"),
    )

    point_size = 28 if num_points > 36 else 38 if num_points > 24 else 45

    line = base.mark_line(strokeWidth=2.8).encode(
        x=x_encoding,
        y=y_encoding,
        color=color_encoding,
    )

    points = base.mark_point(filled=True, size=point_size).encode(
        x=x_encoding,
        y=y_encoding,
        color=color_encoding,
    )

    selectors = alt.Chart(chart_df[[x_col]].drop_duplicates()).mark_point(opacity=0).encode(
        x=x_encoding
    ).add_params(nearest)

    rule = alt.Chart(chart_df[[x_col]].drop_duplicates()).mark_rule(color="#9CA3AF").encode(
        x=x_encoding
    ).transform_filter(nearest)

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

    chart = alt.layer(
        line,
        points,
        selectors,
        rule,
        hover_points,
    ).properties(height=height)

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


# -----------------------------
# render chart sections
# -----------------------------
def render_inventory_chart(view: pd.DataFrame, lang: str) -> None:
    st.subheader(tr("inventory_chart_title", lang))
    st.caption(tr("inventory_chart_caption", lang))

    inv_chart_df = view[["report_month_dt", "report_month", "months_inventory"]].dropna().copy()
    if inv_chart_df.empty:
        return

    inv_chart_df["market_zone"] = inv_chart_df["months_inventory"].apply(moi_zone)
    inv_chart_df["market_zone_display"] = inv_chart_df["market_zone"].map(lambda x: localized_label(x, lang))

    y_max = max(7.0, float(inv_chart_df["months_inventory"].max()) + 0.6)

    balanced_band = alt.Chart(
        pd.DataFrame({"ymin": [5.0], "ymax": [6.0]})
    ).mark_rect(opacity=0.12).encode(
        y=alt.Y(
            "ymin:Q",
            scale=alt.Scale(domain=[0, y_max]),
            title="MOI (Months of Inventory)" if lang == "en" else "MOI（库存月数）",
        ),
        y2="ymax:Q",
    )

    line_5 = alt.Chart(pd.DataFrame({"y": [5.0]})).mark_rule(
        strokeDash=[6, 4],
        size=1.5,
        color="#111827",
    ).encode(
        y=alt.Y("y:Q", scale=alt.Scale(domain=[0, y_max]))
    )

    line_6 = alt.Chart(pd.DataFrame({"y": [6.0]})).mark_rule(
        strokeDash=[6, 4],
        size=1.5,
        color="#111827",
    ).encode(
        y=alt.Y("y:Q", scale=alt.Scale(domain=[0, y_max]))
    )

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

    inventory_chart = alt.layer(
        balanced_band,
        line_5,
        line_6,
        main_chart,
    ).resolve_scale(y="shared").properties(height=390)

    st.altair_chart(inventory_chart, width="stretch")

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
    st.dataframe(zone_df, width="content", hide_index=True)


def render_listings_sales_chart(view: pd.DataFrame, lang: str) -> None:
    st.subheader(tr("ls_title", lang))
    st.caption(tr("ls_caption", lang))

    chart_df = view[["report_month_dt", "report_month", "listings", "sales"]].dropna(subset=["report_month_dt"]).copy()
    if chart_df.empty:
        return

    chart_df = chart_df.melt(
        id_vars=["report_month_dt", "report_month"],
        value_vars=["listings", "sales"],
        var_name="series_raw",
        value_name="value",
    )

    series_map = {
        "listings": tr("listings", lang),
        "sales": tr("sales", lang),
    }
    chart_df["series_display"] = chart_df["series_raw"].map(series_map)

    chart = build_interactive_multi_line_chart(
        chart_df=chart_df,
        x_col="report_month_dt",
        y_col="value",
        series_col="series_display",
        lang=lang,
        y_title=tr("value", lang),
        height=360,
    )

    st.altair_chart(chart, width="stretch")


def render_price_chart(view: pd.DataFrame, lang: str) -> None:
    st.subheader(tr("price_title", lang))
    st.caption(tr("price_caption", lang))

    price_df = view[["report_month_dt", "report_month", "median_price"]].dropna().copy()
    if price_df.empty:
        return

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

    st.altair_chart(chart, width="stretch")


# -----------------------------
# language switch
# -----------------------------
if "lang" not in st.session_state:
    st.session_state.lang = "en"

lang_col1, lang_col2, _ = st.columns([1, 1, 8])

with lang_col1:
    if st.button("English", width="stretch"):
        st.session_state.lang = "en"

with lang_col2:
    if st.button("中文", width="stretch"):
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
# page header
# -----------------------------
st.title(tr("page_title", lang))
st.caption(tr("page_caption", lang))


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
    index=1 if tr("last_24m", lang) in time_range_map else 0,
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
view = filtered.loc[mask].copy()

if view.empty:
    st.warning(tr("no_data_range", lang))
    st.stop()

view = view.sort_values("report_month_dt").copy()


# -----------------------------
# headline / KPI section
# -----------------------------
st.markdown(f"## {tr('headline_title', lang)}")
st.caption(tr("headline_caption", lang))

meta_col1, meta_col2 = st.columns([4, 1])
with meta_col2:
    st.metric(tr("selected_data_points", lang), len(view))

k1, k2, k3, k4 = st.columns(4)

latest_month = str(view["report_month"].iloc[-1])
inventory_val = latest_value(view, "months_inventory")
listings_val = latest_value(view, "listings")
sales_val = latest_value(view, "sales")

k1.metric(tr("latest_month", lang), value=latest_month)
k2.metric(tr("inventory_months", lang), value=fmt_float(inventory_val, 2))
k3.metric(tr("listings", lang), value=fmt_int(listings_val))
k4.metric(tr("sales", lang), value=fmt_int(sales_val))

st.divider()


# -----------------------------
# charts
# -----------------------------
render_inventory_chart(view, lang)

st.divider()

render_listings_sales_chart(view, lang)

st.divider()

render_price_chart(view, lang)

st.divider()


# -----------------------------
# new NC Market Signal framework
# -----------------------------
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

current_moi_zone_display = localized_label(current_moi_zone_raw, lang)
demand_signal_display = localized_label(demand_signal_raw, lang)
price_signal_display = localized_label(price_signal_raw, lang)
supply_signal_display = localized_label(supply_signal_raw, lang)
moi_trend_display = localized_label(moi_trend_raw, lang)
overall_display = localized_label(overall_raw, lang)


# -----------------------------
# signal layout
# -----------------------------
st.markdown(f"## {tr('market_signal', lang)}")

card1, card2, card3, card4, card5 = st.columns(5)

with card1:
    st.metric(
        tr("current_moi_zone", lang),
        current_moi_zone_display,
        delta=f"MOI {fmt_float(inventory_val, 2)}",
    )

with card2:
    st.metric(
        tr("demand_signal", lang),
        demand_signal_display,
        delta=f"{tr('sales_yoy', lang)} {fmt_pct(latest_yoy_sales, 1)}",
    )

with card3:
    st.metric(
        tr("price_signal", lang),
        price_signal_display,
        delta=f"{tr('price_yoy', lang)} {fmt_pct(latest_yoy_price, 1)}",
    )

with card4:
    st.metric(
        tr("supply_signal", lang),
        supply_signal_display,
        delta=f"{tr('listings_yoy', lang)} {fmt_pct(latest_yoy_listings, 1)}",
    )

with card5:
    st.metric(
        tr("moi_trend_3m", lang),
        moi_trend_display,
        delta=f"MOI {fmt_float(inventory_val, 2)}",
    )

st.markdown("")

left_col, right_col = st.columns([2, 3])

with left_col:
    st.markdown(f"### {tr('overall_market', lang)}")
    st.success(f"**{overall_display}**")

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
                current_moi_zone_display,
                f"{demand_signal_display} ({fmt_pct(latest_yoy_sales, 1)})",
                f"{price_signal_display} ({fmt_pct(latest_yoy_price, 1)})",
                f"{supply_signal_display} ({fmt_pct(latest_yoy_listings, 1)})",
                moi_trend_display,
            ],
        }
    )
    st.dataframe(detail_df, width="stretch", hide_index=True)

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

st.divider()


# -----------------------------
# explainers
# -----------------------------
with st.expander(tr("how_to_read", lang)):
    st.write(tr("how_to_read_text", lang))

with st.expander(tr("source_note", lang)):
    st.write(tr("source_note_text", lang))

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

    st.dataframe(latest_rows, width="stretch", hide_index=True)