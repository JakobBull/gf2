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

@pytest.mark.parametrize(
    "file, expected_errors",
    # expected_errors, list of list of properties for each error that should occur
    # each error will take a list of the form:
    # error_type, symbol_string_that_caused_error, line_number, start_char_number
    # can determine line_number and start_char_number from text editor like
    # atom/vs code for writing tests. Usually at the bottom in the form:
    # line# : char#
    [
        ("no_errors", []),
        ("test_1",[[0,"CONNECTIONS",1,1]]),
        ("test_2",[[1,"SW1",3,5]]),
        ("test_3",[[2,"912",4,5]]),
        ("test_4",[[4,"-",6,8]]),
        ("test_5",[[13,"1",9,14]]),
        ("test_6",[[12,";",10,15]]),
        ("test_7",[[11,"G2.I1",11,8]]),
        ("test_8",[[10,"G22",12,5]]),
        ("test_9",[[18,"SW19",15,5]]),
        ("test_10",[[19,"0",16,9]]),
        ("test_11",[[27,"W2",20,5]]),
        ("test_12",[[24,"W2",20,5]]),
    ]
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
