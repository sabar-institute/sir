#!/usr/bin/env python3
"""
Add a new Appellate Tribunal list to data/tribunal.json from a CSV.

Usage:
    python tools/csv_to_tribunal.py LIST.csv \
        --id list2 \
        --list-no 02 \
        --title "Appellate Tribunal Deleted list 2" \
        --date-short "01.05.26" \
        --date-long "1 May 2026" \
        --description "Voters declared not eligible — adjudicated supplementary deletion list (S25)."

CSV must have these columns (any order, header row required):
    ac_no, ac_name, district, pdf_file, part_no, page_no, box_no, epic, name, gender, warning
"""

import argparse
import csv
import json
import sys
from pathlib import Path

TRIBUNAL_JSON = Path(__file__).parent.parent / "data" / "tribunal.json"

REQUIRED_COLS = {"ac_no", "ac_name", "district", "pdf_file",
                 "part_no", "page_no", "box_no", "epic", "name", "gender",
                 "ocr_pass", "warning", "repeat"}

INT_COLS = {"ac_no", "part_no", "page_no", "box_no", "ocr_pass", "repeat"}


NULLABLE_COLS = {"warning", "repeat"}

def parse_row(row: dict) -> dict:
    out = {}
    for k, v in row.items():
        k = k.strip()
        v = v.strip()
        if k in INT_COLS:
            try:
                out[k] = int(v)
            except ValueError:
                out[k] = None if v == "" else v
        elif k in NULLABLE_COLS:
            out[k] = v if v else None
        else:
            out[k] = v
    return out


def main():
    p = argparse.ArgumentParser(description="Append a tribunal list from CSV to tribunal.json")
    p.add_argument("csv_file", help="Path to CSV file")
    p.add_argument("--id",           required=True, help="Unique id, e.g. list2")
    p.add_argument("--list-no",      required=True, help="Display number, e.g. 02")
    p.add_argument("--title",        required=True, help="Full title")
    p.add_argument("--date-short",   required=True, help="Short date, e.g. 01.05.26")
    p.add_argument("--date-long",    required=True, help="Long date, e.g. 1 May 2026")
    p.add_argument("--description",  required=True, help="One-line description")
    p.add_argument("--out", default=str(TRIBUNAL_JSON), help="Output JSON path (default: data/tribunal.json)")
    args = p.parse_args()

    csv_path = Path(args.csv_file)
    if not csv_path.exists():
        sys.exit(f"ERROR: CSV not found: {csv_path}")

    out_path = Path(args.out)

    # Load existing tribunal.json
    if out_path.exists():
        with open(out_path, encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    # Check for duplicate id
    if any(x["id"] == args.id for x in data):
        sys.exit(f"ERROR: id '{args.id}' already exists in {out_path}. Choose a different --id.")

    # Parse CSV
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        cols = set(reader.fieldnames or [])
        missing = REQUIRED_COLS - {c.strip() for c in cols}
        if missing:
            sys.exit(f"ERROR: CSV missing columns: {', '.join(sorted(missing))}")
        rows = [parse_row(r) for r in reader]

    if not rows:
        sys.exit("ERROR: CSV has no data rows.")

    new_list = {
        "id":          args.id,
        "listNo":      args.list_no,
        "title":       args.title,
        "dateShort":   args.date_short,
        "dateLong":    args.date_long,
        "description": args.description,
        "rows":        rows,
    }

    data.append(new_list)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"OK: Added '{args.title}' ({len(rows)} rows) → {out_path}")
    print(f"    Total lists now: {len(data)}")


if __name__ == "__main__":
    main()
