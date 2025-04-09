import os
import streamlit as st
import pandas as pd
import glob

# Configure the page layout
st.set_page_config(page_title="MultiSynDS", layout="wide")

# Directory and CSV file settings
DATA_FOLDER = "pairs"  # Adjust path to your folder containing files
RESULTS_FILE = "results.csv"  # CSV file to store answers
COLUMNS = ["doc_id", "annotator", "Information Completeness", "Clarity and Structure", "Content Accuracy", "Made-up Content", "Overall Quality", "Feedback"]
INSTRUCTION = """
One of the main bottlenecks for the development of clinical NLP resources if the lack of access to clinical records due to data privacy issues. This is particularly true for developments beyond English, as most of the accessible anonymized clinical record datasets are only available for this language.
To examine if clinical case report publications could potentially be considered as a data source to generate synthetic clinical discharge summaries by means of generative AI solutions, prompt instructions combined with automatic clinical were applied.
This structured summary has the purpose to systematically characterize the clinical language characteristics of synthetic discharge summaries.
Each discharge summary was assessed for a predefined set of features.

Please, provide a rating from 1 to 5 for each of the following questions. 

**Text feedback will be key to understand the rationale. Pay special attention to the features with score strictly lower thnan 4.**
"""

def get_file_pairs(folder_path):
    """
    Scans the folder for files starting with 'case' and 'summary'
    and pairs them together based on their sorted order.
    """
    case_path = os.path.join(folder_path, "original")
    summary_path = os.path.join(folder_path, "generated")
    
    case_files = glob.glob(os.path.join(case_path, "*.txt"))
    summary_files = glob.glob(os.path.join(summary_path, "*.txt"))
    
    pairs = list(zip(sorted(case_files), sorted(summary_files)))
    # Assumes that corresponding files are in the same order.

    return pairs


# Retrieve the file pairs from the folder
pairs = get_file_pairs(DATA_FOLDER)
# pairs = [cc, ds, False for cc, ds in pairs]
total_docs = len(pairs)

# Initialize session state to track the current file pair index
if 'index' not in st.session_state:
    st.session_state.index = 0

# Define the annotator names
annotator_names = ["Leti", "Laura"]

# Title
st.title("MultiSynDS Review Tool")

# --- Show Progress for Each Annotator ---
# Load the current results if available, otherwise use an empty DataFrame.
if os.path.exists(RESULTS_FILE):
    df_progress = pd.read_csv(RESULTS_FILE, delimiter=";", dtype={"doc_id": str, "annotator": str})
else:
    df_progress = pd.DataFrame(columns=COLUMNS)
    
st.subheader("Annotation Progress")

status_cols = st.columns(len(annotator_names))
for idx, annotator in enumerate(annotator_names):
    
    # Count how many documents this annotator has reviewed.
    num_reviewed = df_progress[df_progress['annotator'] == annotator].shape[0] if not df_progress.empty else 0
    # Calculate progress ratio (make sure to avoid division by zero)
    progress_val = num_reviewed / total_docs if total_docs > 0 else 0
    st.write(f"{annotator}: {num_reviewed} / {total_docs} documents reviewed")
    st.progress(progress_val)


# --- Navigation Controls ---
nav_cols = st.columns(2)
if nav_cols[0].button("Previous"):
    if st.session_state.index > 0:
        st.session_state.index -= 1
if nav_cols[1].button("Next"):
    if st.session_state.index < total_docs - 1:
        st.session_state.index += 1

doc_id = pairs[st.session_state.index][0]
case_id = os.path.basename(doc_id).split(".")[0]

# --- Display Visible Flag for the Current Document ---
st.subheader("Current Document Annotation Status")
status_cols = st.columns(len(annotator_names))
for idx, annotator in enumerate(annotator_names):
    # Check if this document has been reviewed by this annotator
    # print(df_progress[(df_progress["doc_id"] == doc_id) & (df_progress["annotator"] == annotator)].shape)
    if df_progress[(df_progress["doc_id"] == case_id) & (df_progress["annotator"] == annotator)].shape[0] > 0:
        status = "Annotated"
        style = "background-color: #d4edda; color: #155724; padding: 8px; border-radius: 5px; text-align: center;"
    else:
        status = "Pending"
        style = "background-color: #fff3cd; color: #856404; padding: 8px; border-radius: 5px; text-align: center;"
    with status_cols[idx]:
        st.markdown(f"**{annotator}**", unsafe_allow_html=True)
        st.markdown(f"<div style='{style}'>{status}</div>", unsafe_allow_html=True)


