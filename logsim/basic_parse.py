class Parser:
    def __init__(self, names, scanner):
        """Initialise constants."""
        self.names = names
        self.scanner = scanner
        self.symbol = None

    def phrase_detection(self, phrase_type_list, end_detection = 1):
        """
        checks if lines are all of a certain phrase type

        Our EBNF breaks all phrase types into different headings.
        Once the parser is in a particular heading, phrase_detection
        can be called to ensure only the expected phrase is being called.

        The expected phrase is defined by the phrase_type_list,
        which should be a touple describing the order of types expected in
        a phrase.

        phrase_detection will return a list of a list of essential data from
        phrase that will allow for collection of key data for each phrase

        end_detection is the type which will terminate the repeated search
        for the phrase, which is set to "}" by default

        RETURN:
            error if line doesn't match expected phrase determined by
            phrase_type_list

            phrase_detection will return no errors if the correct phrase is
            detected multiple times and then a "}" is detected.
            If no errors are detected, phrase_detection will return a list of a
            list of: ids of all names that occur in a phrase, or string for all
            numbers that occur in a phrase
        """
        type_dict = {
            0: "{",
            1: "}",
            2: "=",
            3: ".",
            4: "-",
            5: ":",
            6: "KEYWORD",
            7: "NUMBER",
            8: "NAME",
            9: "EOF",
        }
        #create output list for whole function, where line_output
        #will be added after each read of a line
        output = []

        #output
        line_output = []

        #length of phrase
        length = len(phrase_type_list)
        i = 0
        while  i < length:
            # Call for the next symbol from scanner
            self.symbol = self.scanner.get_symbol()
            print(self.symbol.type)
            if (self.symbol.type == end_detection): return output
            if(self.symbol.type != phrase_type_list[i]):
                raise TypeError(
                    "Wrong type! at " + self.symbol.string +
                    " on line " + str(self.symbol.line_number) +
                    " and character " + str(self.symbol.start_char_number) +
                    "\n expected: " + str(type_dict.get(phrase_type_list[i])) +
                    " but got: " + str(type_dict.get(self.symbol.type))
                )
            elif (self.symbol.type in (6,7,8)):
                #if symbol type is keyword, number or name
                line_output.append(self.symbol.id)
                i += 1
            elif (i == length-1 and self.symbol.type == phrase_type_list[length - 1]):
                output.append(line_output)
                line_output = []
                i = 0
            else:
                i += 1
