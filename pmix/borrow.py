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
Last modified: 14 November 2018
Author: James K. Pringle
E-mail: jpringle@jhu.edu
"""
import argparse
import os.path
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


def write_translation_file(translation_dict: TranslationDict, outpath: str,
                           add: List[str], diverse: str) -> None:
    """Write a translation file.

    Args:
        translation_dict: The object with translation information
        outpath: Path where to save the result. Can be a directory or not.
        add: Languages to add to the translation file
        diverse: If true, write a diverse translations file
    """
    default_filename = pathlib.Path('translations.xlsx')
    default_directory = pathlib.Path('.')
    default_outpath = default_directory / default_filename
    if outpath:
        path = pathlib.Path(outpath)
        if path.is_dir():
            result_path = path / default_filename
        else:
            result_path = path
    else:
        result_path = default_outpath
    if diverse:
        translation_dict.write_diverse_excel(str(result_path), diverse)
    else:
        translation_dict.write_excel(str(result_path), add)
    print('Created translation file: "{}"'.format(str(result_path)))


# pylint: disable=too-many-arguments
def merge_translation_file(merge: List[str], translation_dict: TranslationDict,
                           outpath: str, add: List[str], ignore: Set[str],
                           carry: bool, no_diverse: bool):
    """Merge in translations to designated ODK files.

    Args:
        merge: The files to merge into
        translation_dict: The object with translation information
        outpath: Path where to save the result. Can be a directory or not.
        add: Languages to add
        ignore: Languages to ignore when merging
        carry: If true, carry text from the source language to the translations
        no_diverse: If true, do not insert a translation that has various
            choices
    """
    if outpath and len(merge) > 1:
        pathlib.Path(outpath).mkdir(parents=True, exist_ok=True)
    for path in merge:
        xlsform = Xlsform(path)
        for language in add:
            xlsform.add_language(language)
        xlsform.merge_translations(translation_dict, ignore, carry=carry,
                                   no_diverse=no_diverse)
        base, ext = os.path.splitext(path)
        default_filename = ''.join((base, '-borrow', ext))
        if outpath is None:
            this_outpath = default_filename
        elif len(merge) > 1 or pathlib.Path(outpath).is_dir():
            this_outpath = os.path.join(outpath, default_filename)
        else:
            this_outpath = outpath
        xlsform.write_out(this_outpath)
        print('Merged translations into file: "{}"'.format(this_outpath))


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
        '-o', '--outpath',
        help=('Path to write output. If this argument is not supplied, then '
              'defaults are used. If multiple files are given, then this is '
              'interpreted as a directory.')
    )

    args = parser.parse_args()
    borrow(merge=args.merge,
           merge_all=args.merge_all,
           correct=args.correct,
           no_diverse=args.no_diverse,
           diverse=args.diverse,
           add=args.add,
           ignore=args.ignore,
           carry=args.carry,
           outpath=args.outpath,
           xlsxfiles=args.xlsxfile)


def borrow(xlsxfiles: List[str], merge: List[str], merge_all: List[str],
           correct: List[str], add: List[str], ignore: List[str],
           no_diverse: bool = False, diverse=None, carry: bool = False,
           outpath: str = ''):
    """Borrow"""
    xlsx_list = [xlsxfiles] if isinstance(xlsxfiles, str) else xlsxfiles
    ignore_set = set(ignore) if ignore else None
    add_list = sorted(list(set(add))) if add else None
    correct_list = correct if correct else []
    translation_dict = create_translation_dict(xlsx_list, correct_list)
    if merge is None and merge_all is None:
        write_translation_file(translation_dict, outpath, add_list, diverse)
    else:
        merge_list = []
        if merge:
            pre_merge_list = [merge] if isinstance(merge, str) else merge
            merge_list.extend(pre_merge_list)
        if merge_all:
            merge_list.extend(merge_all)
        merge_translation_file(merge_list, translation_dict, outpath, add_list,
                               ignore_set, carry, no_diverse)


if __name__ == '__main__':
    borrow_cli()
