import unittest

from bom_analyzer.analyzer import analyze


class AnalyzerTests(unittest.TestCase):
    def test_valid_row(self):
        report = analyze([
            {
                "MPN": "STM32F103C8T6",
                "Manufacturer": "STMicroelectronics",
                "Description": "Microcontroller",
                "Qty": "1",
                "RefDes": "U1",
            }
        ])
        self.assertEqual(report["summary"]["errors"], 0)
        self.assertEqual(report["summary"]["unique_components"], 1)

    def test_duplicate_mpn_is_consolidated(self):
        rows = [
            {"MPN": "ABC", "Manufacturer": "Maker", "Description": "Part", "Qty": "2", "RefDes": "R1 R2"},
            {"MPN": "abc", "Manufacturer": "Maker", "Description": "Part", "Qty": "3", "RefDes": "R3 R4 R5"},
        ]
        report = analyze(rows)
        self.assertEqual(report["summary"]["unique_components"], 1)
        self.assertEqual(report["summary"]["total_quantity"], 5)
        self.assertTrue(any(issue["code"] == "duplicate_mpn" for issue in report["issues"]))

    def test_invalid_quantity_is_error(self):
        report = analyze([{"MPN": "ABC", "Qty": "1.5"}])
        self.assertTrue(any(issue["code"] == "invalid_quantity" for issue in report["issues"]))

    def test_duplicate_reference_is_error(self):
        rows = [
            {"MPN": "A", "Qty": "1", "RefDes": "U1"},
            {"MPN": "B", "Qty": "1", "RefDes": "U1"},
        ]
        report = analyze(rows)
        self.assertTrue(any(issue["code"] == "duplicate_reference" for issue in report["issues"]))

    def test_missing_required_columns(self):
        report = analyze([{"Description": "Unknown part"}])
        codes = [issue["code"] for issue in report["issues"]]
        self.assertGreaterEqual(codes.count("missing_column"), 2)


if __name__ == "__main__":
    unittest.main()
