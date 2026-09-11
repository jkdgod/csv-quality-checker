# CSV Quality Checker

A lightweight, dependency-free Python command-line utility that checks common CSV data-quality conditions and prints a readable report.

This project uses only synthetic sample data. It is intended as a small portfolio example of Python automation, data-quality checks, and clear operational reporting.

## Checks included

- File readability and CSV header detection
- Row and column counts
- Inconsistent row widths
- Blank or missing values by column
- Duplicate data rows
- Optional required-column validation

## Requirements

- Python 3.9 or later
- No third-party packages

## Quick start

```bash
python csv_quality_checker.py sample_data/clean_contacts.csv
```

Check a file against required columns:

```bash
python csv_quality_checker.py sample_data/problem_contacts.csv --required-columns first_name,last_name,email
```

Return a nonzero exit status when quality findings are present:

```bash
python csv_quality_checker.py sample_data/problem_contacts.csv --fail-on-findings
```

## Example output

```text
CSV Quality Report
==================
File: sample_data/problem_contacts.csv
Columns: 4
Data rows: 5

Required columns
----------------
All required columns are present.

Findings
--------
Inconsistent row widths: 1
Duplicate rows: 1
Missing values:
  - email: 1
  - department: 1

Status: FINDINGS PRESENT
```

## Exit codes

| Code | Meaning |
|---:|---|
| 0 | Check completed; no findings, or findings were allowed |
| 1 | Check completed and findings were present with `--fail-on-findings` |
| 2 | Input, parsing, or argument error |

## Project layout

```text
.
├── csv_quality_checker.py
├── sample_data/
│   ├── clean_contacts.csv
│   └── problem_contacts.csv
├── tests/
│   └── test_csv_quality_checker.py
├── .gitignore
└── LICENSE
```

## Data handling

Do not commit production exports, employee/customer data, credentials, or other restricted information. Use synthetic or approved sanitized data for demonstrations.

## License

MIT. See `LICENSE`.
