import re
import time
from pathlib import Path

import pandas as pd
import requests

BASE = "https://support.dataposit.co.ke"
COOKIE_NAME = "OSTSESSID"
COOKIE_VALUE = "upg9nl4sr795m2f5bjt83lg1gb" 

OUT_DIR = Path(r"C:\Users\ADMIN\Desktop\Ticket dashboard\email details")
OUT_DIR.mkdir(parents=True, exist_ok=True)

CSV_PATH = r"C:\Users\ADMIN\Desktop\Ticket dashboard\combined_tickets_all_sources.csv"

ID_RE = re.compile(r"tickets\.php\?id=(\d+)")


def find_internal_id(session: requests.Session, ticket_number: str) -> int | None:
    """
    Searches staff ticket list for the visible Ticket Number.
    Handles both direct redirects and list results.
    """
    search_url = f"{BASE}/scp/tickets.php?a=search&query={ticket_number}"

    try:
        r = session.get(search_url, allow_redirects=True, timeout=30)
    except requests.RequestException as e:
        print(f"  ! Network error searching for {ticket_number}: {e}")
        return None

    if "login.php" in r.url.lower():
        raise RuntimeError("Session expired (redirected to login). Update your OSTSESSID.")

    # FIX 2: Check if osTicket redirected us directly to the ticket (Common for exact matches)
    # The URL will look like: .../scp/tickets.php?id=12345
    if "id=" in r.url:
        match = re.search(r"[?&]id=(\d+)", r.url)
        if match:
            return int(match.group(1))

    specific_pattern = re.compile(rf'tickets\.php\?id=(\d+)[^>]*?>(?:\s*<[^>]+>\s*)*{ticket_number}', re.IGNORECASE)
    
    m = specific_pattern.search(r.text)
    if m:
        return int(m.group(1))

    m_generic = ID_RE.search(r.text)
    if m_generic:
        found_id = int(m_generic.group(1))
       
        return found_id

    return None


def download_zip(session: requests.Session, internal_id: int) -> Path:
    url = f"{BASE}/scp/tickets.php?id={internal_id}&a=zip&notes=1&tasks=1"
    out_file = OUT_DIR / f"ticket-internal-{internal_id}.zip"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": f"{BASE}/scp/tickets.php?id={internal_id}",
    }

    try:
        r = session.get(url, headers=headers, stream=True, allow_redirects=True, timeout=60)
    except requests.RequestException as e:
        raise RuntimeError(f"Network error downloading ZIP: {e}")

    if "login.php" in r.url.lower():
        raise RuntimeError("Session expired (redirected to login).")

    ctype = (r.headers.get("Content-Type") or "").lower()
    if "zip" not in ctype:

        raise RuntimeError(f"Expected ZIP, got Content-Type={ctype}. Response text prefix: {r.text[:100]}")

    with open(out_file, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 128):
            if chunk:
                f.write(chunk)

    return out_file


def main():
    print(f"Reading CSV from: {CSV_PATH}")
    try:
        df = pd.read_csv(CSV_PATH)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # Normalize ticket numbers to string and remove empty ones
    if "Ticket Number" not in df.columns:
        print("Error: CSV is missing 'Ticket Number' column.")
        return
        
    ticket_numbers = df["Ticket Number"].dropna().astype(str).unique().tolist()
    print(f"Found {len(ticket_numbers)} unique tickets to process.")

    with requests.Session() as s:
        # Set the cookie
        s.cookies.set(COOKIE_NAME, COOKIE_VALUE, domain="support.dataposit.co.ke", path="/")

        # Quick auth check
        try:
            chk = s.get(f"{BASE}/scp/", allow_redirects=True, timeout=30)
            if "login.php" in chk.url.lower():
                raise RuntimeError("Not logged in. Update OSTSESSID cookie value.")
        except Exception as e:
             print(f"Critical Error during auth check: {e}")
             return
       
        for i, tn in enumerate(ticket_numbers, 1):
            print(f"[{i}/{len(ticket_numbers)}] Processing {tn}...", end=" ", flush=True)
            try:
                internal_id = find_internal_id(s, tn)
                
                if internal_id is None:
                    print(f"✗ Could not find internal ID (Search failed or no match)")
                    continue

                # Small sanity check: if the internal_id is 3043, and the ticket number ISN'T the one for 3043, warn.
                # (You can remove this if 3043 is actually one of your targets)
                if internal_id == 3043 and tn != "YOUR_TICKET_NUMBER_FOR_3043": 
                     # This suggests the search failed and we fell back to the default list again
                     pass 

                out = download_zip(s, internal_id)
                print(f"✓ Found ID {internal_id} -> Saved to {out.name}")

                time.sleep(1)  # Be polite to the server
            except Exception as e:
                print(f"✗ Error: {e}")
                time.sleep(2)

if __name__ == "__main__":
    main()