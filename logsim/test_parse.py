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
    "file, expected_errors",
    # expected_errors, list of list of properties for each error that should occur
    # each error will take a list of the form:
    # error_type, symbol_string_that_caused_error, line_number, start_char_number
    # can determine line_number and start_char_number from text editor like
    # atom/vs code for writing tests. Usually at the bottom in the form:
    # line# : char#
    [
        ("test_1", [[0,"CONNECTIONS",1,1],[3,"-",3,9]])
    ],
)
# tests if query returns correct name ID for a name sting
def test_error_detection(file, expected_errors):
    path = "parse_test_files/"
    path += file
    path += ".txt"
    scan = Scanner(path, Names())
    parse = Parser(Names(), scan)
    parse.parse_network()
    for i in range(len(expected_errors)):
        error = expected_errors[i] # the list for the ith error from expected_errors
        # make sure error types stored in error class align with those expected
        # by expected_errors
        assert(Error.types[i] == error[0])
        assert(Error.symbols[i].string == error[1])
        assert(Error.symbols[i].line_number == error[2])
        assert(Error.symbols[i].start_char_number == error[3])
