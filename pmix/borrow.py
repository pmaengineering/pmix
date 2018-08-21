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
Last modified: 21 August 2018
Author: James K. Pringle
E-mail: jpringle@jhu.edu
"""

import argparse
import os.path
import pathlib

from pmix.verbiage import TranslationDict
from pmix.xlsform import Xlsform


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
    print(args)
    ignore = set(args.ignore) if args.ignore else None
    add = sorted(list(set(args.add))) if args.add else None

    translation_dict = TranslationDict()
    extracted = set()
    if args.correct:
        for path in args.correct:
            if path in extracted:
                continue
            xlsform = Xlsform(path)
            translation_dict.extract_translations(xlsform, correct=True)
            extracted.add(path)
    for path in args.xlsxfile:
        if path in extracted:
            continue
        xlsform = Xlsform(path)
        translation_dict.extract_translations(xlsform)
        extracted.add(path)

    if args.merge is None and args.merge_all is None:
        outpath = 'translations.xlsx' if args.outpath is None else args.outpath
        if args.diverse:
            translation_dict.write_diverse_excel(outpath, args.diverse)
        else:
            translation_dict.write_excel(outpath, add)
        print('Created translation file: "{}"'.format(outpath))
    else:
        merge = []
        if args.merge:
            merge.extend(args.merge)
        if args.merge_all:
            merge.extend(args.merge_all)
        outpath = args.outpath
        if outpath and len(merge) > 1:
            pathlib.Path(outpath).mkdir(parents=True, exist_ok=True)
        for path in merge:
            xlsform = Xlsform(path)
            # wb.add_language(add)
            xlsform.merge_translations(translation_dict, ignore,
                                       carry=args.carry,
                                       no_diverse=args.no_diverse)
            if outpath is None:
                orig = xlsform.file
                base, ext = os.path.splitext(orig)
                this_outpath = ''.join((base, '-borrow', ext))
            elif len(merge) > 1:
                orig = xlsform.file
                base, ext = os.path.splitext(orig)
                this_outpath = ''.join((outpath, base, '-borrow', ext))
            else:
                this_outpath = outpath
            xlsform.write_out(this_outpath)
            print('Merged translations into file: "{}"'.format(this_outpath))


if __name__ == '__main__':
    borrow_cli()
