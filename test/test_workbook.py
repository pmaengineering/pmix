"""Tests for Workbook module."""
import os.path
import unittest

from pmix.workbook import Workbook


class ExcelErrorDetectionTest(unittest.TestCase):
    """Detect Excel errors in an Excel file."""

    FORM_DIR = 'test/static'

    def test_find_errors(self):
        """Find errors in Excel workbook."""
        answers = {
            'error-basic.xlsx': {
                                    'Sheet1': {
                                        '#VALUE!': ['B1'],
                                        '#N/A': ['B2'],
                                        '#NAME?': ['B3'],
                                    }
                                }
        }
        for path, answer in answers.items():
            full_path = os.path.join(self.FORM_DIR, path)
            wb = Workbook(full_path)
            found_unclean = wb.get_excel_errors()
            found = {k: dict(v) for k, v in found_unclean.items()}
            self.assertEqual(answer, found)
