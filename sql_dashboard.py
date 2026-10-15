
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =====================================================
# FINSIGHT | INTERACTIVE SQL BUSINESS INTELLIGENCE
# =====================================================

st.set_page_config(
    page_title="FinSight | Business Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "data" / "database" / "finsight.db"

# ---------------- PROFESSIONAL THEME ------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.stApp {
    background: #0b1020;
    color: #edf0ff;
    font-family: 'Inter', sans-serif;
}

/* Main content */
.main .block-container {
    color: #edf0ff;
    padding-top: 2rem;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #10172a;
    border-right: 1px solid #27334f;
}

[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #edf0ff !important;
}

/* KPI cards */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #151f38, #1b2040);
    border: 1px solid #303c60;
    border-radius: 14px;
    padding: 18px;
    min-width: 0;
    overflow: hidden;
}

[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] p {
    color: #cbd5e1 !important;
}

[data-testid="stMetricValue"],
[data-testid="stMetricValue"] div {
    color: #ffffff !important;
    font-size: clamp(20px, 2vw, 32px) !important;
}

/* Headings */
h1, h2, h3, h4,
[data-testid="stHeader"] {
    color: #e0e7ff;
}

/* Tabs */
button[data-baseweb="tab"] {
    color: #cbd5e1 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #ff7777 !important;
}

/* Select boxes - keep selected values readable */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: #ffffff;
}

[data-testid="stSidebar"] [data-baseweb="select"] input {
    color: #111827 !important;
}

/* Input labels */
.stSelectbox label,
.stMultiSelect label {
    color: #e2e8f0 !important;
}

/* Plotly charts */
div[data-testid="stPlotlyChart"] {
    background: #11182b;
    border: 1px solid #27334f;
    border-radius: 14px;
    padding: 10px;
}

/* Data tables */
div[data-testid="stDataFrame"] {
    border: 1px solid #27334f;
    border-radius: 10px;
}

/* Insight cards */
.insight-card {
    background: #151f38;
    border: 1px solid #303c60;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 8px;
}

.insight-label {
    color: #cbd5e1;
    font-size: 13px;
}

.insight-value {
    color: #c4b5fd;
    font-size: 22px;
    font-weight: 700;
}

.small-note {
    color: #cbd5e1;
    font-size: 12px;
}

/* General text */
.stMarkdown, .stCaption {
    color: #e2e8f0;
}
</style>
""", unsafe_allow_html=True)


# ---------------- SQL HELPER --------------------------
def run_query(query, params=()):
    with sqlite3.connect(DB_FILE) as conn:
        return pd.read_sql_query(query, conn, params=params)


# ---------------- DATABASE VALIDATION -----------------
st.sidebar.markdown("## FinSight")
st.sidebar.caption("FINANCIAL INTELLIGENCE PLATFORM")
st.sidebar.divider()

if not DB_FILE.exists():
    st.error("SQLite database not found. Run: python create_db.py")
    st.stop()

try:
    total_rows = run_query(
        "SELECT COUNT(*) AS n FROM financial_data"
    ).iloc[0]["n"]
except Exception as exc:
    st.error(f"Could not read the financial_data table: {exc}")
    st.stop()


# ---------------- SIDEBAR FILTERS ----------------------
st.sidebar.subheader("Global Filters")

country_options = run_query("""
    SELECT DISTINCT country
    FROM financial_data
    WHERE country IS NOT NULL
    ORDER BY country
""")["country"].tolist()

product_options = run_query("""
    SELECT DISTINCT product
    FROM financial_data
    WHERE product IS NOT NULL
    ORDER BY product
""")["product"].tolist()

segment_options = run_query("""
    SELECT DISTINCT segment
    FROM financial_data
    WHERE segment IS NOT NULL
    ORDER BY segment
