"""Module defining Xlsform class to work with ODK XLSForms."""
from copy import deepcopy
from xlsxwriter.utility import xl_col_to_name
from typing import List, Optional

from pmix.xlstab import Xlstab
from pmix.workbook import Workbook


class Xlsform(Workbook):
    """Class to represent an Xlsform spreadsheet.

    The Xlsform class extends the Workbook class to provide functionality
    related specifically to Xlsforms and would not be expected for a general-
    purpose Workbook.

    Note: Analogously, the Xlstab class extends the Worksheet class.
    """

    def __init__(self, path: str, stripstr: bool = True):
        """Initialize workbook and cache Xlsform-specific info.

        Args:
            path: The path where to find the Xlsform file.
            stripstr: Remove trailing / leading whitespace from text?
        """
        super().__init__(path, stripstr)
        self.data = [Xlstab.from_worksheet(ws) for ws in self]
        self.settings = {}
        self.init_settings()
        self.warnings = {}
        self.init_warnings()

    def init_settings(self):
        """Get settings from Xlsform.

        Post-condition: the Xlsform's settings are stored in the instance.
        """
        try:
            local_settings = self['settings']
            headers = local_settings[0]
            values = local_settings[1]
            self.settings = {str(k): str(v) for k, v in zip(headers, values) if
                             not k.is_blank() and not v.is_blank()}
        except (KeyError, IndexError):
            self.settings = {}

    @property
    def form_id(self) -> str:
        """Return form_id setting value."""
        self.init_settings()
        form_id = self.settings['form_id']
        return form_id

    @property
    def form_title(self) -> str:
        """Return form_title setting value."""
        self.init_settings()
        form_title = self.settings['form_title']
        return form_title

    @property
    def settings_language(self) -> Optional[str]:
        """Return default language from settings or None if not found."""
        self.init_settings()
        default_language = self.settings.get('default_language', None)
        return default_language

    @property
    def survey_languages(self) -> List[str]:
        """Return sorted languages from headers for survey worksheet."""
        return self['survey'].sheet_languages()

    @property
    def form_language(self) -> Optional[str]:
        """Return default language for a form.

        Considers settings tab first, then gets language from survey tab.

        Returns:
            A string for the default language or None if there is no language
            specified.
        """
        language = self.settings_language
        if language is None:
            try:
                language = self.survey_languages[0]
            except KeyError:
                # Keep language as None
                pass
        return language

    def init_warnings(self):
        """Validate data and return warnings.

        Side effects:
            self.warnings (dict): sets warnings

        Examples:
            self.warnings =
            '#VALUE!': {
                'survey': [X10, C56, E122]
            },
            '#REF!': {
                'survey': [T5, C53]
            },
        }
        """
        warnings_schema = {  # taken from xlrd.error_text_from_code
            '#NULL!': {},  # Intersection of two cell ranges is empty
            '#DIV/0': {},  # Division by zero
            '#VALUE!': {},  # Wrong type of operand
            '#REF!': {},  # Illegal or deleted cell reference
            '#NAME?': {},  # Wrong function or range name
            '#NUM!': {},  # Value range overflow
            '#N/A': {},  # Argument or function not available
        }
        warnings = deepcopy(warnings_schema)
        error_codes = [k for k, v in warnings.items()]
        for ws in self.data:
            for i, row in enumerate(ws.data):
                for j, cell in enumerate(row):
                    if cell.value in error_codes:
                        if ws.name not in warnings[cell.value]:
                            warnings[cell.value][ws.name] = []
                        label = xl_col_to_name(j)
                        warnings[cell.value][ws.name].append(label + str(i))
        warnings = {k: v for k, v in warnings.items() if v != {}}
        self.warnings = warnings

    def add_language(self, language: str):
        """Add appropriate language columns to an Xlsform.

        Args:
            language: The language to add to all relevant sheets.
        """
        for sheet in self:
            sheet.add_language(language)

    def add_languages(self, languages: List[str]):
        """Add appropriate language columns to an Xlsform.

        Args:
            languages: The languages to add to all relevant sheets.
        """
        for language in languages:
            self.add_language(language)

    def merge_translations(self, translations, ignore=None, carry=False,
                           no_diverse=False):
        """Merge translations.

        Args:
            translations (TranslationDict): Translations
            ignore (set of str): The languages to ignore when translating
            carry (bool): Carry source language over to missing translations
            no_diverse (bool): If true, then do not translate text that has
                multiple translations.
        """
        for sheet in self:
            sheet.merge_translations(translations, ignore, carry=carry,
                                     no_diverse=no_diverse)
