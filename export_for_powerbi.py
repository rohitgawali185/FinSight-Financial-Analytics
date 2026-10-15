
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "data" / "database" / "finsight.db"
OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "powerbi_financial_data.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

if not DB_PATH.exists():
    raise FileNotFoundError(f"Database not found: {DB_PATH}")

with sqlite3.connect(DB_PATH) as conn:
    df = __import__("pandas").read_sql_query(
        "SELECT * FROM financial_data", conn
    )

if df.empty:
    raise ValueError("financial_data table is empty.")

df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print("Power BI export completed successfully!")
print(f"Rows exported: {len(df)}")
print(f"Columns exported: {len(df.columns)}")
print(f"CSV location: {OUTPUT_FILE}")
