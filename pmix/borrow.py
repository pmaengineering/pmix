#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a translation file and use it.

Supply source XLSForm(s) to build a translation file. Optionally supply an
XLSForm into which to merge translations. This file is a command-line tool.

Example:

    $ python -m pmix.borrow *.xlsx

    Creates a translation file from all ".xlsx" files in the directory and
    writes it out to a new file.

    $ python -m pmix.borrow *.xlsx -m path/to/specific.xlsx

    Grabs all translations from all ".xlsx" files in the directory and uses
    them to translate path/to/specific.xlsx. Writes out the product to a new
    file.

Created: 3 October 2016
Last modified: 12 December 2018
Author: James K. Pringle
E-mail: jpringle@jhu.edu
"""
import argparse
import pathlib
from typing import List, Set

from pmix.verbiage import TranslationDict
from pmix.xlsform import Xlsform


def create_translation_dict(xlsxfile: List[str], correct: List[str]) \
        -> TranslationDict:
    """Create a translation dict from source Excel files.

    Args:
        xlsxfile: Paths to Excel files
        correct: Paths to Excel files that should be marked correct
    """
    translation_dict = TranslationDict()
    extracted = set()
    for path in correct:
        if path in extracted:
            continue
        xlsform = Xlsform(path)
        translation_dict.extract_translations(xlsform, correct=True)
        extracted.add(path)
    for path in xlsxfile:
        if path in extracted:
            continue
        xlsform = Xlsform(path)
        translation_dict.extract_translations(xlsform)
        extracted.add(path)
    return translation_dict


def get_translation_file_path(*, outfile: str = None, outdir: str = None,
                              create_parents: bool = True) -> str:
    """Get the file write path for a translation file.

    Args:
        outfile: The supplied path for writing a file
        outdir: The supplied directory. Need not exist
        create_parents: If true, create the outdir if it doesn't exist

    Returns:
        A string for where to save a translation file
    """
    default_directory = pathlib.Path('.')
    default_filename = pathlib.Path('translations.xlsx')
    result_path = default_directory / default_filename
    if outfile:
        specific_path = pathlib.Path(outfile)
        if specific_path.is_dir():
            msg = f'Cannot use outfile {outfile} as a file. It is a directory!'
            raise IOError(msg)
        result_path = specific_path
    elif outdir:
        specific_path = pathlib.Path(outdir)
        if specific_path.is_file():
            msg = f'Cannot use outdir {outdir} as directory. It is a file!'
            raise IOError(msg)
        elif not specific_path.is_dir() and create_parents:
            specific_path.mkdir(parents=True, exist_ok=True)
        result_path = specific_path / default_filename
    return str(result_path)


def write_translation_file(translation_dict: TranslationDict, outfile: str,
                           add: List[str], diverse: str) -> None:
    """Write a translation file.

    Args:
        translation_dict: The object with translation information
        outfile: Path where to save the result.
        add: Languages to add to the translation file
        diverse: If true, write a diverse translations file
    """
    if diverse:
        translation_dict.write_diverse_excel(outfile, diverse)
    else:
        translation_dict.write_excel(outfile, add)
    print('Created translation file: "{}"'.format(outfile))


def get_merged_file_paths(merge: List[str], outfile: str, outdir: str,
                          create_parents: bool = True) -> List[str]:
    """Get the file paths for results of merging translations.

    Args:
        merge: The files to merge into
        outfile: Filename where to write the result
        outdir: Directory where to write the result
        create_parents: If true, create the outdir if it doesn't exist

    Returns:
        The file paths where the results of merging should be saved
    """
    if len(merge) == 1 and outfile:
        return [outfile]
    if len(merge) > 1 and outfile:
        msg = f'Ignoring outfile {outfile} since merging into multiple files'
        print(msg)
    file_paths = []
    default_directory = pathlib.Path('.')
    result_directory = default_directory
    if outdir:
        result_directory = pathlib.Path(outdir)
        if result_directory.is_file():
            msg = f'Cannot use outdir {outdir} as directory. It is a file!'
            raise IOError(msg)
        if create_parents:
            result_directory.mkdir(parents=True, exist_ok=True)
    default_suffix = '-borrow'
    for merge_file in merge:
        this_merge = pathlib.Path(merge_file)
        merge_result = this_merge.stem + default_suffix + this_merge.suffix
        full_merge_result = result_directory / merge_result
        file_paths.append(str(full_merge_result))
    return file_paths


# pylint: disable=too-many-arguments
def merge_translation_file(merge: List[str], translation_dict: TranslationDict,
                           outfile: List[str], add: List[str],
                           ignore: Set[str], carry: bool, no_diverse: bool):
    """Merge in translations to designated ODK files.

    Args:
        merge: The files to merge into
        translation_dict: The object with translation information
        outfile: Where to write the merged files. Should be the same length as
            `merge`.
        add: Languages to add
        ignore: Languages to ignore when merging
        carry: If true, carry text from the source language to the translations
        no_diverse: If true, do not insert a translation that has various
            choices
    """
    for merge_source, merge_destination in zip(merge, outfile):
        xlsform = Xlsform(merge_source)
        xlsform.add_languages(add)
        xlsform.merge_translations(translation_dict, ignore, carry=carry,
                                   no_diverse=no_diverse)
        xlsform.write_out(merge_destination)
        print('Merged translations into file: "{}"'.format(merge_destination))


def borrow_cli():
    """Run the CLI for this module."""
    parser = argparse.ArgumentParser(
        description='Grab translations from existing XLSForms'
    )
    parser.add_argument(
        'xlsxfile', nargs='+',
        help='One or more paths to source XLSForms containing translations.'
    )
    parser.add_argument(
        '-m', '--merge', action='append',
        help=('An XLSForm that receives the translations from source '
              'files. If this argument is not supplied, then a '
              'translation file is created. Multiple files can be supplied, '
              'each with the -m flag.')
    )
    parser.add_argument(
        '-M', '--merge_all', nargs='+',
        help=('Merge into many files. To avoid ambiguity, this must be placed '
              'after the source XLSForms.')
    )
    parser.add_argument(
        '-C', '--correct', action='append',
        help=('Mark a given file as correct. Text from these files will '
              'disallow diverse translations from files not marked as '
              'correct. This is a way to give files precedence for '
              'translations.')
    )
    parser.add_argument(
        '-D', '--no_diverse', action='store_true',
        help='If text has diverse translations, do not borrow it.'
    )
    parser.add_argument(
        '-d', '--diverse',
        help=('Supply a language. Used without the --merge argument, '
              'this creates a worksheet that shows only strings with '
              'diverse translations for the supplied language.')
    )
    parser.add_argument(
        '-a', '--add', action='append',
        help=('Add a language to the resulting output. The translation file '
              'will have a column for that language. Or, the merged XLSForm '
              'will include columns for that language and have translations '
              'for them if possible. This option can be supplied multiple '
              'times.')
    )
    parser.add_argument(
        '-i', '--ignore', action='append',
        help=('A language to ignore when collecting and making '
              'translations. This option can be supplied multiple times')
    )
    parser.add_argument(
        '-c', '--carry', action='store_true',
        help=('If translations are missing, carry over the same text from '
              'the source language. The default is to leave missing.')
    )
    parser.add_argument(
        '-o', '--outfile',
        help=('Path to write output. If this argument is not supplied, then '
              'defaults are used. If a command would produce multiple '
              'outputs, then do not use this argument. Instead use '
              '"--outdir".')
    )
    parser.add_argument(
        '-O', '--outdir',
        help=('A directory to use (and create if it does not exist) for '
              'writing output. Ignored if -o is supplied. Defaults are used'
              'for filenames. If neither outfile nor outdir are supplied, '
              'then default filenames are used in the current directory.')
    )

    args = parser.parse_args()
    borrow(
        xlsxfiles=args.xlsxfile,
        correct=args.correct,
        merge=args.merge,
        merge_all=args.merge_all,
        no_diverse=args.no_diverse,
        diverse=args.diverse,
        add=args.add,
        ignore=args.ignore,
        carry=args.carry,
        outfile=args.outfile,
        outdir=args.outdir,
    )


# pylint: disable=too-many-locals
def borrow(*, xlsxfiles: List[str], correct: List[str], merge: List[str],
           merge_all: List[str], add: List[str], ignore: List[str],
           no_diverse: bool = False, diverse: str = None, carry: bool = False,
           outfile: str = None, outdir: str = None):
    """Borrow files with this Python routine.

    This method exists so that non-CLI users can run borrow. See CLI help
    commands for more information about these parameters.

    Args:
        xlsxfiles: Source Excel files where to find translations
        correct: Source Excel files that are marked correct
        merge: Files to merge into
        merge_all: Files to merge into
        add: Languages to add
        ignore: Languages to ignore
        no_diverse: Do not allow source segments with diverse translations to
            be updated
        carry: Copy over source segments as a translation if no translation
            exists
        outfile: Filename where to write the result
        outdir: Directory where to write the result
    """
    source_files = xlsxfiles
    correct_files = correct if correct else []
    translation_dict = create_translation_dict(source_files, correct_files)
    to_add = sorted(list(set(add))) if add else []
    if not merge and not merge_all:
        outfile = get_translation_file_path(outfile=outfile, outdir=outdir,
                                            create_parents=True)
        write_translation_file(translation_dict, outfile, to_add, diverse)
    else:
        ignored = set(ignore) if ignore else None
        combined_merge = []
        if merge:
            combined_merge.extend(merge)
        if merge_all:
            combined_merge.extend(merge_all)
        outfiles = get_merged_file_paths(merge=combined_merge, outfile=outfile,
                                         outdir=outdir, create_parents=True)
        merge_translation_file(combined_merge, translation_dict, outfiles,
                               to_add, ignored, carry, no_diverse)


if __name__ == '__main__':
    borrow_cli()
