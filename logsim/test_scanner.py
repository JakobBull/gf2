from scanner import Symbol
from scanner import Scanner
from names import Names
import pytest


def test_advance():
    scan = Scanner("scanner_test_files/test_advance.txt", Names())
    assert(scan.current_character == 'a')
    scan.advance()
    assert(scan.current_character == 'b')
    scan.advance()
    assert(scan.current_character == 'c')


def test_skip_spaces():
    scan = Scanner("scanner_test_files/test_skip_spaces.txt", Names())
    assert(scan.current_character == 'a')
    scan.advance()  # move forward to whitespace
    scan.skip_spaces()
    assert(scan.current_character == 'h')   # just spaces
    scan.advance()  # move forward to whitespace
    scan.skip_spaces()
    assert(scan.current_character == 'b')   # tabs aswell


def test_get_name():
    scan1 = Scanner("scanner_test_files/test_get_name1.txt", Names())
    assert(scan1.get_name() == "hello")
    scan2 = Scanner("scanner_test_files/test_get_name2.txt", Names())
    assert(scan2.get_name() == "bye")


def test_get_number():
    scan1 = Scanner("scanner_test_files/test_get_number1.txt", Names())
    assert(scan1.get_name() == "123")
    scan2 = Scanner("scanner_test_files/test_get_number2.txt", Names())
    assert(scan2.get_name() == "0900")


# tests scanner works on a single line
def test_scanner():
    scan = Scanner("scanner_test_files/scanner_test_line.txt", Names())
    symbol = scan.get_symbol()
    assert(symbol.type == scan.KEYWORD)      # DEVICES
    assert(symbol.line_number == 1)
    assert(symbol.start_char_number == 1)
    assert(symbol.end_char_number == 8)
    assert(scan.get_symbol().type == scan.NUMBER)       # 123
    assert(scan.get_symbol().type == scan.NAME)         # hello
    assert(scan.get_symbol().type == scan.EQUALS)       # =
    assert(scan.get_symbol().type == scan.KEYWORD)      # XOR
    # "test specific to our ebnf")
    symbol = scan.get_symbol()
    assert(symbol.type == scan.NAME)                    # bye
    assert(symbol.line_number == 1)
    assert(symbol.start_char_number == 25)
    assert(symbol.end_char_number == 28)
    assert(scan.get_symbol().type == scan.SEMICOLON)    # ;
    symbol = scan.get_symbol()
    assert(symbol.type == scan.KEYWORD)                 # CONNECTIONS
    # "test specific to our ebnf")
    assert(symbol.line_number == 2)
    assert(symbol.start_char_number == 1)
    assert(symbol.end_char_number == 12)
    symbol = scan.get_symbol()
    assert(symbol.type == scan.KEYWORD)                  # NETWORK
    # "test specific to our ebnf")
    assert(symbol.line_number == 2)
    assert(symbol.start_char_number == 13)
    assert(symbol.end_char_number == 20)
    symbol = scan.get_symbol()
    assert(symbol.type == scan.NAME)                    # hello
    assert(symbol.line_number == 3)
    assert(symbol.start_char_number == 1)
    assert(symbol.end_char_number == 6)
    symbol = scan.get_symbol()
    assert(symbol.type == scan.NAME)                    # bye
    assert(symbol.line_number == 3)
    assert(symbol.start_char_number == 7)
    assert(symbol.end_char_number == 10)
    assert(scan.get_symbol().type == scan.EOF)

# order of symbol_type_list definition in scanner determines which
# numbers mean which type as shown below

# the symbol_type_list from scanner
# self.symbol_type_list = [self.LEFT_BRACKET, self.RIGHT_BRACKET,
# self.EQUALS, self.PERIOD, self.DASH, self.SEMICOLON, self.KEYWORD,
# self.NUMBER, self.NAME, self.EOF] = range(10)

# {         0
# }         1
# =         2
# .         3
# -         4
# ;         5
# KEYWORD   6
# NUMEBR    7
# NAME      8
# EOF       9

correct_type_list = [
    6, 0,                   # :NETWORK{
    6, 0,                   # :  DEVICES{
    8, 2, 6, 5,             # :      SW1 = SWITCH;
    8, 2, 6, 5,             # :      SW2 = SWITCH;
    8, 2, 6, 5,             # :      G1 = NAND;
    8, 2, 6, 5,             # :      G2 = NAND;
    1,                      # :  }
    6, 0,                   # :  CONNECTIONS{
    8, 4, 8, 3, 8, 5,       # :      SW1 - G1.I1;
    8, 4, 8, 3, 8, 5,       # :      SW2 - G2.I2;
    8, 4, 8, 3, 8, 5,       # :      G1 - G2.I1;
    8, 4, 8, 3, 8, 5,       # :      G2 - G1.I2;
    1,                      # :  }
    6, 0,                   # :  SIGNALS{
    6, 0,                   # :      SETSIGNAL{
    8, 2, 7, 6, 7, 5,       # :          SW1 = 0 starttime 0;
    8, 2, 7, 6, 7, 5,       # :          SW2 = 0 starttime 0;
    1,                      # :      }
    6, 0, 1,                # :      SETCLOCK{}
    1,                      # :  }
    6, 0,                   # :  MONITOR{
    8, 5,                   # :      G1;
    8, 5,                   # :      G2;
    1,                      # :  }
    1,                      # :}
    9                       # :EOF
]

# test that the scanner works on our example_1
def test_scanner_example_file():
    scan = Scanner("scanner_test_files/example_1.txt", Names())
    i = 0
    while True:
        symbol = scan.get_symbol()
        assert(symbol.type == correct_type_list[i])
        print(i, end="\t")
        print(correct_type_list[i], end="\t")
        print(symbol.type)
        if(i == 10):
            assert(symbol.line_number == 4)
            assert(symbol.start_char_number == 8)
        i += 1
        if(symbol.type == scan.EOF):
            break
# test that the scanner works on our example_1
def test_scanner_example_file_with_comments():
    scan = Scanner("scanner_test_files/example_1_with_comments.txt", Names())
    i = 0
    while True:

        symbol = scan.get_symbol()
        assert(symbol.type == correct_type_list[i])
        print(i, end="\t")
        print(correct_type_list[i], end="\t")
        print(symbol.type)
        if(i == 10):
            assert(symbol.line_number == 13)
            assert(symbol.start_char_number == 8)
        i += 1
        if(symbol.type == scan.EOF):
            break
