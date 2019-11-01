"""Useful string functions for PMIX."""
from collections import namedtuple
import re
import string


NUMBER_RE = r"""
            ^\s*                # Begin with possible whitespace.
            (
                [a-zA-Z]        # Start with a letter
            |
                (
                    \S*         # or start with non-whitespace and
                    \d+         # one or more numbers, then possibly
                    [.a-z]*     # dots (.) and lower-case letters
                )
            )
            [.:)]               # Always end with one of '.', ':', ')' and
            \s+                 # finally whitespace
            """


# pylint: disable=no-member
NUMBER_PROG = re.compile(NUMBER_RE, re.VERBOSE)


NumberLabelSplit = namedtuple('NumberLabelSplit',
                              ['number', 'delimiter', 'space', 'label'])
NUMBER_DELIMITER = ('.', ':', ')')
VALID_NUMBER_ALPHABET = tuple(string.ascii_letters + string.digits + '._-')


def split_numbered_text(text: str) -> NumberLabelSplit:
    stripped = text.strip()
    this_split = stripped.split(maxsplit=1)
    if not this_split:
        return NumberLabelSplit('', '', '', '')
    else:
        label = this_split[1].strip() if len(this_split) > 1 else ''
        space = ' ' if len(this_split) > 1 else ''
        candidate_number = this_split[0]
        if is_proper_number(candidate_number):
            number, delimiter = candidate_number[:-1], candidate_number[-1]
            return NumberLabelSplit(number, delimiter, space, label)
        return NumberLabelSplit('', '', '', stripped)


def is_proper_number(text: str):
    if len(text) < 2:
        return False
    ends_with = ['.', ':', ')']
    proper_ending = any(text.endswith(ending) for ending in ends_with)
    if not proper_ending:
        return False
    if len(text) == 2 and text[0] in string.ascii_letters:
        return True
    number, delimiter = text[:-1], text[-1]
    has_digit = any(i.isdigit() for i in number)
    all_valid_characters = all(i in VALID_NUMBER_ALPHABET for i in number)
    first_valid = number[0] in string.ascii_letters + string.digits
    last_valid = number[-1] in string.ascii_letters + string.digits
    return has_digit and all_valid_characters and first_valid and last_valid


def td_clean_string(text):
    """Clean a string for a translation dictionary.

    Removes extra whitespace and a number if found.

    Args:
        text (str): String to be cleaned.

    Returns:
        String with extra whitespace and leading number (if found) removed.
    """
    text = clean_string(text)
    _, text = td_split_text(text)
    return text


def td_split_text(text):
    """Split text into a number and the rest.

    This splitting is done using the regex program `NUMBER_PROG`.

    Args:
        text (str): String to split

    Returns:
        A tuple `(number, the_rest)`. The original string is `number +
        the_rest`. If no number is found with the regex, then `number` is
        '', the empty string.
    """
    number = ''
    the_rest = text
    if len(text.split()) > 1:
        match = NUMBER_PROG.match(text)
        if match:
            number = text[match.span()[0]:match.span()[1]]
            the_rest = text[match.span()[1]:]
    return number, the_rest


def clean_string(text):
    """Clean a string for addition into the translation dictionary.

    Leading and trailing whitespace is removed. Newlines are converted to
    the UNIX style.

    Args:
        text (str): String to be cleaned.

    Returns:
        A cleaned string with number removed.
    """
    text = text.strip()
    text = text.replace('\r\n', '\n')
    text = text.replace('\r', '\n')
    text = space_newline_fix(text)
    text = newline_space_fix(text)
    text = space_space_fix(text)
    return text


def newline_space_fix(text):
    """Replace "newline-space" with "newline".

    This function was particularly useful when converting between Google
    Sheets and .xlsx format.

    Args:
        text (str): The string to work with

    Returns:
        The text with the appropriate fix.
    """
    newline_space = '\n '
    fix = '\n'
    while newline_space in text:
        text = text.replace(newline_space, fix)
    return text


def space_space_fix(text):
    """Replace "space-space" with "space".

    Args:
        text (str): The string to work with

    Returns:
        The text with the appropriate fix.
    """
    space_space = '  '
    space = ' '
    while space_space in text:
        text = text.replace(space_space, space)
    return text


def space_newline_fix(text):
    """Replace "space-newline" with "newline".

    Args:
        text (str): The string to work with

    Returns:
        The text with the appropriate fix.
    """
    space_newline = ' \n'
    fix = '\n'
    while space_newline in text:
        text = text.replace(space_newline, fix)
    return text


def show_whitespace(text):
    """Replace whitespace characters with unicode.

    Args:
        text (str): The string to work with

    Returns:
        The text with the whitespace now visible.
    """
    text = text.replace('\r\n', '\n')
    text = text.replace('\r', '\n')
    # Middle dot
    text = text.replace(' ', '\u00b7')
    # Small right triangle
    text = text.replace('\t', '\u25b8')
    # Downwards arrow with corner leftwards
    text = text.replace('\n', '\u21b5')
    return text
