from scanner import Symbol
from scanner import Scanner
from names import Names
from parse import Parser
from error import Error


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
        ("test_1", Error.error_message[0]),
        ("test_2", Error.error_message[1]),
        ("test_3", Error.error_message[2]),
        ("test_4", Error.error_message[3]),
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
