
import sqlite3
from pathlib import Path
import pandas as pd

# ==========================================
# FINSIGHT - SQL DATABASE SETUP
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

CSV_FILE = BASE_DIR / "data" / "processed" / "cleaned_financial_data.csv"
DB_DIR = BASE_DIR / "data" / "database"
DB_FILE = DB_DIR / "finsight.db"

TABLE_NAME = "financial_data"

print("=" * 55)
print("FINSIGHT | SQLITE DATABASE SETUP")
print("=" * 55)

# 1. Check CSV
if not CSV_FILE.exists():
    raise FileNotFoundError(
        f"Cleaned CSV not found: {CSV_FILE}\n"
        "Run python clean_data.py first."
    )

# 2. Read CSV
df = pd.read_csv(CSV_FILE)

if df.empty:
    raise ValueError("The cleaned dataset contains no records.")

# 3. Prepare database folder
DB_DIR.mkdir(parents=True, exist_ok=True)

# 4. Connect to SQLite
with sqlite3.connect(DB_FILE) as conn:

    # Import CSV data into SQLite.
    # This replaces the table when you rerun this setup script.
    df.to_sql(
        TABLE_NAME,
        conn,
        if_exists="replace",
        index=False
    )

    # Create useful indexes if these columns exist.
    columns = set(df.columns)

    if "date" in columns:
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_financial_date "
            "ON financial_data(date)"
        )

    if "country" in columns:
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_financial_country "
            "ON financial_data(country)"
        )

    if "product" in columns:
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_financial_product "
            "ON financial_data(product)"
        )

    # 5. Verify imported data
    row_count = conn.execute(
        "SELECT COUNT(*) FROM financial_data"
    ).fetchone()[0]

    table_info = conn.execute(
        "PRAGMA table_info(financial_data)"
    ).fetchall()

    print("\nDATABASE CREATED SUCCESSFULLY")
    print("-" * 40)
    print("Database:", DB_FILE)
    print("Table:", TABLE_NAME)
    print("Rows imported:", row_count)

    print("\nTABLE COLUMNS:")
    for column in table_info:
        print(f"- {column[1]} ({column[2]})")

    # 6. First SQL test
    result = conn.execute("""
        SELECT
            ROUND(SUM(sales), 2),
            ROUND(SUM(profit), 2),
            ROUND(
                100.0 * SUM(profit) / NULLIF(SUM(sales), 0),
                2
            )
        FROM financial_data
    """).fetchone()

    print("\nFINANCIAL SUMMARY FROM SQL")
    print("Total Sales:", result[0])
    print("Total Profit:", result[1])
    print("Profit Margin (%):", result[2])

print("\nSQL SETUP COMPLETED!")
