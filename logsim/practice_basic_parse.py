from scanner import Symbol
from scanner import Scanner
from names import Names
from basic_parse import Parser
import sys
import os


def open_file(path):
    try:
        """Open and return the file specified by path for reading"""
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
        path = os.getcwd()+ "/" + arguments[0]
        print(path)    #print path
        scan = Scanner(path, Names())
        print("scanning from: " + path)
        print("")
        print("type\tid\tline#\tstart_char#\tend_char#\tstring")
        while True:
            symbol = scan.get_symbol()
            print(symbol.type, end="\t")
            print(symbol.id, end="\t")
            print(symbol.line_number, end="\t")
            print(symbol.start_char_number, end="\t\t")
            print(symbol.end_char_number, end="\t\t")
            print(symbol.string)
            if(symbol.type == scan.EOF):
                break
        scan = Scanner(path, Names())
        parse = Parser(Names(), scan)
        print(parse.phrase_detection((8,2,6,5),(None,None,range(2,10),None),scan.EOF))

if __name__ == "__main__":
    main()
