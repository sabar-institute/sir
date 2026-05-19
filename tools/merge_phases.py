#!/usr/bin/env python3
"""Merge per-phase CSVs into single deletion.csv with phase column per AC."""
import os, csv, re, glob

AC_ROOT = os.path.join(os.path.dirname(__file__), '..', 'AC')

def extract_phase(filename):
    m = re.match(r'phase_?(\w+)\.csv', filename)
    return m.group(1) if m else None

def natural_sort_key(ph):
    """Sort phase keys numerically then alphabetically: 1,2,3,4,4a,5..."""
    m = re.match(r'^(\d+)(.*)$', ph)
    if m:
        return (int(m.group(1)), m.group(2))
    return (9999, ph)

def merge_ac(ac_dir):
    # Support both 'deletion' and 'deletions' subdir names
    del_dir = None
    for name in ('deletion', 'deletions'):
        candidate = os.path.join(ac_dir, name)
        if os.path.isdir(candidate):
            del_dir = candidate
            break
    if not del_dir:
        return 0

    phase_files = {}
    for f in os.listdir(del_dir):
        if not f.endswith('.csv'):
            continue
        ph = extract_phase(f)
        if ph:
            phase_files[ph] = os.path.join(del_dir, f)

    if not phase_files:
        return 0

    out_path = os.path.join(ac_dir, 'deletion.csv')
    total = 0
    COLS = ['phase', 'pdf_file', 'part_no', 'page_no', 'box_no', 'epic', 'name', 'gender', 'ocr_pass', 'warning', 'repeat', 'religion']

    with open(out_path, 'w', newline='', encoding='utf-8') as out:
        writer = csv.DictWriter(out, fieldnames=COLS, extrasaction='ignore')
        writer.writeheader()
        for ph in sorted(phase_files.keys(), key=natural_sort_key):
            with open(phase_files[ph], newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row['phase'] = ph
                    writer.writerow(row)
                    total += 1

    print(f"  {os.path.basename(ac_dir)}: {len(phase_files)} phases → {total} rows → deletion.csv")
    return total

def main():
    ac_dirs = sorted([
        os.path.join(AC_ROOT, d)
        for d in os.listdir(AC_ROOT)
        if os.path.isdir(os.path.join(AC_ROOT, d)) and not d.startswith('.')
    ])
    grand_total = 0
    for ac_dir in ac_dirs:
        grand_total += merge_ac(ac_dir)
    print(f"\nDone. {grand_total} total rows across {len(ac_dirs)} ACs.")

if __name__ == '__main__':
    main()
