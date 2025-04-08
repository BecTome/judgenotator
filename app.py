import os
import streamlit as st
import pandas as pd

# Configure the page layout
st.set_page_config(page_title="Clinical Review Tool", layout="wide")

# Directory and CSV file settings
DATA_FOLDER = "data"  # adjust path to your folder containing files
RESULTS_FILE = "results.csv"  # CSV file to store answers

def get_file_pairs(folder_path):
    """
    Scans the folder for files starting with 'case' and 'summary'
    and pairs them together based on their sorted order.
    """
    files = sorted(os.listdir(folder_path))
    case_files = sorted([f for f in files if f.startswith("case")])
    summary_files = sorted([f for f in files if f.startswith("summary")])
    
    pairs = []
    # Assumes that corresponding files are in the same order.
    for case, summary in zip(case_files, summary_files):
        pairs.append((os.path.join(folder_path, case), os.path.join(folder_path, summary)))
    return pairs

# Retrieve the file pairs from the folder
pairs = get_file_pairs(DATA_FOLDER)

# Initialize session state to track the current file pair index
if 'index' not in st.session_state:
    st.session_state.index = 0

# Navigation buttons for Previous and Next
nav_cols = st.columns(2)
if nav_cols[0].button("Previous"):
    if st.session_state.index > 0:
        st.session_state.index -= 1
if nav_cols[1].button("Next"):
    if st.session_state.index < len(pairs) - 1:
        st.session_state.index += 1

# Read the current file pair based on the session state index
current_pair = pairs[st.session_state.index]
with open(current_pair[0], "r", encoding="utf-8") as f:
    clinical_text = f.read()
with open(current_pair[1], "r", encoding="utf-8") as f:
    discharge_text = f.read()

# Title and status
st.title("Clinical Case Review Tool")
st.write(f"Reviewing file pair {st.session_state.index + 1} of {len(pairs)}")

# Display the clinical case and discharge summary side by side (non-editable)
col1, col2 = st.columns(2)
with col1:
    st.header("Clinical Case")
    st.text_area("Clinical Case", value=clinical_text, height=300, disabled=True)
with col2:
    st.header("Discharge Summary")
    st.text_area("Discharge Summary", value=discharge_text, height=300, disabled=True)

st.markdown("---")
st.header("Review Questions")

# Create the form with mandatory fields
with st.form("review_form"):
    # Use a default option to force users to select a value from 1 to 5.
    rating_options = ["Select an answer", "1", "2", "3", "4", "5"]

    q1 = st.radio("1. How clear is the clinical case presentation?", rating_options, index=0)
    q2 = st.radio("2. How consistent is the discharge summary with the clinical case?", rating_options, index=0)
    q3 = st.radio("3. How confident are you in the overall documentation quality?", rating_options, index=0)

    comments = st.text_area("4. Additional Comments (required):")
    
    submitted = st.form_submit_button("Submit Answers")



if submitted:
    # Validate that all questions have answers
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
        # Use the clinical case file name as a unique document ID
        doc_id = os.path.basename(current_pair[0])
        
        # Check if the CSV file exists; if not, create an empty DataFrame
        if os.path.exists(RESULTS_FILE):
            df = pd.read_csv(RESULTS_FILE)
        else:
            df = pd.DataFrame(columns=["doc_id", "q1", "q2", "q3", "comments"])
        
        # Check if this document's results have already been submitted
        if doc_id in df["doc_id"].values:
            st.warning("Results for this document have already been submitted and cannot be changed.")
        else:
            new_row = pd.DataFrame({
                "doc_id": [doc_id],
                "q1": [q1],
                "q2": [q2],
                "q3": [q3],
                "comments": [comments]
            })
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(RESULTS_FILE, index=False)
            st.success("Your answers have been submitted and saved successfully!")
            st.write("**Your Responses:**")
            st.write("Question 1:", q1)
            st.write("Question 2:", q2)
            st.write("Question 3:", q3)
            st.write("Comments:", comments)

if os.path.exists(RESULTS_FILE):
    with open(RESULTS_FILE, "rb") as f:
        st.download_button(
            label="Download Results CSV",
            data=f,
            file_name=RESULTS_FILE,
            mime="text/csv"
        )