""")["segment"].tolist()

countries_selected = st.sidebar.multiselect(
    "Country",
    country_options,
    default=country_options,
)

products_selected = st.sidebar.multiselect(
    "Product",
    product_options,
    default=product_options,
)

segments_selected = st.sidebar.multiselect(
    "Segment",
    segment_options,
    default=segment_options,
)

st.sidebar.divider()
st.sidebar.caption(f"Database records: {int(total_rows):,}")
st.sidebar.caption("Data source: Financial Sample")


# ---------------- BUILD SAFE FILTERS -------------------
conditions = []
params = []

def add_filter(column, selected, all_options):
    if len(selected) == 0:
        conditions.append("1 = 0")
    elif len(selected) < len(all_options):
        placeholders = ", ".join(["?"] * len(selected))
        conditions.append(f"{column} IN ({placeholders})")
        params.extend(selected)

add_filter("country", countries_selected, country_options)
add_filter("product", products_selected, product_options)
add_filter("segment", segments_selected, segment_options)

where_clause = (
    "WHERE " + " AND ".join(conditions)
    if conditions else ""
)

filtered_count = run_query(
    f"SELECT COUNT(*) AS n FROM financial_data {where_clause}",
    params,
).iloc[0]["n"]


# ---------------- HEADER --------------------------------
st.title("FinSight")
st.markdown("### Financial Performance & Business Intelligence")
st.caption(
    "SQL-powered analytics • Interactive filtering • "
    "Profitability insights"
)

if filtered_count == 0:
    st.warning("No records match the selected filters. Change the filters.")
    st.stop()


# ---------------- EXECUTIVE KPIs ------------------------
kpi = run_query(f"""
    SELECT
        COUNT(*) AS records,
        SUM(sales) AS sales,
        SUM(profit) AS profit,
        100.0 * SUM(profit) / NULLIF(SUM(sales), 0) AS margin
    FROM financial_data
    {where_clause}
""", params).iloc[0]

sales_value = float(kpi["sales"] or 0)
profit_value = float(kpi["profit"] or 0)
margin_value = (
    float(kpi["margin"])
    if pd.notna(kpi["margin"]) else 0
)

k1, k2, k3, k4 = st.columns(4)

k1.metric("Total Sales", f"{sales_value:,.2f}")
k2.metric("Total Profit", f"{profit_value:,.2f}")
k3.metric("Profit Margin", f"{margin_value:.2f}%")
k4.metric("Records Analyzed", f"{int(kpi['records']):,}")

st.divider()


# ---------------- LOAD SQL ANALYSES ---------------------
country_df = run_query(f"""
    SELECT country,
           SUM(sales) AS total_sales,
           SUM(profit) AS total_profit
    FROM financial_data
    {where_clause}
    GROUP BY country
    ORDER BY total_sales DESC
""", params)

product_df = run_query(f"""
    SELECT product,
           SUM(sales) AS total_sales,
           SUM(profit) AS total_profit,
           100.0 * SUM(profit) / NULLIF(SUM(sales), 0)
               AS profit_margin_pct
    FROM financial_data
    {where_clause}
    GROUP BY product
    ORDER BY total_profit DESC
""", params)

segment_df = run_query(f"""
    SELECT segment,
           SUM(sales) AS total_sales,
           SUM(profit) AS total_profit,
           100.0 * SUM(profit) / NULLIF(SUM(sales), 0)
               AS profit_margin_pct
    FROM financial_data
    {where_clause}
    GROUP BY segment
    ORDER BY total_profit DESC
""", params)


monthly_conditions = conditions.copy()
monthly_conditions.append("date IS NOT NULL")

monthly_where_clause = (
    "WHERE " + " AND ".join(monthly_conditions)
    if monthly_conditions else "WHERE date IS NOT NULL"
)

monthly_df = run_query(f"""
    SELECT
        strftime('%Y-%m', date) AS sales_month,
        SUM(sales) AS total_sales,
        SUM(profit) AS total_profit
    FROM financial_data
    {monthly_where_clause}
    GROUP BY strftime('%Y-%m', date)
    ORDER BY sales_month
""", params)


discount_df = run_query(f"""
    SELECT COALESCE(discount_band, 'Unknown') AS discount_band,
           COUNT(*) AS records,
           SUM(sales) AS total_sales,
           SUM(profit) AS total_profit,
           100.0 * SUM(profit) / NULLIF(SUM(sales), 0)
               AS profit_margin_pct
    FROM financial_data
    {where_clause}
    GROUP BY COALESCE(discount_band, 'Unknown')
    ORDER BY total_sales DESC
