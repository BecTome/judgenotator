import os
import glob

import pandas as pd
import streamlit as st
from typing import List, Tuple  # Use compatibility imports for Python 3.8

# ----------------------------------------
# Configuration and Constants
# ----------------------------------------

# Set Streamlit page configuration (title and layout)
st.set_page_config(page_title="MultiSynDS", layout="wide")

# Directory containing input files (adjust as needed)
DATA_FOLDER = "pairs"

# CSV file to store annotation results
RESULTS_FILE = "results.csv"

# Column names for the results CSV
COLUMNS = [
    "doc_id",
    "annotator",
    "Key Information CC",
    "Key Information DS",
    "Medical Entities Completeness",
    "Structure - Headers",
    "Structure - Content",
    "Content Accuracy",
    "Made-up Content",
    "Coherence",
    "Overall Quality",
    "Feedback",
]

# Instructions displayed at the top of the annotation form
INSTRUCTION = """
One of the main bottlenecks for the development of clinical NLP resources is the lack of access to
clinical records due to data privacy issues. This is particularly true for developments beyond English,
as most accessible anonymized clinical record datasets are only available in English.

To examine if clinical case report publications could be considered as a data source to generate
synthetic clinical discharge summaries using generative AI, prompt instructions combined with
automatic clinical methods were applied. This structured summary aims to systematically
characterize the clinical language features of synthetic discharge summaries. Each discharge
summary is assessed for a predefined set of features.

Please provide a rating from 1 to 5 for each question. **Text feedback is key, especially for
features with a score strictly lower than 4.**
"""

# Annotator names
ANNOTATORS = ["Leti", "Laura"]


# ----------------------------------------
# Helper Functions
# ----------------------------------------

def get_file_pairs(folder_path: str) -> List[Tuple[str, str]]:
    """
    Scan the 'original' and 'generated' subfolders for text files and pair them
    based on sorted order. Each pair is (clinical_case_file, discharge_summary_file).
    """
    original_dir = os.path.join(folder_path, "original")
    generated_dir = os.path.join(folder_path, "generated")

    # Find all .txt files in each subdirectory
    case_files = glob.glob(os.path.join(original_dir, "*.txt"))
    summary_files = glob.glob(os.path.join(generated_dir, "*.txt"))

    # Sort and zip them into pairs [(case1, summary1), (case2, summary2), ...]
    pairs = list(zip(sorted(case_files), sorted(summary_files)))
    return pairs


def load_progress(csv_path: str) -> pd.DataFrame:
    """
    Load existing annotation progress from RESULTS_FILE if it exists;
    otherwise, return an empty DataFrame with the expected columns.
    """
    if os.path.exists(csv_path):
        # Read the tab-delimited CSV with doc_id and annotator as strings
        return pd.read_csv(csv_path, delimiter="\t", dtype={"doc_id": str, "annotator": str})
    else:
        # Create an empty DataFrame with the predefined columns
        return pd.DataFrame(columns=COLUMNS)


# ----------------------------------------
# Main App Logic
# ----------------------------------------

# Retrieve all file pairs and count total documents
pairs = get_file_pairs(DATA_FOLDER)
total_docs = len(pairs)

# Initialize session state for navigation index if not already set
if "index" not in st.session_state:
    st.session_state.index = 0

# Page title
st.title("MultiSynDS Review Tool")

# -------------------------
# Annotation Progress Panel
# -------------------------

st.subheader("Annotation Progress")
df_progress = load_progress(RESULTS_FILE)

# Create columns to display progress for each annotator
status_cols = st.columns(len(ANNOTATORS))

for idx, annotator in enumerate(ANNOTATORS):
    # Count documents reviewed by this annotator
    if not df_progress.empty:
        num_reviewed = df_progress[df_progress["annotator"] == annotator].shape[0]
    else:
        num_reviewed = 0

    # Avoid division by zero
    progress_ratio = num_reviewed / total_docs if total_docs > 0 else 0

    with status_cols[idx]:
        st.write(f"**{annotator}**: {num_reviewed} / {total_docs} documents reviewed")
        st.progress(progress_ratio)

# -------------------------
# Navigation Controls
# -------------------------

nav_cols = st.columns(2)
if nav_cols[0].button("Previous"):
    if st.session_state.index > 0:
        st.session_state.index -= 1
if nav_cols[1].button("Next"):
    if st.session_state.index < total_docs - 1:
        st.session_state.index += 1

# Get the current file pair based on session index
current_case_path, current_summary_path = pairs[st.session_state.index]
current_doc_id = os.path.basename(current_case_path).split(".")[0]

# -------------------------
# Current Document Status
# -------------------------

st.subheader("Current Document Annotation Status")
status_cols = st.columns(len(ANNOTATORS))

