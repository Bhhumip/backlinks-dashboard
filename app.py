print("App.py started")

from flask import Flask, jsonify, render_template, request
import pandas as pd
from pdf_processor import process_all_pdfs

app = Flask(__name__)

INPUT_FOLDER = "Backlinks"
OUTPUT_FOLDER = "cleaned_outputs"
CSV_PATH = f"{OUTPUT_FOLDER}/ALL_BACKLINKS_COMBINED.csv"

# ---------- UI ----------
@app.route("/")
def home():
    return render_template("index.html")

# ---------- API: Run PDF Processing ----------
@app.route("/api/process")
def process_pdfs():
    process_all_pdfs(INPUT_FOLDER, OUTPUT_FOLDER)
    return jsonify({"status": "PDFs processed successfully"})

# ---------- API: Get Backlinks (DataTables server-side) ----------
@app.route("/api/backlinks")
def get_backlinks():

    # ---------------- DataTables params ----------------
    draw = int(request.args.get("draw", 1))
    start = int(request.args.get("start", 0))
    length = int(request.args.get("length", 10))

    # ---------------- Filters ----------------
    da_min = request.args.get("da_min", type=int)
    da_max = request.args.get("da_max", type=int)
    source_url = request.args.get("source_url", "").lower()
    target_url = request.args.get("target_url", "").lower()

    # ---------------- Load CSV ----------------
    df = pd.read_csv(CSV_PATH)

    # ---------------- Clean URLs ----------------
    def extract_url(x):
        if isinstance(x, str) and x.startswith('=HYPERLINK'):
            return x.split('"')[1]
        return x

    df["Source_url"] = df["Source_url"].apply(extract_url)
    df["Target_url"] = df["Target_url"].apply(extract_url)

    records_total = len(df)

    # ---------------- Apply filters ----------------
    if da_min is not None:
        df = df[df["DA"] >= da_min]

    if da_max is not None:
        df = df[df["DA"] <= da_max]

    if source_url:
        df = df[df["Source_url"].str.lower().str.contains(source_url, na=False)]

    if target_url:
        df = df[df["Target_url"].str.lower().str.contains(target_url, na=False)]

    records_filtered = len(df)

    # ---------------- Pagination ----------------
    df = df.iloc[start:start + length]

    # ---------------- Response ----------------
    return jsonify({
        "draw": draw,
        "recordsTotal": records_total,
        "recordsFiltered": records_filtered,
        "data": df.to_dict(orient="records")
    })

if __name__ == "__main__":
    app.run(debug=True)

