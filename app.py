import streamlit as st
import pandas as pd

# File path
EXCEL_FILE = "database.xlsx"
SHEET_NAME = "Sheet1"

st.page_link("pages/add_record.py", label="➕ नवीन मंजुरी फॉर्म भरा", icon="📝")


# Load Excel data
@st.cache_data
def load_data():
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME, dtype=str)
    except FileNotFoundError:
        st.error("Database file not found!")
        return pd.DataFrame()
    return df

# Save updated data back to Excel
def save_data(df):
    with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="w") as writer:
        df.to_excel(writer, sheet_name=SHEET_NAME, index=False)

# Load data
df = load_data()

st.title("DARNA DAM")

# --- SEARCH FUNCTIONALITY ---
st.subheader("Search Record")
search_query = st.text_input("Search By:  अ.क्र  or  Name:")
filtered_df = df[
    df["अ.क्र"].str.contains(search_query, na=False) |
    df["मंजुरीधारकाचे नाव"].str.contains(search_query, na=False)
] if search_query else df

# Show the filtered results
if not filtered_df.empty:
    st.write("Search Results:")
    st.dataframe(filtered_df[
        ["अ.क्र", "मंजुरीधारकाचे नाव", "गट नंबर", "गावाचे नाव", "Mobile Number", "Status", "तालुका", "जिल्हा",
         "मंजुरीचा जावक क्र. व दिनांक", "मंजुर क्षेत्र (हेक्टर)   प्रवाही सिंचना साठी",
         "मंजुर क्षेत्र (हेक्टर) सुक्ष्म सिंचना साठी", "मंजुर पिके",
         "पंपाची मंजूर अश्वशक्ती ( एच.पी.)"]
    ])
else:
    st.warning("No matching records found.")

# --- UPDATE FUNCTIONALITY ---
st.subheader("Edit Mobile Number & Status")

if not filtered_df.empty:
    selected_id = st.selectbox("Select अ.क्र (ID) to Edit", filtered_df["अ.क्र"].unique())

    if selected_id:
        row_index = df[df["अ.क्र"] == selected_id].index[0]

        # Text
        st.text(df.at[row_index, "मंजुरीधारकाचे नाव"])


        # Editable fields
        new_mobile = st.text_input("Mobile Number", df.at[row_index, "Mobile Number"])

        # Dropdown for Status selection

        status_options = ["नियमित सुरु", "मयत-वारस आहे", "मयत-वारस नाही", "त्या नवाची व्यक्ती मिळाली नाही"] # Modify as needed
        new_status = st.selectbox("Status", status_options, index=status_options.index(df.at[row_index, "Status"]) if df.at[row_index, "Status"] in status_options else 0)

        if st.button("Update"):
            df.at[row_index, "Mobile Number"] = new_mobile
            df.at[row_index, "Status"] = new_status
            save_data(df)
            st.success("Data updated successfully!")
            st.rerun()

# Load data
df = load_data()

# --- FILTER BY गावाचे नाव ---
st.subheader("Filter by  गावाचे नाव")
village_list = df["गावाचे नाव"].dropna().unique().tolist()
selected_village = st.selectbox("Select गावाचे नाव", ["All"] + village_list)

# Filter data based on selected village
if selected_village != "All":
    filtered_df = df[df["गावाचे नाव"] == selected_village]
else:
    filtered_df = df

# Show the filtered results
if not filtered_df.empty:
    st.write("Filtered Records:")
    st.dataframe(filtered_df[
                     ["अ.क्र", "मंजुरीधारकाचे नाव", "गट नंबर", "गावाचे नाव", "तालुका",
                      "जिल्हा",
                      "मंजुरीचा जावक क्र. व दिनांक", "मंजुर क्षेत्र (हेक्टर)   प्रवाही सिंचना साठी",
                      "मंजुर क्षेत्र (हेक्टर) सुक्ष्म सिंचना साठी", "मंजुर पिके",
                      "पंपाची मंजूर अश्वशक्ती ( एच.पी.)", "Mobile Number", "Status"]
    ])
else:
    st.warning("No matching records found.")

