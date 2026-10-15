import sqlite3
from pathlib import Path

from csv_upload import render_csv_upload, render_data_preview
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from sql_utils import (
    get_sql_summary,
    get_country_summary,
    run_custom_query,
)
from advanced_sql_page import render_advanced_sql_page
from business_insights_page import render_business_insights_page


# ============================================================
# FINSIGHT | PREMIUM FINANCIAL PERFORMANCE ANALYTICS
# ============================================================

st.set_page_config(
    page_title="FinSight | Financial Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "processed" / "cleaned_financial_data.csv"


# ============================================================
# PREMIUM DARK UI
# ============================================================

st.markdown(
    """
    <style>
    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
    );

    :root {
        --bg: #080d1b;
        --panel: #111a2d;
        --panel-light: #17223a;
        --border: rgba(148, 163, 184, 0.17);
        --text: #edf2ff;
        --muted: #98a8c5;
        --purple: #8b7cff;
        --cyan: #2dd4bf;
        --blue: #60a5fa;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 0% 0%,
                rgba(93, 80, 210, 0.16),
                transparent 29%
            ),
            radial-gradient(
                circle at 100% 10%,
                rgba(45, 212, 191, 0.08),
                transparent 25%
            ),
            var(--bg);
        color: var(--text);
    }

    [data-testid="stHeader"] {
        background: rgba(8, 13, 27, 0.96);
    }

    [data-testid="stToolbar"],
    [data-testid="stDecoration"] {
        background: transparent;
    }

    .block-container {
        max-width: 1550px;
        padding-top: 1.8rem;
        padding-bottom: 2.8rem;
    }

    /* Sidebar */

    section[data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #10182b 0%,
            #0a1020 100%
        );
        border-right: 1px solid var(--border);
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1.4rem;
    }

    section[data-testid="stSidebar"] * {
        color: #e4ebfa;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2 {
        letter-spacing: -0.7px;
        font-weight: 800;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] label {
        border-radius: 9px;
        padding: 5px 8px;
    }

    /* Typography */

    h1, h2, h3 {
        color: #f5f7ff !important;
        letter-spacing: -0.6px;
        font-weight: 750 !important;
    }

    h2 {
        margin-top: 0.6rem;
    }

    p, li, label {
        color: #dbe4f5;
    }

    [data-testid="stCaptionContainer"] {
        color: var(--muted);
    }

    /* Hero banner */

    .hero {
        position: relative;
        overflow: hidden;
        background:
            radial-gradient(
                circle at 95% 5%,
                rgba(139, 124, 255, 0.20),
                transparent 35%
            ),
            linear-gradient(115deg, #141d35, #1c1a3b);
        border: 1px solid rgba(139, 124, 255, 0.26);
        border-radius: 22px;
        padding: 30px 32px;
        margin-bottom: 24px;
        box-shadow: 0 14px 40px rgba(0, 0, 0, 0.15);
    }

    .hero-tag {
        display: inline-block;
        color: #c5bcff;
        background: rgba(139, 124, 255, 0.12);
        border: 1px solid rgba(139, 124, 255, 0.25);
        border-radius: 30px;
        padding: 5px 11px;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1.4px;
        margin-bottom: 13px;
    }

    .hero h1 {
        color: #ffffff !important;
        font-size: clamp(25px, 3vw, 36px);
        line-height: 1.2;
        font-weight: 800 !important;
        margin: 0;
    }

    .hero p {
        color: #b3c0dc;
        font-size: 12px;
        line-height: 1.8;
        margin: 12px 0 0;
        letter-spacing: 0.6px;
    }

    /* Custom KPI cards */

    .metric-card {
        height: 100%;
        min-height: 128px;
        background: linear-gradient(
            145deg,
            rgba(24, 36, 61, 0.98),
            rgba(15, 23, 41, 0.98)
        );
        border: 1px solid rgba(129, 155, 205, 0.21);
        border-radius: 17px;
        padding: 20px;
        box-shadow: 0 8px 28px rgba(0, 0, 0, 0.13);
        transition: transform 0.2s ease,
                    border-color 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-3px);
        border-color: rgba(139, 124, 255, 0.65);
    }

    .metric-label {
        color: #a9b8d4;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1px;
        margin-bottom: 13px;
    }

    .metric-value {
        color: #ffffff;
        font-size: clamp(23px, 2vw, 31px);
        font-weight: 800;
        line-height: 1.25;
        overflow-wrap: anywhere;
    }

    .metric-note {
        color: #93a2c0;
        font-size: 11px;
        margin-top: 10px;
        line-height: 1.5;
    }

    /* Native Streamlit metrics */

    div[data-testid="stMetric"] {
        background: linear-gradient(
            145deg,
            #17233b,
            #111a2d
        );
        border: 1px solid var(--border);
        border-radius: 15px;
        padding: 16px 18px;
    }

    div[data-testid="stMetricLabel"] {
        color: #a9b8d4 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 800;
    }

    /* Charts */

    div[data-testid="stPlotlyChart"] {
        background: rgba(17, 26, 45, 0.78);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 7px;
        box-shadow: 0 7px 22px rgba(0, 0, 0, 0.10);
    }

    /* Tables */

    div[data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 13px;
        overflow: hidden;
    }

    /* Buttons */

    .stButton > button,
    .stDownloadButton > button {
        background: linear-gradient(
            110deg,
            #5969ec,
            #825ce5
        );
        color: #ffffff !important;
        border: 0;
        border-radius: 10px;
        padding: 0.55rem 1rem;
        font-weight: 700;
        transition: filter 0.2s ease,
                    transform 0.2s ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        filter: brightness(1.12);
        transform: translateY(-1px);
    }

    /* Inputs */

    div[data-baseweb="select"] > div {
        background: #111b2d;
        border-color: #34435e;
        border-radius: 9px;
    }

    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input {
        background: #111b2d;
        color: #f1f5f9;
        border-radius: 9px;
    }

    /* Expanders and containers */

    div[data-testid="stExpander"] {
        background: rgba(17, 26, 45, 0.68);
        border: 1px solid var(--border);
        border-radius: 13px;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: var(--border);
        border-radius: 15px;
    }

    hr {
        border-color: var(--border);
    }

    div[data-testid="stAlert"] {
        border-radius: 12px;
    }

    /* Footer */

    .footer {
        color: #7f90b1;
        text-align: center;
        font-size: 11px;
        letter-spacing: 0.4px;
        padding: 8px 0 2px;
    }

    @media (max-width: 768px) {
        .block-container {
            padding: 1rem 0.8rem 2rem;
        }

        .hero {
            padding: 22px 19px;
        }

        .metric-card {
            padding: 15px;
            min-height: 110px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_data(path, modified_time):
    data = pd.read_csv(path)

    data.columns = (
        data.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )

    if "date" in data.columns:
        data["date"] = pd.to_datetime(
            data["date"], errors="coerce"
        )

    numeric_columns = [
        "sales",
        "profit",
        "cogs",
        "gross_sales",
        "discounts",
        "units_sold",
        "year",
        "month_number",
        "sale_price",
        "manufacturing_price",
    ]

    for col in numeric_columns:
        if col in data.columns:
            data[col] = pd.to_numeric(
                data[col], errors="coerce"
            )

    for col in [
        "country",
        "product",
        "segment",
        "discount_band",
    ]:
        if col in data.columns:
            data[col] = (
                data[col].fillna("Unknown").astype(str)
            )

    return data


if not DATA_FILE.exists():
    st.error(f"Cleaned dataset not found: {DATA_FILE}")
    st.info(
        "Run `python clean_data.py` from your FinSight project folder."
    )
    st.stop()

try:
    df = load_data(
        str(DATA_FILE),
        DATA_FILE.stat().st_mtime,
    )
    df = render_csv_upload(df)
except Exception as error:
    st.error(f"Could not load the cleaned dataset: {error}")
    st.stop()

if not {"sales", "profit"}.issubset(df.columns):
    st.error("Dataset must contain sales and profit columns.")
    st.write("Available columns:", df.columns.tolist())
    st.stop()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def money(value):
    """Format financial numbers in a compact readable format."""

    if pd.isna(value):
        return "N/A"

    value = float(value)

    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:,.2f}M"

    if abs(value) >= 1_000:
        return f"${value / 1_000:,.1f}K"

    return f"${value:,.2f}"


def chart_layout(fig, height=370):
    """Apply consistent FinSight chart styling."""

    fig.update_layout(
        template="plotly_dark",
        height=height,
        margin=dict(l=20, r=20, t=55, b=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter, sans-serif",
            color="#dce5f5",
            size=12,
        ),
        title_font=dict(
            family="Inter, sans-serif",
            size=16,
            color="#f1f5ff",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        hoverlabel=dict(
            bgcolor="#17223a",
            font_color="#ffffff",
        ),
        coloraxis_colorbar=dict(
            outlinewidth=0,
            tickfont=dict(color="#cbd5e1"),
        ),
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor="rgba(148,163,184,0.18)",
        tickfont=dict(color="#b8c5dc"),
    )

    fig.update_yaxes(
        gridcolor="rgba(148,163,184,0.12)",
        zeroline=False,
        tickfont=dict(color="#b8c5dc"),
    )

    return fig


def show_chart(fig, height=370):
    """Display a consistently styled interactive Plotly chart."""

    st.plotly_chart(
        chart_layout(fig, height),
        use_container_width=True,
        config={
            "displaylogo": False,
            "responsive": True,
        },
    )


def metric_card(label, value, note):
    """Display a premium HTML KPI card."""

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_heading(title, description=None):
    st.markdown(f"### {title}")

    if description:
        st.caption(description)


def empty_chart_message(message):
    st.info(message)


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

with st.sidebar:
    st.markdown(
        """
        <div style="padding: 5px 0 8px;">
            <div style="
                font-size: 26px;
                font-weight: 800;
                letter-spacing: -1px;
                color: #ffffff;">
                ◈ FINSIGHT
            </div>
            <div style="
                color: #9babe0;
                font-size: 10px;
                letter-spacing: 2px;
                margin-top: 3px;">
                FINANCIAL INTELLIGENCE
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    page = st.radio(
        "WORKSPACE",
        [
            "Executive Overview",
            "Revenue & Profit",
            "Expense Analysis",
            "Product & Market",
            "SQL Analytics",
            "Advanced SQL Analytics",
            "Business Insights",
            "Data Explorer",
            render_data_preview(df)
        ],
        key="finsight_navigation",
    )

    st.divider()

    st.caption("DATASET OVERVIEW")
    st.write(f"**{len(df):,}** records")
    st.write(f"**{len(df.columns)}** columns")

    st.divider()

    st.caption("TECHNOLOGY STACK")
    st.markdown(
        """
        `Python` `Pandas`

        `Streamlit` `Plotly`

        `SQLite` `SQL`
        """
    )

    st.divider()
    st.caption("DATABASE CONNECTION")

    try:
        sql_summary = get_sql_summary()

        st.success("SQLite Connected")
        st.metric(
            "Database Records",
            f"{sql_summary['total_records']:,}",
        )
        st.metric(
            "Database Sales",
            money(sql_summary["total_sales"]),
        )
        st.metric(
            "Database Profit",
            money(sql_summary["total_profit"]),
        )

    except Exception as error:
        st.warning("SQLite connection unavailable")
        st.caption(str(error))


# ============================================================
# HERO BANNER
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-tag">
            FINANCIAL PERFORMANCE PLATFORM
        </div>
        <h1>FinSight Financial Analytics</h1>
        <p>
            TURN FINANCIAL DATA INTO BUSINESS DECISIONS
            <br>
            PERFORMANCE &nbsp; • &nbsp;
            PROFITABILITY &nbsp; • &nbsp;
            MARKET INTELLIGENCE
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# GLOBAL FILTERS
# ============================================================

filtered = df.copy()

with st.expander(
    "⚙️  GLOBAL FILTERS",
    expanded=True,
):
    filter_cols = st.columns(3)

    if "year" in filtered.columns:
        years = sorted(
            filtered["year"].dropna().unique().tolist()
        )

        selected_years = filter_cols[0].multiselect(
            "Financial Year",
            years,
            default=years,
            key="filter_year",
        )

        filtered = filtered[
            filtered["year"].isin(selected_years)
        ]

    if "country" in filtered.columns:
        countries = sorted(
            filtered["country"].dropna().unique().tolist()
        )

        selected_countries = filter_cols[1].multiselect(
            "Country",
            countries,
            default=countries,
            key="filter_country",
        )

        filtered = filtered[
            filtered["country"].isin(selected_countries)
        ]

    if "segment" in filtered.columns:
        segments = sorted(
            filtered["segment"].dropna().unique().tolist()
        )

        selected_segments = filter_cols[2].multiselect(
            "Customer Segment",
            segments,
            default=segments,
            key="filter_segment",
        )

        filtered = filtered[
            filtered["segment"].isin(selected_segments)
        ]

if filtered.empty:
    st.warning(
        "No records match your current filters. "
        "Select at least one value in each active filter."
    )
    st.stop()


# ============================================================
# FILTERED KPI CALCULATIONS
# ============================================================

total_sales = float(filtered["sales"].sum())
total_profit = float(filtered["profit"].sum())

margin = (
    total_profit / total_sales * 100
    if total_sales
    else 0.0
)

total_records = len(filtered)

st.caption(
    f"Showing {total_records:,} of {len(df):,} records "
    f"based on the selected filters."
)


# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================

if page == "Executive Overview":

    section_heading(
        "Executive Overview",
        "A high-level snapshot of financial performance and business health.",
    )

    st.markdown("#### Key Performance Indicators")

    c1, c2, c3, c4 = st.columns(4, gap="medium")

    with c1:
        metric_card(
            "TOTAL SALES",
            money(total_sales),
            "Revenue across selected records",
        )

    with c2:
        metric_card(
            "TOTAL PROFIT",
            money(total_profit),
            "Profit across selected records",
        )

    with c3:
        metric_card(
            "PROFIT MARGIN",
            f"{margin:.2f}%",
            "Profit divided by sales",
        )

    with c4:
        metric_card(
            "TOTAL RECORDS",
            f"{total_records:,}",
            "Records included in this view",
        )

    st.markdown("---")

    left, right = st.columns(2, gap="large")

    # Monthly trend
    with left:
        section_heading(
            "Sales & Profit Trend",
            "Monthly financial performance over time.",
        )

        if (
            "date" in filtered.columns
            and filtered["date"].notna().any()
        ):
            trend = (
                filtered.dropna(subset=["date"])
                .groupby(
                    pd.Grouper(key="date", freq="MS")
                )[["sales", "profit"]]
                .sum()
                .reset_index()
            )

            if not trend.empty:
                fig = go.Figure()

                fig.add_trace(
                    go.Scatter(
                        x=trend["date"],
                        y=trend["sales"],
                        name="Sales",
                        mode="lines+markers",
                        line=dict(
                            color="#8b7cff",
                            width=3,
                        ),
                        marker=dict(size=6),
                        fill="tozeroy",
                        fillcolor="rgba(139,124,255,0.08)",
                        hovertemplate=(
                            "%{x|%b %Y}<br>"
                            "Sales: $%{y:,.2f}"
                            "<extra></extra>"
                        ),
                    )
                )

                fig.add_trace(
                    go.Scatter(
                        x=trend["date"],
                        y=trend["profit"],
                        name="Profit",
                        mode="lines+markers",
                        line=dict(
                            color="#2dd4bf",
                            width=3,
                        ),
                        marker=dict(size=5),
                        hovertemplate=(
                            "%{x|%b %Y}<br>"
                            "Profit: $%{y:,.2f}"
                            "<extra></extra>"
                        ),
                    )
                )

                show_chart(fig)

            else:
                empty_chart_message(
                    "No monthly trend is available."
                )
        else:
            empty_chart_message(
                "Valid date data is unavailable."
            )

    # Profit by segment
    with right:
        section_heading(
            "Profit by Segment",
            "Compare profit contribution across customer segments.",
        )

        if "segment" in filtered.columns:
            segment_data = (
                filtered.groupby("segment")["profit"]
                .sum()
                .reset_index()
                .sort_values("profit", ascending=True)
            )

            fig = px.bar(
                segment_data,
                x="profit",
                y="segment",
                orientation="h",
                text_auto=".3s",
                color="profit",
                color_continuous_scale=[
                    "#4f46e5",
                    "#8b7cff",
                    "#2dd4bf",
                ],
            )

            fig.update_layout(
                coloraxis_showscale=False,
                xaxis_title="Profit",
                yaxis_title="",
            )

            show_chart(fig)

        else:
            empty_chart_message(
                "Segment information is unavailable."
            )

    left, right = st.columns(2, gap="large")

    # Sales by country
    with left:
        section_heading(
            "Revenue by Country",
            "Identify the strongest revenue-generating markets.",
        )

        if "country" in filtered.columns:
            country_data = (
                filtered.groupby("country")["sales"]
                .sum()
                .reset_index()
                .sort_values("sales", ascending=False)
            )

            fig = px.bar(
                country_data,
                x="country",
                y="sales",
                text_auto=".3s",
                color="sales",
                color_continuous_scale=[
                    "#4338ca",
                    "#818cf8",
                ],
            )

            fig.update_layout(
                coloraxis_showscale=False,
                xaxis_title="Country",
                yaxis_title="Sales",
            )

            show_chart(fig)

        else:
            empty_chart_message(
                "Country information is unavailable."
            )

    # Product performance
    with right:
        section_heading(
            "Product Performance",
            "Compare sales and profitability by product.",
        )

        if "product" in filtered.columns:
            product_data = (
                filtered.groupby("product")[["sales", "profit"]]
                .sum()
                .reset_index()
                .sort_values("sales", ascending=False)
            )

            fig = px.bar(
                product_data,
                x="product",
                y=["sales", "profit"],
                barmode="group",
                color_discrete_sequence=[
                    "#8b7cff",
                    "#2dd4bf",
                ],
                labels={
                    "value": "Amount",
                    "variable": "Metric",
                    "product": "Product",
                },
            )

            show_chart(fig)

        else:
            empty_chart_message(
                "Product information is unavailable."
            )

    st.markdown("---")
    section_heading("Business Performance Snapshot")

    snapshot = pd.DataFrame(
        {
            "Metric": [
                "Total Sales",
                "Total Profit",
                "Profit Margin",
                "Records Analyzed",
            ],
            "Value": [
                f"${total_sales:,.2f}",
                f"${total_profit:,.2f}",
                f"{margin:.2f}%",
                f"{total_records:,}",
            ],
        }
    )

    st.dataframe(
        snapshot,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# REVENUE & PROFIT
# ============================================================

elif page == "Revenue & Profit":

    section_heading(
        "Revenue & Profit Analysis",
        "Explore revenue trends, profit generation and segment contribution.",
    )

    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        metric_card(
            "TOTAL SALES",
            money(total_sales),
            "Sales after filters",
        )

    with c2:
        metric_card(
            "TOTAL PROFIT",
            money(total_profit),
            "Profit after filters",
        )

    with c3:
        metric_card(
            "PROFIT MARGIN",
            f"{margin:.2f}%",
            "Profit / Sales × 100",
        )

    st.markdown("---")

    if (
        "date" in filtered.columns
        and filtered["date"].notna().any()
    ):
        trend = (
            filtered.dropna(subset=["date"])
            .groupby(
                pd.Grouper(key="date", freq="MS")
            )[["sales", "profit"]]
            .sum()
            .reset_index()
        )

        if not trend.empty:
            section_heading(
                "Monthly Revenue & Profit",
                "Track the movement of financial performance over time.",
            )

            fig = px.line(
                trend,
                x="date",
                y=["sales", "profit"],
                markers=True,
                color_discrete_sequence=[
                    "#8b7cff",
                    "#2dd4bf",
                ],
                labels={
                    "date": "Month",
                    "value": "Amount",
                    "variable": "Metric",
                },
            )

            show_chart(fig, 430)

    if "segment" in filtered.columns:
        section_heading(
            "Segment Revenue vs Profit",
            "Compare sales and profit for each customer segment.",
        )

        segment_data = (
            filtered.groupby("segment")[["sales", "profit"]]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            segment_data,
            x="segment",
            y=["sales", "profit"],
            barmode="group",
            color_discrete_sequence=[
                "#8b7cff",
                "#2dd4bf",
            ],
        )

        show_chart(fig, 410)

    if "date" in filtered.columns:
        st.markdown("#### Monthly Financial Table")

        if filtered["date"].notna().any():
            monthly_table = (
                filtered.dropna(subset=["date"])
                .groupby(
                    pd.Grouper(key="date", freq="MS")
                )[["sales", "profit"]]
                .sum()
                .reset_index()
            )

            if not monthly_table.empty:
                monthly_table["profit_margin_pct"] = np.where(
                    monthly_table["sales"] != 0,
                    monthly_table["profit"]
                    / monthly_table["sales"] * 100,
                    np.nan,
                )

                monthly_table["date"] = (
                    monthly_table["date"].dt.strftime("%Y-%m")
                )

                monthly_table = monthly_table.rename(
                    columns={
                        "date": "Month",
                        "sales": "Sales",
                        "profit": "Profit",
                        "profit_margin_pct": "Profit Margin (%)",
                    }
                )

                st.dataframe(
                    monthly_table.sort_values(
                        "Month", ascending=False
                    ),
                    use_container_width=True,
                    hide_index=True,
                )


# ============================================================
# EXPENSE ANALYSIS
# ============================================================

elif page == "Expense Analysis":

    section_heading(
        "Expense & Cost Analysis",
        "Understand recorded product costs and cost distribution.",
    )

    if "cogs" in filtered.columns:

        total_cogs = float(filtered["cogs"].sum())

        cogs_pct = (
            total_cogs / total_sales * 100
            if total_sales
            else 0.0
        )

        remaining = max(total_sales - total_cogs, 0.0)

        c1, c2, c3 = st.columns(3, gap="medium")

        with c1:
            metric_card(
                "TOTAL COGS",
                money(total_cogs),
                "Recorded cost of goods sold",
            )

        with c2:
            metric_card(
                "COGS / SALES",
                f"{cogs_pct:.2f}%",
                "Cost relative to sales",
            )

        with c3:
            metric_card(
                "SALES LESS COGS",
                money(total_sales - total_cogs),
                "Sales minus recorded COGS",
            )

        st.markdown("---")

        left, right = st.columns(2, gap="large")

        with left:
            section_heading("COGS by Segment")

            if "segment" in filtered.columns:
                cost_data = (
                    filtered.groupby("segment")["cogs"]
                    .sum()
                    .reset_index()
                    .sort_values("cogs", ascending=False)
                )

                fig = px.bar(
                    cost_data,
                    x="segment",
                    y="cogs",
                    color_discrete_sequence=["#fb7185"],
                    labels={
                        "segment": "Segment",
                        "cogs": "COGS",
                    },
                )

                show_chart(fig)

            else:
                empty_chart_message(
                    "Segment information is unavailable."
                )

        with right:
            section_heading("Cost Distribution by Product")

            if "product" in filtered.columns:
                cost_product = (
                    filtered.groupby("product")["cogs"]
                    .sum()
                    .reset_index()
                    .sort_values("cogs", ascending=False)
                )

                fig = px.pie(
                    cost_product,
                    names="product",
                    values="cogs",
                    hole=0.60,
                    color_discrete_sequence=[
                        "#8b7cff",
                        "#2dd4bf",
                        "#60a5fa",
                        "#f59e0b",
                        "#fb7185",
                        "#a78bfa",
                    ],
                )

                fig.update_traces(
                    textposition="inside",
                    textinfo="percent+label",
                )

                show_chart(fig)

            else:
                empty_chart_message(
                    "Product information is unavailable."
                )

        st.caption(
            "COGS means recorded cost of goods sold. "
            "It may not include all operating expenses. "
            "Sales minus COGS is not necessarily net profit."
        )

    else:
        st.info(
            "COGS data is not available in the current dataset."
        )


# ============================================================
# PRODUCT & MARKET
# ============================================================

elif page == "Product & Market":

    section_heading(
        "Product & Market Intelligence",
        "Analyze product profitability and compare market performance.",
    )

    if "product" in filtered.columns:

        product_data = (
            filtered.groupby("product")[["sales", "profit"]]
            .sum()
            .reset_index()
        )

        product_data["profit_margin_pct"] = np.where(
            product_data["sales"] != 0,
            product_data["profit"]
            / product_data["sales"] * 100,
            np.nan,
        )

        top_product = product_data.sort_values(
            "sales", ascending=False
        ).iloc[0]

        profitable_product = product_data.sort_values(
            "profit", ascending=False
        ).iloc[0]

        c1, c2 = st.columns(2, gap="medium")

        with c1:
            metric_card(
                "TOP SALES PRODUCT",
                str(top_product["product"]),
                f"Sales: {money(top_product['sales'])}",
            )

        with c2:
            metric_card(
                "TOP PROFIT PRODUCT",
                str(profitable_product["product"]),
                f"Profit: {money(profitable_product['profit'])}",
            )

        st.markdown("---")

        section_heading(
            "Product Profitability",
            "Products ranked by total profit.",
        )

        fig = px.bar(
            product_data.sort_values(
                "profit", ascending=False
            ),
            x="product",
            y="profit",
            color="profit_margin_pct",
            text_auto=".3s",
            color_continuous_scale="Viridis",
            labels={
                "product": "Product",
                "profit": "Profit",
                "profit_margin_pct": "Margin (%)",
            },
        )

        show_chart(fig)

        st.markdown("#### Product Summary")

        product_display = product_data.sort_values(
            "profit", ascending=False
        ).rename(
            columns={
                "product": "Product",
                "sales": "Total Sales",
                "profit": "Total Profit",
                "profit_margin_pct": "Profit Margin (%)",
            }
        )

        st.dataframe(
            product_display,
            use_container_width=True,
            hide_index=True,
        )

    if "country" in filtered.columns:

        st.markdown("---")

        section_heading(
            "Country Performance",
            "Compare sales, profit and margin across countries.",
        )

        country_data = (
            filtered.groupby("country")[["sales", "profit"]]
            .sum()
            .reset_index()
        )

        country_data["profit_margin_pct"] = np.where(
            country_data["sales"] != 0,
            country_data["profit"]
            / country_data["sales"] * 100,
            np.nan,
        )

        fig = px.bar(
            country_data.sort_values(
                "sales", ascending=False
            ),
            x="country",
            y="sales",
            color="profit_margin_pct",
            text_auto=".3s",
            color_continuous_scale="Teal",
            labels={
                "country": "Country",
                "sales": "Sales",
                "profit_margin_pct": "Profit Margin (%)",
            },
        )

        show_chart(fig)

        country_display = country_data.sort_values(
            "sales", ascending=False
        ).rename(
            columns={
                "country": "Country",
                "sales": "Total Sales",
                "profit": "Total Profit",
                "profit_margin_pct": "Profit Margin (%)",
            }
        )

        st.dataframe(
            country_display,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# SQL ANALYTICS
# ============================================================

elif page == "SQL Analytics":

    section_heading(
        "SQL Analytics",
        "Live read-only queries against the FinSight SQLite database.",
    )

    try:
        summary = get_sql_summary()

        c1, c2, c3, c4 = st.columns(4, gap="medium")

        with c1:
            metric_card(
                "SQL RECORDS",
                f"{summary['total_records']:,}",
                "Total database rows",
            )

        with c2:
            metric_card(
                "SQL SALES",
                money(summary["total_sales"]),
                "All database records",
            )

        with c3:
            metric_card(
                "SQL PROFIT",
                money(summary["total_profit"]),
                "All database records",
            )

        with c4:
            metric_card(
                "SQL MARGIN",
                f"{summary['profit_margin']:.2f}%",
                "Profit divided by sales",
            )

        st.markdown("---")

        section_heading(
            "Country-wise SQL Summary",
            "Results calculated directly by SQL.",
        )

        country_summary = get_country_summary()

        if not country_summary.empty:
            st.dataframe(
                country_summary,
                use_container_width=True,
                hide_index=True,
            )

            if {
                "country",
                "total_sales",
                "total_profit",
            }.issubset(country_summary.columns):

                fig = px.bar(
                    country_summary,
                    x="country",
                    y="total_sales",
                    color="total_profit",
                    text_auto=".3s",
                    color_continuous_scale="Teal",
                    labels={
                        "country": "Country",
                        "total_sales": "Sales",
                        "total_profit": "Profit",
                    },
                )

                show_chart(fig)

        else:
            st.info(
                "The country summary query returned no records."
            )

        st.markdown("---")

        section_heading(
            "SQL Query Workspace",
            "Write a read-only SELECT query and export its results.",
        )

        st.caption(
            "Only SELECT queries are permitted. "
            "Use the existing SQL utility for query validation."
        )

        default_query = (
            "SELECT country, "
            "SUM(sales) AS total_sales, "
            "SUM(profit) AS total_profit "
            "FROM financial_data "
            "GROUP BY country "
            "ORDER BY total_sales DESC"
        )

        query_text = st.text_area(
            "SQL Query",
            value=default_query,
            height=145,
            key="finsight_sql_query",
        )

        if st.button(
            "▶ Run SQL Query",
            type="primary",
            key="run_finsight_sql",
        ):
            try:
                result = run_custom_query(query_text)

                st.success(
                    f"Query completed: {len(result):,} rows returned."
                )

                st.dataframe(
                    result,
                    use_container_width=True,
                    hide_index=True,
                )

                st.download_button(
                    "⬇ Download SQL Results",
                    data=result.to_csv(
                        index=False
                    ).encode("utf-8"),
                    file_name="finsight_sql_results.csv",
                    mime="text/csv",
                    key="download_sql_results",
                )

            except Exception as error:
                st.error(f"SQL query failed: {error}")

    except Exception as error:
        st.error(
            "Could not read the FinSight SQLite database."
        )
        st.exception(error)


# ============================================================
# ADVANCED SQL ANALYTICS
# ============================================================

elif page == "Advanced SQL Analytics":

    section_heading(
        "Advanced SQL Analytics",
        "Explore advanced queries, aggregations and database insights.",
    )

    try:
        render_advanced_sql_page(
            BASE_DIR,
            money,
            show_chart,
        )
    except Exception as error:
        st.error(
            "Could not render Advanced SQL Analytics."
        )
        st.exception(error)


# ============================================================
# BUSINESS INSIGHTS
# ============================================================

elif page == "Business Insights":

    section_heading(
        "Business Insights",
        "Explore generated financial findings and business recommendations.",
    )

    try:
        render_business_insights_page(
            BASE_DIR,
            money,
            show_chart,
        )
    except Exception as error:
        st.error(
            "Could not render Business Insights."
        )
        st.exception(error)


# ============================================================
# DATA EXPLORER
# ============================================================

elif page == "Data Explorer":

    section_heading(
        "Data Explorer",
        "Search, inspect and export financial records.",
    )

    c1, c2 = st.columns([2, 1], gap="medium")

    with c1:
        search = st.text_input(
            "Search records by text",
            placeholder="Enter country, product, segment...",
            key="data_explorer_search",
        )

    with c2:
        st.metric(
            "Filtered Records",
            f"{len(filtered):,}",
        )

    view = filtered.copy()

    if search.strip():

        text_cols = view.select_dtypes(
            include=["object", "string"]
        ).columns.tolist()

        if text_cols:
            mask = (
                view[text_cols]
                .fillna("")
                .astype(str)
                .apply(
                    lambda col: col.str.contains(
                        search,
                        case=False,
                        regex=False,
                    )
                )
                .any(axis=1)
            )

            view = view[mask]

        else:
            view = view.iloc[0:0]

    st.caption(
        f"{len(view):,} matching records found."
    )

    st.dataframe(
        view,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "⬇ Download Filtered CSV",
        data=view.to_csv(
            index=False
        ).encode("utf-8"),
        file_name="finsight_filtered_data.csv",
        mime="text/csv",
        key="download_filtered_csv",
    )

    st.markdown("---")

    section_heading(
        "Data Quality Report",
        "Missing values and data types for the original cleaned dataset.",
    )

    quality = pd.DataFrame(
        {
            "Column": df.columns,
            "Missing Values": [
                int(df[col].isna().sum())
                for col in df.columns
            ],
            "Data Type": [
                str(df[col].dtype)
                for col in df.columns
            ],
        }
    )

    st.dataframe(
        quality,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("#### Dataset Preview")

    st.dataframe(
        df.head(10),
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    """
    <div class="footer">
        <strong>FINSIGHT</strong> &nbsp; | &nbsp;
        FINANCIAL PERFORMANCE ANALYTICS
        <br><br>
        Built with Python • Streamlit • Pandas • Plotly • SQLite • SQL
    </div>
    """,
    unsafe_allow_html=True,
)
