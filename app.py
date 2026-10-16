import os
import uuid
import json
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file,
)

# Local NLP utilities
from nlp.preprocessing import extract_text_from_file
from nlp.extraction import extract_information

app = Flask(__name__)
# Secret key is required for flash messages to work
app.config["SECRET_KEY"] = "tenderiq-secure-key-12345"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB limit
app.config["UPLOAD_EXTENSIONS"] = [".pdf", ".txt"]
app.config["UPLOAD_PATH"] = os.path.join(os.getcwd(), "uploads")
os.makedirs(app.config["UPLOAD_PATH"], exist_ok=True)


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/history')
def history():
    return "History page – to be implemented."

@app.route('/analyze', methods=["GET", "POST"])
def analyze():
    if request.method == "POST":
        uploaded_file = request.files.get("tender_file")
        pasted_text = request.form.get("tender_text")
        source = None
        raw_text = ""
        filename = ""

        # 1. Uploaded file handling
        if uploaded_file and uploaded_file.filename:
            filename = uploaded_file.filename
            ext = os.path.splitext(filename)[1].lower()
            if ext not in app.config["UPLOAD_EXTENSIONS"]:
                flash("Unsupported file type – only PDF or TXT are allowed.", "error")
                return redirect(request.url)
            
            safe_name = f"{uuid.uuid4().hex}{ext}"
            file_path = os.path.join(app.config["UPLOAD_PATH"], safe_name)
            uploaded_file.save(file_path)
            try:
                raw_text = extract_text_from_file(file_path)
                source = f"File: {filename}"
            except Exception as exc:
                flash(f"Error extracting text from file: {exc}", "error")
                return redirect(request.url)

        # 2. Pasted text handling
        elif pasted_text and pasted_text.strip():
            raw_text = pasted_text.strip()
            source = "Pasted text"

        # 3. Sample tender loading
        elif request.form.get("load_sample") == "true":
            sample_path = os.path.join("data", "sample_tender.txt")
            try:
                with open(sample_path, "r", encoding="utf-8") as f:
                    raw_text = f.read()
                source = "Sample tender"
            except FileNotFoundError:
                flash("Sample tender file not found on the server.", "error")
                return redirect(request.url)

        else:
            flash("Please provide a file, paste text, or load the sample tender.", "warning")
            return redirect(request.url)

        # 4. Run the NLP extraction pipeline
        try:
            extraction_result = extract_information(raw_text)
        except Exception as e:
            flash(f"NLP Processing Error: {str(e)}", "error")
            return redirect(request.url)

        # Store the full result temporarily so the user can download it
        result_id = uuid.uuid4().hex
        result_path = os.path.join(app.config["UPLOAD_PATH"], f"result_{result_id}.json")
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(
                {"source": source, "text": raw_text, "extraction": extraction_result},
                f,
                ensure_ascii=False,
                indent=2,
            )

        # Render results page
        return render_template(
            "results.html",
            source=source,
            extraction=extraction_result,
            result_id=result_id,
        )

    # GET – simply show the upload form.
    return render_template("analyze.html")

@app.route('/download/<result_id>')
def download_result(result_id):
    result_path = os.path.join(app.config["UPLOAD_PATH"], f"result_{result_id}.json")
    if not os.path.exists(result_path):
        flash("Requested analysis result not found.", "error")
        return redirect(url_for("index"))
    return send_file(
        result_path,
        as_attachment=True,
        download_name="tender_analysis_result.json",
    )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")