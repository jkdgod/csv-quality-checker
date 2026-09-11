#!/usr/bin/env python3
"""Check a CSV file for common structural and data-quality issues."""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable


def read_csv(path: Path) -> tuple[list[str], list[list[str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    if not rows:
        raise ValueError("The CSV file is empty.")
    header = rows[0]
    if not header or not any(cell.strip() for cell in header):
        raise ValueError("The CSV file does not contain a usable header row.")
    return header, rows[1:]


def normalize_row(row: Iterable[str]) -> tuple[str, ...]:
    return tuple(cell.strip() for cell in row)


def analyze(header: list[str], rows: list[list[str]], required_columns: list[str]) -> dict:
    expected_width = len(header)
    inconsistent_rows = [index + 2 for index, row in enumerate(rows) if len(row) != expected_width]
    normalized_rows = [normalize_row(row) for row in rows if len(row) == expected_width]
    duplicates = sum(count - 1 for count in Counter(normalized_rows).values() if count > 1)

    missing_by_column: dict[str, int] = {column: 0 for column in header}
    for row in rows:
        padded = row + [""] * max(0, expected_width - len(row))
        for index, column in enumerate(header):
            if index >= len(padded) or not padded[index].strip():
                missing_by_column[column] += 1

    missing_by_column = {column: count for column, count in missing_by_column.items() if count}
    normalized_headers = {column.strip().casefold() for column in header}
    absent_required = [column for column in required_columns if column.casefold() not in normalized_headers]

    return {
        "columns": len(header),
        "rows": len(rows),
        "inconsistent_rows": inconsistent_rows,
        "duplicate_rows": duplicates,
        "missing_by_column": missing_by_column,
        "absent_required": absent_required,
    }


def has_findings(result: dict) -> bool:
    return any((
        result["inconsistent_rows"],
        result["duplicate_rows"],
        result["missing_by_column"],
        result["absent_required"],
    ))


def print_report(path: Path, result: dict, required_columns: list[str]) -> None:
    print("CSV Quality Report")
    print("==================")
    print(f"File: {path}")
    print(f"Columns: {result['columns']}")
    print(f"Data rows: {result['rows']}")

    if required_columns:
        print("\nRequired columns")
        print("----------------")
        if result["absent_required"]:
            print("Missing: " + ", ".join(result["absent_required"]))
        else:
            print("All required columns are present.")

    print("\nFindings")
    print("--------")
    if not has_findings(result):
        print("No data-quality findings detected.")
    else:
        if result["inconsistent_rows"]:
            row_numbers = ", ".join(str(row) for row in result["inconsistent_rows"])
            print(f"Inconsistent row widths: {len(result['inconsistent_rows'])} (CSV rows: {row_numbers})")
        if result["duplicate_rows"]:
            print(f"Duplicate rows: {result['duplicate_rows']}")
        if result["missing_by_column"]:
            print("Missing values:")
            for column, count in result["missing_by_column"].items():
                print(f"  - {column}: {count}")
        if result["absent_required"]:
            print("Required columns missing: " + ", ".join(result["absent_required"]))

    status = "FINDINGS PRESENT" if has_findings(result) else "PASS"
    print(f"\nStatus: {status}")


def parse_required_columns(value: str) -> list[str]:
    return [column.strip() for column in value.split(",") if column.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check a CSV file for common data-quality issues.")
    parser.add_argument("csv_file", type=Path, help="Path to the CSV file to check")
    parser.add_argument(
        "--required-columns",
        default="",
        help="Comma-separated columns that must exist in the header",
    )
    parser.add_argument(
        "--fail-on-findings",
        action="store_true",
        help="Exit with status 1 when findings are present",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.csv_file.is_file():
        print(f"Error: file not found: {args.csv_file}", file=sys.stderr)
        return 2

    try:
        header, rows = read_csv(args.csv_file)
    except (OSError, UnicodeDecodeError, csv.Error, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2

    required_columns = parse_required_columns(args.required_columns)
    result = analyze(header, rows, required_columns)
    print_report(args.csv_file, result, required_columns)
    return 1 if args.fail_on_findings and has_findings(result) else 0


if __name__ == "__main__":
    raise SystemExit(main())
