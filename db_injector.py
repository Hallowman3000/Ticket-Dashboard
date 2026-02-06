import argparse, csv, hashlib, io, json, os, re, zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import pdfplumber

# ---------------- CONFIGURATION ----------------

# UPDATED: Patterns now handle the "Table/CSV" style formatting seen in your PDFs
# e.g., "Status\n","Closed\n"
METADATA_PATTERNS = {
    "ticket_number": [
        r"Ticket\s*#\s*([A-Za-z0-9\-]+)", 
        r"Ticket\s*Number\s*[:#]?\s*([A-Za-z0-9\-]+)"
    ],
    "status": [
        r'"Status\s*"\s*,[\s\n]*"([^"]+)"',  # Table format
        r"Status\s*[:#]?\s*([A-Za-z ]+)"      # Standard format
    ],
    "department": [
        r'"Department\s*"\s*,[\s\n]*"([^"]+)"',
        r"Department\s*[:#]?\s*([A-Za-z0-9 &/._-]+)"
    ],
    "created_at_raw": [
        r'"Create\s*Date\s*"\s*,[\s\n]*"([^"]+)"',
        r"Create\s*Date\s*[:#]?\s*(.+)"
    ],
    "from_email": [
        r"Email\s*[:#]?\s*([\w\.-]+@[\w\.-]+\.\w+)",
        r'"Email\s*"\s*,[\s\n]*"([\w\.-]+@[\w\.-]+\.\w+)"'
    ],
    "customer_name": [
        r"Name\s*[:#]?\s*([^\n]+)",
        r'"Name\s*"\s*,[\s\n]*"([^"]+)"'
    ],
}

# UPDATED: Supports newlines between Date and Author, plus new date formats
# Matches: "2/4/26 9:02 AM Sync Invoice\nNorman Mungai"
THREAD_ANCHOR_PATTERN = re.compile(
    r"(?P<ts>"
    r"(?:\d{1,2}/\d{1,2}/(?:\d{2}|\d{4})\s+\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)" # 2/4/26 9:02 AM
    r"|"
    r"(?:\d{4}/\d{2}/\d{2}\s+\d{1,2}:\d{2})"             # 2025/12/05 11:03
    r"|"
    r"(?:\d{1,2}\s+[A-Za-z]+\s+\d{4}\s+\d{1,2}:\d{2})"   # 08 December 2025 09:22
    r")"
    r"(?:.*?)"  # Non-greedy match for Subject line (e.g., "Sync Invoice")
    r"[\r\n]+"  # Must see at least one newline
    r"(?P<author>[A-Za-z][A-Za-z .,'’\-]{1,60})" # The Author Name on the next line
)

# Footer noise to remove so it doesn't clutter the index
FOOTER_PATTERN = re.compile(r"Ticket #\d+ printed by .*? on .*? Page \d+", re.IGNORECASE)

@dataclass
class ThreadItem:
    ts_raw: str
    ts: Optional[datetime]
    author: str
    kind: str
    text: str
    page: int

def normalize_ws(s: str) -> str:
    """Cleans up whitespace and removes quote marks from CSV-style extraction."""
    if not s: return ""
    return " ".join(s.replace('"', '').split()).strip()

def parse_dt(ts: str) -> Optional[datetime]:
    # Normalize: "2/4/26 9:02 AM" -> "2/4/26 9:02 AM"
    # Also handles "08 December 2025 09:22"
    ts_norm = re.sub(r"\s+(am|pm)\b", lambda m: f" {m.group(1).upper()}", normalize_ws(ts), flags=re.IGNORECASE)
    
    fmts = [
        "%m/%d/%Y %I:%M %p", "%m/%d/%y %I:%M %p", # US standard
        "%m/%d/%Y %H:%M", "%m/%d/%y %H:%M",       # US 24hr
        "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M",    # ISO standard
        "%Y/%m/%d %H:%M",                         # Slashes ISO (found in your data)
        "%d %B %Y %H:%M"                          # "08 December 2025 09:22" (found in your data)
    ]
    for f in fmts:
        try: return datetime.strptime(ts_norm, f)
        except: continue
    return None

def extract_content(pdf_bytes: bytes) -> List[Dict]:
    """Reads PDF and strips out the repeated footer noise."""
    pages = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for i, p in enumerate(pdf.pages):
            txt = p.extract_text() or ""
            # Remove footer lines before processing
            txt_clean = FOOTER_PATTERN.sub("", txt)
            pages.append({"page": i + 1, "text": txt_clean})
    return pages

