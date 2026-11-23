import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

RAW_DIR = Path("data/raw")
SUBSET_FILE = RAW_DIR / "eu_ai_act_subset.txt"
PROVENANCE_FILE = RAW_DIR / "eu_ai_act_subset.provenance.json"

DOC_ID = "eu_ai_act_2024_1689"
SOURCE_URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:02024R1689-20260727"
REGULATION_ID = "Regulation (EU) 2024/1689"
CONSOLIDATED_VERSION = "27.07.2026"


def fetch() -> str:
    text = SUBSET_FILE.read_text(encoding="utf-8")
    checksum = hashlib.sha256(text.encode("utf-8")).hexdigest()

    provenance = {
        "doc_id": DOC_ID,
        "source_url": SOURCE_URL,
        "regulation_id": REGULATION_ID,
        "consolidated_version": CONSOLIDATED_VERSION,
        "fetch_timestamp": datetime.now(timezone.utc).isoformat(),
        "checksum": checksum,
    }
    PROVENANCE_FILE.write_text(json.dumps(provenance, indent=2))

    print(f"Loaded {SUBSET_FILE} ({len(text)} chars), checksum {checksum[:12]}...")
    return text, provenance


if __name__ == "__main__":
    fetch()