""", params)


# ---------------- NAVIGATION TABS -----------------------
overview_tab, market_tab, segment_tab, discount_tab, data_tab = st.tabs([
    "Executive Overview",
    "Country & Product",
    "Segment Analysis",
    "Discount Analysis",
    "SQL Data Explorer",
])


# ========================================================
# TAB 1 - EXECUTIVE OVERVIEW
# ========================================================
with overview_tab:
    st.subheader("Sales & Profit Trend")

    if not monthly_df.empty:
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=monthly_df["sales_month"],
            y=monthly_df["total_sales"],
            mode="lines+markers",
            name="Sales",
            line=dict(width=3, color="#a78bfa"),
        ))

        fig.add_trace(go.Scatter(
            x=monthly_df["sales_month"],
            y=monthly_df["total_profit"],
            mode="lines+markers",
            name="Profit",
            line=dict(width=3, color="#34d399"),
        ))

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=410,
            xaxis_title="Month",
            yaxis_title="Amount",
            legend_title="Metric",
            margin=dict(l=20, r=20, t=35, b=20),
        )

        st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)

    with left:
        st.markdown("#### Country Sales")
        fig_country = px.bar(
            country_df.sort_values("total_sales"),
            x="total_sales",
            y="country",
            orientation="h",
            color="total_sales",
            color_continuous_scale="Purples",
            template="plotly_dark",
        )
        fig_country.update_layout(
            height=350,
            coloraxis_showscale=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_country, use_container_width=True)

    with right:
        st.markdown("#### Product Profit")
        fig_product = px.bar(
            product_df.sort_values("total_profit"),
            x="total_profit",
            y="product",
            orientation="h",
            color="total_profit",
            color_continuous_scale="Teal",
            template="plotly_dark",
        )
        fig_product.update_layout(
            height=350,
            coloraxis_showscale=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_product, use_container_width=True)


# ========================================================
# TAB 2 - COUNTRY & PRODUCT
# ========================================================
with market_tab:
    st.subheader("Country Performance")

    fig = px.scatter(
        country_df,
        x="total_sales",
        y="total_profit",
        size="total_sales",
        color="country",
        hover_name="country",
        template="plotly_dark",
        labels={
            "total_sales": "Total Sales",
            "total_profit": "Total Profit",
        },
    )
    fig.update_layout(
        height=420,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        country_df.sort_values("total_profit", ascending=False)
        .round(2),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    st.subheader("Product Profitability")

    fig = px.bar(
        product_df,
        x="product",
        y="total_profit",
        color="profit_margin_pct",
        color_continuous_scale="Viridis",
        text_auto=".3s",
        template="plotly_dark",
        hover_data=["total_sales", "profit_margin_pct"],
    )
    fig.update_layout(
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        product_df.sort_values("total_profit", ascending=False)
        .round(2),
        use_container_width=True,
        hide_index=True,
    )


# ========================================================
# TAB 3 - SEGMENT ANALYSIS
# ========================================================
with segment_tab:
    st.subheader("Segment-wise Profitability")

    fig = px.bar(
        segment_df.sort_values("total_profit"),
        x="total_profit",
        y="segment",
        orientation="h",
        color="profit_margin_pct",
        color_continuous_scale="RdYlGn",
        text_auto=".3s",
        template="plotly_dark",
        hover_data=["total_sales", "profit_margin_pct"],
    )
    fig.update_layout(
        height=430,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)

    negative_segments = segment_df[
        segment_df["total_profit"] < 0
    ]

    if not negative_segments.empty:
        st.warning(
            "Some segments have negative total profit. "
            "Review their pricing, costs, and sales mix."
        )
        st.dataframe(
            negative_segments.round(2),
            use_container_width=True,
            hide_index=True,
        )

    st.dataframe(
        segment_df.round(2),
        use_container_width=True,
        hide_index=True,
    )


# ========================================================
# TAB 4 - DISCOUNT ANALYSIS
# ========================================================
with discount_tab:
    st.subheader("Discount Band Performance")

    fig = px.bar(
        discount_df,
        x="discount_band",
        y="total_profit",
        color="profit_margin_pct",
        text_auto=".3s",
        color_continuous_scale="RdYlGn",
        template="plotly_dark",
        hover_data=["records", "total_sales"],
    )
    fig.update_layout(
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        discount_df.round(2),
        use_container_width=True,
        hide_index=True,
    )

    st.info(
        "Discount band results show association, not proof of causation. "
        "Consider product mix, sales volume, and segment differences "
        "before recommending discount changes."
    )


# ========================================================
# TAB 5 - SQL DATA EXPLORER
# ========================================================
with data_tab:
    st.subheader("Explore Filtered SQL Records")

    search_text = st.text_input(
        "Search country, product, or segment",
        placeholder="Enter a keyword...",
    )

    data_df = run_query(f"""
        SELECT date, country, product, segment,
               discount_band, sales, profit
        FROM financial_data
        {where_clause}
        ORDER BY date DESC
    """, params)

    if search_text.strip():
        keyword = search_text.strip().lower()
        mask = (
            data_df["country"].fillna("").str.lower().str.contains(
                keyword, regex=False
            )
            | data_df["product"].fillna("").str.lower().str.contains(
                keyword, regex=False
            )
            | data_df["segment"].fillna("").str.lower().str.contains(
                keyword, regex=False
            )
        )
        data_df = data_df[mask]

    st.caption(f"Matching records: {len(data_df):,}")

    st.dataframe(
        data_df,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Download Filtered Data (CSV)",
        data=data_df.to_csv(index=False).encode("utf-8"),
        file_name="finsight_filtered_data.csv",
        mime="text/csv",
    )

    st.divider()
    st.markdown("#### Run a Read-only SQL Query")

    query_options = {
        "Top 10 profitable records": """
            SELECT date, country, product, segment, sales, profit
            FROM financial_data
            WHERE profit IS NOT NULL
            ORDER BY profit DESC
            LIMIT 10
        """,
        "Country performance": """
            SELECT country, SUM(sales) AS total_sales,
                   SUM(profit) AS total_profit
            FROM financial_data
            GROUP BY country
            ORDER BY total_profit DESC
        """,
        "Product performance": """
            SELECT product, SUM(sales) AS total_sales,
                   SUM(profit) AS total_profit
            FROM financial_data
            GROUP BY product
            ORDER BY total_profit DESC
        """,
        "Monthly trend": """
            SELECT strftime('%Y-%m', date) AS month,
                   SUM(sales) AS total_sales,
                   SUM(profit) AS total_profit
            FROM financial_data
            WHERE date IS NOT NULL
            GROUP BY strftime('%Y-%m', date)
            ORDER BY month
        """,
    }

    selected_query = st.selectbox(
        "Choose a saved SQL query",
        list(query_options.keys()),
    )

    if st.button("Execute SQL Analysis", type="primary"):
        query_result = run_query(
            query_options[selected_query]
        )
        st.dataframe(
            query_result.round(2),
            use_container_width=True,
            hide_index=True,
        )
        st.download_button(
            "Download Query Result",
            data=query_result.to_csv(index=False).encode("utf-8"),
            file_name="finsight_query_result.csv",
            mime="text/csv",
        )


# ---------------- AUTOMATED BUSINESS INSIGHTS ----------
st.divider()
st.subheader("Business Insights")

insight_cols = st.columns(3)

if not country_df.empty:
    best_country = country_df.loc[
        country_df["total_profit"].idxmax()
    ]
    with insight_cols[0]:
        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-label">Highest-profit country</div>
                <div class="insight-value">{best_country['country']}</div>
                <div class="small-note">
                    Profit: {best_country['total_profit']:,.2f}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

if not product_df.empty:
    best_product = product_df.loc[
        product_df["total_profit"].idxmax()
    ]
    with insight_cols[1]:
        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-label">Highest-profit product</div>
                <div class="insight-value">{best_product['product']}</div>
                <div class="small-note">
                    Profit: {best_product['total_profit']:,.2f}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

if not segment_df.empty:
    best_segment = segment_df.loc[
        segment_df["total_profit"].idxmax()
    ]
    with insight_cols[2]:
        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-label">Highest-profit segment</div>
                <div class="insight-value">{best_segment['segment']}</div>
                <div class="small-note">
                    Profit: {best_segment['total_profit']:,.2f}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.caption(
    "FinSight | SQL-powered financial analysis | "
    "Amounts shown in the dataset's original units."
)
