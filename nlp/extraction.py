import re
# TF-IDF import commented out as requested
# from sklearn.feature_extraction.text import TfidfVectorizer

def extract_information(text):
    if not text or not text.strip():
        return {
            "overview": {"title": "N/A", "reference": "Not found", "issuing_organization": "Not found", "summary": "No text provided."},
            "eligibility": [], "financial": [], "dates": [], "mandatory_docs": [], "disqualification": [], "alerts": [], "keywords": [], "summary": ""
        }

    lines = [line.strip() for line in text.split('\n') if line.strip()]

    # --- 1. OVERVIEW EXTRACTION ---
    # Title
    title_match = re.search(r'(?:Tender Title|Title|Subject)\s*[:\-]\s*(.+)', text, re.IGNORECASE)
    if title_match:
        title = title_match.group(1).split('\n')[0].strip()
    else:
        title = lines[0] if lines else "Tender Document"
    
    if len(title) > 120:
        title = title[:117] + "..."

    # Reference Number
    ref_match = re.search(r'(?:Tender Reference Number|Ref(?:erence)?\s*(?:No|Number)?)\s*[:\-]\s*([A-Za-z0-9/\-_]+)', text, re.IGNORECASE)
    reference = ref_match.group(1).strip() if ref_match else "Not found in document"

    # Issuer / Department
    issuer_match = re.search(r'(?:Department|Issuing Organization|Issuer|Authority)\s*[:\-]\s*(.+)', text, re.IGNORECASE)
    if issuer_match:
        issuing_org = issuer_match.group(1).split('\n')[0].strip()
    else:
        issuing_org = "Not found in document"

    # --- 2. DATES EXTRACTION ---
    dates = []
    date_keywords = ['date', 'deadline', 'submission', 'opening', 'schedule']
    for line in lines:
        if any(kw in line.lower() for kw in date_keywords):
            if line not in dates and len(line) < 120:
                dates.append(line)

    # --- 3. SECTION PARSING (Eligibility, Financial, Docs) ---
    eligibility, financial, mandatory_docs, disqualification = [], [], [], []
    current_section = None

    for line in lines:
        line_lower = line.lower()
        if 'eligibility' in line_lower:
            current_section = 'eligibility'
            continue
        elif 'financial' in line_lower:
            current_section = 'financial'
            continue
        elif 'required documents' in line_lower or 'mandatory documents' in line_lower:
            current_section = 'docs'
            continue
        elif 'terms and conditions' in line_lower or 'disqualification' in line_lower:
            current_section = 'disqualification'
            continue
        elif re.match(r'^\d+\.\s+[A-Z\s]{4,}', line):
            current_section = None

        if current_section == 'eligibility' and len(line) > 5:
            eligibility.append(line)
        elif current_section == 'financial' and len(line) > 5:
            financial.append(line)
        elif current_section == 'docs' and len(line) > 5:
            mandatory_docs.append(line)
        elif current_section == 'disqualification' and len(line) > 5:
            disqualification.append(line)

    # Fallbacks
    if not eligibility:
        eligibility = [l for l in lines if any(k in l.lower() for k in ['must be', 'must possess', 'turnover', 'experience'])][:6]
    if not financial:
        financial = [l for l in lines if any(k in l.lower() for k in ['inr', 'emd', 'fee', 'payment', 'deposit'])][:6]

    # --- 4. ALERTS & KEYWORDS ---
    alerts = []
    if disqualification or any('blacklist' in l.lower() for l in lines):
        alerts.append({"type": "Risk Warning", "message": "Document contains strict non-compliance/blacklisting clauses."})
    if any('emd' in l.lower() or 'deposit' in l.lower() for l in lines):
        alerts.append({"type": "Financial Alert", "message": "Earnest Money Deposit (EMD) or Tender Fee required."})

    # --- TF-IDF KEYWORD RANKING (DISABLED) ---
    # keywords = []
    # try:
    #     tfidf = TfidfVectorizer(stop_words='english', max_features=12)
    #     tfidf.fit([text])
    #     keywords = list(tfidf.get_feature_names_out())
    # except Exception:
    #     keywords = []
    keywords = []

    # --- 5. EXPANDED EXECUTIVE SUMMARY EXTRACTION ---
    # Pull contextual sentences from Introduction, Scope, and Objectives
    summary_sentences = []
    for line in lines:
        # Ignore short header/metadata key-value pairs
        if len(line) > 40 and not line.endswith(':'):
            line_lower = line.lower()
            if any(kw in line_lower for kw in ['invites', 'objective', 'scope', 'supply', 'installation', 'commissioning', 'procurement', 'requirement', 'project', 'infrastructure']):
                if line not in summary_sentences:
                    summary_sentences.append(line)
            if len(summary_sentences) >= 5:
                break

    # Fallback to major descriptive lines if no scope keywords hit
    if not summary_sentences:
        summary_sentences = [l for l in lines if len(l) > 45 and not l.isupper()][:4]

    executive_summary = " ".join(summary_sentences) if summary_sentences else "No detailed executive summary could be generated from the document text."

    return {
        "overview": {
            "title": title,
            "reference": reference,
            "issuing_organization": issuing_org,
            "summary": executive_summary
        },
        "eligibility": eligibility,
        "financial": financial,
        "dates": dates,
        "mandatory_docs": mandatory_docs,
        "disqualification": disqualification,
        "alerts": alerts,
        "keywords": keywords,
        "summary": executive_summary
    }