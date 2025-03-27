import os
import pandas as pd
import streamlit as st
from io import BytesIO
import urllib.parse

st.set_page_config(page_title="File Renaming Tool", layout="centered")
st.title("🔄 File Renaming Tool")

# Step 1: File Type Selection
st.header("Step 1: Select File Type")
file_type = st.selectbox("Select the file type to rename:", options=["IES", "PDF", "GOS", "All Files"])

# Step 2: Download Template (CSV)
st.header("Step 2: Download CSV Template")

def create_template():
    return pd.DataFrame({
        "Old File Name": ["example_file.ies", "example_file.pdf", "example_file.gos"],
        "IES": ["new_ies_file.ies", "", ""],
        "Photometric_Report": ["", "new_pdf_file.pdf", ""],
        "Gos_Report": ["", "", "new_gos_file.gos"]
    })

template_df = create_template()
template_io = BytesIO()
template_df.to_csv(template_io, index=False)
template_io.seek(0)

st.download_button(
    label="📥 Download Template (CSV)",
    data=template_io,
    file_name="File_Renaming_Template.csv",
    mime="text/csv"
)

# Step 3: Upload Folder Path and CSV File
st.header("Step 3: Upload Folder Path and CSV File")
folder_path = st.text_input("Enter the folder path where the files are located:")

# Clean path in case it's copied as file:///D:/...
if folder_path.startswith("file:///"):
    folder_path = folder_path.replace("file:///", "")
    folder_path = urllib.parse.unquote(folder_path)

uploaded_file = st.file_uploader("Upload the CSV file with renaming details", type=["csv"])

# Renaming Function
def rename_files_from_all(folder_path, df, selected_file_type):
    renamed = []
    not_found = []

    for _, row in df.iterrows():
        old_file = row["Old File Name"]
        ext = os.path.splitext(old_file)[1].lower()
        old_path = os.path.join(folder_path, old_file)

        # Choose correct new name
        if ext == ".ies":
            new_name = row.get("IES", "").strip()
        elif ext == ".pdf":
            new_name = row.get("Photometric_Report", "").strip()
        elif ext == ".gos":
            new_name = row.get("Gos_Report", "").strip()
        else:
            continue

        if not new_name:
            not_found.append(f"⚠️ New name not provided for: {old_file}")
            continue

        new_path = os.path.join(folder_path, new_name)

        try:
            os.rename(old_path, new_path)
            renamed.append(f"✅ {old_file} → {new_name}")
        except FileNotFoundError:
            not_found.append(f"❌ File not found: {old_file}")
        except Exception as e:
            not_found.append(f"⚠️ Error renaming {old_file}: {e}")

    return renamed, not_found

# Step 4: Rename
if st.button("🚀 Rename Files"):
    if not folder_path or not uploaded_file:
        st.error("Please provide both the folder path and the CSV file.")
    else:
        try:
            df = pd.read_csv(uploaded_file)

            required_cols = {"Old File Name", "IES", "Photometric_Report", "Gos_Report"}
            if not required_cols.issubset(df.columns):
                st.error("Template must contain columns: Old File Name, IES, Photometric_Report, Gos_Report")
            else:
                renamed, not_found = rename_files_from_all(folder_path, df, file_type)

                if renamed:
                    st.success("Renamed Files:")
                    for msg in renamed:
                        st.write(msg)
                if not_found:
                    st.warning("Issues Found:")
                    for msg in not_found:
                        st.write(msg)
                if not renamed:
                    st.error("No files were renamed.")
        except Exception as e:
            st.error(f"Error processing file: {e}")
