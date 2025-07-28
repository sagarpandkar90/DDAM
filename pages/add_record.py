
import time
import streamlit as st
import pandas as pd
from io import BytesIO
import os

EXCEL_FILE = "form_b_database.xlsx"
SHEET_NAME = "Sheet1"

# 🎯 Manually defined village list
MANUAL_VILLAGE_LIST = ["नांदगाव बु.", "लक्ष्मीनगर", "वाघेरे", "मालुंजे", "समनेरे", "सोमज", "मोगरे", "मुंढेगाव", "धामणगाव", "खंबाळे", "बेळगाव त-हाळे", "धामणी", "साकुर", "घोटी खुर्द", "पिंपळगाव मोर", "देवळे", "दौंडत", "उभाडे", "उंबरकोन", "कृष्णानगर", "माणिकखांब"]

VILLAGE_OPTIONS = MANUAL_VILLAGE_LIST + ["🔼 नवीन गाव जोडा..."]

# 📥 Load or create Excel file
def load_data():
    if os.path.exists(EXCEL_FILE):
        return pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME, dtype=str)
    else:
        return pd.DataFrame(columns=[
            "मंजुरीधारकाचे नाव", "गावाचे नाव", "भुमापन क्रमांक",
            "एकुण क्षेत्रफळ", "मंजुरीचे क्षेत्र", "पीक"
        ])

def save_data(df):
    with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="w") as writer:
        df.to_excel(writer, index=False, sheet_name=SHEET_NAME)

# 🌟 Title
st.title("📄 नवीन मंजुरी फॉर्म")

df = load_data()

# ========== Add Form ==========
with st.form(key="add_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("🧑 मंजुरीधारकाचे नाव")
        selected_village = st.selectbox("🏡 गावाचे नाव", VILLAGE_OPTIONS)
        if selected_village == "🔼 नवीन गाव जोडा...":
            village = st.text_input("➕ नवीन गावाचे नाव")
        else:
            village = selected_village
        survey_no = st.text_input("🧾 भुमापन क्रमांक")

    with col2:
        total_area = st.text_input("🌾 एकुण क्षेत्रफळ")
        approved_area = st.text_input("✅ मंजुरीचे क्षेत्र")
        crop = st.text_input("🌱 मंजुर पिके")

    submitted = st.form_submit_button("💾 सबमिट करा")

    if submitted:
        if not name.strip() or not village.strip():
            st.warning("कृपया नाव व गाव माहिती भरा.")
        else:
            new_record = {
                "मंजुरीधारकाचे नाव": name.strip(),
                "गावाचे नाव": village.strip(),
                "भुमापन क्रमांक": survey_no.strip(),
                "एकुण क्षेत्रफळ": total_area.strip(),
                "मंजुरीचे क्षेत्र": approved_area.strip(),
                "पीक": crop.strip()
            }
            updated_df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
            save_data(updated_df)
            st.success(f"✅ रेकॉर्ड सेव्ह झाला: {name}")
            time.sleep(2)
            st.rerun()

# ========== Display Saved Records ==========
df = load_data()
if not df.empty:
    st.subheader("📋 सेव्ह झालेले रेकॉर्ड:")
    st.dataframe(df, use_container_width=True)

    with st.expander("🗑️ रेकॉर्ड डिलीट करा."):

        max_index = len(df) - 1
        row_to_delete = st.number_input("❌ डिलीट करायचा रेकॉर्ड क्रमांक लिहा:", min_value=0, max_value=max_index,
                                        step=1)

        if st.button("✅ रेकॉर्ड डिलीट करा"):
            if 0 <= row_to_delete <= max_index:
                df = df.drop(index=row_to_delete).reset_index(drop=True)
                save_data(df)
                st.success(f"✅ क्रमांक {row_to_delete} असलेला रेकॉर्ड डिलीट झाला.")
                st.rerun()
            else:
                st.warning("❌ अवैध क्रमांक.")

    # ========== Download by Village ==========
    with st.expander("📥 गावानुसार रेकॉर्ड डाउनलोड करा"):
        available_villages = sorted(df["गावाचे नाव"].dropna().unique())
        selected_village = st.selectbox("🏘️ गाव निवडा:", available_villages)

        filtered_df = df[df["गावाचे नाव"] == selected_village]
        if not filtered_df.empty:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                filtered_df.to_excel(writer, index=False, sheet_name="Records")
            output.seek(0)

            st.download_button(
                label=f"⬇️ {selected_village} गावाचे रेकॉर्ड डाउनलोड करा",
                data=output,
                file_name=f"{selected_village}_records.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
