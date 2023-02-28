#!/usr/bin/env python3

import sys
import csv
from parse import pdf_to_xml, xml_to_textlines, textlines_to_records, Record


def format(record: Record) -> Record:
    # Only get first row of col0
    columns = [record.columns[0].split('\n')[0]]

    # Strip newlines from the rest
    for column in record.columns[1:]:
        columns.append(column.replace('\n', ' '))

    return Record(columns)


def main(filename):
    xml = pdf_to_xml(filename)
    textlines = xml_to_textlines(xml)
    without_footer = filter(lambda line: line.y1 > 10, textlines)
    records = textlines_to_records(list(without_footer))
    formated = map(format, records)
    csvwriter = csv.writer(sys.stdout)
    csvwriter.writerows(formated)


if __name__ == "__main__":
    main(*sys.argv[1:])
