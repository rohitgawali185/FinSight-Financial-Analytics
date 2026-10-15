
from io import BytesIO
import re

import pandas as pd
import streamlit as st


# ============================================
# FINSIGHT - PROFESSIONAL CSV UPLOAD MODULE
# ============================================

MAX_FILE_SIZE_MB = 50

REQUIRED_COLUMNS = [
    "segment",
    "country",
    "product",
    "sales",
    "profit",
]

NUMERIC_COLUMNS = [
    "units_sold",
    "manufacturing_price",
    "sale_price",
    "gross_sales",
    "discounts",
    "sales",
    "cogs",
    "profit",
]


def normalize_column_name(column):
    """Convert headers to lowercase snake_case."""
    column = str(column).strip().lower()
    column = re.sub(r"[^a-z0-9]+", "_", column)
    return column.strip("_")


def prepare_dataframe(dataframe):
    """Standardize column names and clean basic data types."""
    df = dataframe.copy()

    df.columns = [
        normalize_column_name(column)
        for column in df.columns
    ]

    if df.columns.duplicated().any():
        raise ValueError(
            "Duplicate column names found after standardization. "
            "Please rename the duplicate columns in your CSV."
        )

    missing = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "Required columns missing: "
            + ", ".join(missing)
        )

    if df.empty:
        raise ValueError("The uploaded CSV contains no records.")

    # Convert known numeric columns safely.
    for column in NUMERIC_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column].astype(str).str.replace(",", "", regex=False),
                errors="coerce",
            )

    # Convert date column if present.
    if "date" in df.columns:
        df["date"] = pd.to_datetime(
            df["date"], errors="coerce"
        )

    # Keep category fields consistent.
    for column in ["segment", "country", "product", "discount_band"]:
        if column in df.columns:
            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
            )

    return df


def render_csv_upload(default_df):
    """
    Show the upload panel and return the active dataset.

    The existing dashboard dataset is not overwritten on disk.
    """
    if "finsight_uploaded_df" not in st.session_state:
        st.session_state["finsight_uploaded_df"] = None

    if "finsight_uploaded_filename" not in st.session_state:
        st.session_state["finsight_uploaded_filename"] = None

    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📂 Data Management")
        st.caption("Upload a compatible financial CSV dataset.")

        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=["csv"],
            key="finsight_csv_uploader",
            help="Maximum file size: 50 MB",
        )

        if uploaded_file is not None:
            if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                st.error("File is larger than 50 MB.")
            else:
                try:
                    raw_df = pd.read_csv(
                        BytesIO(uploaded_file.getvalue())
                    )
                    candidate_df = prepare_dataframe(raw_df)

                    # Update the active dataset only after validation.
                    st.session_state["finsight_uploaded_df"] = (
                        candidate_df
                    )
                    st.session_state[
                        "finsight_uploaded_filename"
                    ] = uploaded_file.name

                    st.success(
                        f"Loaded {len(candidate_df):,} records."
                    )

                except (ValueError, pd.errors.ParserError,
                        UnicodeDecodeError, pd.errors.EmptyDataError) as error:
                    st.error(f"CSV validation failed: {error}")
                except Exception as error:
                    st.error(
                        "Could not read this file. "
                        f"Details: {error}"
                    )

        active_upload = st.session_state["finsight_uploaded_df"]

        if active_upload is not None:
            st.caption(
                "Active file: "
                + str(
                    st.session_state["finsight_uploaded_filename"]
                )
            )

            if st.button(
                "↩️ Restore Original Dataset",
                use_container_width=True,
            ):
                st.session_state["finsight_uploaded_df"] = None
                st.session_state["finsight_uploaded_filename"] = None
                st.rerun()

    active_df = st.session_state["finsight_uploaded_df"]

    if active_df is not None:
        return active_df.copy()

    return default_df


def render_data_preview(dataframe):
    """Display upload statistics and a preview."""
    st.markdown("## Data Preview")
    st.caption("Inspect the active dataset before analysis.")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Records", f"{len(dataframe):,}")

    with col2:
        st.metric("Total Columns", f"{len(dataframe.columns):,}")

    with col3:
        st.metric(
            "Duplicate Rows",
            f"{int(dataframe.duplicated().sum()):,}",
        )

    with col4:
        missing_count = int(dataframe.isna().sum().sum())
        st.metric("Missing Values", f"{missing_count:,}")

    with st.expander("View data quality report", expanded=False):
        quality_df = pd.DataFrame({
            "Column": dataframe.columns,
            "Data Type": [
                str(dtype) for dtype in dataframe.dtypes
            ],
            "Missing Values": [
                int(value)
                for value in dataframe.isna().sum().values
            ],
            "Missing %": [
                round(value / max(len(dataframe), 1) * 100, 2)
                for value in dataframe.isna().sum().values
            ],
        })

        st.dataframe(
            quality_df,
            use_container_width=True,
            hide_index=True,
        )

    st.dataframe(
        dataframe.head(20),
        use_container_width=True,
        hide_index=True,
    )

    csv_bytes = dataframe.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Download Active Dataset",
        data=csv_bytes,
        file_name="finsight_active_dataset.csv",
        mime="text/csv",
    )
