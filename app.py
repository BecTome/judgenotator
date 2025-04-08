import os
import streamlit as st
import requests

# Configure the page layout for Streamlit
st.set_page_config(page_title="Clinical Review Tool", layout="wide")

# URL for Sheety API endpoint (provided)
SHEETY_URL = "https://api.sheety.co/50c6df322e25ab952a7497309b181500/sheetyExample/hoja1"

# Directory for your source files
DATA_FOLDER = "data"  # adjust this to your local folder

def get_file_pairs(folder_path):
    """
    Retrieve files in the folder that start with 'case' and 'summary' and pair them.
    This example assumes that corresponding files are ordered similarly.
    """
    files = sorted(os.listdir(folder_path))
    case_files = sorted([f for f in files if f.startswith("case")])
    summary_files = sorted([f for f in files if f.startswith("summary")])
    pairs = []
    for case_file, summary_file in zip(case_files, summary_files):
        pairs.append((os.path.join(folder_path, case_file), os.path.join(folder_path, summary_file)))
    return pairs

# Get file pairs from the DATA_FOLDER
pairs = get_file_pairs(DATA_FOLDER)
if not pairs:
    st.error("No file pairs found in the folder. Please check your folder or naming convention.")
    st.stop()

# Use session state to track the current index among file pairs
if 'index' not in st.session_state:
    st.session_state.index = 0

# Navigation buttons for Previous and Next
nav_cols = st.columns(2)
if nav_cols[0].button("Previous") and st.session_state.index > 0:
    st.session_state.index -= 1
if nav_cols[1].button("Next") and st.session_state.index < len(pairs) - 1:
    st.session_state.index += 1

# Read the current file pair based on the session state index
current_pair = pairs[st.session_state.index]
with open(current_pair[0], "r", encoding="utf-8") as f:
    clinical_text = f.read()
with open(current_pair[1], "r", encoding="utf-8") as f:
    discharge_text = f.read()

# Define a unique document id based on the clinical case file name
doc_id = os.path.basename(current_pair[0])

# Title and basic document info
st.title("Clinical Case Review Tool")
st.write(f"Reviewing document: **{doc_id}** (File pair {st.session_state.index + 1} of {len(pairs)})")

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

# Create a review form with 3 mandatory rating questions and one free-text field
with st.form("review_form"):
    rating_options = ["Select an answer", "1", "2", "3", "4", "5"]
    q1 = st.radio("1. How clear is the clinical case presentation?", rating_options, index=0)
    q2 = st.radio("2. How consistent is the discharge summary with the clinical case?", rating_options, index=0)
    q3 = st.radio("3. How confident are you in the overall documentation quality?", rating_options, index=0)
    comments = st.text_area("4. Additional Comments (required):")
    submitted = st.form_submit_button("Submit Answers")

if submitted:
    # Validate that all required fields are answered
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
        # Retrieve current rows from Sheety
        get_response = requests.get(SHEETY_URL)
        if get_response.status_code == 200:
            data = get_response.json()
            # Assuming Sheety returns a JSON object with a key "hoja1"
            rows = data.get("hoja1", [])
            if any(row.get("doc_id") == doc_id for row in rows):
                st.warning("Results for this document have already been submitted and cannot be changed.")
            else:
                # Prepare the new row data to append
                new_row = {
                    "doc_id": doc_id,
                    "q1": q1,
                    "q2": q2,
                    "q3": q3,
                    "comments": comments
                }
                # Sheety expects the data to be wrapped in the sheet name's key.
                payload = {"hoja1": new_row}
                post_response = requests.post(SHEETY_URL, json=payload)
                if post_response.status_code in (200, 201):
                    st.success("Your answers have been submitted and saved successfully!")
                    st.write("**Your Responses:**")
                    st.write("Question 1:", q1)
                    st.write("Question 2:", q2)
                    st.write("Question 3:", q3)
                    st.write("Comments:", comments)
                else:
                    st.error("There was an error saving your submission. Please try again later.")
        else:
            st.error("Error retrieving existing submissions from the sheet.")
