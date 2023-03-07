
import json
from pathlib import Path

WEBAPP_DIR = Path(__file__).parent
BASE_DIR = WEBAPP_DIR.parent
REPORTS_DIR = BASE_DIR / "cache"

def combine_reports():
    reports = []
    for reports_file in REPORTS_DIR.glob("*.json"):
        with reports_file.open() as f:
            reports.append(json.load(f))

    return reports

def main():
    reports = combine_reports()
    combined_file = WEBAPP_DIR / 'src' / 'data' / 'reports.json'
    combined_file.write_text(json.dumps(reports, indent=2))

if __name__ == "__main__":
    main()
    