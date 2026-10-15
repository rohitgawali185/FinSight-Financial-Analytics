
import sqlite3
from pathlib import Path
from datetime import datetime

import pandas as pd

# ==========================================
# FINSIGHT - BUSINESS INSIGHTS REPORT
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "database" / "finsight.db"

REPORT_DIR = BASE_DIR / "reports" / "business_insights"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

if not DB_PATH.exists():
    raise FileNotFoundError(
        f"Database not found: {DB_PATH}\n"
        "Please check your project folder and database path."
    )


def read_sql(query):
    """Execute a SQL query and return its result as a DataFrame."""
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn)


def save_report(df, filename):
    """Save analysis results to a CSV file."""
    path = REPORT_DIR / filename
    df.to_csv(path, index=False)
    print(f"Saved: {path.name}")


# ==========================================
# 1. LOAD DATA
# ==========================================

df = read_sql("SELECT * FROM financial_data")

if df.empty:
    raise ValueError("The financial_data table is empty.")

required = {
    "sales", "profit", "country",
    "product", "segment", "discount_band"
}

missing = required - set(df.columns)

if missing:
    raise ValueError(
        f"Missing required columns: {sorted(missing)}\n"
        f"Available columns: {list(df.columns)}"
    )

for col in ["sales", "profit"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=["sales", "profit"])

if df.empty:
    raise ValueError("No valid sales and profit records were found.")

print("\n" + "=" * 55)
print("FINSIGHT | BUSINESS INSIGHTS REPORT")
print("=" * 55)

# ==========================================
# 2. OVERALL PERFORMANCE
# ==========================================

total_records = len(df)
total_sales = df["sales"].sum()
total_profit = df["profit"].sum()

profit_margin = (
    total_profit / total_sales * 100
    if total_sales else 0
)

overall = pd.DataFrame([{
    "Total Records": total_records,
    "Total Sales": round(total_sales, 2),
    "Total Profit": round(total_profit, 2),
    "Profit Margin (%)": round(profit_margin, 2)
}])

save_report(overall, "overall_performance.csv")

print("\n1. OVERALL PERFORMANCE")
print(overall.to_string(index=False))


# ==========================================
# 3. COUNTRY ANALYSIS
# ==========================================

country_df = (
    df.groupby("country", dropna=False)
    .agg(
        total_sales=("sales", "sum"),
        total_profit=("profit", "sum"),
        records=("profit", "size")
    )
    .reset_index()
)

country_df["profit_margin_pct"] = (
    country_df["total_profit"]
    .div(country_df["total_sales"].replace(0, float("nan")))
    .mul(100)
    .fillna(0)
)

country_df = country_df.sort_values(
    "total_profit", ascending=False
)

save_report(country_df, "country_analysis.csv")

print("\n2. COUNTRY PERFORMANCE")
print(country_df.round(2).to_string(index=False))


# ==========================================
# 4. PRODUCT ANALYSIS
# ==========================================

product_df = (
    df.groupby("product", dropna=False)
    .agg(
        total_sales=("sales", "sum"),
        total_profit=("profit", "sum"),
        records=("profit", "size")
    )
    .reset_index()
)

product_df["profit_margin_pct"] = (
    product_df["total_profit"]
    .div(product_df["total_sales"].replace(0, float("nan")))
    .mul(100)
    .fillna(0)
)

product_df = product_df.sort_values(
    "total_profit", ascending=False
)

save_report(product_df, "product_analysis.csv")

print("\n3. PRODUCT PERFORMANCE")
print(product_df.round(2).to_string(index=False))


# ==========================================
# 5. SEGMENT ANALYSIS
# ==========================================

segment_df = (
    df.groupby("segment", dropna=False)
    .agg(
        total_sales=("sales", "sum"),
        total_profit=("profit", "sum"),
        records=("profit", "size")
    )
    .reset_index()
)

segment_df["profit_margin_pct"] = (
    segment_df["total_profit"]
    .div(segment_df["total_sales"].replace(0, float("nan")))
    .mul(100)
    .fillna(0)
)

segment_df = segment_df.sort_values(
    "total_profit", ascending=False
)

save_report(segment_df, "segment_analysis.csv")

print("\n4. SEGMENT PERFORMANCE")
print(segment_df.round(2).to_string(index=False))


# ==========================================
# 6. DISCOUNT ANALYSIS
# ==========================================

discount_df = (
    df.groupby("discount_band", dropna=False)
    .agg(
        total_sales=("sales", "sum"),
        total_profit=("profit", "sum"),
        records=("profit", "size")
    )
    .reset_index()
)

