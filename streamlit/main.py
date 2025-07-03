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
st.markdown(
    "_A minimal ETL interface for importing, exploring, and preparing structured data files._"
)
st.markdown("Supported formats: `.csv`, `.xlsx`, `.json`")

# --- Input URL ---
url = st.text_input(
    label="Enter file URL:",
    placeholder="https://example.com/data.csv"
)

# Initialize state to hold dataframe
if "df" not in st.session_state:
    st.session_state.df = None

# --- Section 1: Download and Save ---
if url and st.session_state.df is None:
    try:
        st.write("Fetching file...")

        # Parse URL and filename
        parsed_url = urlparse(url)
        filename = Path(parsed_url.path).name
        suffix = filename.split('.')[-1].lower()

        # Prepare storage path
        raw_folder = Path("data/raw")
        raw_folder.mkdir(parents=True, exist_ok=True)
        save_path = raw_folder / filename

        # Download file
        response = requests.get(url)
        response.raise_for_status()

        # Parse based on file type
        if suffix == "csv":
            df = pd.read_csv(StringIO(response.text))
        elif suffix in ("xls", "xlsx"):
            df = pd.read_excel(BytesIO(response.content))
        elif suffix == "json":
            df = pd.read_json(StringIO(response.text))
        else:
            st.error(f"Unsupported file type: `{suffix}`.")
            st.stop()

        # Save to disk
        df.to_csv(save_path, index=False)
        st.success(f"`{filename}` downloaded and saved to `data/raw/`.")

        # Store in session
        st.session_state.df = df

    except Exception as e:
        st.error(f"Failed to process file: {e}")

# --- Section 2: Explore Interface ---
if st.session_state.df is not None:
    df = st.session_state.df

    st.markdown("### 🔍 Explore Imported Data")

    # Column selection
    columns = st.multiselect("Select columns to view", df.columns.tolist(), default=df.columns.tolist())

    # Search input
    search_text = st.text_input("Search by Model or GenModel:")

    # Dropdown filters
    make_filter = st.selectbox("Filter by Make:", ["All"] + sorted(df["Make"].dropna().unique().tolist()))
    fuel_filter = st.selectbox("Filter by Fuel:", ["All"] + sorted(df["Fuel"].dropna().unique().tolist()))
    licence_filter = st.selectbox("Filter by Licence Status:", ["All"] + sorted(df["LicenceStatus"].dropna().unique().tolist()))

    # Apply filters
    filtered_df = df.copy()

    if search_text:
        filtered_df = filtered_df[
            filtered_df["Model"].str.contains(search_text, case=False, na=False) |
            filtered_df["GenModel"].str.contains(search_text, case=False, na=False)
        ]

    if make_filter != "All":
        filtered_df = filtered_df[filtered_df["Make"] == make_filter]

    if fuel_filter != "All":
        filtered_df = filtered_df[filtered_df["Fuel"] == fuel_filter]

    if licence_filter != "All":
        filtered_df = filtered_df[filtered_df["LicenceStatus"] == licence_filter]

    # Row limiter
    row_limit = st.slider("Rows to display", 5, 100, 10)
    st.dataframe(filtered_df[columns].head(row_limit))

    # --- Section 3: Placeholder for Transform ---
    st.markdown("### 🧪 Transform (Coming Soon)")
    st.info("Once filters are applied, this section will allow transformations to be triggered.")
