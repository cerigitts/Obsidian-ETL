# streamlit/main.py
import streamlit as st
import pandas as pd
from pathlib import Path
import requests
from io import StringIO

# --- Title ---
st.title("ETL Data Import Tool")

# --- Input: URL ---
url = st.text_input("Enter CSV URL:", "")

# --- Action: Download and Preview ---
if url:
    try:
        st.write("Downloading CSV...")
        response = requests.get(url)
        response.raise_for_status()

        # Parse CSV into DataFrame
        csv_content = StringIO(response.text)
        df = pd.read_csv(csv_content)

        # Display preview
        st.success("File downloaded and parsed successfully.")
        st.dataframe(df.head())

        # Option to save locally
        save_path = Path("data/raw_download.csv")
        df.to_csv(save_path, index=False)
        st.info(f"Saved to {save_path.resolve()}")

    except Exception as e:
        st.error(f"Failed to process file: {e}")
