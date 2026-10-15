
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# =====================================================
# FINSIGHT | FINANCIAL PERFORMANCE ANALYTICS
# =====================================================

st.set_page_config(
    page_title="FinSight | Financial Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- THEME ---------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #080d1b 0%, #10152a 55%, #0a1020 100%);
    color: #f1f5f9;
}

[data-testid="stSidebar"] {
    background: #0c1222;
    border-right: 1px solid #252d45;
}

[data-testid="stSidebar"] * {
    color: #e2e8f0;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.hero {
    background: linear-gradient(115deg, #171e38, #25204a);
    border: 1px solid #38345f;
    padding: 28px;
    border-radius: 20px;
    margin-bottom: 22px;
}

.hero h1 {
    font-size: 34px;
    margin: 0;
    color: #ffffff;
}

.hero p {
    color: #b7c2dc;
    margin-top: 10px;
    font-size: 14px;
}

.metric-card {
    background: linear-gradient(145deg, #171f35, #121a2d);
    border: 1px solid #2b3652;
    border-radius: 16px;
    padding: 20px;
    min-height: 125px;
}

.metric-label {
    color: #9baaca;
    font-size: 13px;
    margin-bottom: 12px;
}

.metric-value {
    color: #ffffff;
    font-size: 26px;
    font-weight: 800;
    overflow-wrap: anywhere;
}

.metric-note {
    color: #8b9ab8;
    font-size: 11px;
    margin-top: 9px;
}

.section-title {
    font-size: 21px;
    font-weight: 700;
    margin: 28px 0 12px;
    color: #f1f5f9;
}

div[data-testid="stPlotlyChart"] {
    background: #111a2d;
    border: 1px solid #27344d;
    border-radius: 14px;
    padding: 8px;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #27344d;
    border-radius: 12px;
}

.stDownloadButton button {
    background: #7c5cfc;
    color: white;
    border: none;
    border-radius: 9px;
    font-weight: 600;
}

hr {
    border-color: #29344b;
}
</style>
""", unsafe_allow_html=True)

# -------------------- LOAD DATA -----------------------

DATA_FILE = Path("data/processed/cleaned_financial_data.csv")

@st.cache_data
def load_data(path):
    data = pd.read_csv(path)
    data.columns = (
        data.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )

    if "date" in data.columns:
        data["date"] = pd.to_datetime(data["date"], errors="coerce")

    for col in [
        "sales", "profit", "cogs", "gross_sales",
        "discounts", "units_sold", "year",
        "month_number", "sale_price",
        "manufacturing_price"
    ]:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

    if "discount_band" in data.columns:
        data["discount_band"] = (
            data["discount_band"].fillna("Unknown").astype(str)
        )

    return data

if not DATA_FILE.exists():
    st.error("Cleaned dataset not found.")
    st.info(
        "Please run: python clean_data.py "
        "from the main project folder."
    )
    st.stop()

df = load_data(str(DATA_FILE))

required = {"sales", "profit"}
if not required.issubset(df.columns):
    st.error("Dataset must contain sales and profit columns.")
    st.write("Available columns:", df.columns.tolist())
    st.stop()

# -------------------- HELPERS -------------------------

def money(value):
    if pd.isna(value):
        return "N/A"
    value = float(value)
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:,.2f}M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:,.1f}K"
    return f"${value:,.2f}"

def chart_layout(fig, height=350):
    fig.update_layout(
        template="plotly_dark",
        height=height,
        margin=dict(l=20, r=20, t=55, b=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#dce5f5"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        hoverlabel=dict(bgcolor="#171f35")
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#26324a")
    return fig

def metric_card(label, value, note):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------- SIDEBAR -------------------------

with st.sidebar:
    st.markdown("## ◈ FINSIGHT")
    st.caption("FINANCIAL INTELLIGENCE")
    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "Executive Overview",
            "Revenue & Profit",
            "Expense Analysis",
            "Product & Market",
            "Data Explorer"
        ]
    )

    st.divider()
    st.caption("DATASET")
    st.write(f"**{len(df):,}** records")
    st.write(f"**{len(df.columns)}** columns")
    st.caption("Python • SQL • Power BI")

# -------------------- GLOBAL FILTERS ------------------

st.markdown(
    """
    <div class="hero">
        <h1>Financial Performance Analytics</h1>
        <p>FINANCIAL INTELLIGENCE / BUSINESS PERFORMANCE / DATA-DRIVEN DECISIONS</p>
    </div>
    """,
    unsafe_allow_html=True
)

filtered = df.copy()

with st.expander("⚙️ Dashboard Filters", expanded=True):
    filter_cols = st.columns(3)

    if "year" in filtered.columns:
        years = sorted(filtered["year"].dropna().unique().tolist())
        selected_years = filter_cols[0].multiselect(
            "Year",
            years,
            default=years
        )
        filtered = filtered[filtered["year"].isin(selected_years)]

    if "country" in filtered.columns:
        countries = sorted(
            filtered["country"].dropna().astype(str).unique().tolist()
        )
        selected_countries = filter_cols[1].multiselect(
            "Country",
            countries,
            default=countries
        )
        filtered = filtered[
            filtered["country"].astype(str).isin(selected_countries)
        ]

    if "segment" in filtered.columns:
        segments = sorted(
            filtered["segment"].dropna().astype(str).unique().tolist()
        )
        selected_segments = filter_cols[2].multiselect(
            "Segment",
            segments,
            default=segments
        )
        filtered = filtered[
            filtered["segment"].astype(str).isin(selected_segments)
        ]

if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

total_sales = filtered["sales"].sum()
total_profit = filtered["profit"].sum()
margin = total_profit / total_sales * 100 if total_sales else 0
total_orders = len(filtered)

# -------------------- EXECUTIVE OVERVIEW --------------

if page == "Executive Overview":

    st.markdown('<div class="section-title">Executive Summary</div>',
                unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card("TOTAL SALES", money(total_sales),
                    "Sales in selected records")
    with c2:
        metric_card("TOTAL PROFIT", money(total_profit),
                    "Profit in selected records")
    with c3:
        metric_card("PROFIT MARGIN", f"{margin:.2f}%",
                    "Total profit / total sales")
    with c4:
        metric_card("RECORDS", f"{total_orders:,}",
                    "Rows after filtering")

    left, right = st.columns(2)

    with left:
        st.markdown("### Sales vs Profit")

        if "date" in filtered.columns and filtered["date"].notna().any():
            trend = (
                filtered.dropna(subset=["date"])
                .groupby(pd.Grouper(key="date", freq="MS"))[
                    ["sales", "profit"]
                ].sum().reset_index()
            )

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=trend["date"], y=trend["sales"],
                name="Sales", mode="lines+markers",
                line=dict(color="#8b7cff", width=3),
                fill="tozeroy", fillcolor="rgba(139,124,255,0.08)"
            ))
            fig.add_trace(go.Scatter(
                x=trend["date"], y=trend["profit"],
                name="Profit", mode="lines+markers",
                line=dict(color="#2dd4bf", width=3)
            ))
            st.plotly_chart(chart_layout(fig), use_container_width=True)
        else:
            st.info("Date data is not available for trend analysis.")

    with right:
        st.markdown("### Profit by Segment")

        if "segment" in filtered.columns:
            segment_data = (
                filtered.groupby("segment", dropna=False)["profit"]
                .sum().reset_index().sort_values("profit")
            )
            fig = px.bar(
                segment_data, x="profit", y="segment",
                orientation="h", text_auto=".3s",
                color="profit",
                color_continuous_scale=["#5b4bce", "#9d8cff"]
            )
            st.plotly_chart(
                chart_layout(fig), use_container_width=True
            )
        else:
            st.info("Segment column is not available.")

    left, right = st.columns(2)

    with left:
        st.markdown("### Revenue by Country")
        if "country" in filtered.columns:
            country_data = (
                filtered.groupby("country")["sales"].sum()
                .sort_values(ascending=False).head(10).reset_index()
            )
            fig = px.bar(
                country_data, x="country", y="sales",
                text_auto=".3s", color_discrete_sequence=["#8b7cff"]
            )
            st.plotly_chart(
                chart_layout(fig), use_container_width=True
            )

    with right:
        st.markdown("### Product Performance")
        if "product" in filtered.columns:
            product_data = (
                filtered.groupby("product")[["sales", "profit"]]
                .sum().reset_index().sort_values("sales", ascending=False)
            )
            fig = px.bar(
                product_data, x="product", y="sales",
                color="profit", text_auto=".3s",
                color_continuous_scale="Teal"
            )
            st.plotly_chart(
                chart_layout(fig), use_container_width=True
            )

# -------------------- REVENUE & PROFIT ----------------

elif page == "Revenue & Profit":
    st.markdown("## Revenue & Profit Analysis")

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("REVENUE", money(total_sales), "Filtered sales")
    with c2:
        metric_card("PROFIT", money(total_profit), "Filtered profit")
    with c3:
        metric_card("MARGIN", f"{margin:.2f}%", "Profit / sales")

    if "date" in filtered.columns:
        trend = (
            filtered.dropna(subset=["date"])
            .groupby(pd.Grouper(key="date", freq="MS"))[
                ["sales", "profit"]
            ].sum().reset_index()
        )

        fig = px.line(
            trend, x="date", y=["sales", "profit"],
            markers=True, title="Monthly Revenue and Profit"
        )
        st.plotly_chart(
            chart_layout(fig, 430), use_container_width=True
        )

    if "segment" in filtered.columns:
        segment_data = (
            filtered.groupby("segment")[["sales", "profit"]]
            .sum().reset_index()
        )
        fig = px.bar(
            segment_data, x="segment", y=["sales", "profit"],
            barmode="group", title="Sales and Profit by Segment"
        )
        st.plotly_chart(
            chart_layout(fig), use_container_width=True
        )

# -------------------- EXPENSE ANALYSIS ----------------

elif page == "Expense Analysis":
    st.markdown("## Expense & Cost Analysis")

    if "cogs" in filtered.columns:
        total_cogs = filtered["cogs"].sum()
        c1, c2 = st.columns(2)
        with c1:
            metric_card("COST OF GOODS SOLD", money(total_cogs),
                        "Recorded COGS")
        with c2:
            metric_card(
                "COGS / SALES",
                f"{total_cogs / total_sales * 100:.2f}%"
                if total_sales else "N/A",
                "Cost relative to sales"
            )

        if "segment" in filtered.columns:
            cost_data = (
                filtered.groupby("segment")["cogs"]
                .sum().reset_index().sort_values("cogs", ascending=False)
            )
            fig = px.bar(
                cost_data, x="segment", y="cogs",
                title="Cost of Goods Sold by Segment",
                color_discrete_sequence=["#fb7185"]
            )
            st.plotly_chart(
                chart_layout(fig), use_container_width=True
            )

        if "product" in filtered.columns:
            cost_product = (
                filtered.groupby("product")["cogs"]
                .sum().reset_index().sort_values("cogs", ascending=False)
            )
            fig = px.pie(
                cost_product, names="product", values="cogs",
                hole=0.58, title="COGS Distribution by Product"
            )
            st.plotly_chart(
                chart_layout(fig), use_container_width=True
            )
    else:
        st.info("COGS data is not available in this dataset.")

    st.caption(
        "Note: COGS is the recorded cost of goods sold, not a complete "
        "measure of all operating expenses."
    )

# -------------------- PRODUCT & MARKET ---------------

elif page == "Product & Market":
    st.markdown("## Product & Market Performance")

    if "product" in filtered.columns:
        product_data = (
            filtered.groupby("product")[["sales", "profit"]]
            .sum().reset_index()
        )
        product_data["profit_margin_pct"] = np.where(
            product_data["sales"] != 0,
            product_data["profit"] / product_data["sales"] * 100,
            np.nan
        )

        fig = px.bar(
            product_data.sort_values("profit", ascending=False),
            x="product", y="profit",
            color="profit_margin_pct",
            title="Product Profitability",
            text_auto=".3s",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(
            chart_layout(fig), use_container_width=True
        )
        st.dataframe(
            product_data.sort_values("profit", ascending=False),
            use_container_width=True, hide_index=True
        )

    if "country" in filtered.columns:
        st.markdown("### Country Performance")
        country_data = (
            filtered.groupby("country")[["sales", "profit"]]
            .sum().reset_index()
        )
        country_data["profit_margin_pct"] = np.where(
            country_data["sales"] != 0,
            country_data["profit"] / country_data["sales"] * 100,
            np.nan
        )
        st.dataframe(
            country_data.sort_values("sales", ascending=False),
            use_container_width=True, hide_index=True
        )

# -------------------- DATA EXPLORER ------------------

elif page == "Data Explorer":
    st.markdown("## Data Explorer")
    st.write("Inspect and download the filtered financial records.")

    search = st.text_input("Search records by text")

    view = filtered.copy()

    if search.strip():
        text_cols = view.select_dtypes(
            include=["object", "string"]
        ).columns.tolist()

        if text_cols:
            mask = view[text_cols].fillna("").astype(str).apply(
                lambda col: col.str.contains(
                    search, case=False, regex=False
                )
            ).any(axis=1)
            view = view[mask]

    st.caption(f"{len(view):,} matching records")
    st.dataframe(view, use_container_width=True, hide_index=True)

    csv = view.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇ Download filtered CSV",
        data=csv,
        file_name="finsight_filtered_data.csv",
        mime="text/csv"
    )

    st.markdown("### Data Quality")
    quality = pd.DataFrame({
        "Column": df.columns,
        "Missing Values": [int(df[col].isna().sum()) for col in df.columns],
        "Data Type": [str(df[col].dtype) for col in df.columns]
    })
    st.dataframe(quality, use_container_width=True, hide_index=True)

# -------------------- FOOTER --------------------------

st.divider()
st.caption(
    "FINSIGHT • Financial Performance Analytics | "
    "Built with Python, Pandas, Streamlit & Plotly"
)
