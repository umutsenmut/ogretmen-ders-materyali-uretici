import sys
import os
import unittest

# Make sure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsers.pdf_parser import PdfParser
from parsers.word_parser import WordParser
from parsers.excel_parser import ExcelParser


class TestPdfParser(unittest.TestCase):
    def setUp(self):
        self.parser = PdfParser()

    def test_row_to_entry_full(self):
        row = ["1", "Doğal Sayılar", "Kazanım 1", "Açıklama", "Anlatım", "Tahta", "Gözlem", ""]
        entry = self.parser._row_to_entry(row)
        self.assertIsNotNone(entry)
        self.assertEqual(entry["week_number"], "1")
        self.assertEqual(entry["unit_topic"], "Doğal Sayılar")
        self.assertEqual(entry["learning_outcomes"], "Kazanım 1")

    def test_row_to_entry_short_row(self):
        row = ["2", "Kesirler"]
        entry = self.parser._row_to_entry(row)
        self.assertIsNotNone(entry)
        self.assertEqual(entry["week_number"], "2")
        self.assertEqual(entry["unit_topic"], "Kesirler")
        self.assertEqual(entry["learning_outcomes"], "")
        self.assertEqual(entry["assessment"], "")

    def test_row_to_entry_all_empty(self):
        row = ["", "", "", "", "", "", "", ""]
        entry = self.parser._row_to_entry(row)
        self.assertIsNone(entry)

    def test_row_to_entry_none_values(self):
        row = [None, "Geometri", None, None, None, None, None, None]
        entry = self.parser._row_to_entry(row)
        self.assertIsNotNone(entry)
        self.assertEqual(entry["unit_topic"], "Geometri")
        self.assertEqual(entry["week_number"], "")

    def test_column_keys(self):
        self.assertEqual(len(self.parser.COLUMN_KEYS), 8)
        self.assertIn("week_number", self.parser.COLUMN_KEYS)
        self.assertIn("special_days", self.parser.COLUMN_KEYS)

    def test_parse_nonexistent_file(self):
        entries = self.parser.parse("/nonexistent/path/file.pdf")
        self.assertIsInstance(entries, list)
        self.assertGreater(len(entries), 0)
        self.assertIn("Hata", entries[0]["week_number"])


class TestWordParser(unittest.TestCase):
    def setUp(self):
        self.parser = WordParser()

    def test_cells_to_entry_full(self):
        cells = ["3", "Sözcük Türleri", "İsim, fiil ayırt eder", "Açıklama", "Tartışma", "Kitap", "Yazılı sınav", ""]
        entry = self.parser._cells_to_entry(cells)
        self.assertIsNotNone(entry)
        self.assertEqual(entry["week_number"], "3")
        self.assertEqual(entry["unit_topic"], "Sözcük Türleri")

    def test_cells_to_entry_short(self):
        cells = ["5", "Ses Bilgisi"]
        entry = self.parser._cells_to_entry(cells)
        self.assertIsNotNone(entry)
        self.assertEqual(entry["week_number"], "5")
        self.assertEqual(entry["assessment"], "")

    def test_cells_to_entry_all_empty(self):
        cells = [""] * 8
        entry = self.parser._cells_to_entry(cells)
        self.assertIsNone(entry)

    def test_parse_nonexistent_file(self):
        entries = self.parser.parse("/nonexistent/path/file.docx")
        self.assertIsInstance(entries, list)
        self.assertGreater(len(entries), 0)
        self.assertIn("Hata", entries[0]["week_number"])


class TestExcelParser(unittest.TestCase):
    def setUp(self):
        self.parser = ExcelParser()

    def test_cells_to_entry_full(self):
        cells = ["7", "Vücudumuz", "Organları sayar", "Açıklama", "Gösteri", "Model", "Performans", "29 Ekim"]
        entry = self.parser._cells_to_entry(cells)
        self.assertIsNotNone(entry)
        self.assertEqual(entry["week_number"], "7")
        self.assertEqual(entry["special_days"], "29 Ekim")

    def test_cells_to_entry_pads_short_rows(self):
        cells = ["8"]
        entry = self.parser._cells_to_entry(cells)
        self.assertIsNotNone(entry)
        self.assertEqual(entry["week_number"], "8")
        self.assertEqual(entry["tools_equipment"], "")

    def test_cells_to_entry_nan_handling(self):
        cells = ["nan", "Elektrik", "nan", "nan", "nan", "nan", "nan", "nan"]
        entry = self.parser._cells_to_entry(cells)
        self.assertIsNotNone(entry)
        self.assertEqual(entry["week_number"], "nan")
        self.assertEqual(entry["unit_topic"], "Elektrik")

    def test_parse_nonexistent_file(self):
        entries = self.parser.parse("/nonexistent/path/file.xlsx")
        self.assertIsInstance(entries, list)
        self.assertGreater(len(entries), 0)
        self.assertIn("Hata", entries[0]["week_number"])


class TestParserOutputFormat(unittest.TestCase):
    """Verify all parsers produce consistently structured output."""

    REQUIRED_KEYS = {
        "week_number", "unit_topic", "learning_outcomes", "outcome_description",
        "teaching_techniques", "tools_equipment", "assessment", "special_days",
    }

    def _assert_entry_keys(self, entry):
        for key in self.REQUIRED_KEYS:
            self.assertIn(key, entry, f"Missing key: {key}")

    def test_pdf_parser_error_entry_has_all_keys(self):
        parser = PdfParser()
        entries = parser.parse("/nonexistent.pdf")
        for entry in entries:
            self._assert_entry_keys(entry)

    def test_word_parser_error_entry_has_all_keys(self):
        parser = WordParser()
        entries = parser.parse("/nonexistent.docx")
        for entry in entries:
            self._assert_entry_keys(entry)

    def test_excel_parser_error_entry_has_all_keys(self):
        parser = ExcelParser()
        entries = parser.parse("/nonexistent.xlsx")
        for entry in entries:
            self._assert_entry_keys(entry)


if __name__ == "__main__":
    unittest.main()