for idx, annotator in enumerate(ANNOTATORS):
    # Check if this annotator has already annotated the current document
    annotated = (
        (df_progress["doc_id"] == current_doc_id)
        & (df_progress["annotator"] == annotator)
    ).any()

    if annotated:
        status_text = "Annotated"
        status_style = (
            "background-color: #d4edda; color: #155724; "
            "padding: 8px; border-radius: 5px; text-align: center;"
        )
    else:
        status_text = "Pending"
        status_style = (
            "background-color: #fff3cd; color: #856404; "
            "padding: 8px; border-radius: 5px; text-align: center;"
        )

    with status_cols[idx]:
        st.markdown(f"**{annotator}**")
        st.markdown(f"<div style='{status_style}'>{status_text}</div>", unsafe_allow_html=True)

# -------------------------
# Display Clinical Texts
# -------------------------

# Read clinical case and discharge summary from files
with open(current_case_path, "r", encoding="utf-8") as f:
    clinical_text = f.read()

with open(current_summary_path, "r", encoding="utf-8") as f:
    discharge_text = f.read()

# Display progress bar for document navigation
st.write(f"Reviewing file pair {st.session_state.index + 1} of {total_docs}")
st.progress((st.session_state.index + 1) / total_docs)

# Side-by-side display of Clinical Case (CC) and Discharge Summary (DS)
col1, col2 = st.columns(2)
with col1:
    st.header("Clinical Case")
    st.text_area(f"Clinical Case {current_doc_id}", value=clinical_text, height=300)

with col2:
    st.header("Discharge Summary")
    st.text_area(f"Discharge Summary {current_doc_id}", value=discharge_text, height=300)

st.markdown("---")
st.header("Review Questions")

# ----------------------------------------
# Review Questions Text Definitions
# ----------------------------------------

q1_text = """
Q1. **Key Information CC**: Does the original **clinical case report text (CC)** provide details on
different aspects of the medical situation of an individual patient?
\n**Unselect only the MISSING aspects.**
"""

q2_text = """
Q2. **Key Information DS**: Does the **discharge summary (DS)** provide details on different aspects
of the medical situation of an individual patient?
\n**Unselect only the MISSING aspects.**
"""

q3_text = """
Q3. **Medical Entities Completeness**: Does the discharge summary (DS) include all medical entities
(diseases, medications, procedures) originally in the CC? (Percentage of entities in DS that appear
in CC)

**Score 1**:  <50% of relevant entities are included  
**Score 2**:  50% - 65% of relevant entities are included  
**Score 3**:  65% - 80% of relevant entities are included  
**Score 4**:  80% - 95% of relevant entities are included  
**Score 5**:  95% - 100% of relevant entities are included  
"""

q4_text = """
Q4. **Structure - Headers**: Does the discharge summary (DS) contain the typical sections?  
(e.g., patient information/history, physical examination, clinical findings, symptoms, signs,
diagnostic assessment/diagnosis, therapeutic interventions/treatment, outcomes and follow up)

**Score 1**: Most of the important sections are missing  
**Score 2**: At least 2 of the most important section headers are missing  
**Score 3**: Section headers are correct but not in natural order  
**Score 4**: The main section headers are included but some irrelevant ones are included  
**Score 5**: Section headers correspond to those expected in a real discharge summary  
"""

q5_text = """
Q5. **Structure - Content**: Is the content in the discharge summary sections correct?

**Score 1**: Sections are very short or almost empty  
**Score 2**: At least 2 section headers don't correspond to the expected content  
**Score 3**: At least 1 section header doesn't correspond to the expected content  
**Score 4**: Information is well-structured but too short in at least one section  
**Score 5**: Information is correctly assigned to each section  
"""

q6_text = """
Q6. **Content Accuracy**: Does the discharge summary (DS) accurately reflect the clinical entities
(findings, diseases, signs, and symptoms) from the CC?  

**Score 1**: Overall, the content in DS is more concrete than in the CC  
**Score 2**: Overall, the content in DS is more general than in the CC  
**Score 3**: Two or more clinical entities are not completely accurate  
**Score 4**: One or more clinical entities are not completely accurate  
**Score 5**: All clinical entities are accurate  
"""

q7_text = """
Q7. **Made-up Content**: Does the discharge summary (DS) include additional patient information not
described in the clinical case (CC)? (Fabricated content)

**Score 1**: Made up two or more medication dosages or disease severity  
**Score 2**: Made up one or more medication dosages or disease severity  
**Score 3**: Made up other patient information  
**Score 4**: Made up irrelevant information  
**Score 5**: No fabricated content  
"""

q8_text = """
Q8. **Coherence**: Does the discharge summary (DS) show clinical incoherencies not present in the
original clinical case report (CC)? (e.g., disease-sex incompatibilities, temporal or age group
incompatibilities, deceased patient recommended follow-up, etc.)
"""

q9_text = """
Q9. **Overall Quality**: How would you rate the overall quality of the summary?

**Score 1**: Completely failed all assessments  
**Score 2**: Failed three of the previous aspects  
**Score 3**: Failed two of the previous aspects  
**Score 4**: Failed one of the previous aspects  
**Score 5**: Complete, well-structured, accurate, and without made-up content  
"""

