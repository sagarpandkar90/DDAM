import streamlit as st
import sqlite3
import pandas as pd

# Database and Excel file paths
DB_FILE = "database.db"
EXCEL_FILE = "database.xlsx"


TABLE_NAME = "records"

# Function to connect to SQLite
def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

# Function to create or update table schema
def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            अक्र TEXT UNIQUE,
            मंजुरीधारकाचे_नाव TEXT,
            गट_नंबर TEXT,
            गावाचे_नाव TEXT,
            तालुका TEXT,
            जिल्हा TEXT,
            मंजुरीचा_जावक_क्र_व_दिनांक TEXT,
            मंजुर_क्षेत्र_प्रवाही TEXT,
            मंजुर_क्षेत्र_सुक्ष्म TEXT,
            मंजुर_पिके TEXT,
            पंपाची_मंजूर_एचपी TEXT,
            Mobile_Number TEXT,
            Status TEXT,
            Aadhar_Number TEXT,
            Area TEXT,
            Nominee TEXT
        )
    """)
    conn.commit()
    conn.close()

# Function to import Excel data into SQLite
def import_excel_to_sqlite():
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name="Sheet1", dtype=str)
        conn = get_connection()
        df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)  # Replace old data
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error importing Excel: {e}")
        return False

# Function to load data from SQLite
@st.cache_data
def load_data():
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", conn)
    conn.close()
    return df

# Function to update fields in SQLite
def update_data(record_id, new_mobile, new_status, new_aadhar, new_area, new_nominee):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        UPDATE {TABLE_NAME}
        SET Mobile_Number = ?, Status = ?, Aadhar_Number = ?, Area = ?, Nominee = ?
        WHERE अक्र = ?
    """, (new_mobile, new_status, new_aadhar, new_area, new_nominee, record_id))
    conn.commit()
    conn.close()

# Initialize the database table
create_table()

# Load data
df = load_data()

st.title("DARNA DAM")

# --- SEARCH FUNCTIONALITY ---
st.subheader("Search Record")
search_query = st.text_input("Search By:  अ.क्र  or  Name:")
filtered_df = df[df[ "अ.क्र"].str.contains(search_query, na=False) |
                 df["मंजुरीधारकाचे_नाव"].str.contains(search_query, na=False)] if search_query else df

if not filtered_df.empty:
    st.write("Search Results:")
    st.dataframe(filtered_df[["अक्र", "मंजुरीधारकाचे_नाव", "गट_नंबर", "गावाचे_नाव", "Mobile_Number", "Status", "Aadhar_Number", "Area", "Nominee"]])
else:
    st.warning("No matching records found.")

# --- UPDATE FUNCTIONALITY ---
st.subheader("Edit Mobile Number, Status, Aadhar, Area & Nominee")

if not filtered_df.empty:
    selected_id = st.selectbox("Select अ.क्र (ID) to Edit", filtered_df["अ.क्र"].unique())

    if selected_id:
        row_data = df[df["अ.क्र"] == selected_id].iloc[0]

        # Display Name (Read-only)
        st.write(f"**मंजुरीधारकाचे नाव:** {row_data['मंजुरीधारकाचे_नाव']}")

        # Editable fields
        new_mobile = st.text_input("Mobile Number", row_data["Mobile_Number"])
        new_aadhar = st.text_input("Aadhar Number", row_data["Aadhar_Number"])
        new_area = st.text_input("Area", row_data["Area"])
        new_nominee = st.text_input("Nominee", row_data["Nominee"])

        # Dropdown for Status selection
        status_options = ["नियमित सुरु", "मयत-वारस आहे", "मयत-वारस नाही", "त्या नवाची व्यक्ती मिळाली नाही"]
        new_status = st.selectbox("Status", status_options, 
                                  index=status_options.index(row_data["Status"]) if row_data["Status"] in status_options else 0)

        if st.button("Update"):
            update_data(selected_id, new_mobile, new_status, new_aadhar, new_area, new_nominee)
            st.success("Data updated successfully!")
            st.experimental_rerun()  # Refresh the app

# --- FILTER BY गावाचे नाव ---
st.subheader("Filter by गावाचे नाव")
village_list = df["गावाचे_नाव"].dropna().unique().tolist()
selected_village = st.selectbox("Select गावाचे नाव", ["All"] + village_list)

filtered_df = df[df["गावाचे_नाव"] == selected_village] if selected_village != "All" else df

if not filtered_df.empty:
    st.write("Filtered Records:")
    st.dataframe(filtered_df[["अ.क्र", "मंजुरीधारकाचे_नाव", "गट_नंबर", "गावाचे_नाव", "तालुका", "जिल्हा", 
                              "मंजुरीचा_जावक_क्र_व_दिनांक", "मंजुर_क्षेत्र_प्रवाही", "मंजुर_क्षेत्र_सुक्ष्म",
                              "मंजुर_पिके", "पंपाची_मंजूर_एचपी", "Mobile_Number", "Status", "Aadhar_Number", "Area", "Nominee"]])
else:
    st.warning("No matching records found.")

# --- IMPORT EXCEL BUTTON ---
st.subheader("Import Data from Excel to SQLite")
if st.button("Import Now"):
    success = import_excel_to_sqlite()
    if success:
        st.success("Excel data imported successfully!")
        
