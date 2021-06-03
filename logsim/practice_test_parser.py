"""
A test independent from pytests, allowing visualisation of parser output.

Useful for debugging.
"""

from scanner import Symbol
from scanner import Scanner
from names import Names
from parse import Parser
# from devices import Device
# from network import Network
import sys
import os


def open_file(path):
    """Open and return the file specified by path for reading."""
    try:
        return open(path, "r", encoding="utf-8")
    except IOError:
        print("error, can't find or open file")
        sys.exit()


def main():
    """Preliminary exercises for Part IIA Project GF2."""
    # Check command line arguments
    arguments = sys.argv[1:]
    if len(arguments) != 1:
        print("Error! One command line argument is required.")
        sys.exit()

    else:
        print("\nNow opening file...")
        # Print the path provided and try to open the file for reading
        path = os.getcwd() + "/" + arguments[0]
        print(path)    # print path
        names = Names()
        scan = Scanner(path, names)
        parse = Parser(names, scan)
        parse.parse_network()


if __name__ == "__main__":
    main()
