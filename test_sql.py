
import sqlite3
from pathlib import Path
import pandas as pd

DB_FILE = (
    Path(__file__).resolve().parent
    / "data" / "database" / "finsight.db"
)

if not DB_FILE.exists():
    raise FileNotFoundError(
        "Database not found. Run python create_db.py first."
    )

queries = {
    "Country Performance": """
        SELECT country,
               ROUND(SUM(sales), 2) AS total_sales,
               ROUND(SUM(profit), 2) AS total_profit
        FROM financial_data
        GROUP BY country
        ORDER BY total_sales DESC
    """,

    "Product Performance": """
        SELECT product,
               ROUND(SUM(sales), 2) AS total_sales,
               ROUND(SUM(profit), 2) AS total_profit
        FROM financial_data
        GROUP BY product
        ORDER BY total_profit DESC
    """,

    "Monthly Performance": """
        SELECT strftime('%Y-%m', date) AS month,
               ROUND(SUM(sales), 2) AS total_sales,
               ROUND(SUM(profit), 2) AS total_profit
        FROM financial_data
        WHERE date IS NOT NULL
        GROUP BY strftime('%Y-%m', date)
        ORDER BY month
    """
}

with sqlite3.connect(DB_FILE) as conn:
    for title, query in queries.items():
        print("\n" + "=" * 55)
        print(title.upper())
        print("=" * 55)

        result = pd.read_sql_query(query, conn)
        print(result.to_string(index=False))

print("\nALL SQL TESTS COMPLETED!")
