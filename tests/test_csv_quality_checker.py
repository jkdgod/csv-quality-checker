import tempfile
import unittest
from pathlib import Path

from csv_quality_checker import analyze, read_csv


class CsvQualityCheckerTests(unittest.TestCase):
    def test_analyze_identifies_common_findings(self):
        header = ["first_name", "last_name", "email"]
        rows = [
            ["Avery", "Nguyen", "avery.nguyen@example.com"],
            ["Jordan", "Patel", ""],
            ["Avery", "Nguyen", "avery.nguyen@example.com"],
            ["Morgan", "Reed"],
        ]

        result = analyze(header, rows, ["first_name", "email", "department"])

        self.assertEqual(result["columns"], 3)
        self.assertEqual(result["rows"], 4)
        self.assertEqual(result["inconsistent_rows"], [5])
        self.assertEqual(result["duplicate_rows"], 1)
        self.assertEqual(result["missing_by_column"], {"email": 2})
        self.assertEqual(result["absent_required"], ["department"])

    def test_read_csv_rejects_empty_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "empty.csv"
            path.write_text("", encoding="utf-8")
            with self.assertRaises(ValueError):
                read_csv(path)


if __name__ == "__main__":
    unittest.main()
