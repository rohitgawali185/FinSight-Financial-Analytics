
import sqlite3
from pathlib import Path

import pandas as pd

# ==========================================
# FINSIGHT - ADVANCED SQL BUSINESS ANALYSIS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "data" / "database" / "finsight.db"


def run_query(conn, title, query):
    print("\n" + "=" * 75)
    print(title.upper())
    print("=" * 75)

    df = pd.read_sql_query(query, conn)

    if df.empty:
        print("No records found.")
    else:
        print(df.to_string(index=False))

    return df


def main():
    if not DB_FILE.exists():
        print("Database not found!")
        print("Run python create_db.py first.")
        return

    with sqlite3.connect(DB_FILE) as conn:

        # 1. Overall business performance
        overall = run_query(
            conn,
            "1. Overall Financial Performance",
            """
            SELECT
                COUNT(*) AS total_records,
                ROUND(SUM(sales), 2) AS total_sales,
                ROUND(SUM(profit), 2) AS total_profit,
                ROUND(
                    100.0 * SUM(profit) /
                    NULLIF(SUM(sales), 0), 2
                ) AS profit_margin_pct
            FROM financial_data;
            """
        )

        # 2. Country performance
        countries = run_query(
            conn,
            "2. Country-wise Performance",
            """
            SELECT
                country,
                ROUND(SUM(sales), 2) AS total_sales,
                ROUND(SUM(profit), 2) AS total_profit,
                ROUND(
                    100.0 * SUM(profit) /
                    NULLIF(SUM(sales), 0), 2
                ) AS profit_margin_pct
            FROM financial_data
            GROUP BY country
            ORDER BY total_profit DESC;
            """
        )

        # 3. Product profitability
        products = run_query(
            conn,
            "3. Product-wise Profitability",
            """
            SELECT
                product,
                ROUND(SUM(sales), 2) AS total_sales,
                ROUND(SUM(profit), 2) AS total_profit,
                ROUND(
                    100.0 * SUM(profit) /
                    NULLIF(SUM(sales), 0), 2
                ) AS profit_margin_pct
            FROM financial_data
            GROUP BY product
            ORDER BY total_profit DESC;
            """
        )

        # 4. Segment performance
        segments = run_query(
            conn,
            "4. Segment-wise Performance",
            """
            SELECT
                segment,
                ROUND(SUM(sales), 2) AS total_sales,
                ROUND(SUM(profit), 2) AS total_profit,
                ROUND(
                    100.0 * SUM(profit) /
                    NULLIF(SUM(sales), 0), 2
                ) AS profit_margin_pct
            FROM financial_data
            GROUP BY segment
            ORDER BY total_profit DESC;
            """
        )

        # 5. Monthly sales and profit trend
        monthly = run_query(
            conn,
            "5. Monthly Performance",
            """
            SELECT
                strftime('%Y-%m', date) AS sales_month,
                ROUND(SUM(sales), 2) AS total_sales,
                ROUND(SUM(profit), 2) AS total_profit
            FROM financial_data
            WHERE date IS NOT NULL
            GROUP BY strftime('%Y-%m', date)
            ORDER BY sales_month;
            """
        )

        # 6. Discount band analysis
        discounts = run_query(
            conn,
            "6. Discount Band Analysis",
            """
            SELECT
                COALESCE(discount_band, 'Unknown') AS discount_band,
                COUNT(*) AS record_count,
                ROUND(SUM(sales), 2) AS total_sales,
                ROUND(SUM(profit), 2) AS total_profit
            FROM financial_data
            GROUP BY COALESCE(discount_band, 'Unknown')
            ORDER BY total_profit DESC;
            """
        )

        # 7. Top 10 highest-profit records
        top_records = run_query(
            conn,
            "7. Top 10 Highest-profit Records",
            """
            SELECT
                date, country, product, segment, sales, profit
            FROM financial_data
            WHERE profit IS NOT NULL
            ORDER BY profit DESC
            LIMIT 10;
            """
        )

        # 8. Data quality check
        quality = run_query(
            conn,
            "8. Data Quality Check",
            """
            SELECT
                COUNT(*) AS total_records,
                SUM(CASE WHEN sales IS NULL
                    THEN 1 ELSE 0 END) AS missing_sales,
                SUM(CASE WHEN profit IS NULL
                    THEN 1 ELSE 0 END) AS missing_profit,
                SUM(CASE WHEN date IS NULL
                    THEN 1 ELSE 0 END) AS missing_dates
            FROM financial_data;
            """
        )

        # ======================================
        # AUTOMATIC BUSINESS INSIGHTS
        # ======================================
        print("\n" + "=" * 75)
        print("9. AUTOMATIC BUSINESS INSIGHTS")
        print("=" * 75)

        if not overall.empty:
            row = overall.iloc[0]
            print(f"Total records: {int(row['total_records']):,}")
            print(f"Total sales: {row['total_sales']:,.2f}")
            print(f"Total profit: {row['total_profit']:,.2f}")
            print(f"Profit margin: {row['profit_margin_pct']:.2f}%")

        if not countries.empty:
            best_country = countries.iloc[0]
            print(
                "\nHighest-profit country:",
                best_country["country"],
                "| Profit:",
                f"{best_country['total_profit']:,.2f}"
            )

        if not products.empty:
            best_product = products.iloc[0]
            print(
                "Highest-profit product:",
                best_product["product"],
                "| Profit:",
                f"{best_product['total_profit']:,.2f}"
            )

        if not segments.empty:
            best_segment = segments.iloc[0]
            print(
                "Highest-profit segment:",
                best_segment["segment"],
                "| Profit:",
                f"{best_segment['total_profit']:,.2f}"
            )

        if not monthly.empty:
            best_month = monthly.loc[
                monthly["total_sales"].idxmax()
            ]
            print(
                "Highest-sales month:",
                best_month["sales_month"],
                "| Sales:",
                f"{best_month['total_sales']:,.2f}"
            )

        # ======================================
        # EXPORT RESULTS TO CSV
        # ======================================
        output_dir = BASE_DIR / "reports" / "sql_analysis"
        output_dir.mkdir(parents=True, exist_ok=True)

        results = {
            "overall_performance": overall,
            "country_performance": countries,
            "product_profitability": products,
            "segment_performance": segments,
            "monthly_performance": monthly,
            "discount_analysis": discounts,
            "top_profit_records": top_records,
            "data_quality": quality,
        }

        for name, df in results.items():
            df.to_csv(
                output_dir / f"{name}.csv",
                index=False
            )

        print("\n" + "=" * 75)
        print("SQL ANALYSIS COMPLETED SUCCESSFULLY!")
        print("Reports saved to:", output_dir)
        print("=" * 75)


if __name__ == "__main__":
    main()

