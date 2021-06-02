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
        (
            "test_1",
            [
                [0,"CONNECTIONS",3,1],
                [1,"SW1",5,5],
                [2,"912",6,5],
                [3,"SW1",7,5],
                [4,"-",8,8],
                [13,"1",11,14],
                [12,";",12,15],
                [11,"G2.I1",13,8],
                [10,"G22",14,5],
                [18,"SW19",17,5],
                [19,"0",18,9],
                [27,"W2",22,5],
                [24,"W2",22,5]
            ]
        ),
        (
            "test_2",
            [
                [5,";",5,11],
                [7,"0",7,22],
                [6,"2",8,15],
                [14,"SW1",12,5],
                [20,"222",17,11],
                [22, "}",19,3],
                [26,"G1",22,5]
            ]
        ),
        (
            "test_3",
            [
                [8,"2",8,18],
                [9,"0",9,29],
                [16,";",12,14],
                [17,"I2",13,14],
                [23,"}",20,3]
            ]
        )
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
