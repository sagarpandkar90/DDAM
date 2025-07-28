import streamlit as st
import pandas as pd
from io import BytesIO
import xlsxwriter
import os

EXCEL_FILE = "form_b_database.xlsx"
SHEET_NAME = "Sheet1"

# Available villages (you can manually update this list)
village_options = ["पिंपळगांव", "धोंडगाव", "कुसुमे", "नवीन गाव जोडा..."]

# Load or initialize data
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

st.title("📄 नवीन मंजुरी फॉर्म")

df = load_data()

# Form
with st.form("new_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("मंजुरीधारकाचे नाव")

        selected_village = st.selectbox("गावाचे नाव", village_options)
        if selected_village == "नवीन गाव जोडा...":
            village = st.text_input("नवीन गावाचे नाव")
        else:
            village = selected_village

        survey_no = st.text_input("भुमापन क्रमांक")
    with col2:
        total_area = st.text_input("एकुण क्षेत्रफळ")
        approved_area = st.text_input("मंजुरीचे क्षेत्र")
        crop = st.text_input("मंजुर पिके")

    submitted = st.form_submit_button("✅ सबमिट करा")

    if submitted:
        if not name or not village:
            st.warning("कृपया सर्व माहिती भरा.")
        else:
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

# Record display with delete
if not df.empty:
    st.subheader("📋 सेव्ह झालेले रेकॉर्ड:")
    selected_village_filter = st.selectbox("गाव निवडा (डाउनलोडसाठी):", sorted(df["गावाचे नाव"].unique()))
    filtered_df = df[df["गावाचे नाव"] == selected_village_filter]
    st.dataframe(filtered_df, use_container_width=True)

    # Delete Record
    delete_index = st.number_input("डिलीट करायचा क्रमांक (0 पासून):", min_value=0, max_value=len(df)-1, step=1)
    if st.button("🗑️ डिलीट करा"):
        df = df.drop(index=delete_index).reset_index(drop=True)
        save_data(df)
        st.success("रेकॉर्ड डिलीट झाला.")
        st.rerun()

    # Download button for selected village
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name=SHEET_NAME)
    output.seek(0)

    st.download_button(
        label=f"📥 '{selected_village_filter}' गावाचा एक्सेल डाउनलोड करा",
        data=output,
        file_name=f"{selected_village_filter}_records.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
