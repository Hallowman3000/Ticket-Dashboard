import argparse
import json
import re
import hashlib
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

import pdfplumber


# -----------------------------
# Helpers
# -----------------------------
def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def sha1_short(data: bytes, n: int = 12) -> str:
    return hashlib.sha1(data).hexdigest()[:n]


def normalize_spaces(s: str) -> str:
    s = s.replace("\u00a0", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


# -----------------------------
# CONFIG (compiled at import time)
# -----------------------------
METADATA_PATTERNS: Dict[str, List[re.Pattern]] = {
    "ticket_number": [re.compile(p, re.I) for p in [
        r"Ticket\s*#\s*([A-Z0-9\-]+)",
        r"Ticket\s*Number\s*[:#]?\s*([A-Z0-9\-]+)",
        r"\bth(\d{3,})\b",
    ]],
    "status": [re.compile(p, re.I) for p in [
        r'"Status\s*"\s*,[\s\n]*"([^"]+)"',
        r"\bStatus\b\s*[:#]?\s*([A-Za-z ]{3,30})",
    ]],
    "department": [re.compile(p, re.I) for p in [
        r'"Department\s*"\s*,[\s\n]*"([^"]+)"',
        r"\bDepartment\b\s*[:#]?\s*([A-Za-z0-9 &/\-]{2,60})",
    ]],
    "priority": [re.compile(p, re.I) for p in [
        r'"Priority\s*"\s*,[\s\n]*"([^"]+)"',
        r"\bPriority\b\s*[:#]?\s*([A-Za-z0-9 \-]{2,30})",
    ]],
    "subject": [re.compile(p, re.I) for p in [
        r'"Subject\s*"\s*,[\s\n]*"([^"]+)"',
        r"\bSubject\b\s*[:#]?\s*(.{5,120})",
    ]],
}

CLASS_RULES: Dict[str, List[str]] = {
    "billing": ["invoice", "payment", "mpesa", "billing", "charge", "quotation", "quote"],
    "connectivity": ["internet", "link down", "latency", "packet loss", "fiber", "uplink", "wan"],
    "hardware": ["router", "switch", "access point", "mikrotik", "ubiquiti", "cisco", "device"],
    "software": ["bug", "error", "crash", "upgrade", "update", "version", "license", "install"],
    "account_access": ["login", "password", "access", "credentials", "2fa", "otp", "locked"],
    "general_support": ["help", "support", "issue", "problem", "request"],
}


# -----------------------------
# Data model
# -----------------------------
@dataclass(frozen=True)
class PdfRecord:
    record_id: str
    source_file: str
    extracted_at: str = field(default_factory=now_iso)

    num_pages: int = 0
    text: str = ""
    metadata: Dict[str, Optional[str]] = field(default_factory=dict)
    labels: Dict[str, Any] = field(default_factory=dict)


# -----------------------------
# Processor
# -----------------------------
class TicketProcessor:
    def __init__(self, patterns: Dict[str, List[re.Pattern]], rules: Dict[str, List[str]]):
        self.patterns = patterns
        self.rules = rules
        self.class_regex = self._compile_class_rules(rules)

    @staticmethod
    def _compile_class_rules(rules: Dict[str, List[str]]) -> Dict[str, List[re.Pattern]]:
        """
        Compile keyword patterns.
        - single words use word boundaries: \bword\b
        - phrases use plain substring regex with escaping
        """
        compiled: Dict[str, List[re.Pattern]] = {}
        for label, kws in rules.items():
            pats: List[re.Pattern] = []
            for kw in kws:
                k = (kw or "").strip().lower()
                if not k:
                    continue
                if " " in k:
                    pats.append(re.compile(re.escape(k), re.I))
                else:
                    pats.append(re.compile(rf"\b{re.escape(k)}\b", re.I))
            compiled[label] = pats
        return compiled

    def extract_text(self, pdf_path: Path) -> Tuple[str, int]:
        parts: List[str] = []
        num_pages = 0

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                num_pages += 1
                txt = page.extract_text() or ""
                txt = normalize_spaces(txt)
                if txt:
                    parts.append(txt)

        full_text = "\n\n".join(parts).strip()
        return full_text, num_pages

    def get_metadata(self, text: str) -> Dict[str, Optional[str]]:
        md: Dict[str, Optional[str]] = {}
        for field_name, regexes in self.patterns.items():
            value: Optional[str] = None
            for r in regexes:
                m = r.search(text)
                if m:
                    value = normalize_spaces(m.group(1))
                    break
            md[field_name] = value
        return md

    def classify(self, text: str, metadata: Dict[str, Optional[str]]) -> Dict[str, Any]:
        subj = metadata.get("subject") or ""
        dept = metadata.get("department") or ""
        body = text or ""

        scores: Dict[str, int] = {}
        for label, patterns in self.class_regex.items():
            score = 0
            for pat in patterns:
                score += len(pat.findall(body))
                score += 3 * len(pat.findall(subj))
                score += 2 * len(pat.findall(dept))
            scores[label] = score

        primary = max(scores, key=scores.get) if scores else "unclassified"
        confidence = scores.get(primary, 0)
        if confidence == 0:
            primary = "unclassified"

        return {"primary": primary, "confidence": confidence, "scores": scores}


# -----------------------------
# IO pipeline
# -----------------------------
def iter_pdfs(input_dir: Path) -> List[Path]:
    # returns a stable order (helps reproducibility)
    return sorted([p for p in input_dir.rglob("*.pdf") if p.is_file()])


def build_record_id(pdf_path: Path, text: str) -> str:
    # stable + low collision: absolute path + size + snippet
    base = f"{str(pdf_path)}||{pdf_path.stat().st_size}||{len(text)}||{text[:2000]}"
    return sha1_short(base.encode("utf-8", errors="ignore"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract + classify PDFs from a directory (PDFs only)")
    parser.add_argument(
        "--input-dir",
        default=r"C:\Users\ADMIN\Desktop\Ticket dashboard\emails extracted",
        help="Directory containing PDFs",
    )
    parser.add_argument(
        "--output-dir",
        default=r"C:\Users\ADMIN\Desktop\Ticket dashboard\pdf_output",
        help="Directory for records.jsonl and errors.jsonl",
    )
    parser.add_argument(
        "--write-texts",
        action="store_true",
        help="Also write extracted texts to output-dir/texts/<record_id>.txt",
    )
    args = parser.parse_args()

    input_dir: Path = Path(args.input_dir)
    output_dir: Path = Path(args.output_dir)

    safe_mkdir(output_dir)

    records_path: Path = output_dir / "records.jsonl"
    errors_path: Path = output_dir / "errors.jsonl"

    texts_dir: Optional[Path] = (output_dir / "texts") if args.write_texts else None
    if texts_dir is not None:
        safe_mkdir(texts_dir)

    processor = TicketProcessor(patterns=METADATA_PATTERNS, rules=CLASS_RULES)

    pdf_paths: List[Path] = iter_pdfs(input_dir)

    sources_scanned: int = len(pdf_paths)
    pdfs_processed: int = 0
    pdfs_failed: int = 0

    with records_path.open("w", encoding="utf-8") as rf, errors_path.open("w", encoding="utf-8") as ef:
        for pdf_path in pdf_paths:
            try:
                text, num_pages = processor.extract_text(pdf_path)
                metadata = processor.get_metadata(text)
                labels = {"rule_based": processor.classify(text, metadata)}

                record_id = build_record_id(pdf_path, text)

                record = PdfRecord(
                    record_id=record_id,
                    source_file=str(pdf_path),
                    num_pages=num_pages,
                    text=text,
                    metadata=metadata,
                    labels=labels,
                )

                rf.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
                pdfs_processed += 1

                if texts_dir is not None:
                    (texts_dir / f"{record_id}.txt").write_text(text, encoding="utf-8", errors="ignore")

            except Exception as e:
                pdfs_failed += 1
                ef.write(json.dumps({
                    "source_file": str(pdf_path),
                    "error": repr(e),
                    "at": now_iso(),
                }, ensure_ascii=False) + "\n")

    print(f"Done.")
    print(f"PDFs found: {sources_scanned}")
    print(f"PDFs processed: {pdfs_processed}")
    print(f"PDFs failed: {pdfs_failed}")
    print(f"Wrote: {records_path}")
    print(f"Wrote: {errors_path}")
    if texts_dir is not None:
        print(f"Wrote texts to: {texts_dir}")


if __name__ == "__main__":
    main()
