import zipfile
import io
import re
import json
from datetime import datetime

import pdfplumber

# ---------- CONFIG ----------
import sys
import os

# ---------- CONFIG ----------
DEFAULT_ZIP = "ticket-964007.zip"
FALLBACK_ZIP = "email details - Copy.zip"

if len(sys.argv) > 1:
    ZIP_PATH = sys.argv[1]
elif os.path.exists(DEFAULT_ZIP):
    ZIP_PATH = DEFAULT_ZIP
elif os.path.exists(FALLBACK_ZIP):
    ZIP_PATH = FALLBACK_ZIP
else:
    print(f"Error: Could not find '{DEFAULT_ZIP}' or '{FALLBACK_ZIP}'.")
    print("Usage: python plumber.py <path_to_zip>")
    sys.exit(1)
OUTPUT_FILE = "extracted_ticket_data.json"

STATUS_KEYWORDS = [
    "open", "opened", "resolved", "closed", "reopened",
    "in progress", "pending", "completed"
]

# ---------- REGEX ----------
DATE_REGEX = r"\b\d{4}-\d{2}-\d{2}\b|\b\d{2}/\d{2}/\d{4}\b"
TIME_REGEX = r"\b\d{2}:\d{2}(:\d{2})?\b"
EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
TICKET_ID_REGEX = r"(ticket\s*#?\s*\d+|\bID[:\s]*\d+)"

# ---------- HELPERS ----------
def extract_text_and_metadata(pdf_bytes):
    text = ""
    metadata = {}

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        metadata = pdf.metadata or {}
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        return text.strip(), metadata, len(pdf.pages)


def find_matches(regex, text):
    return sorted(set(re.findall(regex, text, re.IGNORECASE)))


def extract_status_keywords(text):
    found = set()
    lower = text.lower()
    for kw in STATUS_KEYWORDS:
        if kw in lower:
            found.add(kw)
    return sorted(found)


# ---------- MAIN ----------
def process_zip(zip_path):
    results = []

    with zipfile.ZipFile(zip_path, "r") as z:
        for name in z.namelist():
            if not name.lower().endswith(".pdf"):
                continue

            print(f"Processing PDF: {name}")

            pdf_bytes = z.read(name)
            text, metadata, num_pages = extract_text_and_metadata(pdf_bytes)

            record = {
                "pdf_filename": name,
                "num_pages": num_pages,
                "pdf_metadata": metadata,
                "timestamps": {
                    "dates": find_matches(DATE_REGEX, text),
                    "times": find_matches(TIME_REGEX, text),
                },
                "email_addresses": find_matches(EMAIL_REGEX, text),
                "ticket_ids": find_matches(TICKET_ID_REGEX, text),
                "status_keywords": extract_status_keywords(text),
                "raw_text": text,
                "extracted_at": datetime.utcnow().isoformat()
            }

            results.append(record)

    return results


if __name__ == "__main__":
    data = process_zip(ZIP_PATH)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nExtraction complete → {OUTPUT_FILE}")
