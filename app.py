import os
import streamlit as st

# Configure the page layout
st.set_page_config(page_title="Clinical Review Tool", layout="wide")

# Define the folder containing your file pairs
DATA_FOLDER = "data"  # adjust this path as needed

def get_file_pairs(folder_path):
    """
    Scans the folder for files that start with 'case' and 'summary'.
    Returns a sorted list of tuples, each containing the full paths to a clinical case file and its corresponding summary file.
    """
    files = sorted(os.listdir(folder_path))
    # Filter files that start with "case" or "summary"
    case_files = sorted([f for f in files if f.startswith("case")])
    summary_files = sorted([f for f in files if f.startswith("summary")])
    
    # Pair the files by their order in the lists.
    # Make sure that they correspond correctly (this method assumes that the sorted order aligns the pairs)
    pairs = []
    for case_file, summary_file in zip(case_files, summary_files):
        pairs.append((os.path.join(folder_path, case_file), os.path.join(folder_path, summary_file)))
    return pairs

# Retrieve file pairs from the designated folder
pairs = get_file_pairs(DATA_FOLDER)

# Initialize a session state variable to track the current index
if 'index' not in st.session_state:
    st.session_state.index = 0

# Functions to navigate between file pairs
def next_pair():
    if st.session_state.index < len(pairs) - 1:
        st.session_state.index += 1

def prev_pair():
    if st.session_state.index > 0:
        st.session_state.index -= 1

# Read the current file pair based on the session state index
current_pair = pairs[st.session_state.index]

with open(current_pair[0], "r", encoding="utf-8") as f:
    clinical_text = f.read()

with open(current_pair[1], "r", encoding="utf-8") as f:
    discharge_text = f.read()

# Title and navigation status
st.title("Clinical Case Review Tool")
st.write(f"Reviewing file pair {st.session_state.index + 1} of {len(pairs)}")

# Create two columns for side-by-side display
col1, col2 = st.columns(2)

with col1:
    st.header("Clinical Case")
    st.text_area("Clinical Case Text", value=clinical_text, height=300, key="clinical")

with col2:
    st.header("Discharge Summary")
    st.text_area("Discharge Summary Text", value=discharge_text, height=300, key="summary")

# Navigation buttons (Previous and Next)
nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
with nav_col1:
    if st.button("Previous") and st.session_state.index > 0:
        prev_pair()
        st.rerun()  # Rerun the app to update the displayed files
with nav_col3:
    if st.button("Next") and st.session_state.index < len(pairs) - 1:
        next_pair()
        st.rerun()

st.markdown("---")

# Interactive review questions with a form
st.header("Review Questions")
with st.form("review_form"):
    answer1 = st.text_input("1. What are your observations regarding the clinical case?")
    answer2 = st.text_input("2. Do you notice any discrepancies between the clinical case and the discharge summary?")
    # You can add additional questions as needed

    submitted = st.form_submit_button("Submit Answers")

if submitted:
    st.success("Your answers have been submitted successfully!")
    st.write("**Your Responses:**")
    st.write("Observation on Clinical Case:", answer1)
    st.write("Discrepancies Noted:", answer2)
    # Here you can add logic to save the answers to a database or a file if needed.
