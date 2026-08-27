# SIR Data Repository

Booth-wise electoral roll deletion data for the West Bengal Special Intensive Revision (SIR) 2026, published by [Sabar Institute](https://sabarinstitute.org).

Live site: **https://sabar-institute.github.io/sir/**

The repository holds the extracted supplementary deletion lists for all **294 assembly constituencies** across **23 districts**, covering roughly **2.7 million** deletion records, plus the Appellate Tribunal adjudication lists.

## What is in here

```
AC/<no>_<Name>/          one folder per assembly constituency (294 total)
  deletion.csv           merged, phase-tagged deletion records
  meta.json              AC number, name, district, muslim population pct, phases present
data/
  assemblies.json        per-AC summary stats used by the site
  tribunal.json          Appellate Tribunal deleted lists (list 1, list 2, ...)
  team.json              team profiles rendered on the site
  all_deletions.xlsx     every AC as a separate sheet (Git LFS, ~123 MB)
tools/                   Python scripts for ingest and export
index.html               main site: search, AC browser, tribunal lists
assembly.html            per-AC detail page
assets/                  logos and images
```

### deletion.csv columns

| Column | Meaning |
| --- | --- |
| `phase` | supplementary list phase the record came from (`1`, `2`, ... `4a`, `12a`) |
| `pdf_file` | source ECI PDF filename |
| `part_no`, `page_no`, `box_no` | location of the record inside that PDF |
| `epic` | voter EPIC number |
| `name` | voter name as printed (Bengali script) |
| `gender` | Male / Female / Others, blank when the source PDF left it blank |
| `ocr_pass` | OCR pass that produced the row |
| `warning`, `repeat` | extraction flags |
| `religion` | derived classification, Muslim / Non-Muslim |

`religion`, `ocr_pass`, `warning`, `repeat` and `confidence` are excluded from the published XLSX export.

### meta.json

```json
{
  "ac_no": 86,
  "ac_name": "Santipur",
  "district": "Nadia",
  "muslim_population_pct": "16.07",
  "phases": ["2", "3", "4", "4a", "5", "6", "7", "8", "9", "10", "11", "12", "12a", "14"]
}
```

`muslim_population_pct` is the AC level census share, not a deletion figure. It is `null` where no reliable figure exists.

## Downloads

The full workbook is served from a GitHub Release, not from Pages, because it exceeds the Pages size limit:

**https://github.com/sabar-institute/sir/releases/download/data-2026-08/all_deletions.xlsx**

Per AC CSVs can be fetched directly from this repo, for example `AC/86_Santipur/deletion.csv`.

## Tools

All scripts are plain Python 3. Only `generate_all_xlsx.py` needs a third party package.

```bash
pip install openpyxl
```

**`tools/merge_phases.py`** merges per phase CSVs in `AC/<ac>/deletion/` into a single phase tagged `deletion.csv`.

```bash
python3 tools/merge_phases.py
```

**`tools/ingest_phases.py`** ingests raw OCR phase CSVs for one AC, rewrites `deletion.csv`, updates `meta.json` and refreshes the AC entry in `data/assemblies.json`. Safe to re run; already ingested phases are skipped.

```bash
python3 tools/ingest_phases.py 52_Mothabari /path/to/ocr_output
```

**`tools/csv_to_tribunal.py`** appends a new Appellate Tribunal list to `data/tribunal.json`.

```bash
python3 tools/csv_to_tribunal.py list2.csv \
  --id list2 \
  --list-no 02 \
  --title "Appellate Tribunal Deleted list 2" \
  --date-short "01.05.26" \
  --date-long "1 May 2026" \
  --description "Voters declared not eligible, adjudicated supplementary deletion list (S25)."
```

**`tools/generate_all_xlsx.py`** rebuilds `data/all_deletions.xlsx` from every `AC/*/deletion.csv`, one sheet per AC, with restricted columns dropped.

```bash
python3 tools/generate_all_xlsx.py
```

After regenerating the workbook, upload it to the GitHub Release rather than committing a new copy to Pages.

## Running the site locally

Both pages fetch data over HTTP, so open them through a server and not from `file://`.

```bash
python3 -m http.server 8000
# then visit http://localhost:8000/
```

## Git LFS

`data/all_deletions.xlsx` is tracked with Git LFS. Install LFS before cloning if you want the real file instead of a pointer.

```bash
git lfs install
git clone git@github.com:sabar-institute/sir.git
```

## Data notes

- Records come from OCR of the official ECI supplementary PDFs. Errors are possible; `warning` and `ocr_pass` flag rows that needed extra handling.
- Blank gender values are preserved as blank rather than guessed. `deleted_other` in `assemblies.json` counts only records explicitly marked Others.
- Tribunal lists carry fresh exclusions only. Deletions already present in an earlier supplementary list are not repeated there.
- Every field traces back to a source PDF through `pdf_file`, `part_no`, `page_no` and `box_no`, so any row can be verified against the original document.

## Licence and use

Data is published for research, journalism and public scrutiny. Please credit Sabar Institute and link back to the repository when you reuse it.
