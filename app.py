import os
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Configure the page layout
st.set_page_config(page_title="Clinical Review Tool", layout="wide")

# --- Google Sheets Authentication ---
# Define the scope required to access sheets and drive
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Use the service account credentials from Streamlit secrets
credentials = Credentials.from_service_account_info(
    st.secrets["gdrive_service_account"], scopes=scope
)
gc = gspread.authorize(credentials)

# Open the Google Sheet (using the sheet ID from secrets)
spreadsheet_id = st.secrets["spreadsheet_id"]
sheet = gc.open_by_key(spreadsheet_id).sheet1  # using the first sheet

# --- File Handling: Reading Files from Local Folder (or Google Drive) ---
# This example assumes you have your files locally.
# If you're still reading from Google Drive, you can use your previous logic.
DATA_FOLDER = "data"  # adjust to your folder path

def get_file_pairs(folder_path):
    files = sorted(os.listdir(folder_path))
    case_files = sorted([f for f in files if f.startswith("case")])
    summary_files = sorted([f for f in files if f.startswith("summary")])
    pairs = []
    for case_file, summary_file in zip(case_files, summary_files):
        pairs.append((os.path.join(folder_path, case_file), os.path.join(folder_path, summary_file)))
    return pairs

pairs = get_file_pairs(DATA_FOLDER)

if not pairs:
    st.error("No file pairs found. Check your folder and file naming convention.")
    st.stop()

# --- Session State for Navigation ---
if 'index' not in st.session_state:
    st.session_state.index = 0

nav_cols = st.columns(2)
if nav_cols[0].button("Previous") and st.session_state.index > 0:
    st.session_state.index -= 1
if nav_cols[1].button("Next") and st.session_state.index < len(pairs) - 1:
    st.session_state.index += 1

# Read the current file pair
current_pair = pairs[st.session_state.index]
with open(current_pair[0], "r", encoding="utf-8") as f:
    clinical_text = f.read()
with open(current_pair[1], "r", encoding="utf-8") as f:
    discharge_text = f.read()

# Display the file names (using the case file as the unique document ID)
doc_id = os.path.basename(current_pair[0])

st.title("Clinical Case Review Tool")
st.write(f"Reviewing document: **{doc_id}** (File pair {st.session_state.index + 1} of {len(pairs)})")

# --- Display the Documents Side by Side (Non-Editable) ---
col1, col2 = st.columns(2)
with col1:
    st.header("Clinical Case")
    st.text_area("Clinical Case", value=clinical_text, height=300, disabled=True)
with col2:
    st.header("Discharge Summary")
    st.text_area("Discharge Summary", value=discharge_text, height=300, disabled=True)

st.markdown("---")
st.header("Review Questions")

# --- Review Form ---
with st.form("review_form"):
    rating_options = ["Select an answer", "1", "2", "3", "4", "5"]
    q1 = st.radio("1. How clear is the clinical case presentation?", rating_options, index=0)
    q2 = st.radio("2. How consistent is the discharge summary with the clinical case?", rating_options, index=0)
    q3 = st.radio("3. How confident are you in the overall documentation quality?", rating_options, index=0)
    comments = st.text_area("4. Additional Comments (required):")
    submitted = st.form_submit_button("Submit Answers")

if submitted:
    # Validate that all fields have been answered
    errors = []
    if q1 == "Select an answer":
        errors.append("Please select an answer for Question 1.")
    if q2 == "Select an answer":
        errors.append("Please select an answer for Question 2.")
    if q3 == "Select an answer":
        errors.append("Please select an answer for Question 3.")
    if not comments.strip():
        errors.append("Please provide additional comments.")
    
    if errors:
        for error in errors:
            st.error(error)
    else:
        # --- Save Data to Google Sheets ---
        # Check if the current doc_id is already recorded in the sheet.
        # Assuming the header row has columns: "doc_id", "q1", "q2", "q3", "comments"
        records = sheet.get_all_records()
        if any(record.get("doc_id") == doc_id for record in records):
            st.warning("Results for this document have already been submitted and cannot be changed.")
        else:
            # Append the new row
            new_row = [doc_id, q1, q2, q3, comments]
            sheet.append_row(new_row)
            st.success("Your answers have been submitted and saved successfully!")
            st.write("**Your Responses:**")
            st.write("Question 1:", q1)
            st.write("Question 2:", q2)
            st.write("Question 3:", q3)
            st.write("Comments:", comments)