# Read the current file pair based on the session state index
current_pair = pairs[st.session_state.index]
with open(current_pair[0], "r", encoding="utf-8") as f:
    clinical_text = f.read()
with open(current_pair[1], "r", encoding="utf-8") as f:
    discharge_text = f.read()

# Status of the currently viewed document
st.write(f"Reviewing file pair {st.session_state.index + 1} of {total_docs}")
docs_remaining = total_docs - (st.session_state.index + 1)
progress_percent = (st.session_state.index + 1) / total_docs
st.progress(progress_percent)



# Display the clinical case and discharge summary side by side (non-editable)
col1, col2 = st.columns(2)
case_id = os.path.basename(doc_id).split(".")[0]
with col1:
    st.header("Clinical Case")
    st.text_area(f"Clinical Case {case_id}", value=clinical_text, height=300)
with col2:
    st.header("Discharge Summary")
    st.text_area(f"Discharge Summary {case_id}", value=discharge_text, height=300)

st.markdown("---")
st.header("Review Questions")

# --- Review Form ---
with st.form("review_form"):
    # Use a default option to force selection from 1 to 5.
    st.write(INSTRUCTION)
    rating_options = ["Select an answer", "1", "2", "3", "4", "5"]
    q0 = st.selectbox("Annotator Name", annotator_names, index=0)
    q1 = st.radio("Information Completeness: Does the summary include all key details (diagnoses, treatments, follow-ups)? (Amount of things in DS that are also in CC)", rating_options, index=0)
    q2 = st.radio("Clarity and Structure: Is the information presented in a clear and logically structured manner like a real discharge report? (Sections make sense, content in the corresponding parts)", rating_options, index=0)
    q3 = st.radio("Content Accuracy: Does the report accurately reflect the clinical information provided in the input? (Things contained in both DS and CC are equal)", rating_options, index=0)
    q4 = st.radio("Made-up Content: Are there any factual inaccuracies or fabricated content in the summary? (Things in DS but not in CC)", rating_options, index=0)
    q5 = st.radio("Overall Quality: How would you rate the overall quality of the summary?", rating_options, index=0)
    
    comments = st.text_area("Feedback: Crucial to mention the reason for scores below 4")
    submitted = st.form_submit_button("Submit Answers")

if submitted:
    # Validate that all questions have answers
    errors = []
    if q0 == "Select an answer":
        errors.append("Please select your name.")
    if q1 == "Select an answer":
        errors.append("Please select an answer for Question 1.")
    if q2 == "Select an answer":
        errors.append("Please select an answer for Question 2.")
    if q3 == "Select an answer":
        errors.append("Please select an answer for Question 3.")
    if q4 == "Select an answer":
        errors.append("Please select an answer for Question 4.")
    if q5 == "Select an answer":
        errors.append("Please select an answer for Question 5.")
    if not comments.strip():
        errors.append("Please provide additional comments.")

    if errors:
        for error in errors:
            st.error(error)
    else:
        # Use the clinical case file name as a unique document ID
        doc_id = os.path.basename(current_pair[0].split(".")[0])
        
        # Check if results for this document already exist
        if (doc_id in df_progress["doc_id"].values) and (q0 in df_progress["annotator"].values):
            st.warning("Results for this document have already been submitted and cannot be changed.")
        else:
            new_row = pd.DataFrame({
                "doc_id": [doc_id],
                "annotator": [q0],
                COLUMNS[2]: [q1],
                COLUMNS[3]: [q2],
                COLUMNS[4]: [q3],
                COLUMNS[5]: [q4],
                COLUMNS[6]: [q5],
                "Feedback": [comments]
            })
            df = pd.concat([df_progress, new_row], ignore_index=True)
            df.to_csv(RESULTS_FILE, index=False, sep=";")
            st.success("Your answers have been submitted and saved successfully!")
            st.write("**Your Responses:**")
            st.write("Document ID:", doc_id)
            st.write("Annotator Name:", q0)
            st.write("Question 1:", q1)
            st.write("Question 2:", q2)
            st.write("Question 3:", q3)
            st.write("Question 4:", q4)
            st.write("Question 5:", q5)
            st.write("Comments:", comments)

if os.path.exists(RESULTS_FILE):
    with open(RESULTS_FILE, "rb") as f:
        st.download_button(
            label="Download Results CSV",
            data=f,
            file_name=RESULTS_FILE,
            mime="text/csv"
        )
