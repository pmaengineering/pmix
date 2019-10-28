"""Module for Cell class."""
import datetime
import xlrd

import pmix.utils


class CellContext:
    """Cell context information.

    This class stores information about the cell and where it is.

    Instance attributes:
        filename: The filename of the Excel file
        sheet: The sheet name
        row: The
    """

    def __init__(self, filename: str, sheet: str, row: int, column: int,
                 column_header: str):
        """Initialize a cell context."""
        self.filename = filename
        self.sheet = sheet
        self.row = row
        self.column = column
        self.column_header = column_header

    def to_excel(self) -> str:
        """Get the Excel cell name for this cell."""
        if self.row < 0 or self.column < 0:
            return ""
        return pmix.utils.xl_rowcol_to_cell(self.row, self.column)

    @classmethod
    def empty_context(cls):
        """Create an empty context.

        This is meant to be a place holder until later.
        """
        return cls(None, None, -1, -1, None)

    def __repr__(self):
        """Get a representation of this object."""
        return (f"CellContext(filename={self.filename!r}, sheet={self.sheet!r}, "
                f"row={self.row!r}, column={self.column!r}, "
                f"column_header={self.column_header!r})")


class CellError:
    """An Excel cell error.

    Instance attributes:
        value (integer): The Excel internal value of the error
        error_text (str): The display text of the error
    """

    def __init__(self, value):
        """Initialize with a specific internal error value.

        Args:
            value (integer): An Excel internal error value.
        """
        self.value = value
        self.error_text = xlrd.error_text_from_code[value]

    def __str__(self):
        """Convert an error to be displayed in output.

        We ignore errors because they do not add useful information.
        """
        return ''

    def __repr__(self):
        """Get a representation of this object."""
        return f'CellError({self.value})'


class Cell:
    """Representative class for spreadsheet cell.

    Instance attributes:
        value: A python object that is stored in the cell. Should be
            castable as str.
        highlight (str): The highlight color for this cell.
    """

    def __init__(self, value=None, *, context: CellContext = None):
        """Initialize cell to have value as Python object.

        Args:
            value: The value of the cell. Defaults to None for a blank cell.
        """
        self.value = value
        self.highlight = None
        self.context = context if context else CellContext.empty_context()

    def is_blank(self):
        """Test whether cell is blank."""
        return str(self) == ''

    def is_error(self):
        """Test wheter cell is an error."""
        return isinstance(self.value, CellError)

    def equals(self, other, whitespace=True):
        """Return string equality of the two cells.

        Args:
            other (Cell): The other cell
            whitespace (bool): If False, give equality disregarding whitespace
        """
        if whitespace:
            return str(self) == str(other)
        this_str = ''.join(str(self).split())
        other_str = ''.join(str(other).split())
        return this_str == other_str

    def set_highlight(self, color='HL_YELLOW'):
        """Highlight this cell.

        Args:
            color (str): The highlight color
        """
        self.highlight = color

    def __bool__(self):
        """Get truthiness of the cell.

        Returns:
            Returns the truthiness of the cell value.
        """
        return bool(self.value)

    def __eq__(self, other):
        """Define equality comparison for Cells."""
        if isinstance(other, Cell):
            return self.value == other.value
        return False

    def __str__(self):
        """Return unicode representation of cell."""
        if self.value is None:
            return ''
        return str(self.value)

    def __repr__(self):
        """Return a representation of the cell."""
        msg = '<Cell(value={!r})>'.format(self.value)
        return msg

    @classmethod
    def from_cell(cls, cell, datemode=None, stripstr=True):
        """Create a Cell object by importing Cell from xlrd.

        Args:
            cell (xlrd.Cell): A cell to copy over.
            datemode (int): The datemode for the workbook where the cell is.
            stripstr (bool): Remove trailing / leading whitespace from text?

        Returns:
            An intialized cell object.
        """
        cell_value = cls.cell_value(cell, datemode, stripstr)
        return cls(cell_value)

    @staticmethod
    def cell_value(cell, datemode=None, stripstr=True):
        """Get python object out of xlrd.Cell value.

        Args:
            cell (xlrd.Cell): The cell
            datemode (int): The date mode for the workbook
            stripstr (bool): Remove trailing / leading whitespace from text?

        Returns:
            value (str): The python object represented by this cell.
        """
        value = None
        if cell.ctype == xlrd.XL_CELL_BOOLEAN:
            value = True if cell.value == 1 else False
        elif cell.ctype == xlrd.XL_CELL_EMPTY:
            # value = None  # ... redundant
            pass
        elif cell.ctype == xlrd.XL_CELL_TEXT:
            if stripstr:
                value = cell.value.strip()
            else:
                value = cell.value
        elif cell.ctype == xlrd.XL_CELL_NUMBER:
            # Make integer what is equal to an integer
            int_val = int(cell.value)
            value = int_val if int_val == cell.value else cell.value
        elif cell.ctype == xlrd.XL_CELL_DATE:
            value = Cell.parse_datetime(cell.value, datemode)
        elif cell.ctype == xlrd.XL_CELL_ERROR:
            value = CellError(cell.value)
        else:
            msg = 'Unhandled cell found!\nType: {}\nValue: {}'
            msg = msg.format(cell.ctype, cell.value)
            raise TypeError(msg)
        return value

    @staticmethod
    def parse_datetime(value, datemode):
        """Convert an xlrd cell value to a date time object.

        Args:
            value: The cell value
            datemode (int): The date mode of the Excel workbook
        """
        if datemode is None:
            # set to modern Excel
            datemode = 1
        date_tuple = xlrd.xldate_as_tuple(value, datemode)
        if date_tuple[:3] == (0, 0, 0):
            # must be time only
            value = datetime.time(*date_tuple[3:])
        elif date_tuple[3:] == (0, 0, 0):
            # must be date only
            value = datetime.date(*date_tuple[:3])
        else:
            value = datetime.datetime(*date_tuple)
        return value
