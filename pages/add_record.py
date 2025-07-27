import streamlit as st
import pandas as pd
from io import BytesIO
from xlsxwriter import Workbook


EXCEL_FILE = "form_b_database.xlsx"
SHEET_NAME = "Sheet1"

# Load existing data or create empty DataFrame
@st.cache_data
def load_data():
    try:
        return pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME, dtype=str)
    except FileNotFoundError:
        return pd.DataFrame(columns=[
            "मंजुरीधारकाचे नाव", "गावाचे नाव", "भुमापन क्रमांक",
            "एकुण क्षेत्रफळ", "मंजुरीचे क्षेत्र", "मंजुर पिके"
        ])

def save_data(df):
    with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="w") as writer:
        df.to_excel(writer, index=False, sheet_name=SHEET_NAME)

# UI
st.title("📄 नवीन मंजुरी फॉर्म")

df = load_data()

with st.form("new_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("मंजुरीधारकाचे नाव")
        village = st.text_input("गावाचे नाव")
        survey_no = st.text_input("भुमापन क्रमांक")
    with col2:
        total_area = st.text_input("एकुण क्षेत्रफळ")
        approved_area = st.text_input("मंजुरीचे क्षेत्र")
        crop = st.text_input("मंजुर पिके")

    submitted = st.form_submit_button("✅ सबमिट करा")

    if submitted:
        new_entry = {
            "मंजुरीधारकाचे नाव": name,
            "गावाचे नाव": village,
            "भुमापन क्रमांक": survey_no,
            "एकुण क्षेत्रफळ": total_area,
            "मंजुरीचे क्षेत्र": approved_area,
            "मंजुर पिके": crop
        }
        df = df._append(new_entry, ignore_index=True)
        save_data(df)
        st.success("रेकॉर्ड सेव्ह झाला!")

# Show existing records
if not df.empty:
    st.subheader("📋 सेव्ह झालेले रेकॉर्ड:")
    st.dataframe(df)

    # Download Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=SHEET_NAME)
    output.seek(0)

    st.download_button(
        label="📥 एक्सेल डाउनलोड करा",
        data=output,
        file_name="form_b_records.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
