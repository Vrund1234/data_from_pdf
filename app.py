import streamlit as st
import pandas as pd
import pdfplumber
import re
import tempfile
import os
import streamlit as st
st.set_option("server.maxUploadSize", 1024)  # size in MB (e.g., 1024 MB = 1 GB)

st.set_page_config(page_title="GSEB 10th Result Extractor", layout="wide")

# st.title("📄 Gujarat Board 10th Result Extractor & Ranker")

st.title("Extractor & Ranker")


uploaded_files = st.file_uploader("Upload GSEB PDF Result Files", type="pdf", accept_multiple_files=True)

def extract_data_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    name_match = re.search(r'Student Name\s*:\s*(.+)', text, re.IGNORECASE)
    percentage_match = re.search(r'Percentage\s*:\s*([\d.]+)%', text, re.IGNORECASE)

    if name_match and percentage_match:
        name = name_match.group(1).strip()
        percentage = float(percentage_match.group(1))
        return {"Name": name, "Percentage": percentage}
    else:
        return None

if uploaded_files:
    st.info("⏳ Extracting data from uploaded PDFs...")
    data = []

    for file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(file.read())
            tmp_file_path = tmp_file.name

        result = extract_data_from_pdf(tmp_file_path)
        os.remove(tmp_file_path)

        if result:
            data.append(result)
        else:
            st.warning(f"⚠️ Data could not be extracted from: {file.name}")

    if data:
        df = pd.DataFrame(data)
        df.sort_values(by="Percentage", ascending=False, inplace=True)
        df["Rank"] = range(1, len(df) + 1)

        st.success("✅ Extraction and ranking completed.")
        st.dataframe(df, use_container_width=True)

        # Download CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Ranked CSV",
            data=csv,
            file_name="ranked_results.csv",
            mime="text/csv"
        )
    else:
        st.error("❌ No valid data extracted.")
