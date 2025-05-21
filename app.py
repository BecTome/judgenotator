import os
import streamlit as st
import pandas as pd
import glob

# Configure the page layout
st.set_page_config(page_title="MultiSynDS", layout="wide")

# Directory and CSV file settings
DATA_FOLDER = "pairs"  # Adjust path to your folder containing files
RESULTS_FILE = "results.csv"  # CSV file to store answers
COLUMNS = ["doc_id", 
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
           "Feedback"]
INSTRUCTION = """
One of the main bottlenecks for the development of clinical NLP resources if the lack of access to clinical records due to data privacy issues. This is particularly true for developments beyond English, as most of the accessible anonymized clinical record datasets are only available for this language.
To examine if clinical case report publications could potentially be considered as a data source to generate synthetic clinical discharge summaries by means of generative AI solutions, prompt instructions combined with automatic clinical were applied.
This structured summary has the purpose to systematically characterize the clinical language characteristics of synthetic discharge summaries.
Each discharge summary was assessed for a predefined set of features.

Please, provide a rating from 1 to 5 for each of the following questions. 

**Text feedback will be key to understand the rationale. Pay special attention to the features with score strictly lower than 4.**
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
    df_progress = pd.read_csv(RESULTS_FILE, delimiter="\t", dtype={"doc_id": str, "annotator": str})
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

# print(current_pair)
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

q1_text = """
Q1. **Key Information CC**: Does the original **clinical case report text (CC)** provide details on different aspects of the medical situation of an individual patient?
\n**Unselect only the MISSING aspects.**
"""

q2_text = """
Q2. **Key Information DS**: Does the **discharge summary (DS)** provide details on different aspects of the medical situation of an individual patient?
\n**Unselect only the MISSING aspects.**
"""

q3_text = """
Q3. **Medical Entities Completeness**: Does the discharge summary (DS) include all medical entities (diseases, medications, procedures) originally in the CC? (Amount of entities in DS that are also in CC)

**Score 1**:  <50%        of relevant entities are included\n
**Score 2**:  50% - 65%   of relevant entities are included\n
**Score 3**:  65% - 80%   of relevant entities are included\n
**Score 4**:  80% - 95%   of relevant entities are included\n
**Score 5**:  95% - 100%  of relevant entities are included
"""

q4_text = """
Q4. **Structure - Headers**: Does the discharge summary (DS) contain the typical sections?\n
(e.g. patient information/history, physical examination, clinical findings, symptoms, signs, diagnostic assessment/diagnosis, therapeutic interventions/treatment, outcomes and follow up)

**Score 1**: Most of the important sections are missing\n
**Score 2**: At least 2 of the most important section headers are missing\n
**Score 3**: Section headers are correct but not in natural order\n
**Score 4**: The main section headers are included but some irrelevant ones have been included\n
**Score 5**: The section headers make sense and correspond to the ones expected in a real discharge summary.
"""

q5_text = """
Q5. **Structure - Content**: Is the content in the discharge summary sections correct? 

**Score 1**: Sections are very short or almost empty\n
**Score 2**: At least 2 section header doesn't correspond to the expected content for that header\n
**Score 3**: At least 1 section header doesn't correspond to the expected content for that header\n
**Score 4**: Information is well structured but information is too short in at least 1 case\n
**Score 5**: Information is correctly assigned to each section
"""
# patient information/history, physical examination, clinical findings, symptoms, signs, diagnostic assessment/diagnosis, therapeutic interventions/treatment, outcomes and follow up
q6_text = """
Q6. **Content Accuracy**: Does the discharge summary (DS) accurately reflect the clinical entities (findings, diseases, signs and symptoms) provided in the clinical case report (CC)? (Things contained in both DS and CC are equal)

**Score 1**:  Overall, the content in DS is more concrete than in the CC\n
**Score 2**:  Overall, the content in DS is more general than in the CC\n
**Score 3**:  There are 2 or more clinical entities that are not completely accurate\n
**Score 4**:  There are 1 or more clinical entities that are not completely accurate\n
**Score 5**:  All the clinical entities are accurate
"""

q7_text = """
Q7. **Made-up Content**: Does the discharge summary (DS) include additional patient's medical situation information not described in the clinical case (CC)? (Fabricated content)

**Score 1**:  It made up 2 or more medicament dosage or disease severity\n
**Score 2**:  It made up 1 or more medicament dosage or disease severity\n
**Score 3**:  It made up information about the patient\n
**Score 4**:  It made up irrelevant information\n
**Score 5**:  It didnt make anything up
"""

q8_text = """
Q8. **Coherence**: Does the discharge summary (DS) show clinical incoherencies not present on the original clinical case report (CC)? (disease-sex incompatibilities, temporal or age group incompatibilities, deceased patient recommended follow-up etc).
"""

q9_text = """
Q9. **Overall Quality**: How would you rate the overall quality of the summary?