discount_df["profit_margin_pct"] = (
    discount_df["total_profit"]
    .div(discount_df["total_sales"].replace(0, float("nan")))
    .mul(100)
    .fillna(0)
)

save_report(discount_df, "discount_analysis.csv")

print("\n5. DISCOUNT PERFORMANCE")
print(discount_df.round(2).to_string(index=False))


# ==========================================
# 7. AUTOMATIC BUSINESS INSIGHTS
# ==========================================

best_country = country_df.iloc[0]
best_product = product_df.iloc[0]
best_segment = segment_df.iloc[0]

worst_segment = segment_df.iloc[
    segment_df["total_profit"].argmin()
]

loss_segments = segment_df[
    segment_df["total_profit"] < 0
]

highest_margin_product = product_df.iloc[
    product_df["profit_margin_pct"].argmax()
]

insights = [
    {
        "Insight": "Highest total profit country",
        "Finding": str(best_country["country"]),
        "Value": round(float(best_country["total_profit"]), 2),
        "Recommendation":
            "Study its product mix, customer demand and sales strategy."
    },
    {
        "Insight": "Highest total profit product",
        "Finding": str(best_product["product"]),
        "Value": round(float(best_product["total_profit"]), 2),
        "Recommendation":
            "Review demand and availability before planning expansion."
    },
    {
        "Insight": "Highest profit segment",
        "Finding": str(best_segment["segment"]),
        "Value": round(float(best_segment["total_profit"]), 2),
        "Recommendation":
            "Understand what drives performance and whether it can be sustained."
    },
    {
        "Insight": "Lowest profit segment",
        "Finding": str(worst_segment["segment"]),
        "Value": round(float(worst_segment["total_profit"]), 2),
        "Recommendation":
            "Investigate pricing, costs, discounts and sales mix."
    },
    {
        "Insight": "Highest product profit margin",
        "Finding": str(highest_margin_product["product"]),
        "Value": round(
            float(highest_margin_product["profit_margin_pct"]), 2
        ),
        "Recommendation":
            "Check whether the margin remains strong across markets and segments."
    }
]

insights_df = pd.DataFrame(insights)
save_report(insights_df, "business_insights.csv")

print("\n6. KEY BUSINESS INSIGHTS")

for number, item in enumerate(insights, start=1):
    print(f"\n{number}. {item['Insight']}")
    print(f"   Finding: {item['Finding']}")
    print(f"   Value: {item['Value']}")
    print(f"   Recommendation: {item['Recommendation']}")

if not loss_segments.empty:
    print("\nWARNING: SEGMENTS WITH NEGATIVE TOTAL PROFIT")

    for _, row in loss_segments.iterrows():
        print(
            f"- {row['segment']}: "
            f"{row['total_profit']:,.2f}"
        )


# ==========================================
# 8. CREATE A MARKDOWN REPORT
# ==========================================

report_path = REPORT_DIR / "business_insights_report.md"

lines = [
    "# FinSight — Business Insights Report",
    "",
    f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    "",
    "## Executive Summary",
    "",
    f"- Valid records analysed: {total_records:,}",
    f"- Total sales: {total_sales:,.2f}",
    f"- Total profit: {total_profit:,.2f}",
    f"- Overall profit margin: {profit_margin:.2f}%",
    "",
    "## Key Findings",
    ""
]

for item in insights:
    lines.extend([
        f"### {item['Insight']}",
        "",
        f"- Finding: {item['Finding']}",
        f"- Value: {item['Value']:,.2f}",
        f"- Recommendation: {item['Recommendation']}",
        ""
    ])

lines.extend([
    "## Country Performance",
    "",
    country_df.round(2).to_markdown(index=False),
    "",
    "## Product Performance",
    "",
    product_df.round(2).to_markdown(index=False),
    "",
    "## Segment Performance",
    "",
    segment_df.round(2).to_markdown(index=False),
    "",
    "## Discount Performance",
    "",
    discount_df.round(2).to_markdown(index=False),
    "",
    "## Business Recommendations",
    "",
    "1. Investigate segments with negative total profit.",
    "2. Compare sales growth with profit margin before expanding a product.",
    "3. Review discount performance alongside sales volume and profitability.",
    "4. Compare country performance before allocating sales resources.",
    "5. Validate recommendations against time trends and operational costs.",
    "",
    "---",
    "Generated by FinSight Financial Performance Analytics Platform."
])

report_path.write_text("\n".join(lines), encoding="utf-8")

print("\n" + "=" * 55)
print("REPORT GENERATION COMPLETED")
print("=" * 55)
print(f"Report folder: {REPORT_DIR}")
print(f"Main report: {report_path.name}")
print("\nNext: Open the report folder and review the generated files.")
