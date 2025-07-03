from urllib.parse import urlparse
from pathlib import Path
import streamlit as st
import pandas as pd
import requests
from io import StringIO, BytesIO

# --- Page Config ---
st.set_page_config(page_title="Obsidian", layout="wide")

# --- Inject Custom CSS for Dark Slate Theme ---
st.markdown("""
<style>
    .main {
        background-color: #0e0e0e;
        color: #e0e0e0;
        font-family: 'Rubik', sans-serif !important;
    }
    h1, h2, h3 {
        color: #bbbbbb;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    div[data-baseweb="select"] > div, .stMultiSelect > div {
        background-color: #1a1a1a !important;
        border: 1px solid #2a2a2a !important;
        border-radius: 6px !important;
        color: #e0e0e0 !important;
        padding: 6px 8px !important;
        max-width: 100%;
    }
    .stMultiSelect div[data-baseweb="tag"] {
        background-color: #555555 !important;
        color: #cccccc !important;
        font-weight: 500;
        border-radius: 4px;
    }
    [data-testid="stSlider"] > div {
        background: #333 !important;
    }
    [data-testid="stSlider"] .stSlider > div[role="slider"] {
        background: #666666 !important;
    }
    .stDataFrame {
        background-color: #111 !important;
        border: 1px solid #333 !important;
    }
    /* URL input styling */
    div[data-baseweb="input"] > div > input {
        background-color: #1a1a1a !important;
        border: 1px solid #2a2a2a !important;
        border-radius: 6px !important;
        color: #e0e0e0 !important;
        padding: 6px 8px !important;
        font-family: 'Rubik', sans-serif !important;
        max-width: 320px !important;
        width: 100%;
    }
    div[data-baseweb="input"] > div > input::placeholder {
        color: #666666 !important;
    }
    div[data-baseweb="input"] > div > input:focus {
        border-color: #888888 !important;
        outline: none !important;
        box-shadow: 0 0 5px #888888 !important;
    }
    /* Multiselect box fix */
    .stMultiSelect > div {
        max-width: 320px !important;
        min-width: 320px !important;
        max-height: 5.5rem;
        overflow-y: auto !important;
        overflow-x: hidden !important;
        white-space: normal !important;
        word-wrap: break-word !important;
    }
    .stMultiSelect div[data-baseweb="tag"] {
        max-width: 85%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .stMultiSelect > div::-webkit-scrollbar {
        width: 6px;
    }
    .stMultiSelect > div::-webkit-scrollbar-thumb {
        background-color: #555555;
        border-radius: 3px;
    }
</style>
""", unsafe_allow_html=True)

# --- Interface Header ---
st.title("Obsidian")
st.markdown("_From raw input to structured insight—Obsidian filters, shapes, and readies your data for what comes next._")
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
    st.caption("**Note:** If no values are selected in a filter, all values will be included by default.")

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
