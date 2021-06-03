"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""

from error import Error


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

    def __init__(self, names, devices, network, monitors, scanner):
        """Initialise constants."""
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner

        self.type = None
        self.id = None
        self.parse_errors = 0
        self.device_names = []
        self.gate_var_inputs_IDs = [
            self.scanner.AND_ID,
            self.scanner.NAND_ID,
            self.scanner.OR_ID,
            self.scanner.NOR_ID
        ]
        self.device_IDs = [
            self.scanner.AND_ID,
            self.scanner.NAND_ID,
            self.scanner.OR_ID,
            self.scanner.NOR_ID,
            self.scanner.XOR_ID,
            self.scanner.XOR_ID,
            self.scanner.DTYPE_ID,
            self.scanner.SWITCH_ID,
            self.scanner.CLOCK_ID
        ]
        self.heading_IDs = [self.scanner.NETWORK_ID, self.scanner.DEVICES_ID,
                            self.scanner.CONNECTIONS_ID,
                            self.scanner.SIGNALS_ID,
                            self.scanner.MONITOR_ID]
        self.new_device_id = None
        self.new_device_type = None
        self.numbers = range(20)

        self.headings_found = 0
        self.sections_complete = 0
        self.devices_parsed = False
        self.connections_parsed = False
        self.setsignal_parsed = False
        self.setclock_parsed = False
        self.monitor_parsed = False
        self.input_list = []
        self.input_number = None
        self.input_I = None

    def parse_network(self):
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.

        print(self.gate_var_inputs_IDs)
        print("Netowrk_ID: ", self.scanner.NETWORK_ID)
        while True:

            # Call for the next symbol from scanner
            self.symbol = self.scanner.get_symbol()
            if self.parse_errors != 0:
                Error.print_error(self.scanner)
                return False

            if self.symbol.type == self.scanner.KEYWORD:
                # Check if symbol is a Heading
                print('Keyword')
                print(self.symbol.string)
                if self.symbol.id == self.scanner.NETWORK_ID:
                    self.headings_found += 1
                    self.OPENCURLY_search()

                elif self.symbol.id == self.scanner.DEVICES_ID:

                    if (self.sections_complete == 0 and
                            self.headings_found == 1):
                        self.headings_found += 1
                        print("devices")
                        self.device_list()
                    else:
                        self.parse_errors += 1
                        Error(0, self.symbol)

                elif self.symbol.id == self.scanner.CONNECTIONS_ID:

                    if (self.sections_complete == 1 and
                            self.headings_found == 2):
                        self.headings_found += 1
                        print("connections")
                        self.connection_list()
                    else:
                        self.parse_errors += 1
                        Error(0, self.symbol)

                elif self.symbol.id == self.scanner.SIGNALS_ID:
                    if (self.sections_complete == 2 and
                            self.headings_found == 3):
                        self.headings_found += 1
                        print("signals")
                        self.setsignal_list()
                    else:
                        self.parse_errors += 1
                        Error(0, self.symbol)

                elif self.symbol.id == self.scanner.MONITOR_ID:
                    if (self.sections_complete == 3 and
                            self.headings_found == 4):
                        self.headings_found += 1
                        self.monitor_list()

                    else:
                        self.parse_errors += 1
                        Error(0, self.symbol)

            elif (self.sections_complete == 4 and
                    self.headings_found == 5 and
                    self.parse_errors == 0 and
                    self.symbol.type == self.scanner.EOF):
                print(self.symbol.string)
                print("complete")
                print(self.monitors.monitors_dictionary)
                return True
            elif self.symbol.type == self.scanner.EOF:
                Error.print_error(self.scanner)
                return False

    def OPENCURLY_search(self):
        """Search for a { after a heading."""
        self.symbol = self.scanner.get_symbol()
        if self.symbol.type != self.scanner.LEFT_BRACKET:
            self.parse_errors += 1

            Error(1, self.symbol)
        print('{')

    def device_list(self):
        """Parse the device list."""
        self.OPENCURLY_search()

        self.symbol = self.scanner.get_symbol()
        self.device_parse()
        self.symbol = self.scanner.get_symbol()
        print(self.symbol.string)
        while self.symbol.type == self.scanner.SEMICOLON:
            print(self.symbol.string)
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.RIGHT_BRACKET:
                print(self.symbol.string)
                self.devices_parsed = True
                self.sections_complete += 1
                break
            else:
                self.device_parse()
                self.symbol = self.scanner.get_symbol()

    def device_parse(self):
        """Parse a single line of a device definition."""
        # Expected format : name EQUALS device

        if self.symbol.type != self.scanner.NAME:
            self.parse_errors += 1
            Error(2, self.symbol)
            self.advance_line_error()

        elif self.symbol.id in self.device_names:
            self.parse_errors += 1
            Error(3, self.symbol)
            self.advance_line_error()

        else:
            self.device_names.append(self.symbol.id)
            # add symbol id to a list of device ids
            self.new_device_id = self.symbol.id
            print(self.symbol.string)
            self.symbol = self.scanner.get_symbol()
            # Get next symbol which should be an = sign
            if self.symbol.type != self.scanner.EQUALS:
                self.parse_errors += 1
                Error(4, self.symbol)
                self.advance_line_error()
            else:
                self.symbol = self.scanner.get_symbol()
                print(self.symbol.string)

                if self.symbol.id not in self.device_IDs:
                    self.new_device_id = self.symbol.id
                    self.parse_errors += 1
                    Error(5, self.symbol)
                    self.advance_line_error()

                else:
                    self.new_device_type = self.symbol.id
                    # Check whether inputs required
                    if (self.symbol.id == self.scanner.XOR_ID or
                            self.symbol.id == self.scanner.DTYPE_ID):
                        self.devices.make_device(
                            self.new_device_id, self.new_device_type, None)

                    elif self.symbol.id == self.scanner.SWITCH_ID:
                        print('switch found')
                        # Set switches to 0, can change later
                        self.devices.make_switch(self.new_device_id, 0)

                    elif self.symbol.id in self.gate_var_inputs_IDs:
                        print("gate found")
                        print("symbol string", self.symbol.string)
                        print("symbol id: ", self.symbol.id)
                        print("symbol type:", self.symbol.type)
                        # Next symbol should be "inputs"
                        self.symbol = self.scanner.get_symbol()
                        if self.symbol.string != "inputs":
                            self.parse_errors += 1
                            Error(6, self.symbol)
                            self.advance_line_error()
                        else:
                            self.symbol = self.scanner.get_symbol()
                            print(self.symbol.string)
                            if self.symbol.type != self.scanner.NUMBER:
                                self.parse_errors += 1
                                Error(7, self.symbol)
                                self.advance_line_error()

                            if (self.symbol.number < 1 or
                                    self.symbol.number > 16):
                                # Check number of inputs in range
                                self.parse_errors += 1
                                Error(7, self.symbol)
                                self.advance_line_error()

                            else:
                                self.devices.make_gate(
                                    self.new_device_id, self.new_device_type,
                                    self.symbol.number)
                                # Make the gate

                    elif self.symbol.id == self.scanner.CLOCK_ID:
                        # Next symbol should be "halfperiod"
                        self.symbol = self.scanner.get_symbol()
                        if self.symbol.string != "halfperiod":
                            self.parse_errors += 1
                            Error(8, self.symbol)
                            self.advance_line_error()

                        else:
                            # Next symbol should be a number
                            self.symbol = self.scanner.get_symbol()
                            if self.symbol.type != self.scanner.NUMBER:
                                self.parse_errors += 1
                                Error(9, self.symbol)
                                self.advance_line_error()
                            else:
                                self.devices.make_clock(
                                    self.new_device_id, self.symbol.number)

    def connection_list(self):
        """Parse the connection list."""
        self.OPENCURLY_search()

        self.symbol = self.scanner.get_symbol()
        # Go to first symbol of line
        self.connection_parse()
        self.symbol = self.scanner.get_symbol()
        # Go to last symbol of line, should be ;
        while self.symbol.type == self.scanner.SEMICOLON:
            self.symbol = self.scanner.get_symbol()
            # Go to first symbol of next line
            if self.symbol.type == self.scanner.RIGHT_BRACKET:
                # Check if } which denotes end of connections
                print(self.devices.devices_list)
                self.connections_parsed = True
                self.sections_complete += 1
                break
            else:
                self.connection_parse()
                self.symbol = self.scanner.get_symbol()
                # Go to last symbol of line, should be ;

    def connection_parse(self):
        """Parse a single connection."""
        # Expected format : name DASH name PERIOD Inumber
        # For DTYPE format: name DASH name PERIOD DTYPE_INPUT

        if self.symbol.id not in self.device_names:
            #  print("Not defined:", self.symbol.string)
            self.parse_errors += 1
            Error(10, self.symbol)
            self.advance_line_error()

        else:
            [in_device_id, in_port_id] = self.signame_in()

            self.symbol = self.scanner.get_symbol()

            if self.symbol.type != self.scanner.DASH:
                self.parse_errors += 1
                Error(11, self.symbol)
                self.advance_line_error()

            else:
                self.symbol = self.scanner.get_symbol()
                print(self.symbol.string)
                if self.symbol.id not in self.device_names:
                    self.parse_errors += 1
                    Error(10, self.symbol)
                    self.advance_line_error()

                elif self.devices.get_device(
                        self.symbol.id).device_kind == self.devices.D_TYPE:
                    out_device_id = self.symbol.id
                    self.symbol = self.scanner.get_symbol()
                    if self.symbol.type != self.scanner.PERIOD:
                        self.parse_errors += 1
                        Error(12, self.symbol)
                        self.advance_line_error()

                    else:
                        self.symbol = self.scanner.get_symbol()
                        if self.symbol.id not in self.devices.dtype_input_ids:
                            self.parse_errors += 1
                            Error(13, self.symbol)
                            self.advance_line_error()
                        else:
                            error_type = self.network.make_connection(
                                in_device_id, in_port_id,
                                out_device_id, self.symbol.id)
                            if error_type != self.network.NO_ERROR:
                                self.parse_errors += 1
                                Error(15, self.symbol)
                                self.advance_line_error()
                            else:
                                print("No DTYPE error")

                else:

                    out_device = self.devices.get_device(self.symbol.id)
                    # out_device_id = out_device.device_id
                    out_device_id = self.symbol.id
                    self.symbol = self.scanner.get_symbol()
                    if self.symbol.type != self.scanner.PERIOD:
                        self.parse_errors += 1
                        Error(12, self.symbol)
                        self.advance_line_error()

                    else:
                        self.symbol = self.scanner.get_symbol()
                        out_port_id = self.symbol.id
                        self.input_list = list(self.symbol.string)
                        if self.input_list[0] != "I":
                            self.parse_errors += 1
                            Error(13, self.symbol)
                        self.input_number = "".join(self.input_list[1:])

                        if self.input_number.isdigit() is False:
                            self.parse_errors += 1
                            Error(13, self.symbol)
                            self.advance_line_error()

                        error_type = self.network.make_connection(
                            in_device_id, in_port_id,
                            out_device_id, self.symbol.id)
                        if error_type != self.network.NO_ERROR:
                            self.parse_errors += 1
                            Error(15, self.symbol)
                            self.advance_line_error()

    def signame_in(self):
        """Return the device ID and port ID for a device."""
        in_device = self.devices.get_device(self.symbol.id)
        if in_device.device_kind == self.devices.D_TYPE:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type != self.scanner.PERIOD:
                self.parse_errors += 1
                Error(16, self.symbol)

            else:
                self.symbol = self.scanner.get_symbol()
                if self.symbol.id not in self.devices.dtype_output_ids:
                    self.parse_errors += 1
                    Error(17, self.symbol)

                else:
                    return [in_device.device_id, self.symbol.id]

        else:
            return [in_device.device_id, None]

    def setsignal_list(self):
        """Parse the setsignal section."""
        self.OPENCURLY_search()
        self.symbol = self.scanner.get_symbol()
        #  Go to first symbol of the line
        if self.symbol.type == self.scanner.RIGHT_BRACKET:
            # print(self.symbol.string)
            self.setsignal_parsed = True
            self.sections_complete += 1
            return
        self.setsignal_parse()
        while self.symbol.type == self.scanner.SEMICOLON:
            self.symbol = self.scanner.get_symbol()
            # Go to first symbol of next line
            if self.symbol.type == self.scanner.RIGHT_BRACKET:
                # Check if } which denotes end of setsignal
                self.setsignal_parsed = True
                self.sections_complete += 1
                break
            self.setsignal_parse()

    def setsignal_parse(self):
        """Parse a single line of the setsignal section."""
        # Expected format : name EQUALS BINARYNUMBER SEMICOLON
        if self.symbol.id not in self.device_names:
            self.parse_errors += 1
            Error(18, self.symbol)
            self.advance_line_error()

        switch_set_ID = self.devices.get_device(self.symbol.id)

        self.symbol = self.scanner.get_symbol()
        if self.symbol.type != self.scanner.EQUALS:
            self.parse_errors += 1
            Error(19, self.symbol)
            self.advance_line_error()
        self.symbol = self.scanner.get_symbol()
        if self.symbol.string != "0" and self.symbol.string != "1":
            self.parse_errors += 1
            Error(20, self.symbol)
            self.advance_line_error()

        elif self.symbol.type != self.scanner.NUMBER:
            self.parse_errors += 1
            Error(20, self.symbol)
            self.advance_line_error()
        elif self.symbol.string == "1":
            self.devices.set_switch(switch_set_ID, 1)

        self.symbol = self.scanner.get_symbol()

        if self.symbol.type != self.scanner.SEMICOLON:
            self.parse_errors += 1
            Error(22, self.symbol)
            self.advance_line_error()

    def monitor_list(self):
        """Parse the monitor section of the code."""
        self.OPENCURLY_search()

        self.symbol = self.scanner.get_symbol()

        if self.symbol.type == self.scanner.RIGHT_BRACKET:
            self.parse_errors += 1
            Error(23, self.symbol)

        else:
            self.monitor_parse()
            while self.symbol.type == self.scanner.SEMICOLON:
                self.symbol = self.scanner.get_symbol()
                if self.symbol.type == self.scanner.RIGHT_BRACKET:
                    # print(self.symbol.string)
                    self.sections_complete += 1
                    self.monitor_parsed = True
                    break
                else:
                    self.monitor_parse()

    def monitor_parse(self):
        """Parse a line in Monitor."""
        # Expected format : name SEMICOLON
        if self.symbol.id not in self.device_names:
            self.parse_errors += 1
            Error(24, self.symbol)
            self.advance_line_error()

        else:

            [device_id, output_id] = self.signame_in()

            error_type = self.monitors.make_monitor(device_id, output_id)

            if error_type == self.monitors.NOT_OUTPUT:
                self.parse_errors += 1
                Error(25, self.symbol)
                self.advance_line_error()

            elif error_type == self.monitors.MONITOR_PRESENT:
                self.parse_errors += 1
                Error(26, self.symbol)
                self.advance_line_error()

            self.symbol = self.scanner.get_symbol()

            if self.symbol.type != self.scanner.SEMICOLON:
                self.parse_errors += 1
                Error(27, self.symbol)
                self.advance_line_error()

    def advance_line_error(self):
        """Advances to the next ; xafter an error to continue parsing."""
        # FEATURE REMOVED AS IT CAUSED INFINITE LOOPS
        # while (self.symbol.type != self.scanner.SEMICOLON or
        #        self.symbol.type != self.scanner.RIGHT_BRACKET):
        #    self.symbol = self.scanner.get_symbol()
        #  if self.symbol.id in self.heading_IDs:
        pass
