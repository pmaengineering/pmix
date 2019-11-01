import argparse
import itertools
import logging
import os.path
import re

from pmix.utils import split_numbered_text
from pmix.xlsform import Xlsform
from pmix.workbook import Workbook


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    level=logging.INFO)


class RenumberMap:

    def __init__(self, filename):
        self.filename = filename
        self.map = {}
        extension = os.path.splitext(filename)[1]
        if extension in ('.xls', '.xlsx'):
            self.map = self.map_from_excel(self.filename)
        self.regex_map = {key: re.compile(r'\b{}\b'.format(key)) for key in self.map}

    def applies_to(self, value):
        if not isinstance(value, str):
            return []
        keys = []
        for key, program in self.regex_map.items():
            if program.search(value):
                keys.append(key)
        return keys

    def apply(self, value, keys) -> str:
        if not isinstance(value, str):
            return value
        updated_value = value
        placeholders = [f'yQQQy{self.map[key]}yQQQy' for key in keys]
        for key, placeholder in zip(keys, placeholders):
            program = self.regex_map[key]
            updated_value = program.sub(placeholder, updated_value)
        updated_value = re.sub('yQQQy', '', updated_value)
        return updated_value



    @staticmethod
    def map_from_excel(filename):
        not_enough_columns = False
        logging.info(f'Loading data from {filename}')
        renumbering = {}
        workbook = Workbook(filename)
        worksheet = workbook[0]
        for i, row in enumerate(worksheet):
            try:
                start = str(row[0])
                finish = str(row[1])
                start_escaped = re.escape(start)
                # TODO: finish probably does not need to be escaped
                if start and finish:
                    if start_escaped in renumbering:
                        msg = f'Duplicate renaming source found: row {i+1}, "{start}"'
                        logging.info(msg)
                    if finish in renumbering.values():
                        msg = (f'Duplicate renaming replacement found: '
                               f'row {i+1}, "{start}"')
                        logging.info(msg)
                    if start != start_escaped:
                        msg = (f'Row {i+1} "{start}" -> "{finish}" has regex '
                               f'special characters, so they were escaped.')
                        logging.info(msg)
                    if start == finish:
                        msg = (f'Row {i + 1} "{start}" -> "{finish}" are equal so '
                               f'will not produce a change.')
                        logging.info(msg)
                    renumbering[start_escaped] = finish
                else:
                    msg = (f'Row {i+1} "{start}" -> "{finish}" skipped since it is not'
                           f'complete.')
                    logging.info(msg)
            except IndexError:
                if not_enough_columns:
                    logging.info(f'First sheet in {filename} does not have two '
                                 f'columns.')
                    not_enough_columns = True
        logging.info(f'Finished collecting renaming rules from {filename}. '
                     f'Number of rules found: {len(renumbering)}')
        return renumbering


def check_label_numbers_match(xlsform: Xlsform) -> bool:
    """Check that all labels have the same question number.

    TODO: This isn't exactly related to renumbering. Put in a more central location?
    """
    logging.info(f'Checking question number consistency in labels '
                 f'of {xlsform.filename}')
    all_match = True
    survey = xlsform['survey']
    labels = survey.label_columns(indices_only=True)
    if len(labels) <= 1:
        logging.info('There are no label translations to inspect.')
        return True
    for i, row in enumerate(survey):
        if i == 0:
            continue
        these_labels = (row[j] for j in labels)
        components = (split_numbered_text(str(cell)) for cell in these_labels)
        numbers = (item.number for item in components)
        distinct = set(numbers)
        if len(distinct) > 1:
            logging.warning(f'Different question numbers found in labels of '
                            f'row {i + 1}: {sorted(list(distinct))}')
            all_match = False
    if all_match:
        logging.info(f'All question numbers consistent in labels of {xlsform.filename}')
    return all_match


def do_renumber(xlsform_path, renumbering_path, dry_run=False, all_columns=False):
    logging.info(f'Renumbering XLSForm {xlsform_path} with rules '
                 f'from {renumbering_path}')
    renumbering = RenumberMap(renumbering_path)
    xlsform = Xlsform(xlsform_path)
    check_label_numbers_match(xlsform)
    survey = xlsform['survey']
    if all_columns:
        columns = list(range(len(survey.column_headers())))
    else:
        columns = survey.translatable_columns(indices_only=True)
    cell_applications = []
    for i, row in enumerate(survey):
        if i == 0:
            continue
        for j in columns:
            value = row[j].value
            applications = renumbering.applies_to(value)
            if applications:
                cell_applications.append((row[j], applications))
    all_starts = set(renumbering.map.keys())
    all_found_starts = set(
        itertools.chain.from_iterable(x for _, x in cell_applications))
    missing = sorted(list(all_starts - all_found_starts))
    if missing:
        logging.warning(f'Found items in renumber file but not '
                        f'in XLSForm: {missing}, count: {len(missing)}')
    change_count = 0
    for cell, applications in cell_applications:
        old_value = cell.value
        new_value = renumbering.apply(old_value, applications)
        if not dry_run:
            cell.value = new_value
        if old_value != new_value:
            change_count += 1
            cell.set_highlight()
        else:
            cell.set_highlight('HL_ORANGE')
    logging.info(f'Done renumbering XLSForm. Number of cell changes: {change_count}')
    return xlsform


def renumber_cli():
    """Run the command line interface for this module."""
    parser = argparse.ArgumentParser(description='Renumber an ODK form')
    parser.add_argument('xlsform', help='Path to source XLSForm.')
    parser.add_argument('renumbering',
                        help='Path to a document with renumbering information.')
    parser.add_argument('-o', '--outpath',
                        help=('Path to write output. If this argument is not supplied, '
                              'then defaults are used.'))
    parser.add_argument('--dry_run', action='store_true',
                        help=('Highlight cells that would be updated but do not make '
                              'any text edits.'))
    parser.add_argument('--all_columns', action='store_true',
                        help=('Look at all columns to renumber? Default is to look '
                              'only at translatable columns.'))
    args = parser.parse_args()

    filename, extension = os.path.splitext(args.xlsform)
    if args.outpath is None:
        outpath = os.path.join(filename + '-renum' + extension)
    else:
        outpath = args.outpath

    xlsform = do_renumber(args.xlsform, args.renumbering, dry_run=args.dry_run,
                          all_columns=args.all_columns)
    xlsform.write_out(outpath)
    print('Wrote file to "{}"'.format(outpath))


if __name__ == '__main__':
    renumber_cli()
