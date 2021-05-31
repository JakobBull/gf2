from scanner import Symbol
from scanner import Scanner
from names import Names
from parse import Parser


import pytest
import sys
import os

def test_working_spec():
    scan = Scanner("parse_test_files/test_working_spec.txt", Names())
    parse = Parser(Names(), scan)
    parse.parse_network()
    assert True

@pytest.mark.parametrize(
    "file, expected_string",
    [
        ("test_1", "Headings called in wrong order"),
        ("test_2", "Always need to follow a heading with {"),
        ("test_3", "Device: Name of device must contain a letter"),
        ("test_4","Device: Name for device already used"),
    ],
)
# tests if query returns correct name ID for a name sting
def test_query_output(file, expected_string):
    path = "parse_test_files/"
    path += file
    path += ".txt"
    scan = Scanner(path, Names())
    parse = Parser(Names(), scan)
    with pytest.raises(SyntaxError, match= expected_string):
        parse.parse_network()
