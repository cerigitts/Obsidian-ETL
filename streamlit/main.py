from urllib.parse import urlparse
from pathlib import Path
import streamlit as st
import pandas as pd
import requests
from io import StringIO, BytesIO

# --- Page Config ---
st.set_page_config(page_title="Obsidian", layout="wide")

# --- Inject Custom CSS ---
st.markdown("""
<style>
    .main {
        background-color: #0e0e0e;
        color: #fafafa;
    }
    h1, h2, h3 {
        color: #F63366;
    }
    div[data-baseweb="select"] > div {
        background-color: #1e1e1e;
        border-radius: 0.5rem;
        border: 1px solid #444;
        padding: 0.25rem;
        color: #fafafa;
    }
    .stSlider > div {
        padding: 0rem 1rem;
    }
    .stMarkdown {
        padding-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

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

    # Identify low-cardinality categorical columns
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    filterable_cols = [col for col in cat_cols if df[col].nunique() < 50]

    # Layout filters in two columns
    col1, col2 = st.columns(2)

    for i, col in enumerate(filterable_cols):
        col_target = col1 if i % 2 == 0 else col2
        with col_target:
            available_options = sorted(df[col].dropna().unique())
            selected = st.multiselect(f"{col}:", available_options, key=col)
            if selected:
                df = df[df[col].isin(selected)]

    # Row limiter
    st.markdown("### 📏 Limit Display")
    row_limit = st.slider("Rows to display", 5, 100, 10)

    # Display filtered results
    st.dataframe(df.head(row_limit), use_container_width=True)

    st.markdown("ℹ️ Numerical and time-series data remains intact, ready for transformation or export.")
