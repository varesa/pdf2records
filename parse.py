#!/usr/bin/env python3
from bs4 import BeautifulSoup
from subprocess import check_output
import sys
from typing import Iterable


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


def main(filename):
    xml = pdf_to_xml(filename)
    textlines = xml_to_textlines(xml)
    
    for line in textlines:
        print(line)


if __name__ == "__main__":
    main(*sys.argv[1:])