# Options for multi-select questions (Key Information CC/DS)
LS_OPTIONS_MULTI = [
    "symptoms, signs and clinical findings",
    "diseases and co-morbidities",
    "medications",
    "clinical procedures",
    "sex",
    "age",
    "past medical conditions",
    "social determinants of health",
]

# Rating options from 1 to 5
RATING_OPTIONS = ["Select an answer", "1", "2", "3", "4", "5"]
# Boolean options for coherence question
BOOLEAN_OPTIONS = ["Select an answer", "True", "False"]

# ----------------------------------------
# Annotation Form
# ----------------------------------------

with st.form("review_form"):
    # Display instruction text
    st.markdown(INSTRUCTION)

    # Annotator selection dropdown
    annotator_choice = st.selectbox("Annotator Name", ANNOTATORS, index=0)

    # Question 1: Key Information CC (multi-select)
    q1 = st.pills(
        q1_text,
        LS_OPTIONS_MULTI,
        selection_mode="multi",
        key="q1",
        default=LS_OPTIONS_MULTI,
    )

    # Question 2: Key Information DS (multi-select)
    q2 = st.pills(
        q2_text,
        LS_OPTIONS_MULTI,
        selection_mode="multi",
        key="q2",
        default=LS_OPTIONS_MULTI,
    )

    # Questions 3-7: Rating from 1 to 5
    q3 = st.pills(q3_text, RATING_OPTIONS, default=["Select an answer"], key="q3")
    q4 = st.pills(q4_text, RATING_OPTIONS, default=["Select an answer"], key="q4")
    q5 = st.pills(q5_text, RATING_OPTIONS, default=["Select an answer"], key="q5")
    q6 = st.pills(q6_text, RATING_OPTIONS, default=["Select an answer"], key="q6")
    q7 = st.pills(q7_text, RATING_OPTIONS, default=["Select an answer"], key="q7")

    # Question 8: Boolean (True/False)
    q8 = st.pills(q8_text, BOOLEAN_OPTIONS, default=["Select an answer"], key="q8")

    # Question 9: Overall Quality (rating)
    q9 = st.pills(q9_text, RATING_OPTIONS, default=["Select an answer"], key="q9")

    # Free-text feedback area
    comments = st.text_area("Feedback: Crucial to mention reasons for scores below 4")

    # Submit button
    submitted = st.form_submit_button("Submit Answers")

# ----------------------------------------
# Form Submission Handling
# ----------------------------------------

if submitted:
    errors = []

    # Validate annotator selection
    if annotator_choice not in ANNOTATORS:
        errors.append("Please select your name from the dropdown.")

    # Validate mandatory ratings
    for question_idx, answer in enumerate([q3, q4, q5, q6, q7, q8, q9], start=3):
        if answer == "Select an answer":
            errors.append(f"Please select an answer for Question {question_idx}.")

    # Validate comments
    if not comments.strip():
        errors.append("Please provide additional comments explaining low scores.")

    if errors:
        # Display all validation errors
        for error in errors:
            st.error(error)
    else:
        # Check if this doc_id + annotator combination already exists
        existing_pairs = df_progress[["doc_id", "annotator"]].drop_duplicates().values.tolist()

        if [current_doc_id, annotator_choice] in existing_pairs:
            # Prevent overwriting existing annotations
            st.warning("Results for this document by this annotator have already been submitted.")
        else:
            # Build a new row to append
            new_row = pd.DataFrame({
                "doc_id": [current_doc_id],
                "annotator": [annotator_choice],
                COLUMNS[2]: [q1],
                COLUMNS[3]: [q2],
                COLUMNS[4]: [q3],
                COLUMNS[5]: [q4],
                COLUMNS[6]: [q5],
                COLUMNS[7]: [q6],
                COLUMNS[8]: [q7],
                COLUMNS[9]: [q8],
                COLUMNS[10]: [q9],
                "Feedback": [comments],
            })

            # Determine if we need to write the header
            write_header = not os.path.exists(RESULTS_FILE)

            # Append to the results CSV
            new_row.to_csv(
                RESULTS_FILE,
                sep="\t",
                index=False,
                header=write_header,
                mode="a",
            )

            # Confirmation message
            st.success("Your answers have been submitted and saved successfully!")
            st.write("**Your Responses:**")
            st.write(f"- Document ID: {current_doc_id}")
            st.write(f"- Annotator Name: {annotator_choice}")
            st.write(f"- Question 1: {q1}")
            st.write(f"- Question 2: {q2}")
            st.write(f"- Question 3: {q3}")
            st.write(f"- Question 4: {q4}")
            st.write(f"- Question 5: {q5}")
            st.write(f"- Question 6: {q6}")
            st.write(f"- Question 7: {q7}")
            st.write(f"- Question 8: {q8}")
            st.write(f"- Question 9: {q9}")
            st.write(f"- Feedback: {comments}")

# -------------------------
# Download Button for Results
# -------------------------

if os.path.exists(RESULTS_FILE):
    with open(RESULTS_FILE, "rb") as f:
        st.download_button(
            label="Download Results CSV",
            data=f,
            file_name=RESULTS_FILE,
            mime="text/csv",
        )