# TENDERIQ - Intelligent Tender Analysis Engine

TENDERIQ is a Python and Flask-based NLP application designed to process, analyze, and extract critical intelligence from tender documents, bid notices, and procurement specifications. It automates the process of identifying key eligibility rules, financial requirements, submission deadlines, required documents, and potential compliance risk factors.

---

## 🌟 Key Features

* **Multi-Format Input:** Supports plain text pasting, PDF files, and `.docx` document uploads.
* **Metadata Extraction:** Automatically isolates Tender Reference Numbers, Titles, and Issuing Organizations/Departments.
* **Categorized Extraction:** Segmented extraction for:
  * **Eligibility Criteria**
  * **Financial Requirements**
  * **Important Dates & Schedules**
  * **Required / Mandatory Documents**
* **Automated Risk Alerts:** Detects non-compliance risks, EMD/Fee requirements, and blacklisting clauses.
* **Executive Summarization:** Extracts contextual background and scope clauses to construct an executive summary.
* **JSON Export:** Download structured extraction reports in `.json` format for integration with downstream tools.

---

## 🛠️ NLP Architecture & Methodology

TENDERIQ uses a **hybrid NLP pipeline** combining traditional text pre-processing, pattern matching, and contextual heuristics:

1. **Text Preprocessing & Extraction (`PyMuPDF / fitz`, `python-docx`, `NLTK`):**
   * Raw text is extracted page-by-page from PDFs using `fitz` (PyMuPDF) or structured paragraphs via `python-docx`.
   * Sentence boundary detection is handled using `NLTK` tokenizers (`punkt`, `punkt_tab`).
2. **Contextual & Rule-Based Extraction (`Regex` & Heuristics):**
   * Pattern-matches reference numbers (`Ref No: ...`), monetary values (`INR ...`), and structured header boundaries.
3. **Temporal Analysis (Important Dates):**
   * Scans sentences for schedule-related keywords (`submission`, `deadline`, `opening`, `schedule`, `date`) and filters out irrelevant paragraph text via line-length constraints.
4. **Risk Alert Detection:**
   * Rule-driven scanning for critical compliance conditions like Earnest Money Deposit (EMD) requirements and blacklisting warnings.

---

## 📂 Project Structure

```text
TENDERIQ/
├── app.py                      # Flask Application Server & Routing
├── nlp/
│   ├── __init__.py             # Module initialization
│   ├── preprocessing.py        # Text extraction (PDF, DOCX, TXT) & NLTK setup
│   └── extraction.py           # Core NLP extraction logic & summarizer
├── templates/
│   ├── base.html               # Shared HTML Layout / Navigation
│   ├── index.html              # Main Upload & Text Input Page
│   └── results.html            # Tender Analysis Dashboard
├── static/                     # CSS / JS static assets
├── requirements.txt            # Python Dependencies
└── README.md                   # Project Documentation
```

---

## 🚀 Setup & Installation

### 1. Prerequisites
* **Python 3.8+** installed on your system.

### 2. Clone / Download Project
```bash
git clone <repository-url>
cd TENDERIQ
```

### 3. Create a Virtual Environment (Optional but Recommended)
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Application
```bash
python app.py
```

The app will download necessary `NLTK` packages (`punkt`, `stopwords`, `averaged_perceptron_tagger`) on first run and launch the development server at:
`http://127.0.0.1:5000/`

---

## 📄 License
This project is open-source and intended for analytical and research purposes.