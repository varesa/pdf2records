#!/usr/bin/env python3
from bs4 import BeautifulSoup
from subprocess import check_output
import sys
from typing import Iterable
import re


class TextLine:
    def __init__(self, text: str, bbox: str):
        self.text = text.strip()
        x1, y1, x2, y2 = map(float, bbox.split(','))
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2

    def __repr__(self) -> str:
        return f"<{self.y1}-{self.y2} {self.x1}-{self.x2}>'{self.text}'"


class Record:
    def __init__(self, columns: Iterable[str]):
        self.columns = columns

    def __repr__(self):
        return '[' + ', '.join([repr(col) for col in self.columns]) + ']'


def pdf_to_xml(filename: str) -> str:
    xml = check_output(["pdf2txt", "-t", "xml", filename])
    return xml


def xml_to_textlines(xml: str) -> Iterable[TextLine]:
    bs = BeautifulSoup(xml, features="xml")
    lines = bs.find_all('textline')
    for line in lines:
        text = ""
        characters = line.find_all('text')
        for character in characters:
            text += character.get_text()
        yield TextLine(text, line['bbox'])


def find_dates(lines: Iterable[TextLine]) -> list[TextLine]:
    sorted_vertically = sorted(lines, key=lambda line: line.y1, reverse=True)
    possibly_dates = filter(lambda line: line.x1 < 100, sorted_vertically)

    dates = []
    for candidate in possibly_dates:
        if re.match(r"[0-9]+\.[0-9]+\.", candidate.text):
            if not dates or dates[-1].y1 - candidate.y1 > 16:
                dates.append(candidate)

    return dates


def textlines_to_records(lines: list[TextLine]) -> Iterable[Record]:
    dates = find_dates(lines)

    for index, date in enumerate(dates):
        ymax = date.y1 + 8
        if index+1 == len(dates):
            ymin = ymax - 10000
        else:
            ymin = dates[index+1].y1 + 8

        record_lines = list(filter(lambda line: ymin < line.y1 <= ymax, lines))

        text_columns = []
        column_starts = sorted({line.x1 for line in record_lines})
        for column_start in column_starts:
            column_lines = filter(
                    lambda line: line.x1 == column_start,
                    record_lines)
            column_lines_vsorted = sorted(
                    column_lines,
                    key=lambda line: line.y1,
                    reverse=True)
            text = '\n'.join([line.text for line in column_lines_vsorted])
            text_columns.append(text)
        yield Record(text_columns)


def main(filename):
    xml = pdf_to_xml(filename)
    textlines = xml_to_textlines(xml)
    records = textlines_to_records(list(textlines))
    for record in records:
        print(record)


if __name__ == "__main__":
    main(*sys.argv[1:])
