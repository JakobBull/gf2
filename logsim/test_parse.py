from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from parse import Parser
from scanner import Symbol
from scanner import Scanner
from error import Error

import pytest
import sys
import os

def test_working_spec():
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    path = "parse_test_files/test_working_spec.txt"
    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner)
    parser.parse_network()
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

    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)

    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner)
    parser.parse_network()
    # print(len(Error.types))
    for i in range(len(expected_errors)):
        error = expected_errors[i] # the list for the ith error from expected_errors
        # make sure error types stored in error class align with those expected
        # by expected_errors
        # print("1:", end="\t")
        # print(Error.types[i], end="\t")
        # print(Error.symbols[i].string, end="\t")
        # print(Error.symbols[i].line_number, end="\t")
        # print(Error.symbols[i].start_char_number)
        assert(Error.types[i] == error[0])
        assert(Error.symbols[i].string == error[1])
        assert(Error.symbols[i].line_number == error[2])
        assert(Error.symbols[i].start_char_number == error[3])
