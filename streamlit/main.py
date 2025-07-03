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
    "_A minimal ETL interface for importing, previewing, and storing structured data files._"
)
st.markdown("Supported formats: `.csv`, `.xlsx`, `.json`")

# --- Input Field ---
url = st.text_input(
    label="Enter file URL:",
    placeholder="https://example.com/data.csv"
)

# --- File Handling ---
if url:
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

        # Show preview
        st.success(f"`{filename}` downloaded and saved to `data/raw/`")
        st.dataframe(df.head())

    except Exception as e:
        st.error(f"Failed to process file: {e}")
