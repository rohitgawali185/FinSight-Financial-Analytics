
import pandas as pd
import numpy as np
from pathlib import Path

# ==========================================
# FINSIGHT - FINANCIAL DATA CLEANING
# ==========================================

INPUT_FILE = Path("data/raw/Financial Sample.xlsx")
OUTPUT_DIR = Path("data/processed")
OUTPUT_FILE = OUTPUT_DIR / "cleaned_financial_data.csv"

print("=" * 55)
print("       FINSIGHT FINANCIAL DATA ANALYSIS")
print("=" * 55)

# 1. Check dataset
if not INPUT_FILE.exists():
    print("ERROR: Dataset not found!")
    print("Check the file path:", INPUT_FILE)
    raise SystemExit

# 2. Load data
df = pd.read_excel(INPUT_FILE)

print("\n1. ORIGINAL DATA")
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

# 3. Clean column names
df.columns = (
    df.columns.astype(str)
    .str.strip()
    .str.lower()
    .str.replace(r"[^a-z0-9]+", "_", regex=True)
    .str.strip("_")
)

# 4. Remove completely empty rows
df = df.dropna(how="all").copy()

# 5. Remove exact duplicate records
duplicates = int(df.duplicated().sum())
df = df.drop_duplicates().copy()

print("\n2. DATA QUALITY")
print("Exact duplicate rows removed:", duplicates)

# 6. Convert date column
if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

# 7. Convert numeric columns
numeric_candidates = [
    "sales", "profit", "units_sold",
    "gross_sales", "discounts", "cogs",
    "manufacturing_price", "sale_price"
]

for column in numeric_candidates:
    if column in df.columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

# 8. Check missing values
print("\n3. MISSING VALUES")
missing = df.isna().sum()
print(missing[missing > 0] if missing.any() else "No missing values found.")

# 9. Calculate profit margin where possible
if "sales" in df.columns and "profit" in df.columns:
    df["profit_margin_pct"] = np.where(
        df["sales"] != 0,
        (df["profit"] / df["sales"]) * 100,
        np.nan
    )

# 10. Save cleaned dataset
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_FILE, index=False, date_format="%Y-%m-%d")

print("\n4. FINANCIAL SUMMARY")

if "sales" in df.columns:
    print(f"Total Sales: {df['sales'].sum():,.2f}")

if "profit" in df.columns:
    print(f"Total Profit: {df['profit'].sum():,.2f}")

if "profit_margin_pct" in df.columns:
    valid_sales = df["sales"].sum()
    if valid_sales != 0:
        overall_margin = df["profit"].sum() / valid_sales * 100
        print(f"Overall Profit Margin: {overall_margin:.2f}%")

print("\n5. FINAL DATASET")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("Saved to:", OUTPUT_FILE)
print("\nDATA CLEANING COMPLETED!")
