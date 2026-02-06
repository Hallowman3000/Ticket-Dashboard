import pdfplumber
import re

text_pages = []
with pdfplumber.open("Ticket-107668.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        text_pages.append({
            "page": i + 1,
            "text": page.extract_text()
        })

def classify_message(text):
    t = text.lower()
    if "urgently" in t:
        return "escalation"
    if "synced" in t:
        return "resolution"
    if "confirmed" in t:
        return "confirmation"
    return "general"


def safe_regex_search(pattern, text, group=1, default="N/A"):
    match = re.search(pattern, text)
    return match.group(group) if match else default

# Extract metadata from first page
header_text = text_pages[0]["text"]

metadata = {
    "ticket_id": safe_regex_search(r"Ticket #(\d+)", header_text),
    "status": safe_regex_search(r"Status\s+(\w+)", header_text),
    "customer": safe_regex_search(r"Name\s+(.+)", header_text),
    "email": safe_regex_search(r"Email\s+([\w\.-]+@[\w\.-]+)", header_text),
    "department": safe_regex_search(r"Department\s+(.+)", header_text),
    "created_date": safe_regex_search(r"Create Date\s+(.+)", header_text),
    "sender": safe_regex_search(r"Sender\s+(.+)", header_text),
    "company": safe_regex_search(r"Company\s+(.+)", header_text)
}

# Extract issue details from second page
issue_page = text_pages[1]["text"] if len(text_pages) > 1 else ""

invoice_numbers = re.findall(r"\b\d{6}\b", issue_page)

error = None
if "error" in issue_page.lower():
    error = "Token not active error"

# Extract messages from pages 2-7
message_pattern = re.compile(
    r"(\d{1,2}/\d{1,2}/\d{2}\s+\d{1,2}:\d{2}\s+[AP]M)\s+([A-Za-z ]+)"
)

messages = []

for page in text_pages[1:7]:
    matches = message_pattern.finditer(page["text"])
    for m in matches:
        msg_text = page["text"]
        messages.append({
            "timestamp": m.group(1),
            "sender": m.group(2),
            "classification": classify_message(msg_text),
            "raw_text": msg_text
        })

# Compile results
results = {
    "metadata": metadata,
    "invoice_numbers": invoice_numbers,
    "error": error,
    "messages": messages
}

# Output results
import json

print(json.dumps(results, indent=2))

# Optionally save to file
with open("ticket_data.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nExtracted data saved to ticket_data.json")
print(f"Found {len(messages)} messages")
print(f"Found {len(invoice_numbers)} invoice numbers")
