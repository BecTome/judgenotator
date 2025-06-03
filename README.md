# Judgenotator Annotation Tool

The Judgenotator Annotation Tool is a web-based application built with Streamlit that facilitates side-by-side comparison of clinical case reports (CC) and synthetic discharge summaries (DS). Its primary purpose is to help annotators systematically evaluate how well a generated summary captures essential patient information, structure, accuracy, and coherence relative to the original case.

Key features include:

* **Automated Pairing**: Text files placed in `pairs/original/` (clinical cases) and `pairs/generated/` (summaries) are automatically paired by their alphabetical order, so you can drop in new documents without editing code.
* **Annotator Management**: A simple list in the code defines who can review; adding or removing an annotator is as easy as editing a Python list.
* **Progress Tracking**: At the top of the interface, each annotator’s progress (documents reviewed vs. total) is displayed as both a count and a progress bar.
* **Document Status Indicators**: For each CC–DS pair, the tool shows whether each annotator has already submitted feedback, preventing duplicate submissions.
* **Side-by-Side Text Display**: The original clinical case and its corresponding generated summary appear in read-only text areas, making it easy to compare content directly.
* **Structured Evaluation Form**: Nine targeted questions—ranging from “Key Information” multi-selects to 1–5 ratings on completeness, structure, accuracy, and an overall quality score—guide the annotator through a consistent checklist. A free-text feedback field ensures qualitative rationale is captured.
* **Result Persistence**: Once an annotator submits, their responses (including all ratings and comments) are appended to a single tab-delimited CSV file (`results.csv`). If someone tries to re-annotate the same document under the same name, the tool will warn them and prevent duplication.
* **Easy Download**: At any time after there is at least one annotation, a “Download Results CSV” button appears so that you can export all collected data in one click.

This app has been developed in the framework of MultiSynDS projects.

Author: Alberto Becerra

1. **Clone & Navigate**

   ```bash
   git clone https://github.com/yourusername/judgenotator.git
   cd judgenotator
   ```

2. **Set Up Python Environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate      # (Windows PowerShell: .\.venv\Scripts\Activate)
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Prepare Your Text Files**

   * Create two subfolders inside `pairs/`:

     ```
     pairs/
     ├── original/    ← place clinical case .txt files here
     └── generated/   ← place corresponding synthetic summary .txt files here
     ```
   * **Naming**: The *n*-th file (alphabetical) in `original/` pairs with the *n*-th in `generated/`.
     Example:

     ```
     original/         generated/
     ├ case_001.txt    ├ summary_001.txt
     ├ case_002.txt    ├ summary_002.txt
     └ …               └ …
     ```

4. **Add or Change Annotators**

   * Open `app.py`, find:

     ```python
     ANNOTATORS = ["Leti", "Laura"]
     ```
   * Edit this list (e.g., `["Leti","Laura","Carlos"]`), save, and restart the app.

5. **Run the App**

   ```bash
   streamlit run app.py
   ```

   * A browser window opens at `http://localhost:8501`.
   * If files were added or renamed, refresh to update.

6. **Using the Interface**

   * **Progress Panel**: Shows how many pairs each annotator has reviewed vs. total.

   * **Navigation**: “Previous” and “Next” buttons move through pairs.

   * **Status Row**: Indicates “Annotated” or “Pending” for each annotator on the current document.

   * **Side‐by‐Side Text**: Left = clinical case; right = discharge summary.

   * **Review Form**:

     1. Select your name from the dropdown.
     2. Answer Q1–Q9 (multi‐select or 1–5 ratings, plus True/False for Q8).
     3. Provide free‐text feedback (required if any score <4).
     4. Click **Submit Answers**.

   * On successful submission, your responses append to `results.csv`. If you try to resubmit for the same `(doc_id, annotator)`, the app warns and does not overwrite.

7. **Downloading Results**

   * Once at least one annotation exists, a **Download Results CSV** button appears at the bottom. Click to download the tab‐delimited `results.csv`.

8. **Adding More Documents**

   * Drop new `.txt` files into `pairs/original/` and `pairs/generated/` (maintain parallel naming).
   * Restart or refresh the Streamlit app; “Total Documents” updates automatically.

9. **Quick Troubleshooting**

   * **“ModuleNotFoundError: streamlit”** → activate venv and `pip install -r requirements.txt`.
   * **“IndexError” or no files found** → ensure `pairs/original/` and `pairs/generated/` exist and contain matching `.txt` files.
   * **Cannot write `results.csv`** → check folder write permissions or close any program locking that file.

That’s it—anyone can replicate, add new document pairs, and expand the annotator list simply by editing the folders and `ANNOTATORS`. Enjoy annotating!
