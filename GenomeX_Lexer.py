import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk

lexical_panel = None  # Define lexical_panel as a global variable

def display_lexical_error(message):
    global lexical_panel  # Use the global lexical_panel
    try:
        lexical_panel.insert(tk.END, message + '\n', 'error')  # Insert error in GUI
        lexical_panel.yview(tk.END)  # Auto-scroll to latest error
        lexical_panel.tag_config('error', foreground='red')  # Highlight in red
    except NameError:
        print(message)  # Fallback if GUI isn't available
        pass

def display_lexical_pass(message):
    global lexical_panel  # Use the global lexical_panel
    try:
        lexical_panel.insert(tk.END, message + '\n', 'pass')  # Insert error in GUI
        lexical_panel.yview(tk.END)  # Auto-scroll to latest error
        lexical_panel.tag_config('pass', foreground='green')  # Highlight in red
    except NameError:
        print(message)  # Fallback if GUI isn't available
        pass

def is_end_of_lexeme(token):
    # End-of-lexeme characters (e.g., space, newline, punctuation)
    return token in {' ', '\n'}

def parseLexer(input_stream):
    print("Lexer Executed")
    """    
    Parameters:
        input_stream (str): The input code to parse.
    
    Returns:
        list: A list of tuples containing lexeme and token type.
    """
    tokens = []
    state = 0
    lexeme = ""
    char_iter = iter(input_stream)
    line_number = 1 
    found_error = False
    ascii = {" ", '!', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', 
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?', 
            '@', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 
            'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '[', '\\', ']', '^', '_', 
            '`', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 
            'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~', '/"'}

    ascii2 = {" ", '!', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', 
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?', 
            '@', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 
            'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '[', '\\', ']', '^', '_', 
            '`', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 
            'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~', '"'}
    
    upchar = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 
              'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 
              'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'}

    lowchar = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 
            'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 
            'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'}

    allchar = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 
               'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 
               'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 
               'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 
               'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z' }

    value = {'1','2','3','4','5','6','7','8','9'}

    allval = {'1','2','3','4','5','6','7','8','9','0'}

    valchar = {'1', '2', '3' ,'4', '5', '6' ,'7' ,'8' ,'9' ,'0',
               'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 
               'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 
               'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 
               'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 
               'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z' }
    
    underscore = {'_'}

    #DELIMITERS
    delim_arith = {'(', ' ', '^', } 
    delim_equal = {' ', '{', '(', '"'}
    delim_gen = {' ', ';' } 
    delim_end = {' ', ';', '=', ',', ')'}
    delim_1 = {' ', '('} 
    delim_2 = {' ', '{'} 
    delim_add = {'"', ' ', '^', '(', } 
    delim_string = {' ', '\n', ',', '}', ')', '+', '\t', ';'} 
    delim_update = {' ', ';', ')'}
    delim_id = {' ', '=', '<', '>', ';', '!', '[', '(', '&', '|', '*', ',', ')', '/', ':', ']'}
    delim_logic = {' ', '(', '^'} | allval | upchar
    delim_comp = {' ', '(', '^'} 
    period_delim = {' ', '(', '^'} | allval | upchar
    terminator_delim = {'\n', ' ', '\t'}
    open_parenthesis_delim = {'\n', '^', ' ', '(', ',', ')', '!'} 
    delim_splice = {'\n', '^', ' ', '(', ',', ')', '!'} 
    close_parenthesis_delim =  {')', ' ', '\n', '{', '}', '^', '+', '-', '/', '*', '%', '#', ';', ':'}
    open_braces_delim = {' ', '\\', "{"} 
    close_braces_delim = {' ', '\n', '#', "{", ",", ";"}
    open_bracket_delim = value
    close_bracket_delim = {' ', '=', '[', ',', ';'}
    delim_num = { '*', '/', '%', '<', '>', '=', ' ', '#', ')', '}', '&', '|', ";", "]", ",", ':'}
    delim_comment = {' ', '\n', ';', '}'}
    lookahead_char = None
    token = None

    while True:
        # print(state)
        if lookahead_char is not None:
            # print(f"token before {token}")
            token = lookahead_char  # Use cached lookahead character
            lookahead_char = None  # Clear the cache
            # print(f"token after {token}")
        else:
            try:
                # print(f"token before {token}")
                token = next(char_iter)
                # print(f"token after {token}")
            except StopIteration:
                # Handle end of stream if in error state
                if state == 1000 and lexeme:
                    display_lexical_error(f"Invalid lexeme: {lexeme.strip()} on line {line_number}")
                break  # End of input stream

        if token =='\n' and state < 424:
            if state == 1000 and lexeme:  # If in error state and lexeme exists
                display_lexical_error(f"Invalid lexeme: {lexeme.strip()} on line {line_number}")
                lexeme = ""  # Reset lexeme to avoid appending invalid values
                state = 0  # Reset state to recover

            if token == '\n':
                tokens.append(("\\n", "newline"))
                line_number += 1
            lexeme = ""  # Reset lexeme after delimiter processing
            state = 0  # Reset state for next token
            continue  # Skip further processing for delimiters

        try:
            # print(f"lookahead_char before {lookahead_char}")
            lookahead_char = next(char_iter)  # Peek the next character
            # print(f"lookahead_char after {lookahead_char}")
        except StopIteration:
            lookahead_char = None  # No more characters to proce
    
        if state == 0:
            print("Passed state 0")
            if token == " ":
                tokens.append((" ", "space"))
                lexeme = ""  # Reset lexeme after delimiter processing
                state = 0  # Reset state for next token
            elif token == "\t":
                tokens.append(("\\t", "tab"))
                lexeme = ""  # Reset lexeme after delimiter processing
                state = 0  # Reset state for next token
            #TEMP SOLUTION
            elif token == ",":
                tokens.append((token, token))
                lexeme = ""  # Reset lexeme after delimiter processing
                state = 0  # Reset state for next token
            #TEMP SOLUTION2
            elif token == "[":
                tokens.append((token, token))
                lexeme = ""  # Reset lexeme after delimiter processing
                state = 0  # Reset state for next token

            #:
            elif token == ':':
                state = 460
                lexeme = token 
                if lookahead_char in delim_splice or lookahead_char is None or lookahead_char == "\n":
                    state = 461
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                elif lookahead_char == ':':
                    state = 462
                elif lookahead_char in allchar or allval:
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                    state = 0
                else:
                    print("ERROR IN STATE 460")
                    state = 1000  # Reset state to recover

            elif token == '_':
                state = 1
                lexeme = token  
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000
                elif lookahead_char is None:
                    display_lexical_error(f"Invalid lexeme: '{lexeme.strip()}' on line {line_number}")
                    state = 1000
                    lexeme = ""
            elif token == 'a':
                state = 6
                lexeme = token  
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000
                elif lookahead_char is None:
                    display_lexical_error(f"Invalid lexeme: '{lexeme.strip()}' on line {line_number}")
                    state = 1000
                    lexeme = ""
            elif token == 'c':
                state = 16
                lexeme = token  
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000
                elif lookahead_char is None:
                    display_lexical_error(f"Invalid lexeme: '{lexeme.strip()}' on line {line_number}")
                    state = 1000
                    lexeme = ""
            elif token == 'd':
                state = 28
                lexeme = token  
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000
                elif lookahead_char is None:
                    display_lexical_error(f"Invalid lexeme: '{lexeme.strip()}' on line {line_number}")
                    state = 1000
                    lexeme = ""
            elif token == 'e':
                state = 43
                lexeme = token  
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000
                elif lookahead_char is None:
                    display_lexical_error(f"Invalid lexeme: '{lexeme.strip()}' on line {line_number}")
                    state = 1000
                    lexeme = ""
            elif token == 'f':
                state = 58
                lexeme = token  
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000
                elif lookahead_char is None:
                    display_lexical_error(f"Invalid lexeme: '{lexeme.strip()}' on line {line_number}")
                    state = 1000
                    lexeme = ""

            elif token == 'g':
                state = 62
                lexeme = token  
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000
                elif lookahead_char is None:
                    display_lexical_error(f"Invalid lexeme: '{lexeme.strip()}' on line {line_number}")
                    state = 1000
                    lexeme = ""
            elif token == 'i':
                state = 67
                lexeme = token 
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000
                elif lookahead_char is None:
                    display_lexical_error(f"Invalid lexeme: '{lexeme.strip()}' on line {line_number}")
                    state = 1000
                    lexeme = ""
            elif token == 'p':
                state = 70
                lexeme = token 
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000
                elif lookahead_char is None:
                    display_lexical_error(f"Invalid lexeme: '{lexeme.strip()}' on line {line_number}")
                    state = 1000
                    lexeme = ""
            elif token == 'q':
                state = 81
                lexeme = token 
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000
                elif lookahead_char is None:
                    display_lexical_error(f"Invalid lexeme: '{lexeme.strip()}' on line {line_number}")
                    state = 1000
                    lexeme = ""
            elif token == 'r':
                state = 87
                lexeme = token
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000
                elif lookahead_char is None:
                    display_lexical_error(f"Invalid lexeme: '{lexeme.strip()}' on line {line_number}")
                    state = 1000
                    lexeme = ""
            elif token == 's':
                state = 91
                lexeme = token 
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000
                elif lookahead_char is None:
                    display_lexical_error(f"Invalid lexeme: '{lexeme.strip()}' on line {line_number}")
                    state = 1000
                    lexeme = ""
            elif token == 'v':
                state = 102
                lexeme = token 
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000
                elif lookahead_char is None:
                    display_lexical_error(f"Invalid lexeme: '{lexeme.strip()}' on line {line_number}")
                    state = 1000
                    lexeme = ""
            elif token == 'w':
                state = 107
                lexeme = token 
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000
                elif lookahead_char is None:
                    display_lexical_error(f"Invalid lexeme: '{lexeme.strip()}' on line {line_number}")
                    state = 1000
                    lexeme = ""

            elif token == '+':
                state = 113
                lexeme = token 
                if lookahead_char in delim_add or lookahead_char is None or lookahead_char == "\n":
                    state = 114
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                elif lookahead_char == '+':
                    state = 115
                elif lookahead_char == '=':
                    state = 117
                elif lookahead_char in allchar or allval:
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                    state = 0
                else:
                    print("ERROR IN STATE 113")
                    state = 1000  # Reset state to recover

            #-
            elif token == '-':
                state = 119
                lexeme = token 
                if lookahead_char in delim_arith or lookahead_char is None or lookahead_char == "\n":
                    state = 120
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                elif lookahead_char in allval:
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                    state = 0
                elif lookahead_char in lowchar:
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                    state = 0
                elif lookahead_char in upchar:
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                    state = 0
                elif lookahead_char == '-':
                    state = 121
                elif lookahead_char == '=':
                    state = 123
                else:
                    print("ERROR IN STATE 119")
                    state = 1000  # Reset state to recover
            
            #*
            elif token == '*':
                state = 125
                lexeme = token 
                if lookahead_char in delim_arith or lookahead_char is None or lookahead_char == "\n":
                    state = 126
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                elif lookahead_char == '*':
                    state = 1125
                elif lookahead_char == '=':
                    state = 127
                else:
                    state = 1000  # Reset state to recover

            elif token == '/':
                state = 129
                lexeme = token 
                if lookahead_char in delim_arith or lookahead_char is None or lookahead_char == "\n":
                    state = 130
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                elif lookahead_char == '/':
                    state = 1129
                elif lookahead_char == '=':
                    state = 131
                elif lookahead_char == '*':
                    state = 425
                else:
                    state = 1000  # Reset state to recover

            elif token == '%':
                state = 133
                lexeme = token 
                if lookahead_char in delim_arith or lookahead_char is None or lookahead_char == "\n":
                    state = 134
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                elif lookahead_char == '=':
                    state = 135
                else:
                    print("ERROR IN STATE 133")
                    state = 1000  # Reset state to recover
            elif token == '&':
                state = 137
                lexeme = token  

            elif token == '|':
                state = 140
                lexeme = token  

            #=
            elif token == '=':
                state = 143
                lexeme = token 
                if lookahead_char in delim_equal or lookahead_char is None or lookahead_char == "\n":
                    state = 144
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                elif lookahead_char == '=':
                    state = 145
                elif lookahead_char in allval or lookahead_char in allchar:
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                    state = 0
                else:
                    print("ERROR IN STATE 143")
                    state = 1000  # Reset state to recover

            #>
            elif token == '>':
                state = 147
                lexeme = token 
                if lookahead_char in delim_comp or lookahead_char is None or lookahead_char == "\n":
                    state = 148
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                elif lookahead_char == '=':
                    state = 149
                else:
                    print("ERROR IN STATE 147")
                    state = 1000  # Reset state to recover

            #<
            elif token == '<':
                state = 151
                lexeme = token 
                if lookahead_char in delim_comp or lookahead_char is None or lookahead_char == "\n":
                    state = 152
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                elif lookahead_char == '=':
                    state = 153
                else:
                    print("ERROR IN STATE 151")
                    state = 1000  # Reset state to recover

            #!
            elif token == '!':
                state = 155
                lexeme = token 
                if lookahead_char in delim_comp or lookahead_char is None or lookahead_char == "\n":
                    state = 156
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                elif lookahead_char in allval or lookahead_char in allchar  :
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                    state = 0
                elif lookahead_char == '=':
                    state = 157
                else:
                    print("ERROR IN STATE 155")
                    state = 1000  # Reset state to recover


            #.
            # elif token == '.':
            #     state = 159
            #     lexeme = token 
            #     if lookahead_char in period_delim or lookahead_char is None or lookahead_char == "\n":
            #         state = 160
            #         tokens.append((lexeme, lexeme))
            #         lexeme = ""

            #     else:
            #         print("ERROR IN STATE 159")
            #         state = 1000  # Reset state to recover

            #;

            elif token == ';':
                state = 165
                lexeme = token 
                if lookahead_char in terminator_delim or lookahead_char is None or lookahead_char == "\n":
                    state = 166
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                elif lookahead_char in lowchar:
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                    state = 0
                else:
                    print("ERROR IN STATE 165")
                    state = 1000  # Reset state to recover

            #(
            elif token == '(':
                print("Passed state 167")
                state = 167
                lexeme = token 
                if lookahead_char in open_parenthesis_delim or lookahead_char is None:
                    print("Passed state 168")
                    state = 168
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                elif lookahead_char in allval:
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                    state = 0
                elif lookahead_char in lowchar:
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                    state = 0
                elif lookahead_char in upchar:
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                    state = 0
                else:
                    print("ERROR IN STATE 167")
                    state = 1000  # Reset state to recover

            #)
            elif token == ')':
                state = 169
                lexeme = token 
                if lookahead_char in close_parenthesis_delim or lookahead_char is None or lookahead_char == "\n":
                    state = 170
                    tokens.append((lexeme, lexeme))
                    lexeme = ""

                else:
                    print("ERROR IN STATE 169")
                    state = 1000  # Reset state to recover

            #{
            elif token == '{':
                state = 171
                lexeme = token 
                if lookahead_char in open_braces_delim or lookahead_char is None or lookahead_char == "\n":
                    state = 172
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                elif lookahead_char in allval:
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                    state = 0
                elif lookahead_char in lowchar:
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                    state = 0
                elif lookahead_char in upchar:
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                    state = 0
                elif lookahead_char == '"':
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                    state = 0
                else:
                    print("ERROR IN STATE 171")
                    state = 1000  # Reset state to recover
            #}
            elif token == '}':
                state = 173
                lexeme = token 
                if lookahead_char in close_braces_delim or lookahead_char is None or lookahead_char == "\n":
                    state = 174
                    tokens.append((lexeme, lexeme))
                    lexeme = ""

                else:
                    print("ERROR IN STATE 173")
                    state = 1000  # Reset state to recover

            #[
            # elif token == '[':
            #     state = 175
            #     lexeme = token 
            #     if lookahead_char in open_bracket_delim or lookahead_char is None or lookahead_char == "\n":
            #         state = 176
            #         tokens.append((lexeme, lexeme))
            #         lexeme = ""

            #     else:
            #         print("ERROR IN STATE 175")
            #         state = 1000  # Reset state to recover

            #]
            elif token == ']':
                state = 177
                lexeme = token 
                if lookahead_char in close_bracket_delim or lookahead_char is None or lookahead_char == "\n":
                    state = 178
                    tokens.append((lexeme, lexeme))
                    lexeme = ""

                else:
                    print("ERROR IN STATE 177")
                    state = 1000  # Reset state to recover
    

            #IDENTIFIER (2)
            elif token in upchar:
                state = 179
                lexeme = token 
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 180
                    tokens.append((lexeme, "Identifier"))
                    lexeme = ""
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 181
                elif lookahead_char == "+":
                    # Specifically handle + operator after an identifier
                    tokens.append((lexeme, "Identifier"))
                    lexeme = ""
                    state = 0
                elif lookahead_char == "-":
                    # Specifically handle - operator after an identifier
                    tokens.append((lexeme, "Identifier"))
                    lexeme = ""
                    state = 0
                elif lookahead_char in "*/=%<>!&|":  # Add other operators here
                    # Handle all other operators similarly
                    tokens.append((lexeme, "Identifier"))
                    lexeme = ""
                    state = 0
                else:
                    state = 1000  # Reset state to recover

            elif token == '"':
                state = 219
                lexeme = token 
            
            #NUMLIT
            elif token == "^":  # Only accept ^ if we're already processing a number
                lexeme = token
                if lookahead_char in allval:  # Must be followed by a number
                    state = 242
                else:
                    print("ERROR: ^ must be followed by a number")
                    state = 1000

            elif token in allval:  # First check for numeric values
                lexeme = token 
                if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":
                    print("Passed state 228")
                    state = 228
                    tokens.append((lexeme, "numlit"))
                    lexeme = ""
                elif lookahead_char in allval:  # Allow numbers to follow
                    state = 242
                elif lookahead_char == "+":
                        tokens.append((lexeme, "numlit"))
                        lexeme = ""
                        state = 0
                elif lookahead_char == "-":
                        tokens.append((lexeme, "numlit"))
                        lexeme = ""
                        state = 0
                elif lookahead_char == '.':
                    state = 229
                else:
                    print("ERROR IN STATE 228")
                    state = 1000  # Reset state to recover

            # SINGLE LINE COMMENT
            elif token == '#':
                print("Passed state 422")
                lexeme = token
                state = 422

            else:
                lexeme = token
                state = 1000  # Reset state to recover
        
        elif state == 1:
            print("Passed state 1")
            lexeme += token
    
            if token == 'G':
                if lookahead_char in delim_gen or lookahead_char is None or lookahead_char == "\n":
                    print("Passed state 2")
                    state = 2
                    tokens.append((lexeme, lexeme))
                    lexeme = ""

                else:
                    print("ERROR IN STATE 1: Invalid sequence before 'G'")
                    state = 1000  # Reset state to recover

            #L
            elif token == 'L':
                if lookahead_char in delim_gen or lookahead_char is None or lookahead_char == "\n":
                    state = 4
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 1: Invalid sequence before 'G'")
                    state = 1000  # Reset state to recover

            else:
                print("ERROR IN STATE 1: Unexpected character")
                state = 1000  # Reset state to recover

        elif state == 6:
            if token == 'c':
                lexeme += token
                state = 7
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000
            elif token == 'l':
                lexeme += token
                state = 10
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000
            else:
                # This is where the fix is needed - always add token to lexeme before going to error state
                lexeme += token
                state = 1000  # Go to error state but keep the full lexeme

        #ACT
        elif state == 7:
            lexeme += token
            if token == 't':
                if lookahead_char in delim_gen or lookahead_char is None or lookahead_char == "\n":
                    state = 8
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR: 'act' must be followed by a delimiter")
                    state = 1000  # Error state
                    # Don't reset lexeme, keep it to report the error
            else:
                print("WRONG IN STATE 7")
                state = 1000  # Reset state to recover


        elif state == 10:
            lexeme += token
            if lookahead_char is None or lookahead_char == "\n":
                state = 1000
            elif token == 'l':
                state = 11
            else:
                print("WRONG IN STATE 10")
                state = 1000  # Reset state to recover

        elif state == 11:
            lexeme += token
            if lookahead_char is None or lookahead_char == "\n":
                state = 1000
            elif token == 'e':
                state = 12
            else:
                print("WRONG IN STATE 11")
                state = 1000  # Reset state to recover

        elif state == 12:
            lexeme += token
            if lookahead_char is None or lookahead_char == "\n":
                state = 1000
            elif token == 'l':
                state = 13
            else:
                print("WRONG IN STATE 12")
                state = 1000  # Reset state to recover

        #ALLELE
        elif state == 13:
            lexeme += token
            if token == 'e':
                if lookahead_char in delim_gen or lookahead_char is None or lookahead_char == "\n":
                    state = 14
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR")
                    state = 1000  # Reset state to recover
                    lexeme += token

            else:
                print("WRONG IN STATE 13")
                state = 1000  # Reset state to recover


        elif state == 16:
            lexeme += token
            if lookahead_char is None or lookahead_char == "\n":
                state = 1000
            elif token == 'l':
                state = 17
            elif token == 'o':
                state = 22
            else:
                print("WRONG IN STATE 16")
                state = 1000  # Reset state to recover

        elif state == 17:
            lexeme += token
            if lookahead_char is None or lookahead_char == "\n":
                state = 1000
            elif token == 'u':
                state = 18
            else:
                print("WRONG IN STATE 17")
                state = 1000  # Reset state to recover

        elif state == 18:
            lexeme += token
            if lookahead_char is None or lookahead_char == "\n":
                state = 1000
            elif token == 's':
                state = 19
            else:
                print("WRONG IN STATE 18")
                state = 1000  # Reset state to recover

        #CLUST
        elif state == 19:
            lexeme += token
            if token == 't':
                if lookahead_char in delim_gen or lookahead_char is None or lookahead_char == "\n":
                    state = 20
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR")
                    state = 1000  # Reset state to recover
                    lexeme += token

            else:
                print("WRONG IN STATE 19")
                state = 1000  # Reset state to recover

        elif state == 22:
            lexeme += token
            if token == 'n':
                state = 23
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            else:
                print("WRONG IN STATE 22")
                state = 1000  # Reset state to recover

        elif state == 23:
            lexeme += token
            if token == 't':
                state = 24
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            else:
                print("WRONG IN STATE 23")
                state = 1000  # Reset state to recover

        elif state == 24:
            lexeme += token
            if token == 'i':
                state = 25
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            else:
                print("WRONG IN STATE 24")
                state = 1000  # Reset state to recover

        #CONTIG
        elif state == 25:
            lexeme += token
            if token == 'g':
                if lookahead_char in delim_end or lookahead_char is None or lookahead_char == "\n":
                    state = 26
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 26")
                    state = 1000  # Reset state to recover
           

            else:
                print("WRONG IN STATE 25")
                state = 1000  # Reset state to recover
       
        elif state == 28:
            print("Passed state 28")
            lexeme += token
                 
            if lookahead_char is None or lookahead_char == "\n":
                state = 1000
            elif token == 'e':
                state = 29
            elif token == 'o':
                print("Passed state 36")
                state = 36
                if lookahead_char == 'm':  # Lookahead check for 'm'
                    state = 38
                elif lookahead_char == 's':
                    state = 40
                else:
                    print("WRONG IN STATE 36")
                    state = 1000  # Reset state to recover
            else:
                print("print IN STATE 28")
                state = 1000  # Reset state to recover
     

        elif state == 29:
            lexeme += token
            if token == 's':
                state = 30
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            else:
                print("WRONG IN STATE 29")
                state = 1000  # Reset state to recover

        elif state == 30:
            lexeme += token
            if token == 't':
                state = 31
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            else:
                print("WRONG IN STATE 30")
                state = 1000  # Reset state to recover

        elif state == 31:
            lexeme += token
            if token == 'r':
                state = 32
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            else:
                print("WRONG IN STATE 31")
                state = 1000  # Reset state to recover

        elif state == 32:
            lexeme += token
            if token == 'o':
                state = 33
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            else:
                print("WRONG IN STATE 32")
                state = 1000  # Reset state to recover

        #DESTROY
        elif state == 33:
            lexeme += token
            if token == 'y':
                if lookahead_char in delim_end or lookahead_char is None or lookahead_char == "\n":
                    state = 34
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 34")
                    state = 1000  # Reset state to recover
                    lexeme += token

            else:
                print("WRONG IN STATE 33")
                state = 1000  # Reset state to recover

        #DOM
        elif state == 38:
            lexeme += token
            if token == 'm':
                if lookahead_char in delim_end or lookahead_char is None or lookahead_char == "\n":
                    state = 39
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 39")
                    state = 1000  # Reset state to recover

            else:
                print("WRONG IN STATE 38")
                state = 1000  # Reset state to recover

        elif state == 40:
            print("Passed state 40")
            lexeme += token
            if lookahead_char is None or lookahead_char == "\n":
                state = 1000
            elif token == 's':
                state = 41
            elif lookahead_char is None or lookahead_char == "\n":
                state = 1000
            else:
                print("WRONG IN STATE 40")
                state = 1000  # Reset state to recover
                
        #DOSE
        elif state == 41:
            print("Passed state 41")
            lexeme += token
            if token == 'e':
                if lookahead_char in delim_gen or lookahead_char is None or lookahead_char == "\n":
                    print("Passed state 42")
                    state = 42
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("WRONG IN STATE 42")
                    state = 1000  # Reset state to recover

            else:
                print("WRONG IN STATE 41")
                state = 1000  # Reset state to recover

        elif state == 43:
            lexeme += token
            if token == 'l':
                state = 44
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000
            elif token == 'x':
                state = 51
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000                
            else:
                print("ERROR IN STATE 43")
                state = 1000  # Reset state to recover

        elif state == 44:
            lexeme += token
            if token == 'i':
                state = 45
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            elif token == 's':
                state = 48
                if lookahead_char is None or lookahead_char == "\n":
                    found_error = True   
            else:
                print("WRONG IN STATE 29")
                state = 1000  # Reset state to recover


        #ELIF
        elif state == 45:
            lexeme += token
            if token == 'f':
                if lookahead_char in delim_1 or lookahead_char is None or lookahead_char == "\n":
                    state = 46
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 46")
                    state = 1000  # Reset state to recover
                
            else:
                print("WRONG IN STATE 45")
                state = 1000  # Reset state to recover

        #ELSE
        elif state == 48:
            lexeme += token
            if token == 'e':
                if lookahead_char in delim_2 or lookahead_char is None or lookahead_char == "\n":
                    state = 49
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 49")
                    state = 1000  # Reset state to recover
                    lexeme += token

            else:
                print("WRONG IN STATE 48")
                state = 1000  
                lexeme += token

        elif state == 51:
            lexeme += token
            if token == 'p':
                state = 52
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            else:
                print("WRONG IN STATE 51")
                state = 1000  # Reset state to recover

        elif state == 52:
            lexeme += token
            if token == 'r':
                state = 53
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            else:
                print("WRONG IN STATE 52")
                state = 1000  # Reset state to recover

        elif state == 53:
            lexeme += token
            if token == 'e':
                state = 54
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            else:
                print("WRONG IN STATE 53")
                state = 1000  # Reset state to recover

        elif state == 54:
            lexeme += token
            if token == 's':
                state = 55
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            else:
                print("WRONG IN STATE 54")
                state = 1000  # Reset state to recover

        #express
        elif state == 55:
            lexeme += token
            if token == 's':
                if lookahead_char in delim_1 or lookahead_char is None or lookahead_char == "\n":
                    state = 56
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 56")
                    state = 1000  # Reset state to recover
            else:
                print("WRONG IN STATE 55")
                state = 1000  # Reset state to recover

        elif state == 58:
            lexeme += token
            if token == 'o':
                state = 59
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            elif token == 'u':
                state = 450
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            else:
                print("WRONG IN STATE 58")
                state = 1000  # Reset state to recover

        elif state == 450:
            lexeme += token
            if token == 'n':
                state = 451
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            else:
                print("WRONG IN STATE 451")
                state = 1000  # Reset state to recover

        #::
        elif state == 462:
            lexeme += token
            if lookahead_char in delim_splice or lookahead_char is None or lookahead_char == "\n":
                state = 463
                tokens.append((lexeme, lexeme))
                lexeme = ""
            elif lookahead_char in allchar or lookahead_char in allval:
                tokens.append((lexeme, lexeme))
                lexeme = ""
                state = 0

            else:
                print("WRONG IN STATE 462")
                state = 1000  # Error state
                
        #FUNC
        elif state == 451:
            lexeme += token
            if token == 'c':
                if (lookahead_char is None or lookahead_char == "\n" or lookahead_char in delim_1 ):
                    state = 452
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 452")
                    state = 1000  # Reset state to recover
            else:
                print("WRONG IN STATE 451")
                state = 1000  # Reset state to recover

        #FOR
        elif state == 59:
            lexeme += token
            if token == 'r':
                if lookahead_char in delim_1 or lookahead_char is None or lookahead_char == "\n":
                    state = 60
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 60")
                    state = 1000  # Reset state to recover
                    lexeme += token
            else:
                print("WRONG IN STATE 59")
                state = 1000  # Reset state to recover

        elif state == 62:
            lexeme += token
            if token == 'e':
                state = 63
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            else:
                print("WRONG IN STATE 62")
                state = 1000  # Reset state to recover

        elif state == 63:
            lexeme += token
            if token == 'n':
                state = 64
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            else:
                print("WRONG IN STATE 62")
                state = 1000  # Reset state to recover

        #GENE
        elif state == 64:
            lexeme += token
            if token == 'e':
                if lookahead_char in delim_1 or lookahead_char is None or lookahead_char == "\n":
                    state = 65
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR: 'gene' must be followed by a delimiter")
                    state = 1000  # Error state
                    # Keep the lexeme for error reporting
            else:
                print("WRONG IN STATE 64")
                state = 1000  # Reset state to recover

        #IF
        elif state == 67:
            lexeme += token
            if token == 'f':
                if lookahead_char in delim_1 or lookahead_char is None or lookahead_char == "\n":
                    state = 68
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 68")
                    state = 1000  # Reset state to recover
                    lexeme += token
            else:
                print("WRONG IN STATE 67")
                state = 1000  # Reset state to recover


        elif state == 70:
            lexeme += token
            if token == 'e':
                state = 71
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            elif token == 'r':
                state = 76
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            else:
                print("ERROR IN STATE 70")
                state = 1000  # Reset state to recover

        elif state == 71:
            lexeme += token
            if token == 'r':
                state = 72
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            else:
                print("WRONG IN STATE 71")
                state = 1000  # Reset state to recover

        elif state == 72:
            lexeme += token
            if token == 'm':
                state = 73
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            else:
                print("WRONG IN STATE 72")
                state = 1000  # Reset state to recover

        #PERMS
        elif state == 73:
            lexeme += token
            if token == 's':
                if lookahead_char in delim_gen or lookahead_char is None or lookahead_char == "\n":
                    state = 74
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 74")
                    state = 1000  # Reset state to recover
                    lexeme += token
            else:
                print("WRONG IN STATE 73")
                state = 1000  # Reset state to recover

        elif state == 76:
            lexeme += token
            if token == 'o':
                state = 77
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            else:
                print("WRONG IN STATE 76")
                state = 1000  # Reset state to recover

        elif state == 77:
            lexeme += token
            if token == 'd':
                if lookahead_char in delim_gen or lookahead_char is None or lookahead_char == "\n":
                    state = 78
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 78")
                    state = 1000  # Reset state to recover
            else:
                print("WRONG IN STATE 77")
                state = 1000  # Reset state to recover

        elif state == 81:
            lexeme += token
            if lookahead_char is None or lookahead_char == "\n":
                state = 1000  
            elif token == 'u':
                state = 82
            else:
                print("WRONG IN STATE 81")
                state = 1000  # Reset state to recover

        elif state == 82:
            lexeme += token
            if lookahead_char is None or lookahead_char == "\n":
                state = 1000    
            elif token == 'a':
                state = 83
            else:
                print("WRONG IN STATE 82")
                state = 1000  # Reset state to recover

        elif state == 83:
            lexeme += token
            if lookahead_char is None or lookahead_char == "\n":
                state = 1000            
            elif token == 'n':
                state = 84
            else:
                print("WRONG IN STATE 83")
                state = 1000  # Reset state to recover

        #QUANT
        elif state == 84:
            lexeme += token
            if token == 't':
                if lookahead_char in delim_gen or lookahead_char is None or lookahead_char == "\n":
                    state = 85
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 85")
                    state = 1000  # Reset state to recover

            else:
                print("WRONG IN STATE 84")
                state = 1000  # Reset state to recover

        elif state == 87:
            lexeme += token
            if token == 'e':
                state = 88
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            else:
                print("WRONG IN STATE 87")
                state = 1000  # Reset state to recover

        #REC
        elif state == 88:
            lexeme += token
            if token == 'c':
                if lookahead_char in delim_end or lookahead_char is None or lookahead_char == "\n":
                    state = 89
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 89")
                    state = 1000  # Reset state to recover
            else:
                print("WRONG IN STATE 88")
                state = 1000  # Reset state to recover

        elif state == 91:
            lexeme += token
            if lookahead_char is None or lookahead_char == "\n":
                state = 1000
            elif token == 'e':
                state = 92
            elif token == 't':
                state = 95
            else:
                print("WRONG IN STATE 91")
                state = 1000  # Reset state to recover

        #SEQ
        elif state == 92:
            lexeme += token
            if token == 'q':
                if lookahead_char in delim_1 or lookahead_char is None or lookahead_char == "\n":
                    state = 93
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 93")
                    state = 1000  # Reset state to recover
            else:
                print("WRONG IN STATE 92")
                state = 1000  # Reset state to recover

        elif state == 95:
            lexeme += token
            if token == 'i':
                state = 96
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            else:
                print("WRONG IN STATE 95")
                state = 1000  # Reset state to recover

        elif state == 96:
            lexeme += token
            if token == 'm':
                state = 97  # Transition to the next state
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            else:
                print("WRONG IN STATE 96")
                state = 1000  # Error state

        elif state == 97:
            lexeme += token
            if token == 'u':
                state = 98  # Transition to the next state
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            else:
                print("WRONG IN STATE 97")
                state = 1000  # Error state

        elif state == 98:
            lexeme += token
            if token == 'l':
                state = 99  # Transition to the next state
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            else:
                print("WRONG IN STATE 98")
                state = 1000  # Error state

        #STIMULI
        elif state == 99:
            lexeme += token
            if token == 'i':
                if lookahead_char in delim_1 or lookahead_char is None or lookahead_char == "\n":
                    state = 100
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 93")
                    state = 1000  # Reset state to recover
            else:
                print("WRONG IN STATE 99")
                state = 1000  # Error state
    
        elif state == 102:
            lexeme += token
            if token == 'o':
                state = 103  # Transition to the next state
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            else:
                print("WRONG IN STATE 102")
                state = 1000  # Error state

        elif state == 103:
            lexeme += token
            if token == 'i':
                state = 104  # Transition to the next state
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            else:
                print("WRONG IN STATE 103")
                state = 1000  # Error state

        #VOID
        elif state == 104:
            lexeme += token
            if token == 'd':
                if lookahead_char in delim_gen or lookahead_char is None or lookahead_char == "\n":
                    state = 105
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 93")
                    state = 1000  # Reset state to recover
            else:
                print("WRONG IN STATE 104")
                state = 1000  # Error state

        elif state == 107:
            lexeme += token
            if token == 'h':
                state = 108  # Transition to the next state
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            else:
                print("WRONG IN STATE 107")
                state = 1000  # Error state

        elif state == 108:
            lexeme += token
            if token == 'i':
                state = 109  # Transition to the next state
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            else:
                print("WRONG IN STATE 108")
                state = 1000  # Error state

        elif state == 109:
            lexeme += token
            if token == 'l':
                state = 110  # Transition to the next state
                if lookahead_char is None or lookahead_char == "\n":
                    state = 1000    
            else:
                print("WRONG IN STATE 109")
                state = 1000  # Error state

        #WHILE
        elif state == 110:
            lexeme += token
            if token == 'e':
                if lookahead_char in delim_1 or lookahead_char is None or lookahead_char == "\n":
                    state = 111
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 111")
                    state = 1000  # Reset state to recover
            else:
                print("WRONG IN STATE 110")
                state = 1000  # Error state

        #++
        elif state == 115:
            lexeme += token
            if token == '+':
                if lookahead_char in delim_update or lookahead_char is None or lookahead_char == "\n":
                    state = 116
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                elif lookahead_char in allval:
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                    state = 0
                elif lookahead_char in upchar:
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                    state = 0
                else:
                    print("ERROR IN STATE 116")
                    state = 1000  # Reset state to recover
            else:
                print("WRONG IN STATE 115")
                state = 1000  # Error state

        #+=
        elif state == 117:
            lexeme += token
            if token == '=':
                if lookahead_char in delim_equal or lookahead_char is None or lookahead_char == "\n":
                    state = 118
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 118")
                    state = 1000  # Reset state to recover
            else:
                print("WRONG IN STATE 117")
                state = 1000  # Error state        # Handling '+' after an identifier

        # elif state == 115:
        #     lexeme += token  # Store first '+'
        #     if lookahead_char == "+":  # Check if next character is '+'
        #         state = 116
        #         state = 0
        #     elif lookahead_char == "=":  # Check if next character is '='
        #         state = 117  # Move to confirm '+='
        #         state = 0
        #     else:
        #         tokens.append((lexeme, lexeme))  # Store single '+'
        #         lexeme = ""
        #         state = 0  # Reset lexer

        # # Handling '++'
        # elif state == 116:
        #     lexeme += token  # Append second '+'
        #     if lookahead_char in delim_update or lookahead_char is None:  # If another '+' follows, trigger an error
        #             tokens.append((lexeme, lexeme))
        #             lexeme = ""
        #             state = 0
        #     else:
        #         state = 1000  # Reset lexer

        # Handling '+='
        elif state == 117:
            lexeme += token  # Append '='
            if lookahead_char == "+":  # Ensure no extra `+` follows
                print("ERROR: Unexpected '+' after '+='")
                state = 1000  
            else:
                tokens.append((lexeme, "+="))  # Store '+=' as a single token
                lexeme = ""
                state = 0  # Reset lexer

        #--
        elif state == 121:
            lexeme += token
            if token == '-':
                if lookahead_char in delim_update or lookahead_char is None or lookahead_char == "\n":
                    state = 122
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 122")
                    state = 1000  # Reset state to recover
            else:
                print("WRONG IN STATE 121")
                state = 1000  # Error state

        #-=
        elif state == 123:
            lexeme += token
            if token == '=':
                if lookahead_char in delim_equal or lookahead_char is None or lookahead_char == "\n":
                    state = 124
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 124")
                    state = 1000  # Reset state to recover
            else:
                print("WRONG IN STATE 123")
                state = 1000  # Error state

        #*=
        elif state == 127:
            lexeme += token
            if token == '=':
                if lookahead_char in delim_equal or lookahead_char is None or lookahead_char == "\n":
                    state = 128
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 127")
                    state = 1000  # Reset state to recover
            else:
                print("WRONG IN STATE 128")
                state = 1000  # Error state

        #/=
        elif state == 131:
            lexeme += token
            if token == '=':
                if lookahead_char in delim_equal or lookahead_char is None or lookahead_char == "\n":
                    state = 132
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 132")
                    state = 1000  # Reset state to recover
            else:
                print("WRONG IN STATE 131")
                state = 1000  # Error state

        #%=
        elif state == 135:
            lexeme += token
            if token == '=':
                if lookahead_char in delim_equal or lookahead_char is None or lookahead_char == "\n":
                    state = 136
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 136")
                    state = 1000  # Reset state to recover
            else:
                print("WRONG IN STATE 135")
                state = 1000  # Error state

        #**
        elif state == 1125:
            lexeme += token
            if token == '*':
                if lookahead_char in delim_update or lookahead_char is None or lookahead_char == "\n":
                    state = 1126
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                elif lookahead_char in allval:
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                    state = 0
                elif lookahead_char in upchar:
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                    state = 0
                else:
                    print("ERROR IN STATE 1126")
                    state = 1000  # Reset state to recover
            else:
                print("WRONG IN STATE 1125")
                state = 1000  # Error state

        #//
        elif state == 1129:
            lexeme += token
            if token == '/':
                if lookahead_char in delim_update or lookahead_char is None or lookahead_char == "\n":
                    state = 1130
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                elif lookahead_char in allval:
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                    state = 0
                elif lookahead_char in upchar:
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                    state = 0
                else:
                    print("ERROR IN STATE 1130")
                    state = 1000  # Reset state to recover
            else:
                print("WRONG IN STATE 1129")
                state = 1000  # Error state

        #&&
        elif state == 137:
            print("Passed state 137")
            lexeme += token
            if token == '&':
                if lookahead_char in delim_logic or lookahead_char is None or lookahead_char == "\n":
                    print("Passed state 138")
                    state = 138
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 138")
                    state = 1000  # Reset state to recover
            else:
                print("WRONG IN STATE 137")
                state = 1000  # Error state

        #||
        elif state == 140:
            print("Passed state 140")
            lexeme += token
            if token == '|':
                if lookahead_char in delim_logic or lookahead_char is None or lookahead_char == "\n":
                    print("Passed state 141")
                    state = 141
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 141")
                    state = 1000  # Reset state to recover
            else:
                print("WRONG IN STATE 140")
                state = 1000  # Error state

        #==
        elif state == 145:
            print("Passed state 145")
            lexeme += token
            if token == '=':
                if lookahead_char in delim_comp or lookahead_char is None or lookahead_char == "\n":
                    print("Passed state 146")
                    state = 146
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 146")
                    state = 1000  # Reset state to recover
            else:
                print("WRONG IN STATE 145")
                state = 1000  # Error state

        #==
        elif state == 145:
            print("Passed state 145")
            lexeme += token
            if token == '=':
                if lookahead_char in delim_logic or lookahead_char is None or lookahead_char == "\n":
                    print("Passed state 146")
                    state = 146
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 146")
                    state = 1000  # Reset state to recover
            else:
                print("WRONG IN STATE 145")
                state = 1000  # Error state

        #>=
        elif state == 149:
            print("Passed state 149")
            lexeme += token
            if token == '=':
                if lookahead_char in delim_comp or lookahead_char is None or lookahead_char == "\n":
                    print("Passed state 150")
                    state = 150
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 150")
                    state = 1000  # Reset state to recover
            else:
                print("WRONG IN STATE 149")
                state = 1000  # Error state

        #<=
        elif state == 153:
            print("Passed state 153")
            lexeme += token
            if token == '=':
                if lookahead_char in delim_comp or lookahead_char is None or lookahead_char == "\n":
                    print("Passed state 154")
                    state = 154
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 154")
                    state = 1000  # Reset state to recover
            else:
                print("WRONG IN STATE 153")
                state = 1000  # Error state

        #!=
        elif state == 157:
            print("Passed state 157")
            lexeme += token
            if token == '=':
                if lookahead_char in delim_comp or lookahead_char is None or lookahead_char == "\n":
                    print("Passed state 158")
                    state = 158
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 158")
                    state = 1000  # Reset state to recover
            else:
                print("WRONG IN STATE 157")
                state = 1000  # Error state

        #IDENTIFIER (3)
        elif state == 181:
            print("Passed state 181")
            lexeme += token
            if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    print("Passed state 182")
                    state = 182
                    tokens.append((lexeme, "Identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the Identifier
            elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 183  # Continue processing as a valid Identifier
            elif lookahead_char == "+":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            elif lookahead_char == "-":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            else:
                    print(f"ERROR IN STATE 181")
                    state = 1000  # Error state

        #IDENTIFIER (4)
        elif state == 183:
            print("Passed state 183")
            lexeme += token
            if token in valchar and token in upchar and token in underscore:
                state = 1000  # Error state
            elif lookahead_char == "+":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            elif lookahead_char == "-":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            else:
                # Check for valid ending of an Identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    print("Passed state 184")
                    state = 184
                    tokens.append((lexeme, "Identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the Identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 185  # Continue processing as a valid Identifier
                else:
                    state = 1000  # Error state

        #IDENTIFIER (5)
        elif state == 185:
            print("Passed state 185")
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for Identifier")
                state = 1000  # Error state
            elif lookahead_char == "+":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            elif lookahead_char == "-":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            else:
                # Check for valid ending of an Identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    print("Passed state 186")
                    state = 186
                    tokens.append((lexeme, "Identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the Identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 187  # Continue processing as a valid Identifier
                else:
                    print(f"ERROR IN STATE 185")
                    state = 1000  # Error state

        #IDENTIFIER (6)
        elif state == 187:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for Identifier")
                state = 1000  # Error state
            elif lookahead_char == "+":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            elif lookahead_char == "-":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            else:
                # Check for valid ending of an Identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 188
                    tokens.append((lexeme, "Identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the Identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 189  # Continue processing as a valid Identifier
                else:
                    print(f"ERROR IN STATE 180")
                    state = 1000  # Error state

        #IDENTIFIER (7)
        elif state == 189:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for Identifier")
                state = 1000  # Error state
            elif lookahead_char == "+":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            elif lookahead_char == "-":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            else:
                # Check for valid ending of an Identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 190
                    tokens.append((lexeme, "Identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the Identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 191  # Continue processing as a valid Identifier
                else:
                    print(f"ERROR IN STATE 189")
                    state = 1000  # Error state

        #IDENTIFIER (7)
        elif state == 191:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for Identifier")
                state = 1000  # Error state
            elif lookahead_char == "+":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            elif lookahead_char == "-":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            else:
                # Check for valid ending of an Identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 192
                    tokens.append((lexeme, "Identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the Identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 193  # Continue processing as a valid Identifier
                else:
                    print(f"ERROR IN STATE 182")
                    state = 1000  # Error state

        #IDENTIFIER (8)
        elif state == 193:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for Identifier")
                state = 1000  # Error state
            elif lookahead_char == "+":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            elif lookahead_char == "-":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            else:
                # Check for valid ending of an Identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 194
                    tokens.append((lexeme, "Identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the Identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 195  # Continue processing as a valid Identifier
                else:
                    print(f"ERROR IN STATE 183")
                    state = 1000  # Error state

        #IDENTIFIER (9)
        elif state == 195:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for Identifier")
                state = 1000  # Error state
            elif lookahead_char == "+":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            elif lookahead_char == "-":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            else:
                # Check for valid ending of an Identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 196
                    tokens.append((lexeme, "Identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the Identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 197  # Continue processing as a valid Identifier
                else:
                    print(f"ERROR IN STATE 184")
                    state = 1000  # Error state

        #IDENTIFIER (10)
        elif state == 197:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for Identifier")
                state = 1000  # Error state
            elif lookahead_char == "+":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            elif lookahead_char == "-":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            else:
                # Check for valid ending of an Identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 198
                    tokens.append((lexeme, "Identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the Identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 199  # Continue processing as a valid Identifier
                else:
                    print(f"ERROR IN STATE 185")
                    state = 1000  # Error state

        #IDENTIFIER (11)
        elif state == 199:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for Identifier")
                state = 1000  # Error state
            elif lookahead_char == "+":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            elif lookahead_char == "-":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            else:
                # Check for valid ending of an Identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 200
                    tokens.append((lexeme, "Identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the Identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 201  # Continue processing as a valid Identifier
                else:
                    print(f"ERROR IN STATE 186")
                    state = 1000  # Error state

        #IDENTIFIER (12)
        elif state == 201:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for Identifier")
                state = 1000  # Error state
            elif lookahead_char == "+":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            elif lookahead_char == "-":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            else:
                # Check for valid ending of an Identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 202
                    tokens.append((lexeme, "Identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the Identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 203  # Continue processing as a valid Identifier
                else:
                    print(f"ERROR IN STATE 187")
                    state = 1000  # Error state

        #IDENTIFIER (13)
        elif state == 203:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for Identifier")
                state = 1000  # Error state
            elif lookahead_char == "+":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            elif lookahead_char == "-":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            else:
                # Check for valid ending of an Identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 204
                    tokens.append((lexeme, "Identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the Identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 205  # Continue processing as a valid Identifier
                else:
                    print(f"ERROR IN STATE 188")
                    state = 1000  # Error state

        #IDENTIFIER (14)
        elif state == 205:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for Identifier")
                state = 1000  # Error state
            elif lookahead_char == "+":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            elif lookahead_char == "-":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            else:
                # Check for valid ending of an Identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 206
                    tokens.append((lexeme, "Identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the Identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 207  # Continue processing as a valid Identifier
                else:
                    print(f"ERROR IN STATE 189")
                    state = 1000  # Error state

        #IDENTIFIER (15)
        elif state == 207:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for Identifier")
                state = 1000  # Error state
            elif lookahead_char == "+":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            elif lookahead_char == "-":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            else:
                # Check for valid ending of an Identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 208
                    tokens.append((lexeme, "Identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the Identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 209  # Continue processing as a valid Identifier
                else:
                    print(f"ERROR IN STATE 190")
                    state = 1000  # Error state

        #IDENTIFIER (16)
        elif state == 209:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for Identifier")
                state = 1000  # Error state
            elif lookahead_char == "+":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            elif lookahead_char == "-":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            else:
                # Check for valid ending of an Identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 210
                    tokens.append((lexeme, "Identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the Identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 211  # Continue processing as a valid Identifier
                else:
                    print(f"ERROR IN STATE 191")
                    state = 1000  # Error state

        #IDENTIFIER (17)
        elif state == 211:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for Identifier")
                state = 1000  # Error state
            elif lookahead_char == "+":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            elif lookahead_char == "-":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
                
            else:
                # Check for valid ending of an Identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 212
                    tokens.append((lexeme, "Identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the Identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 213  # Continue processing as a valid Identifier
                else:
                    print(f"ERROR IN STATE 192")
                    state = 1000  # Error state

        #IDENTIFIER (18)
        elif state == 213:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for Identifier")
                state = 1000  # Error state
            elif lookahead_char == "+":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            elif lookahead_char == "-":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            else:
                # Check for valid ending of an Identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 214
                    tokens.append((lexeme, "Identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the Identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 215  # Continue processing as a valid Identifier
                else:
                    print(f"ERROR IN STATE 192")
                    state = 1000  # Error state

        #IDENTIFIER (19)
        elif state == 215:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for Identifier")
                state = 1000  # Error state
            elif lookahead_char == "+":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            elif lookahead_char == "-":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            else:
                # Check for valid ending of an Identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 216
                    tokens.append((lexeme, "Identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the Identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 217  # Continue processing as a valid Identifier
                else:
                    print(f"ERROR IN STATE 194")
                    state = 1000  # Error state

        #IDENTIFIER(20)
        elif state == 217:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for Identifier")
                state = 1000  # Error state
            elif lookahead_char == "+":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            elif lookahead_char == "-":
                tokens.append((lexeme, "Identifier"))
                lexeme = ""
                state = 0
            else:
                # Check for valid ending of an Identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 218
                    tokens.append((lexeme, "Identifier"))
                    lexeme = ""  # Reset lexeme for next token
                else:
                    print(f"ERROR IN STATE 218")
                    state = 1000  # Error state

        # String literal
        elif state == 219:
            print("Passed state 219")
            print(token)
            lexeme += token
            if lookahead_char == '\\':  # Check for backslash (escape character)
                state = 222  # New state for handling escape sequences
            elif lookahead_char in ascii:
                state = 219  # Stay in state 219 to continue processing ASCII characters
            elif lookahead_char == '"':
                state = 220  # Transition to the next state when a double quote is seen
            else:
                print(f"ERROR IN STATE 219: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        # Add a new state (222) to handle escape sequences
        elif state == 222:
            print("Passed state 222 - Escape sequence")
            lexeme += token  # Add the backslash to the lexeme
            # Handle various escape sequences
            if lookahead_char in ['"', '\\', 'n', 't', 'r']:
                # These are valid escape sequences
                state = 219  # Return to string processing state
            else:
                print(f"ERROR IN STATE 222: Invalid escape sequence \\{lookahead_char}")
                state = 1000  # Error state

        elif state == 220:
            # This state remains unchanged
            print("Passed state 220")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_string or lookahead_char is None or lookahead_char == "\n":
                print("Passed state 221")
                state = 221  # End state for string literal processing
                tokens.append((lexeme, "string literal"))
                lexeme = ""  # Reset lexeme for next token
            else:
                print(f"ERROR IN STATE 220: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        #float
        elif state == 229:
            print("Passed state 229")
            lexeme += token
            # COPYPASTE MO SA LAHAT NG GANTO
            if token == '.':     
                if lookahead_char in allval:     
                    state = 230
                else:
                    print(f"ERROR IN STATE {state}: Unexpected character {lookahead_char}")
                    state = 1000  # Error state

            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 230:
            print("Passed state 230")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 231")      
                state = 231  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 232
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 232:
            print("Passed state 232")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 233")      
                state = 233  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 234
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 234:
            print("Passed state 235")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 235")      
                state = 235  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 236
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 236:
            print("Passed state 236")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 237")      
                state = 237  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 238
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 238:
            print("Passed state 238")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 239")      
                state = 239  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 240
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 240:
            print("Passed state 240")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 241")      
                state = 241  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

         #numlit(2)
        elif state == 242:
            print("Passed state 242")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char == "+":
                        tokens.append((lexeme, "numlit"))
                        lexeme = ""
                        state = 0
            elif lookahead_char == "-":
                        tokens.append((lexeme, "numlit"))
                        lexeme = ""
                        state = 0
            elif lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":  
                print("Passed state 243")      
                state = 243  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char == ".":
                state = 244
            elif lookahead_char in allval:
                state = 257
            else:
                print(f"ERROR IN STATE 243: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 244:
            print("Passed state 244")
            lexeme += token
            if token  == ".":
                if lookahead_char in allval:     
                    state = 245
                else:
                    print(f"ERROR IN STATE {state}: Unexpected character {lookahead_char}")
                    state = 1000  # Error state
            else:
                print(f"ERROR IN STATE 244: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 245:
            print("Passed state 244")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 245")      
                state = 246  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 247
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 247:
            print("Passed state 232")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 233")      
                state = 248  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 249
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 249:
            print("Passed state 235")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 235")      
                state = 250  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 251
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 251:
            print("Passed state 236")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 237")      
                state = 252  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 253
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 253:
            print("Passed state 238")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 239")      
                state = 254  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 255
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 255:
            print("Passed state 240")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 256")      
                state = 256  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        #numlit(3)
        elif state == 257:
            print("Passed state 257")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":  
                    print("Passed state 258")
                    state = 258
                    tokens.append((lexeme, "numlit"))
                    lexeme = ""
            elif lookahead_char == "+":
                        tokens.append((lexeme, "numlit"))
                        lexeme = ""
                        state = 0
            elif lookahead_char == "-":
                        tokens.append((lexeme, "numlit"))
                        lexeme = ""
                        state = 0
            elif lookahead_char == '.':  
                    state = 259
            elif lookahead_char in allval:  
                    state = 272
            else:
                print(f"ERROR IN STATE 257: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 259:
            print("Passed state 259")
            lexeme += token
            if token  == ".":
                state = 260
            else:
                print(f"ERROR IN STATE 259: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 260:
            print("Passed state 244")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 245")      
                state = 261  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 262
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 262:
            print("Passed state 232")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 233")      
                state = 263  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 264
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 264:
            print("Passed state 235")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 265")      
                state = 265  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 266
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 266:
            print("Passed state 236")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 237")      
                state = 267  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 268
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 268:
            print("Passed state 238")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 239")      
                state = 269  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 270
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 270:
            print("Passed state 240")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 256")      
                state = 271  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        #numlit(4)
        elif state == 272:
            print("Passed state 257")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":  
                    print("Passed state 273")
                    state = 273
                    tokens.append((lexeme, "numlit"))
                    lexeme = ""
            elif lookahead_char == "+":
                        tokens.append((lexeme, "numlit"))
                        lexeme = ""
                        state = 0
            elif lookahead_char == "-":
                        tokens.append((lexeme, "numlit"))
                        lexeme = ""
                        state = 0
            elif lookahead_char == '.':  
                    state = 274
            elif lookahead_char in allval:  
                    state = 287
            else:
                print(f"ERROR IN STATE 257: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 274:
            print("Passed state 274")
            lexeme += token
            if token  == ".":
                state = 275
            else:
                print(f"ERROR IN STATE 274: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 275:
            print("Passed state 244")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 245")      
                state = 276  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 277
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 277:
            print("Passed state 232")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 233")      
                state = 278  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 279
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 279:
            print("Passed state 235")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 265")      
                state = 280  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 281
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 281:
            print("Passed state 236")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 237")      
                state = 282  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 283
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 283:
            print("Passed state 238")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 239")      
                state = 284  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 285
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 285:
            print("Passed state 240")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 256")      
                state = 286  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        #numlit(5)
        elif state == 287:
            print("Passed state 257")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":  
                    print("Passed state 273")
                    state = 288
                    tokens.append((lexeme, "numlit"))
                    lexeme = ""
            elif lookahead_char == "+":
                        tokens.append((lexeme, "numlit"))
                        lexeme = ""
                        state = 0
            elif lookahead_char == "-":
                        tokens.append((lexeme, "numlit"))
                        lexeme = ""
                        state = 0
            elif lookahead_char == '.':  
                    state = 289
            elif lookahead_char in allval:  
                    state = 302
            else:
                print(f"ERROR IN STATE 257: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 289:
            print("Passed state 289")
            lexeme += token
            if token  == ".":
                state = 290
            else:
                print(f"ERROR IN STATE 289: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 290:
            print("Passed state 244")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 245")      
                state = 291  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 292
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 292:
            print("Passed state 232")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 233")      
                state = 293  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 294
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 294:
            print("Passed state 235")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 265")      
                state = 295  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 296
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 296:
            print("Passed state 236")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 237")      
                state = 297  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 298
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 298:
            print("Passed state 238")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 239")      
                state = 299  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 300
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 300:
            print("Passed state 240")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 256")      
                state = 301  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        #numlit(6)
        elif state == 302:
            print("Passed state 257")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":  
                    print("Passed state 273")
                    state = 303
                    tokens.append((lexeme, "numlit"))
                    lexeme = ""
            elif lookahead_char == "+":
                        tokens.append((lexeme, "numlit"))
                        lexeme = ""
                        state = 0
            elif lookahead_char == "-":
                        tokens.append((lexeme, "numlit"))
                        lexeme = ""
                        state = 0
            elif lookahead_char == '.':  
                    state = 304
            elif lookahead_char in allval:  
                    state = 317
            else:
                print(f"ERROR IN STATE 257: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 304:
            print("Passed state 304")
            lexeme += token
            if token  == ".":
                state = 305
            else:
                print(f"ERROR IN STATE 304: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 305:
            print("Passed state 244")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 306")      
                state = 306  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 307
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 307:
            print("Passed state 232")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 233")      
                state = 308  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 309
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 309:
            print("Passed state 235")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 265")      
                state = 310  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 311
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 311:
            print("Passed state 236")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 237")      
                state = 312  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 313
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 313:
            print("Passed state 238")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 239")      
                state = 314  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 315
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 315:
            print("Passed state 240")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 316")      
                state = 316  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        #numlit(7)
        elif state == 317:
            print("Passed state 257")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":  
                    print("Passed state 273")
                    state = 318
                    tokens.append((lexeme, "numlit"))
                    lexeme = ""
            elif lookahead_char == "+":
                        tokens.append((lexeme, "numlit"))
                        lexeme = ""
                        state = 0
            elif lookahead_char == "-":
                        tokens.append((lexeme, "numlit"))
                        lexeme = ""
                        state = 0
            elif lookahead_char == '.':  
                    state = 319
            elif lookahead_char in allval:  
                    state = 332
            else:
                print(f"ERROR IN STATE 257: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 319:
            print("Passed state 319")
            lexeme += token
            if token  == ".":
                state = 320
            else:
                print(f"ERROR IN STATE 319: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 320:
            print("Passed state 244")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 306")      
                state = 321  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 322
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 322:
            print("Passed state 232")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 233")      
                state = 323  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 324
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 324:
            print("Passed state 235")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 265")      
                state = 325  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 326
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 326:
            print("Passed state 236")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 237")      
                state = 327  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 328
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 328:
            print("Passed state 238")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 239")      
                state = 329  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 330
            else:
                print(f"ERROR IN STATE 229: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 330:
            print("Passed state 330")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 316")      
                state = 331  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            else:
                print(f"ERROR IN STATE 330: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        #numlit(8)
        elif state == 332:
            print("Passed state 332")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":  
                    print("Passed state 333")
                    state = 333
                    tokens.append((lexeme, "numlit"))
                    lexeme = ""
            elif lookahead_char == "+":
                        tokens.append((lexeme, "numlit"))
                        lexeme = ""
                        state = 0
            elif lookahead_char == "-":
                        tokens.append((lexeme, "numlit"))
                        lexeme = ""
                        state = 0
            elif lookahead_char == '.':  
                    state = 334
            elif lookahead_char in allval:  
                    state = 347
            else:
                print(f"ERROR IN STATE 332: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 334:
            print("Passed state 334")
            lexeme += token
            if token  == ".":
                state = 335
            else:
                print(f"ERROR IN STATE 334: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 335:
            print("Passed state 335")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 336")      
                state = 336  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 337
            else:
                print(f"ERROR IN STATE 335: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 337:
            print("Passed state 337")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 338")      
                state = 338  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 339
            else:
                print(f"ERROR IN STATE 337: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 339:
            print("Passed state 339")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 340")      
                state = 340  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 341
            else:
                print(f"ERROR IN STATE 339: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 341:
            print("Passed state 341")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 342")      
                state = 342  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 343
            else:
                print(f"ERROR IN STATE 341: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 343:
            print("Passed state 343")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 344")      
                state = 344  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 345
            else:
                print(f"ERROR IN STATE 343: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 345:
            print("Passed state 345")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 346")      
                state = 346  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            else:
                print(f"ERROR IN STATE 345: Unexpected character {lookahead_char}")
                state = 1000  # Error state
        
        #numlit(9)
        elif state == 347:
            print("Passed state 347")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":  
                    print("Passed state 348")
                    state = 348
                    tokens.append((lexeme, "numlit"))
                    lexeme = ""
            elif lookahead_char == "+":
                        tokens.append((lexeme, "numlit"))
                        lexeme = ""
                        state = 0
            elif lookahead_char == "-":
                        tokens.append((lexeme, "numlit"))
                        lexeme = ""
                        state = 0
            elif lookahead_char == '.':  
                    state = 349
            elif lookahead_char in allval:  
                    state = 362
            else:
                print(f"ERROR IN STATE 347: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 349:
            print("Passed state 349")
            lexeme += token
            if token  == ".":
                state = 350
            else:
                print(f"ERROR IN STATE 349: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 350:
            print("Passed state 350")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 351")      
                state = 351  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 352
            else:
                print(f"ERROR IN STATE 350: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 352:
            print("Passed state 352")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 353")      
                state = 353  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 354
            else:
                print(f"ERROR IN STATE 352: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 354:
            print("Passed state 354")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 355")      
                state = 355  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 356
            else:
                print(f"ERROR IN STATE 356: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 356:
            print("Passed state 356")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 357")      
                state = 357  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 358
            else:
                print(f"ERROR IN STATE 356: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 358:
            print("Passed state 358")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 358")      
                state = 359  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 360
            else:
                print(f"ERROR IN STATE 358: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 360:
            print("Passed state 360")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 361")      
                state = 361  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            else:
                print(f"ERROR IN STATE 360: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        #numlit(10)
        elif state == 362:
            print("Passed state 362")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":  
                    print("Passed state 363")
                    state = 363
                    tokens.append((lexeme, "numlit"))
                    lexeme = ""
            elif lookahead_char == "+":
                        tokens.append((lexeme, "numlit"))
                        lexeme = ""
                        state = 0
            elif lookahead_char == "-":
                        tokens.append((lexeme, "numlit"))
                        lexeme = ""
                        state = 0
            elif lookahead_char == '.':  
                    state = 364
            elif lookahead_char in allval:  
                    state = 377
            else:
                print(f"ERROR IN STATE 362: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 364:
            print("Passed state 364")
            lexeme += token
            if token  == ".":
                state = 365
            else:
                print(f"ERROR IN STATE 364: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 365:
            print("Passed state 365")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 366")      
                state = 366  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 367
            else:
                print(f"ERROR IN STATE 365: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 367:
            print("Passed state 367")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 368")      
                state = 368  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 369
            else:
                print(f"ERROR IN STATE 367: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 369:
            print("Passed state 369")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 370")      
                state = 370  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 371
            else:
                print(f"ERROR IN STATE 339: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 371:
            print("Passed state 341")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 342")      
                state = 372  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 373
            else:
                print(f"ERROR IN STATE 341: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 373:
            print("Passed state 343")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 344")      
                state = 374  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 375
            else:
                print(f"ERROR IN STATE 343: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 375:
            print("Passed state 345")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 346")      
                state = 376  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            else:
                print(f"ERROR IN STATE 345: Unexpected character {lookahead_char}")
                state = 1000  # Error state
        
        #numlit(11)
        elif state == 377:
            print("Passed state 377")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":  
                    print("Passed state 378")
                    state = 378
                    tokens.append((lexeme, "numlit"))
                    lexeme = ""
            elif lookahead_char == "+":
                        tokens.append((lexeme, "numlit"))
                        lexeme = ""
                        state = 0
            elif lookahead_char == "-":
                        tokens.append((lexeme, "numlit"))
                        lexeme = ""
                        state = 0
            elif lookahead_char == '.':  
                    state = 379
            elif lookahead_char in allval:  
                    state = 392
            else:
                print(f"ERROR IN STATE 377: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 379:
            print("Passed state 379")
            lexeme += token
            if token  == ".":
                state = 380
            else:
                print(f"ERROR IN STATE 379: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 380:
            print("Passed state 380")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 381")      
                state = 381  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 382
            else:
                print(f"ERROR IN STATE 380: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 382:
            print("Passed state 382")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 383")      
                state = 383  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 384
            else:
                print(f"ERROR IN STATE 382: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 384:
            print("Passed state 384")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 385")      
                state = 385  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 386
            else:
                print(f"ERROR IN STATE 386: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 386:
            print("Passed state 386")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 387")      
                state = 387  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 388
            else:
                print(f"ERROR IN STATE 386: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 388:
            print("Passed state 358")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 389")      
                state = 389  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 390
            else:
                print(f"ERROR IN STATE 388: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 390:
            print("Passed state 390")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 391")      
                state = 391  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            else:
                print(f"ERROR IN STATE 360: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        #numlit(12)
        elif state == 392:
            print("Passed state 392")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":  
                    print("Passed state 393")
                    state = 393
                    tokens.append((lexeme, "numlit"))
                    lexeme = ""
            elif lookahead_char == "+":
                        tokens.append((lexeme, "numlit"))
                        lexeme = ""
                        state = 0
            elif lookahead_char == "-":
                        tokens.append((lexeme, "numlit"))
                        lexeme = ""
                        state = 0
            elif lookahead_char == '.':  
                    state = 394
            elif lookahead_char in allval:  
                    state = 407
            else:
                print(f"ERROR IN STATE 392: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 394:
            print("Passed state 364")
            lexeme += token
            if token  == ".":
                state = 395
            else:
                print(f"ERROR IN STATE 364: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 395:
            print("Passed state 395")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 396")      
                state = 396  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 397
            else:
                print(f"ERROR IN STATE 395: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 397:
            print("Passed state 397")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 398")      
                state = 398  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 399
            else:
                print(f"ERROR IN STATE 397: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 399:
            print("Passed state 399")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 400")      
                state = 400  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 401
            else:
                print(f"ERROR IN STATE 399: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 401:
            print("Passed state 401")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 402")      
                state = 402  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 403
            else:
                print(f"ERROR IN STATE 401: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 403:
            print("Passed state 403")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 404")      
                state = 404  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 405
            else:
                print(f"ERROR IN STATE 403: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 405:
            print("Passed state 405")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 406")      
                state = 406  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            else:
                print(f"ERROR IN STATE 405: Unexpected character {lookahead_char}")
                state = 1000  # Error state
        
        #numlit(13)
        elif state == 407:
            print("Passed state 392")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":  
                    print("Passed state 393")
                    state = 408
                    tokens.append((lexeme, "numlit"))
                    lexeme = ""
            elif lookahead_char == "+":
                        tokens.append((lexeme, "numlit"))
                        lexeme = ""
                        state = 0
            elif lookahead_char == "-":
                        tokens.append((lexeme, "numlit"))
                        lexeme = ""
                        state = 0
            elif lookahead_char == '.':  
                    state = 409

            else:
                print(f"ERROR IN STATE 392: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 409:
            print("Passed state 364")
            lexeme += token
            if token  == ".":
                state = 410
            else:
                print(f"ERROR IN STATE 364: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 410:
            print("Passed state 395")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 396")      
                state = 411  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 412
            else:
                print(f"ERROR IN STATE 395: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 412:
            print("Passed state 397")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 398")      
                state = 413  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 414
            else:
                print(f"ERROR IN STATE 397: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 414:
            print("Passed state 399")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 400")      
                state = 415  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 416
            else:
                print(f"ERROR IN STATE 399: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 416:
            print("Passed state 401")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 402")      
                state = 417  # End state for string literal processing
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 418
            else:
                print(f"ERROR IN STATE 401: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 418:
            print("Passed state 403")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 404")      
                state = 419
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            elif lookahead_char in allval:
                state = 420
            else:
                print(f"ERROR IN STATE 403: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 420:
            print("Passed state 405")
            lexeme += token
            # Check if the next character is within ASCII range or is a delimiter, or is None or newline
            if lookahead_char in delim_num or lookahead_char is None or lookahead_char == "\n":     
                print("Passed state 406")      
                state = 421  
                tokens.append((lexeme, "numlit"))
                lexeme = ""  # Reset lexeme for next token
            else:
                print(f"ERROR IN STATE 405: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        #SINGLE LINE COMMENT
        elif state == 422:
            print("Passed state 422")
            print(token)
            lexeme += token
            if lookahead_char in ascii2:
                state = 422  # Stay in state 219 to continue processing ASCII characters

            elif lookahead_char in delim_comment or lookahead_char is None:
                print("Passed state 423")
                state = 423
                tokens.append((lexeme, "comment"))
                lexeme = ""  # Reset lexeme for next token
            else:
                print(f"ERROR IN STATE 422: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        #MULTILINE COMMENT
        elif state == 424:
                    print("Passed state 424")
                    print(token)
                    lexeme += token
                    if lookahead_char == '*':
                        state = 425
                    else:
                        print(f"ERROR IN STATE 424: Unexpected character {lookahead_char}")
                        state = 1000  # Error state
                
        elif state == 425:
            print("Passed state 425")
            lexeme += token
            if lookahead_char in ascii2 :
                state = 425            
                if lookahead_char == '*':
                    state = 426
            elif lookahead_char == '\n':
                lexeme += '\\n'
            else:
                print(f"ERROR IN STATE 425: Unexpected character {lookahead_char}")
                state = 1000  # Error state
    
        elif state == 426:
            print("Passed state 426")
            lexeme += token
            if lookahead_char == '/':
                state = 427
            else:
                print(f"ERROR IN STATE 426: Unexpected character {lookahead_char}")
                state = 1000
                
        elif state == 427:
            print("Passed state 427")
            lexeme += token
            if lookahead_char in delim_comment or lookahead_char is None:
                state = 428
                tokens.append((lexeme, "multiline"))
                lexeme = ""

            else:
                print(f"ERROR IN STATE 427: Unexpected character {lookahead_char}")
                state = 1000
        

        #DELIM_GEN DELIMITERS
        elif state in {2, 4, 8, 14, 20, 41, 74, 78, 85, 105}:
            print("Passed Final State (delim_gen)")
            if token in delim_gen:
                lexeme += token
                if token == ' ':
                    tokens.append((token, "space"))
                elif token == ';':
                    tokens.append((token, token))
                state = 0  # Reset state for the next token
            else:
                print("WRONG IN DELIM_GEN")
                state = 1000  # Reset state to recover

        #DELIM_END
        elif state in {26, 34, 39, 42 ,89}:
            if token in delim_end:
                lexeme += token
                if token == ' ':
                    tokens.append((token, "space"))
                elif token == ';':
                    tokens.append((token, token))
                elif token == ',':
                    tokens.append((token, token))
                elif token == '=':
                    tokens.append((token, token))
                elif token == ')':
                    tokens.append((token, token))
                state = 0  # Reset state for the next token
            else:
                print("WRONG IN DELIM_END")
                state = 1000  # Reset state to recover

        #DELIM_1 DELIMITERS
        elif state in {37, 46, 56, 60, 65, 68, 93, 100, 111, 452}:
            if token in delim_1:
                if token == ' ':
                    tokens.append((token, "space"))
                elif token == '(':
                    tokens.append((token, token))
                state = 0  # Reset state for the next token
            else:
                print("WRONG IN DELIM_1")
                state = 1000  # Reset state to recover

        #DELIM_SPLICE
        elif state in {461, 463}:
            if token in delim_splice:
                if token == '\n':
                    tokens.append((token, "newline"))
                elif token == '^':
                    tokens.append((token, token))
                elif token == ' ':
                    tokens.append((token, "space"))
                elif token == '(':
                    tokens.append((token, token))
                elif token == ',':
                    tokens.append((token, token))
                elif token == ')':
                    tokens.append((token, token))
                elif token in valchar:
                    tokens.append((token, valchar))
                state = 0  # Reset state for the next token
            else:
                print("WRONG IN DELIM_SPLICE")
                state = 1000  # Reset state to recover

        #DELIM_2 DELIMITERS
        elif state in {49}:
            if token in delim_2:
                if token == ' ':
                    tokens.append((token, "space"))
                elif token == '{':
                    tokens.append((token, "{"))
                state = 0  # Reset state for the next token
            else:
                print("WRONG IN DELIM_2")
                state = 1000  # Reset state to recover

        #DELIM_STRING DELIMITERS
        elif state in {221}:
            print("delim_string")
            if token in delim_string:
                if token == ' ':
                    tokens.append((token, "space"))
                elif token == '\n':
                    tokens.append((token, "newline"))
                    line_number += 1  # Increment the line number for tracking
                elif token == ',':
                    tokens.append((token, token))
                elif token == '}':
                    tokens.append((token, token))
                elif token == ')':
                    tokens.append((token, token))
                elif token == '+':
                    tokens.append((token, token))
                elif token == ';':
                    tokens.append((token, token))
                elif token == '\t':
                    tokens.append(("\\t", "tab"))
                state = 0  # Reset state for the next token
            else:
                print("WRONG IN DELIM_STRING")
                state = 1000  # Reset state to recover

        #DELIM_ADD DELIMITERS
        elif state in {114, 115}:
            if token in delim_add:
                if token == '"':
                    tokens.append((token, token))
                elif token == ' ':
                    tokens.append((token, "space"))
                elif token == '^':
                    tokens.append((token, token))
                elif token == '(':
                    tokens.append((token, token))
                state = 0  # Reset state for the next token
            else:
                print("WRONG IN DELIM_ADD")
                state = 1000  # Reset state to recover  # Append token to lexeme to process it in the next cycle

        #DELIM_UPDATE DELIMITERS
        elif state in {116, 122, 1126, 1130}:
            if token in delim_update:
                if token == ' ':
                    tokens.append((token, "space"))
                elif token == ')':
                    tokens.append((token, ")"))
                elif token == ';':
                    tokens.append((token, ";"))
                state = 0  # Reset state for the next token
            else:
                print("WRONG IN DELIM_UPDATE")
                state = 1000  # Reset state to recover  # Append token to lexeme to process it in the next cycle

        #DELIM_EQUAL DELIMITERS
        elif state in {118, 124, 128, 129, 132, 136, 144, 148}:
            if token in delim_equal:
                if token == ' ':
                    tokens.append((token, "space"))
                elif token == '{':
                    tokens.append((token, token))
                elif token in allval:
                    tokens.append((token, "value"))
                elif token in upchar:
                    tokens.append((token, "upchar"))
                elif token == '(':
                    tokens.append((token, token))
                elif token == '"':
                    tokens.append((token, token))
                state = 0  # Reset state for the next token
            else:
                print("WRONG IN DELIM_ADD")
                state = 1000  # Reset state to recover  # Append token to lexeme to process it in the next cycle

        #DELIM_ARITH DELIMITERS
        elif state in {120, 126, 130, 134}:
            if token in delim_arith:
                if token == '(':
                    tokens.append((token, token))
                elif token == ' ':
                    tokens.append((token, "space"))
                elif token == '^':
                    tokens.append((token, "caret"))
                # elif token in valchar:
                #     tokens.append((token, token))
                # elif token in value:
                #     tokens.append((token, "value"))
                # elif token in upchar:
                #     tokens.append((token, "uppercase letter"))
                state = 0  # Reset state for the next token
            else:
                print("WRONG IN DELIM_ADD")
                state = 1000  # Reset state to recover  # Append token to lexeme to process it in the next cycle

        #DELIM_LOGIC DELIMITERS
        elif state in {138, 141, 146, 156}:
            if token in delim_logic:
                if token == '(':
                    tokens.append((token, token))
                elif token == ' ':
                    tokens.append((token, "space"))
                elif token == '^':
                    tokens.append((token, "caret"))
                elif token in allval:
                    tokens.append((token, "all value"))
                elif token in upchar:
                    tokens.append((token, "uppercase letter"))
                state = 0  # Reset state for the next token
            else:
                print("WRONG IN DELIM_LOGIC")
                state = 1000  # Reset state to recover  # Append token to lexeme to process it in the next cycle

        #DELIM_COMP DELIMITERS
        elif state in {145, 148, 150, 152, 154, 158}:
            if token in delim_comp:
                if token == '(':
                    tokens.append((token, token))
                elif token == ' ':
                    tokens.append((token, "space"))
                elif token == '^':
                    tokens.append((token, "caret"))
                elif token in allval:
                    tokens.append((token, "all value"))
                elif token in upchar:
                    tokens.append((token, "uppercase letter"))
                state = 0  # Reset state for the next token
            else:
                print("WRONG IN DELIM_COMP")
                state = 1000  # Reset state to recover  # Append token to lexeme to process it in the next cycle

        #TERMINATOR_DELIM DELIMITERS
        elif state in {166}:
            if token in terminator_delim:
                if token == '\n':
                    tokens.append((token, "newline"))
                elif token == ' ':
                    tokens.append((token, "space"))
                elif token in lowchar:
                    tokens.append((token, "lowchar"))
                state = 0  # Reset state for the next token
            else:
                print("WRONG IN TERMINATOR_DELIM")
                state = 1000  # Reset state to recover  # Append token to lexeme to process it in the next cycle

        #OPEN_PARENTHESIS_DELIM
        elif state in {168}:
            if token in open_parenthesis_delim:
                if token == '\n':
                    tokens.append((token, "newline"))
                elif token == '^':
                    tokens.append((token, token))
                elif token == ' ':
                    tokens.append((token, "space"))
                elif token == '(':
                    tokens.append((token, token))
                elif token == ',':
                    tokens.append((token, token))
                elif token == ')':
                    tokens.append((token, token))
                elif token in valchar:
                    tokens.append((token, valchar))
                state = 0  # Reset state for the next token
            else:
                print("WRONG IN OPEN_PARENTHESIS_DELIM")
                state = 1000  # Reset state to recover  # Append token to lexeme to process it in the next cycle

        #CLOSE_PARENTHESIS_DELIM
        elif state in {170}:
            if token in close_parenthesis_delim:
                if token == ')':
                    tokens.append((token, token))
                elif token == ' ':
                    tokens.append((token, "space"))
                elif token == '\n':
                    tokens.append((token, "newline"))
                elif token == '{':
                    tokens.append((token, token))
                elif token == '}':
                    tokens.append((token, token))
                elif token == '^':
                    tokens.append((token, token))
                elif token == '+':
                    tokens.append((token, token))
                elif token == '-':
                    tokens.append((token, token))
                elif token == '/':
                    tokens.append((token, token))
                elif token == '*':
                    tokens.append((token, token))
                elif token == '%':
                    tokens.append((token, token))
                elif token == '#':
                    tokens.append((token, token))
                elif token == ';':
                    tokens.append((token, token))
                elif token == ':':
                    tokens.append((token, token))
                state = 0  # Reset state for the next token
            else:
                print("WRONG IN CLOSE_PARENTHESIS_DELIM")
                state = 1000  # Reset state to recover  # Append token to lexeme to process it in the next cycle

        #OPEN_BRACES_DELIM
        elif state in {172}:
            if token in open_braces_delim:
                if token == ' ':
                    tokens.append((token, "space"))
                elif token == '\\':
                    tokens.append((token, "backslash"))
                elif token == '"':
                    tokens.append((token, token))
                elif token == '{':
                    tokens.append((token, token))
                elif token in allval:  # Add this condition
                    tokens.append((token, allval))
                    state = 0
                state = 0  # Reset state for the next token
            else:
                state = 1000  # Reset state to recover

        #CLOSE_BRACES_DELIM
        elif state in {174}:
            if token in close_braces_delim:
                if token == ' ':
                    tokens.append((token, "space"))
                elif token == '\n':
                    tokens.append((token, "newline"))
                elif token == ',':
                    tokens.append((token, token))
                elif token == '#':
                    tokens.append((token, token))
                elif token == ';':
                    tokens.append((token, token))
                state = 0  # Reset state for the next token
            else:
                print("WRONG IN CLOSE_BRACE_DELIM")
                state = 1000  # Reset state to recover  # Append token to lexeme to process it in the next cycle

        #OPEN_BRACKET_DELIM
        elif state in {176}:
            if token in open_bracket_delim:
                if token in value:
                    tokens.append((token, "value"))
                    state = 0
                
            else:
                print("WRONG IN OPEN_BRACKET_DELIM")
                state = 1000  # Reset state to recover  # Append token to lexeme to process it in the next cycle

        #COMMENT_BRACKET_DELIM
        elif state in {423, 428}:
            if token in delim_comment:
                if token ==  ' ':
                    tokens.append((token, "space"))
                elif token ==  '\n':
                    tokens.append((token, "newline"))
                state = 0
            else:
                print("WRONG IN COMMENT_DELIM")
                state = 1000  # Reset state to recover  # Append token to lexeme to process it in the next cycle

        #CLOSE_BRACKET_DELIM
        elif state in {178}:
            if token in close_bracket_delim:
                if token ==  ' ':
                    tokens.append((token, "space"))
                elif token ==  '=':
                    tokens.append((token, token))
                elif token ==  '[':
                    tokens.append((token, token))
                elif token ==  ',':
                    tokens.append((token, token))
                elif token ==  ';':
                    tokens.append((token, token))
                state = 0
            else:
                print("WRONG IN CLOSE_BRACKET_DELIM")
                state = 1000  # Reset state to recover  # Append token to lexeme to process it in the next cycle

        # DELIM_ID DELIMITERS
        elif state in {180, 182, 184, 186, 188, 190, 192, 194, 196, 198, 
                       200, 202, 204, 206, 208, 210, 212, 214, 216, 218}:
            # First, check if we have a complete Identifier to add
            if lexeme and (token in delim_id or lookahead_char in delim_id):
                tokens.append((lexeme, "Identifier"))
                lexeme = ""

            # Now handle the current token
            if token in delim_id:
                if token == ' ':
                    tokens.append((' ', "space"))
                elif token == '=':
                    tokens.append(('=', '='))
                elif token == '<':
                    tokens.append(('<', '<'))
                elif token == '>':
                    tokens.append(('>', '>'))
                elif token == ';':
                    tokens.append((';', ';'))
                elif token == '!':
                    tokens.append(('!', '!'))
                elif token == '+':
                    tokens.append(('+', '+'))
                elif token == '[':
                    tokens.append(('[', '['))
                elif token == '(':
                    tokens.append(('(', '('))
                elif token == '&':
                    tokens.append(('&', '&'))
                elif token == '|':
                    tokens.append(('|', '|'))
                elif token == '/':
                    tokens.append(('/', '/'))
                elif token == '-':
                    tokens.append(('-', '-'))
                elif token == '*':
                    tokens.append(('*', '*'))
                elif token == ',':
                    tokens.append((',', ','))
                elif token == ')':
                    tokens.append((')', ')'))
                elif token == ':':
                    tokens.append((':', ':'))
                elif token == ']':
                    tokens.append((']', ']'))
                state = 0  # Reset state for the next token
            else:
                # If it's not a delimiter, continue building the lexeme
                lexeme += token

        #DELIM_NUM DELIMITERS
        elif state in {228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 
                       243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 
                       258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 
                       273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 
                       288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 
                       303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 
                       318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 
                       333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 
                       348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 
                       363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 
                       378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 
                       393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 
                       408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421}:
            # Now handle the current token
            if lexeme and (token in delim_num or lookahead_char in delim_num):
                tokens.append((lexeme, "numlit"))
                lexeme = ""

            if token in delim_num:
                if token == '+':
                    tokens.append((token, "+"))
                elif token == '-':
                    tokens.append((token, '-'))
                elif token == '*':
                    tokens.append((token, '*'))
                elif token == '/':
                    tokens.append((token, '/'))
                elif token == '%':
                    tokens.append((token, '%'))
                elif token == '<':
                    tokens.append((token, '<'))
                elif token == '>':
                    tokens.append((token, '>'))
                elif token == '!=':
                    tokens.append((token, '!='))
                elif token == '=':
                    tokens.append((token, '='))
                elif token == ' ':
                    tokens.append((token, "space"))
                elif token == '#':
                    tokens.append((token, '#'))
                elif token == ')':
                    tokens.append((token, ')'))
                elif token == '}':
                    tokens.append((token, '}'))
                elif token == '&':
                    tokens.append((token, '&'))
                elif token == '|':
                    tokens.append((token, '|'))
                elif token == ']':
                    tokens.append((token, ']'))
                elif token == ';':
                    tokens.append((token, ';'))
                elif token == ',':
                    tokens.append((token, ','))
                elif token == ':':
                    tokens.append((token, ':'))
                state = 0  # Reset state for the next token
            else:
                # If it's not a delimiter, continue building the lexeme
                lexeme += token

        elif state == 1000:  # Error state
            found_error = True

            lexeme += token  # Append the current token to the lexeme
            if is_end_of_lexeme(token):  # Check if the current token marks the end of the invalid lexeme
                display_lexical_error(f"Invalid lexeme: {lexeme.strip()} on line {line_number}")
                state = 0
                if token == '\n':
                    line_number += 1
            
        print(state)
        print(f"found_error: {found_error}")
    return tokens, found_error