def split_thread_items(pages: List[Dict]) -> List[ThreadItem]:
    # Combine all text with page markers
    big = "".join([f"\n<<P:{p['page']}>>\n{p['text']}" for p in pages])
    
    # Use re.DOTALL so '.' matches newlines (needed to skip the Subject line)
    anchors = list(THREAD_ANCHOR_PATTERN.finditer(big))
    items = []
    
    for idx, m in enumerate(anchors):
        # Text for this item runs until the NEXT anchor starts
        start_idx = m.start()
        end_idx = anchors[idx + 1].start() if idx + 1 < len(anchors) else len(big)
        
        raw_block = big[start_idx:end_idx]
        
        # Extract groups
        ts_raw = m.group("ts")
        author = m.group("author")
        
        # The "Body" is everything after the full match (Timestamp + Subject + Author)
        # We split by the matched string to get the remainder
        full_match_str = m.group(0)
        body_part = raw_block.replace(full_match_str, "", 1)
        
        # Clean up page markers from the body text
        body_clean = re.sub(r"<<P:\d+>>", "", body_part)
        body_clean = normalize_ws(body_clean)
        
        # Find which page this started on
        page_marker = re.search(r"<<P:(\d+)>>", big[:start_idx+20])
        page_num = int(page_marker.group(1)) if page_marker else 1

        # Heuristic for "Kind"
        kind = "message"
        lower_body = body_clean.lower()
        if "internal note" in lower_body: kind = "note"
        elif "status changed" in lower_body: kind = "event"
        
        items.append(ThreadItem(
            ts_raw=normalize_ws(ts_raw),
            ts=parse_dt(ts_raw),
            author=normalize_ws(author),
            kind=kind,
            text=body_clean[:5000], # Cap text size
            page=page_num
        ))
    return items

def process_pdf(pdf_bytes: bytes, zip_n: str, pdf_n: str) -> Dict:
    pages = extract_content(pdf_bytes)
    first_page_text = pages[0]["text"] if pages else ""
    
    # Metadata Extraction
    meta = {}
    for key, patterns in METADATA_PATTERNS.items():
        val = "N/A"
        for pat in patterns:
            # We use MULTILINE to handle the line-by-line nature of the text
            m = re.search(pat, first_page_text, re.MULTILINE | re.IGNORECASE)
            if m:
                val = normalize_ws(m.group(1))
                break
        meta[key] = val

    items = split_thread_items(pages)
    dated_items = sorted([x for x in items if x.ts], key=lambda x: x.ts)

    # Derived Logic:
    # If metadata status is "Closed", but we have no event, assume the last message closed it.
    resolved_at = None
    if "closed" in meta.get("status", "").lower() or "resolved" in meta.get("status", "").lower():
        # Try to find explicit event
        explicit = next((it for it in dated_items if it.kind == "event"), None)
        if explicit:
            resolved_at = explicit.ts
        elif dated_items:
            # Fallback: Last message timestamp
            resolved_at = dated_items[-1].ts

    return {
        "ticket_number": meta.get("ticket_number", "N/A"),
        "metadata": meta,
        "source": {
            "zip": zip_n, 
            "pdf": pdf_n, 
            "hash": hashlib.sha256(pdf_bytes).hexdigest()
        },
        "thread_items": [vars(it) for it in items],
        "derived": {
            "raised_at": dated_items[0].ts.isoformat() if dated_items else None,
            "resolved_at": resolved_at.isoformat() if resolved_at else None,
            "count_messages": len(items)
        }
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--zips-dir", required=True, help="Folder with 199+ zip files")
    parser.add_argument("--out-dir", default="out")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(exist_ok=True, parents=True)
    
    json_path = out_dir / "tickets.jsonl"
    err_path = out_dir / "errors.csv"

    with json_path.open("w", encoding="utf-8") as jf, err_path.open("w", newline="", encoding="utf-8") as ef:
        err_writer = csv.writer(ef)
        err_writer.writerow(["zip", "pdf", "error"])
        
        zip_files = list(Path(args.zips_dir).glob("*.zip"))
        print(f"Found {len(zip_files)} zip files to process...")

        count = 0
        for zpath in zip_files:
            try:
                with zipfile.ZipFile(zpath, "r") as z:
                    # Filter for PDFs, ignore __MACOSX junk
                    pdfs = [n for n in z.namelist() if n.lower().endswith(".pdf") and not n.startswith("__")]
                    
                    if not pdfs:
                        err_writer.writerow([zpath.name, "NO_PDF", "No PDF found inside zip"])
                        continue

                    for pdf_name in pdfs:
                        try:
                            record = process_pdf(z.read(pdf_name), zpath.name, pdf_name)
                            jf.write(json.dumps(record, ensure_ascii=False) + "\n")
                            count += 1
                            if count % 10 == 0: print(f"Processed {count} tickets...", end="\r")
                        except Exception as e:
                            err_writer.writerow([zpath.name, pdf_name, str(e)])
            except Exception as e:
                err_writer.writerow([zpath.name, "ZIP_READ_ERR", str(e)])

    print(f"\nDone. Processed {count} tickets.")

if __name__ == "__main__":
    main()