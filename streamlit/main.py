from urllib.parse import urlparse
from pathlib import Path
import streamlit as st
import pandas as pd
import requests
from io import StringIO, BytesIO

# --- Page Config ---
st.set_page_config(page_title="Obsidian", layout="wide")

# --- Interface Header ---
st.title("Obsidian")
st.markdown("_A dynamic ETL interface for importing, exploring, and preparing structured data files._")
st.markdown("Supported formats: `.csv`, `.xlsx`, `.json`")

# --- Input URL ---
url = st.text_input("Enter file URL:", placeholder="https://example.com/data.csv")

# Session state for dataframe
if "df" not in st.session_state:
    st.session_state.df = None

# --- Section 1: Download + Save ---
if url and st.session_state.df is None:
    try:
        st.write("Fetching file...")

        parsed_url = urlparse(url)
        filename = Path(parsed_url.path).name
        suffix = filename.split('.')[-1].lower()

        raw_folder = Path("data/raw")
        raw_folder.mkdir(parents=True, exist_ok=True)
        save_path = raw_folder / filename

        response = requests.get(url)
        response.raise_for_status()

        if suffix == "csv":
            df = pd.read_csv(StringIO(response.text))
        elif suffix in ("xls", "xlsx"):
            df = pd.read_excel(BytesIO(response.content))
        elif suffix == "json":
            df = pd.read_json(StringIO(response.text))
        else:
            st.error(f"Unsupported file type: `{suffix}`.")
            st.stop()

        df.to_csv(save_path, index=False)
        st.success(f"`{filename}` downloaded and saved to `data/raw/`.")
        st.session_state.df = df

    except Exception as e:
        st.error(f"Failed to process file: {e}")

# --- Section 2: Dynamic Filtering ---
if st.session_state.df is not None:
    df = st.session_state.df.copy()

    st.markdown("### 🔍 Filter Your Data")

    # Identify categorical columns (low-cardinality only)
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    filterable_cols = [col for col in cat_cols if df[col].nunique() < 50]

    # Apply filters
    for col in filterable_cols:
        options = ["All"] + sorted(df[col].dropna().unique().tolist())
        selected = st.selectbox(f"Filter by {col}:", options, key=col)
        if selected != "All":
            df = df[df[col] == selected]

    # Row limiter
    row_limit = st.slider("Rows to display", 5, 100, 10)

    # Display filtered results (all columns)
    st.dataframe(df.head(row_limit))

    st.markdown("ℹ️ Numerical data (e.g. time series) is shown untouched and ready for analysis.")