**Score 1**:  It completely failed all the assessments\n
**Score 2**:  Failed 3 of the previous aspects\n
**Score 3**:  Failed 2 of the previous aspects\n
**Score 4**:  Failed 1 of the previous aspects\n
**Score 5**:  It is complete, well structured, accurate and without made-up content
"""

# --- Review Form ---
with st.form("review_form"):
    # Use a default option to force selection from 1 to 5.
    st.write(INSTRUCTION)
    rating_options = ["Select an answer", "1", "2", "3", "4", "5"]
    rating_options_bool = ["Select an answer", "True", "False"]
    q_name = st.selectbox("Annotator Name", annotator_names, index=0)
    # ls_options_multi = ["patient information/history", "physical examination", 
    #                     "clinical findings", "symptoms and signs", "diagnostic assessment/diagnosis", 
    #                     "therapeutic interventions/treatment", "outcomes and follow up"]
    ls_options_multi = ["symptoms, signs and clinical findings", "diseases and co-morbidities",
                        "medications", "clinical procedures", "sex", "age", "past medical conditions", "social determinants of health"]

    
    q1 = st.pills(q1_text, ls_options_multi, selection_mode="multi", key="q1", default=ls_options_multi)
    q2 = st.pills(q2_text, ls_options_multi, selection_mode="multi", key="q2", default=ls_options_multi)

    q3 = st.pills(q3_text, rating_options, default=["Select an answer"], key="q3")#, index=0)
    q4 = st.pills(q4_text, rating_options, default=["Select an answer"], key="q4")#, index=0)
    q5 = st.pills(q5_text, rating_options, default=["Select an answer"], key="q5")#, index=0)
    q6 = st.pills(q6_text, rating_options, default=["Select an answer"], key="q6")#, index=0)
    q7 = st.pills(q7_text, rating_options, default=["Select an answer"], key="q7")#, index=0)
    q8 = st.pills(q8_text, rating_options_bool, default=["Select an answer"], key="q8")#, index=0)
    q9 = st.pills(q9_text, rating_options, default=["Select an answer"], key="q9")#, index=0)
    
    comments = st.text_area("Feedback: Crucial to mention the reason for scores below 4")
    submitted = st.form_submit_button("Submit Answers")

if submitted:
    # Validate that all questions have answers
    errors = []
    if q_name == "Select an answer":
        errors.append("Please select your name.")
    if q3 == "Select an answer":
        errors.append("Please select an answer for Question 3.")
    if q4 == "Select an answer":
        errors.append("Please select an answer for Question 4.")
    if q5 == "Select an answer":
        errors.append("Please select an answer for Question 5.")
    if q6 == "Select an answer":
        errors.append("Please select an answer for Question 6.")
    if q7 == "Select an answer":
        errors.append("Please select an answer for Question 7.")
    if q8 == "Select an answer":
        errors.append("Please select an answer for Question 8.")
    if q9 == "Select an answer":
        errors.append("Please select an answer for Question 9.")    
    if not comments.strip():
        errors.append("Please provide additional comments.")

    if errors:
        for error in errors:
            st.error(error)
    else:
        # Use the clinical case file name as a unique document ID
        # doc_id = os.path.basename(current_pair[0].split(".")[0])
        
        # print(doc_id, q_name)
        # print(doc_id in df_progress["doc_id"].values)
        # print(q_name in df_progress["annotator"].values)
        # Check if results for this document already exist
        already_annotated_pairs = df_progress[["doc_id", "annotator"]].drop_duplicates().values.tolist()
        # print(already_annotated_pairs)
        if [case_id, q_name] in already_annotated_pairs:
            st.warning("Results for this document have already been submitted and cannot be changed.")
        else:
            new_row = pd.DataFrame({
                "doc_id": [case_id],
                "annotator": [q_name],
                COLUMNS[2]: [q1],
                COLUMNS[3]: [q2],
                COLUMNS[4]: [q3],
                COLUMNS[5]: [q4],
                COLUMNS[6]: [q5],
                COLUMNS[7]: [q6],
                COLUMNS[8]: [q7],
                COLUMNS[9]: [q8],
                COLUMNS[10]: [q9],

                "Feedback": [comments]
            })
            # df = pd.concat([df_progress, new_row], ignore_index=True)
            # df.to_csv(RESULTS_FILE, index=False, sep="\t")
            
            # To avoid race condition
            header = not os.path.exists(RESULTS_FILE)
            # with open(RESULTS_FILE, "a", newline="\n", encoding="utf-8") as f:
            #     new_row.to_csv(f, sep="\t", index=False, header=header)
            
            # with open(RESULTS_FILE, "a", newline="") as f:
            new_row.to_csv(
                RESULTS_FILE,
                sep="\t",
                index=False,
                header=header,
                # line_terminator="\n"
                mode="a"
            )
            
            st.success("Your answers have been submitted and saved successfully!")
            st.write("**Your Responses:**")
            st.write("Document ID:", case_id)
            st.write("Annotator Name:", q_name)
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
