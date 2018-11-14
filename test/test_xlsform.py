"""Tests for Xlsform module."""
from glob import glob
import os
import unittest
from pmix.xlsform import Xlsform

TEST_DIR = os.path.dirname(os.path.realpath(__file__)) + '/'
TEST_STATIC_DIR = TEST_DIR + 'static/'


class StaticIOTest(unittest.TestCase):
    """Base class for standard input/output stuff package tests."""

    @classmethod
    def files_dir(cls):
        """Return name of test class."""
        return TEST_STATIC_DIR + cls.__name__

    def input_path(self):
        """Return path of input file folder for test class."""
        return self.files_dir() + '/input/'

    def output_path(self):
        """Return path of output file folder for test class."""
        return self.files_dir() + '/output/'

    def input_files(self):
        """Return paths of input files for test class."""
        all_files = glob(self.input_path() + '*')
        # With sans_temp_files, you can have Excel open while testing.
        sans_temp_files = [x for x in all_files
                           if not x[len(self.input_path()):].startswith('~$')]
        return sans_temp_files

    def output_files(self):
        """Return paths of input files for test class."""
        return glob(self.output_path() + '*')

    def assert_success(self, func, **options):
        """Runs function and asserts success.

        Args:
            func (function): function to run.
            options (kwargs): function options; unpacked keyword args
        """
        if options:
            func(**options)
        else:
            func()
        expected = 'N files: ' + str(len(self.input_files()))
        actual = 'N files: ' + str(len(self.output_files()))
        self.assertEqual(expected, actual)


class XlsFormNonStrictValidation(StaticIOTest):
    """Test that non-strict validation works as expected."""

    def mark_as_success(self):
        """Create a file to mark successful test."""
        path = self.output_path() + 'success.txt'
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        open(path, 'x').close()

    def new_xlsforms(self):
        for form in self.input_files():
            Xlsform(form, strict_validation=False)
        self.mark_as_success()

    def test_non_strict_validation(self):
        """Test that non-strict validation works as expected."""
        self.assert_success(func=self.new_xlsforms)
