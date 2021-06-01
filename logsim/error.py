from scanner import Symbol
import sys
import os
import math

class Error:
    num_errors = 0
    types = []
    symbols = []

    error_message = (
        "Headings called in wrong order",
        "Always need to follow a heading with {",
        "DEVICE: Name of device must contain a letter",
        "DEVICE: Name for device already used",
        "DEVICE: Expected symbol is an =",
        "DEVICE: Device type not found",
        "DEVICE: Word inputs required",
        "DEVICE: Invalid number of inputs",
        "DEVICE: Word halfperiod required",
        "DEVICE: Invalid halfperiod",
        "CONNECTION: Device not defined",
        "CONNECTION: No - found to define connection",
        "CONNECTION: No . found",
        "CONNECTION: Input not initialised",
        "CONNECTION: Input already defined",
        "Error creating connection",
        "D type output denoted by a .",
        "Not a valid D type output",
        "SIGNALS: Device not defined",
        "SIGNALS: = sign expected",
        "SIGNALS: Signal can only be set to 1 or 0",
        "SIGNALS: Integer number required",
        "SIGNALS: Expected ; to end line",
        "MONITOR: No devices monitored",
        "MONITOR: Device not defined",
        "MONITOR: Output not properly defined",
        "MONITOR: Device already monitored",
        "MONITOR: Expected ; to end line"
    )
    def __init__(self, type, symbol):
        Error.types.append(type)        # error type, number from list of error document
        Error.symbols.append(symbol)    # symbol that causes the error
        Error.num_errors += 1           # everytime an error called, number of errors increased

    def print_error(scanner):
        lines = Error.get_lines(scanner)
        print(str(Error.num_errors) + " ERRORS!:\n")
        for i in range(Error.num_errors):
            print("Error " + str(i) + ":")
            line = lines[Error.symbols[i].line_number-1]
            start_spaces = 0
            for c in line:
                if c.isspace():
                    start_spaces+=1
                else: break
            start = Error.symbols[i].start_char_number
            end = Error.symbols[i].end_char_number
            print("\"" + line.strip() + "\"")
            cursor = Error.symbols[i].start_char_number-start_spaces
            for n in range(cursor):
                print(' ', end = '')
            print("^")
            print(Error.error_message[Error.types[i]])
            #for n in range(len(Error.error_message[Error.types[i]])):
            #    print('-', end = '')
            for n in range(8):
                print('-', end = '')
            print("")
    def get_lines(scanner):
        try:
            """Open and return the file specified by path for reading"""
            file = open(scanner.path, "r", encoding="utf-8")
            lines = file.readlines()
            return lines
        except IOError:
            print("error, can't find or open file")
            sys.exit()
