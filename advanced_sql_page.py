import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path


def render_advanced_sql_page(base_dir, money, show_chart):
    """Display the saved FinSight Advanced SQL reports."""

    report_dir = Path(base_dir) / "reports" / "sql_analysis"

    report_files = {
        "overall": "overall_performance.csv",
        "country": "country_performance.csv",
        "product": "product_profitability.csv",
        "segment": "segment_performance.csv",
        "monthly": "monthly_performance.csv",
        "discount": "discount_analysis.csv",
        "top_records": "top_profit_records.csv",
        "quality": "data_quality.csv",
    }

    st.subheader("Advanced SQL Analytics")
    st.caption(
        "Business performance insights generated using SQL "
        "and saved FinSight reports."
    )

    # Load saved CSV reports
    reports = {}

    for key, filename in report_files.items():
        file_path = report_dir / filename

        if not file_path.exists():
            st.error(f"Report not found: {file_path}")
            st.info(
                "Run python advanced_sql_analysis.py "
                "from your FinSight project folder."
            )
            return

        try:
            reports[key] = pd.read_csv(file_path)
        except Exception as error:
            st.error(f"Could not read {filename}: {error}")
            return

    overall = reports["overall"]
    country = reports["country"]
    product = reports["product"]
    segment = reports["segment"]
    monthly = reports["monthly"]
    discount = reports["discount"]
    top_records = reports["top_records"]
    quality = reports["quality"]

    # Overall KPIs
    st.markdown("### Overall Financial Performance")

    if not overall.empty:
        row = overall.iloc[0]

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Total Records",
            f"{int(row['total_records']):,}"
        )
        c2.metric(
            "Total Sales",
            money(row["total_sales"])
        )
        c3.metric(
            "Total Profit",
            money(row["total_profit"])
        )
        c4.metric(
            "Profit Margin",
            f"{row['profit_margin_pct']:.2f}%"
        )

    # Country analysis
    st.markdown("### Country-wise Performance")

    if not country.empty:
        country = country.sort_values(
            "total_sales", ascending=False
        )

        left, right = st.columns(2)

        with left:
            fig = px.bar(
                country,
                x="country",
                y="total_sales",
                color="total_profit",
                text_auto=".3s",
                title="Sales by Country",
                color_continuous_scale="Teal",
            )
            show_chart(fig, 400)

        with right:
            fig = px.bar(
                country.sort_values("total_profit"),
                x="total_profit",
                y="country",
                orientation="h",
                text_auto=".3s",
                title="Profit by Country",
                color="total_profit",
                color_continuous_scale="Viridis",
            )
            show_chart(fig, 400)

        st.dataframe(
            country,
            use_container_width=True,
            hide_index=True,
        )

    # Product analysis
    st.markdown("### Product Profitability")

    if not product.empty:
        product = product.sort_values(
            "total_profit", ascending=False
        )

        fig = px.bar(
            product,
            x="product",
            y="total_profit",
            color="profit_margin_pct",
            text_auto=".3s",
            title="Profit by Product",
            color_continuous_scale="Viridis",
        )
        show_chart(fig, 400)

        st.dataframe(
            product,
            use_container_width=True,
            hide_index=True,
        )

    # Segment analysis
    st.markdown("### Segment Performance")

    if not segment.empty:
        segment = segment.sort_values(
            "total_profit", ascending=True
        )

        fig = px.bar(
            segment,
            x="total_profit",
            y="segment",
            orientation="h",
            color="total_profit",
            text_auto=".3s",
            title="Profit and Loss by Segment",
            color_continuous_scale="RdYlGn",
        )
        show_chart(fig, 420)

        loss_segments = segment[
            segment["total_profit"] < 0
        ]

        if not loss_segments.empty:
            st.warning(
                "One or more segments have negative total profit. "
                "Review these segments before making business decisions."
            )
            st.dataframe(
                loss_segments,
                use_container_width=True,
                hide_index=True,
            )

        st.dataframe(
            segment,
            use_container_width=True,
            hide_index=True,
        )

    # Monthly analysis
    st.markdown("### Monthly Sales and Profit Trends")

    if not monthly.empty:
        monthly["sales_month"] = monthly[
            "sales_month"
        ].astype(str)

        monthly = monthly.sort_values("sales_month")

        fig = px.line(
            monthly,
            x="sales_month",
            y=["total_sales", "total_profit"],
            markers=True,
            title="Monthly Sales vs Profit",
        )
        show_chart(fig, 430)

        best_month = monthly.loc[
            monthly["total_sales"].idxmax()
        ]

        st.info(
            f"Highest-sales month: {best_month['sales_month']} "
            f"— {money(best_month['total_sales'])}"
        )

        st.dataframe(
            monthly,
            use_container_width=True,
            hide_index=True,
        )

    # Discount analysis
    st.markdown("### Discount Band Analysis")

    if not discount.empty:
        fig = px.bar(
            discount,
            x="discount_band",
            y="total_profit",
            color="total_profit",
            text_auto=".3s",
            title="Profit by Discount Band",
            color_continuous_scale="Teal",
        )
        show_chart(fig, 380)

        st.dataframe(
            discount,
            use_container_width=True,
            hide_index=True,
        )

    # Top profitable records
    st.markdown("### Top 10 Highest-Profit Records")

    if not top_records.empty:
        if "date" in top_records.columns:
            top_records["date"] = pd.to_datetime(
                top_records["date"],
                errors="coerce",
            ).dt.strftime("%Y-%m-%d")

        st.dataframe(
            top_records,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "Download Top Profit Records",
            data=top_records.to_csv(
                index=False
            ).encode("utf-8"),
            file_name="finsight_top_profit_records.csv",
            mime="text/csv",
        )

    # Data quality
    st.markdown("### SQL Data Quality Check")

    if not quality.empty:
        st.dataframe(
            quality,
            use_container_width=True,
            hide_index=True,
        )

    # Download all report tables
    st.markdown("### Download SQL Reports")

    for key, filename in report_files.items():
        report = reports[key]

        st.download_button(
            f"Download {filename}",
            data=report.to_csv(index=False).encode("utf-8"),
            file_name=filename,
            mime="text/csv",
            key=f"download_sql_report_{key}",
        )

    st.success("Advanced SQL Analytics reports loaded successfully.")