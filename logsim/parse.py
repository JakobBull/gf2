"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""


class Parser:

    """Parse the definition file and build the logic network.

    The parser deals with error handling. It analyses the syntactic and
    semantic correctness of the symbols it receives from the scanner, and
    then builds the logic network. If there are errors in the definition file,
    the parser detects this and tries to recover from it, giving helpful
    error messages.

    Parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.

    Public methods
    --------------
    parse_network(self): Parses the circuit definition file.
    """

    def __init__(self, names, scanner):
        """Initialise constants."""
        self.names = names
        #self.devices = devices
        #self.network = network
        #self.monitors = monitors
        self.scanner = scanner

        self.type = None
        self.id = None
        self.parse_errors = 0

        self.device_types = [ "NAND","AND", "NOR", "OR", "XOR", "SWITCH", "DTYPE", "CLOCK"]
        self.device_names = []
        self.headings = ["NETWORK","DEVICES", "CONNECTIONS", "SIGNALS", "SETSIGNAL", "SETCLOCK", "MONITOR" ]
        self.punctuation = [";", "{", "}", "-", "="]
        self.numbers = range(20)

        self.headings_found = 0
        self.sections_complete = 0
        self.devices_parsed = False
        self.connections_parsed = False
        self.setsignal_parsed = False
        self.setclock_parsed = False
        self.monitor_parsed = False

    def parse_network(self):
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.

        while True:
            # Call for the next symbol from scanner
            self.symbol = self.scanner.get_symbol()

            if self.symbol.id>=scanner.CONNECTIONS_ID and self.symbol.id<=scanner.MONITOR_ID #Check if symbol is a Heading
                if self.headings.index(self.symbol) != self.headings_found: #Check if headings are called in the right order
                    self.parse_errors += 1
                    raise SyntaxError("Headings called in the wrong order")

                elif self.symbol.id == self.scanner.NETWORK_ID:
                    self.headings_found += 1


                elif self.symbol.id == self.scanner.DEVICES_ID:
                    if self.sections_complete == 0 and self.headings_found == 1:
                        self.headings_found += 1
                        self.device_list()
                    else:
                        raise SyntaxError("Headings called in wrong order")


                elif self.symbol == self.scanner.CONNECTIONS_ID:
                    if self.sections_complete == 1 and self.headings_found == 2:
                        self.headings_found += 1
                        self.connection_list()
                    else:
                        raise SyntaxError("Headings called in wrong order")

                elif self.symbol == self.scanner.SIGNALS_ID:
                    if self.sections_complete == 2 and self.headings_found == 3:
                        self.headings_found += 1
                        self.signal_list()
                    else:
                        raise SyntaxError("Headings called in wrong order")


                elif self.symbol == self.scanner.MONITOR_ID:
                    if self.sections_complete == 5 and self.headings_found == 6:
                        self.headings_found += 1

                    else:
                        raise SyntaxError("Headings called in wrong order")


            elif self.sections_complete == 6 and self.headings_found == 7:
                return True
            else:
                return False



    def OPENCURLY_search(self):
        """Function which searches for a { after a heading"""
        self.symbol = self.scanner.get_symbol()
        if self.symbol.type != self.scanner.LEFT_BRACKET:
            raise SyntaxError("Always need to follow a heading with {")

    def device_list(self):
        """ Function which parses the device list"""

        self.OPENCURLY_search()

        self.symbol = self.scanner.get_symbol()
        self.device_parse()
        self.symbol = self.scanner.get_symbol()
        while self.symbol.type == self.scanner.SEMICOLON:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.RIGHT_BRACKET:
                self.devices_parsed = True
                self.sections_complete += 1
                break
            else:
                self.device_parse()
                self.symbol = self.scanner.get_symbol

    def device_parse(self):
        """Function which parses a single line of a device definition"""
        # Expected format : name EQUALS device

        if self.symbol.type != self.scanner.NAME:
            self.parse_errors += 1
            raise SyntaxError("Name of device must contain a letter")

        else:
            self.device_names.append(self.symbol) # add symbol id to a list of device ids
            self.symbol = self.scanner.get_symbol() #Get next symbol which should be an = sign
            if self.symbol.type != self.scanner.EQUALS:
                    self.parse_errors += 1
                    raise SyntaxError
            else:
                self.symbol = self.scanner.get_symbol()
                if self.symbol.id < 2 and self.symbol.id > 9:
                    self.parse_errors += 1
                    raise SyntaxError("Device type not found")



    def connection_list(self):
        """Function whhich parses the connection list"""

        self.OPENCURLY_search()

        self.symbol = self.scanner.get_symbol() # Go to first symbol of line
        self.connection_parse()
        self.symbol = self.scanner.get_symbol() # Go to last symbol of line, should be ;
        while self.symbol.type == self.scanner.SEMICOLON:
            self.symbol = self.scanner.get_symbol() # Go to first symbol of next line
            if self.symbol.type == self.scanner.LEFT_BRACKET: # Check if } which denotes end of connections
                self.connections_parsed = True
                self.sections_complete += 1
                break
            else:
                self.connection_parse()
                self.symbol = self.scanner.get_symbol  #Go to last symbol of line, should be ;


    def connection_parse(self):
        """Function which parses a single connection"""
        # Expected format : name HYPHEN name DOT INPUT

        if self.symbol not in self.device_names:
            self.parse_errors += 1
            raise SyntaxError("Device not defined")

        else:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type != self.type.DASH:
                self.parse_errors += 1
                raise SyntaxError("No - found to define connection")

            else:
                self.symbol = self.scanner.get_symbol()
                if self.symbol.type != self.type.NAME:
                    self.parse_errors += 1
                    raise SyntaxError("Device not defined")

                else:
                    self.symbol = self.scanner.get_symbol()
                    if self.symbol.type != self.scanner.PERIOD:
                        raise SyntaxError("No . found")

                    else:
                        self.symbol = self.scanner.get_symbol()
                        if self.symbol.type != self.scanner.NUMBER:
                            raise SyntaxError("Input not defined")





    def signal_list(self):
        "function whcih parses the signal setting"

        self.OPENCURLY_search()
        self.symbol = self.scanner.get_symbol() #Get next symbol, should be SETSIGNAL
        if self.symbol.id == self.scanner.SETSIGNALS_ID:
            self.headings_found += 1
            self.setsignal_list()
        else:
            self.parse_errors += 1
            raise SyntaxError("SETSIGNAL heading expected")

        self.symbol = self.scanner.get_symbol() #Get next symbol, should be SETCLOCK
        if self.symbol == self.scanner.SETCLOCK_ID:
            self.headings_found += 1
            self.setclock_parse()

        self.symbol = self.scanner.get_symbol() #Get next symbol, should be }
        if self.symbol.type == self.scanner.RIGHT_BRACKET:
            self.sections_complete += 1




    def setsignal_list(self):
        """Function which parses the setsignal section"""

        self.OPENCURLY_search()
        self.symbol = self.scanner.get_symbol() #Go to first symbol of the line
        if self.symbol.type == self.scanner.RIGHT_BRACKET:
            self.setsignal_parsed = True
            self.sections_complete += 1
            return
        self.setsignal_parse()
        while self.symbol.type == self.scanner.SEMICOLON:
            self.symbol = self.scanner.get_symbol() # Go to first symbol of next line
            if self.symbol.type == self.scanner.RIGHT_BRACKET: # Check if } which denotes end of setsignal
                self.setsignal_parsed = True
                self.sections_complete += 1
                break
            self.setsignal_parse()




    def setsignal_parse(self):
        """Function which parses a single line of the setsignal section"""
        #Expected format : name EQUALS BINARYNUMBER "starttime" NUMBER SEMICOLON



        if self.symbol not in self.device_names:
            self.parse_errors += 1
            raise SyntaxError("Device not defined")


        self.symbol = self.scanner.get_symbol()

        if self.symbol.type != self.scanner.EQUALS:
                self.parse_errors += 1
                raise SyntaxError("= sign expected")

        self.symbol = self.scanner.get_symbol()
        if self.symbol.id != 0 and self.symbol.id != 1 and self.symbol.type == self.scanner.NUMBER:
            self.parse_errors += 1
            raise SyntaxError("Signal can only be set to 1 or 0")
        elif self.symbol.type != self.symbol.NUMBER:
            self.parse_errors += 1
            raise SyntaxError("Signal can only be set to 1 or 0")
        self.symbol = self.scanner.get_symbol()

        if self.symbol != "starttime":
            self.parse_errors += 1
            raise SyntaxError("word starttime expected")

        self.symbol = self.scanner.get_symbol()

        if self.symbol.type != self.scanner.NUMBER:
            self.parse_errors += 1
            raise SyntaxError("Integer number required")

        self.symbol = self.scanner.get_symbol()

        if self.symbol.type != self.scanner.SEMICOLON:
            self.parse_errors += 1
            raise SyntaxError("Expected ; to end line")


    def setclock_list(self):
        self.OPENCURLY_search()
        self.symbol = self.scanner.get_symbol()
        if self.symbol.type == self.scanner.RIGHT_BRACKET:
            self.setclockparsed = True
            self.sections_complete += 1
            return
        self.setclock_parse()
        while self.symbol.type == self.scanner.SEMICOLON:
            self.symbol = self.scanner.get_symbol() # Go to first symbol of next line
            if self.symbol.type == self.scanner.RIGHT_BRACKET: # Check if } which denotes end of setsignal
                self.setclock_parsed = True
                self.sections_complete += 1
                break
            self.setclock_parse()



    def setclock_parse(self):
        """"Function which parses a single line of the setclock section"""
        # Expected format : name EQUALS BINARYNUMBER "starttime" NUMBER "period" NUMBER "first change" NUMBER SEMICOLON


        if self.symbol not in self.device_names:
            self.parse_errors += 1
            raise SyntaxError("Device not defined")

        self.symbol = self.scanner.get_symbol()

        if self.symbol.type != self.scanner.EQUALS:
                self.parse_errors += 1
                raise SyntaxError("= sign expected")

        self.symbol = self.scanner.get_symbol()
        if self.symbol.id != 0 and self.symbol.id != 1 and self.symbol.type == self.scanner.NUMBER:
            self.parse_errors += 1
            raise SyntaxError("Signal can only be set to 1 or 0")
        elif self.symbol.type != self.symbol.NUMBER:
            self.parse_errors += 1
            raise SyntaxError("Signal can only be set to 1 or 0")
        self.symbol = self.scanner.get_symbol()

        if self.symbol.id != self.scanner.starttime_ID:
            self.parse_errors += 1
            raise SyntaxError("word starttime expected")

        self.symbol = self.scanner.get_symbol()

        if self.symbol.type != self.scanner.NUMBER:
            self.parse_errors += 1
            raise SyntaxError("Integer number required")

        self.symbol = self.scanner.get_symbol()

        if self.symbol.type != self.scanner.period_ID:
            self.parse_errors += 1
            raise SyntaxError("word period expected")

        self.symbol = self.scanner.get_symbol()

        if self.symbol.type != self.scanner.NUMBER:
            self.parse_errors += 1
            raise SyntaxError("Integer number required")

        self.symbol = self.scanner.get_symbol()

        if self.symbol.id != self.scanner.firstchange_ID:
            self.parse_errors += 1
            raise SyntaxError("word first expected")

        self.symbol = self.scanner.get_symbol()

        if self.symbol != "symbol":
            self.parse_errors += 1
            raise SyntaxError("word symbol expected")

        self.symbol = self.scanner.get_symbol()

        if self.symbol.type != self.scanner.NUMBER:
            self.parse_errors += 1
            raise SyntaxError("Integer number required")

        self.symbol = self.scanner.get_symbol()

        if self.symbol.type != self.scanner.SEMICOLON:
            self.parse_errors += 1
            raise SyntaxError("Expected ; to end line")


    def monitor_list(self):
        """Function that parses the monitor section of the code"""

        self.OPENCURLY_search()

        self.symbol = self.scanner.get_symbol()

        if self.symbol.type == self.scanner.RIGHTBRACKET:
            self.parse_errors += 1
            raise SyntaxError("No devices monitored")

        else:
            while self.symbol.type == self.scanner.SEMICOLON:
                self.symbol = self.scanner.get_symbol()
                if self.symbol.type == self.scanner.RIGHTBRACKET:
                    self.sections_complete += 1
                    self.monitor_parsed = True
                    break
                else:
                    self.monitor_parse()

    def monitor_parse(self):
        """Function which parses a line in Monitor """
        #Expected format : name SEMICOLON
        if self.symbol not in self.device_names:
            self.parse_errors += 1
            raise SyntaxError("Device not defined")

        self.symbol = self.scanner.get_symbol()

        if self.symbol.type != self.scanner.SEMICOLON:
            self.parse_errors += 1
            raise SyntaxError("Expected ; to end line")
