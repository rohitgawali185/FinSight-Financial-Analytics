
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

DB_FILE = Path("data/database/finsight.db")


def get_connection():
    """Create a connection to the FinSight SQLite database."""
    if not DB_FILE.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_FILE.resolve()}"
        )

    return sqlite3.connect(str(DB_FILE))


@st.cache_data(ttl=60)
def get_sql_summary():
    """Read overall financial KPIs from SQLite."""
    query = """
        SELECT
            COUNT(*) AS total_records,
            COALESCE(SUM(sales), 0) AS total_sales,
            COALESCE(SUM(profit), 0) AS total_profit
        FROM financial_data
    """

    with get_connection() as connection:
        result = pd.read_sql_query(query, connection)

    total_sales = float(result.loc[0, "total_sales"])
    total_profit = float(result.loc[0, "total_profit"])
    total_records = int(result.loc[0, "total_records"])

    profit_margin = (
        total_profit / total_sales * 100
        if total_sales else 0.0
    )

    return {
        "total_records": total_records,
        "total_sales": total_sales,
        "total_profit": total_profit,
        "profit_margin": profit_margin,
    }


def get_country_summary():
    """Return country-level sales and profit."""
    query = """
        SELECT
            country,
            SUM(sales) AS total_sales,
            SUM(profit) AS total_profit
        FROM financial_data
        WHERE country IS NOT NULL
        GROUP BY country
        ORDER BY total_sales DESC
    """

    with get_connection() as connection:
        return pd.read_sql_query(query, connection)


def run_custom_query(query):
    """Execute read-only SQL queries for analysis."""
    cleaned_query = query.strip().rstrip(";")

    if not cleaned_query:
        raise ValueError("Please enter a SQL query.")

    if not cleaned_query.lower().startswith("select"):
        raise ValueError("Only SELECT queries are allowed.")

    with get_connection() as connection:
        connection.execute("PRAGMA query_only = ON")
        return pd.read_sql_query(cleaned_query, connection)
