import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk

def display_lexical_error(message):
    output_text.insert(tk.END, message + '\n')
    output_text.yview(tk.END)  # Scroll to the end

def parseLexer(input_stream):
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

    ascii = {" ", '!', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', 
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?', 
            '@', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 
            'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '[', '\\', ']', '^', '_', 
            '`', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 
            'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~'}

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
               'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'}

    value = {'1','2','3','4','5','6','7','8','9'}

    zero = {'0'}

    allval = {'1','2','3','4','5','6','7','8','9','0'}

    valchar = {'1', '2', '3' ,' 4', '5', '6' ,'7' ,'8' ,'9' ,'0',
               'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 
               'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 
               'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 
               'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 
               'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z' }
    
    underscore = {'_'}

    #DELIMITERS
    delim_arith = {'(', ' ', '^', } | value | upchar
    delim_equal = {' ', '{', '(', '"'} | allval | upchar
    delim_gen = {' '} 
    delim_end = {' ', ';'} 
    delim_1 = {' ', '('} 
    delim_2 = {' ', '{'} 
    delim_add = {'"', ' ', '^', '(', } 
    delim_string = {' ', '\n', ',', '}', ')', '+', '\t'} 
    delim_update = {' ', ';', ')'} 
    delim_id = {' ', '=', '<', '>', ';', '!', '+', '[', '(', '&', '|', '-', '*', ','}
    delim_logic = {' ', '(', '^'} | allval | upchar
    delim_comp = {' ', '(', '^'} | allval | upchar
    period_delim = {' ', '(', '^'} | allval | upchar
    terminator_delim = {'\n', ' '} | lowchar
    open_parenthesis_delim = {'\n', '^', ' ', '"', '(', ',', ')'} | allval | allchar
    close_parenthesis_delim =  {')', ' ', '\n', '{', '}', '^', '+', '-', '/', '*', '%', '#', ';'}
    open_braces_delim = {' ', '\\', '"'} | value | allchar
    close_braces_delim = {' ', '\n', '#'}
    open_bracket_delim = value
    close_bracket_delim = {' ', '='}

    lookahead_char = None
    
    while True:
        if lookahead_char is not None:
            token = lookahead_char  # Use cached lookahead character
            lookahead_char = None  # Clear the cache
        else:
            try:
                token = next(char_iter)
            except StopIteration:
                # Handle end of stream if in error state
                if state == 1000 and lexeme:
                    display_lexical_error(f"Invalid lexeme: {lexeme.strip()} on line {line_number}")
                break  # End of input stream

        if token in {'\n', ' '}:
            if state == 1000 and lexeme:  # If in error state and lexeme exists
                display_lexical_error(f"Invalid lexeme: {lexeme.strip()} on line {line_number}")
                lexeme = ""  # Reset lexeme to avoid appending invalid values
                state = 0  # Reset state to recover

            if token == '\n':
                tokens.append(("\\n", "newline"))
                line_number += 1
            elif token == ' ':
                tokens.append((" ", "space"))
            lexeme = ""  # Reset lexeme after delimiter processing
            state = 0  # Reset state for next token
            continue  # Skip further processing for delimiters

        try:
            lookahead_char = next(char_iter)  # Peek the next character
        except StopIteration:
            lookahead_char = None  # No more characters to proce
        
        if state == 0:
            print("Passed state 0")
            if token == '_':
                state = 1
                lexeme = token  
            elif token == 'a':
                state = 6
                lexeme = token  
            elif token == 'c':
                state = 16
                lexeme = token  
            elif token == 'd':
                state = 28
                lexeme = token  
            elif token == 'e':
                state = 43
                lexeme = token  
            elif token == 'f':
                state = 58
                lexeme = token  
            elif token == 'g':
                state = 62
                lexeme = token  
            elif token == 'i':
                state = 67
                lexeme = token 
            elif token == 'p':
                state = 70
                lexeme = token 
            elif token == 'q':
                state = 81
                lexeme = token 
            elif token == 'r':
                state = 87
                lexeme = token 
            elif token == 's':
                state = 91
                lexeme = token 
            elif token == 'v':
                state = 102
                lexeme = token 
            elif token == 'w':
                state = 107
                lexeme = token 
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
                else:
                    print("ERROR IN STATE 113")
                    state = 1000  # Reset state to recover
            elif token == '-':
                state = 119
                lexeme = token 
                if lookahead_char in delim_arith or lookahead_char is None or lookahead_char == "\n":
                    state = 120
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                elif lookahead_char == '-':
                    state = 121
                elif lookahead_char == '=':
                    state = 123
                else:
                    print("ERROR IN STATE 119")
                    state = 1000  # Reset state to recover
            elif token == '*':
                state = 125
                lexeme = token 
                if lookahead_char in delim_arith or lookahead_char is None or lookahead_char == "\n":
                    state = 126
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                elif lookahead_char == '=':
                    state = 127
                else:
                    print("ERROR IN STATE 125")
                    state = 1000  # Reset state to recover
            elif token == '/':
                state = 129
                lexeme = token 
                if lookahead_char in delim_arith or lookahead_char is None or lookahead_char == "\n":
                    state = 130
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                elif lookahead_char == '=':
                    state = 131
                else:
                    print("ERROR IN STATE 129")
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
                    print("ERROR IN STATE 143")
                    state = 1000  # Reset state to recover

            #<
            elif token == '>':
                state = 151
                lexeme = token 
                if lookahead_char in delim_comp or lookahead_char is None or lookahead_char == "\n":
                    state = 152
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                elif lookahead_char == '=':
                    state = 153
                else:
                    print("ERROR IN STATE 143")
                    state = 1000  # Reset state to recover

            #!
            elif token == '!':
                state = 155
                lexeme = token 
                if lookahead_char in delim_comp or lookahead_char is None or lookahead_char == "\n":
                    state = 156
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                elif lookahead_char == '=':
                    state = 157
                else:
                    print("ERROR IN STATE 143")
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

                else:
                    print("ERROR IN STATE 165")
                    state = 1000  # Reset state to recover

            #(
            elif token == '(':
                print("Passed state 167")
                state = 167
                lexeme = token 
                if lookahead_char in open_parenthesis_delim or lookahead_char is None or lookahead_char == "\n":
                    print("Passed state 168")
                    state = 168
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
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

                else:
                    print("ERROR IN STATE 172")
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
                    print("ERROR IN STATE 172")
                    state = 1000  # Reset state to recover

            #[
            elif token == '[':
                state = 175
                lexeme = token 
                if lookahead_char in open_bracket_delim or lookahead_char is None or lookahead_char == "\n":
                    state = 176
                    tokens.append((lexeme, lexeme))
                    lexeme = ""

                else:
                    print("ERROR IN STATE 175")
                    state = 1000  # Reset state to recover

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

            #IDENTIFIER (1)
            elif token in upchar:
                state = 179
                lexeme = token 
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 180
                    tokens.append((lexeme, "Identifier"))
                    lexeme = ""
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 181
                else:
                    print("ERROR IN STATE 179")
                    state = 1000  # Reset state to recover

            elif token == '"':
                state = 219
                lexeme = token 

            else:
                state = 1000  # Reset state to recover
                lexeme += token
        
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
                
            elif token == 'l':
                lexeme += token
                state = 10
            else:
                print("WRONG IN STATE 6")
                state = 1000  # Reset state to recover
                lexeme += token

        #ACT
        elif state == 7:
            lexeme += token
            if token == 't':
                if lookahead_char in delim_gen or lookahead_char is None or lookahead_char == "\n":
                    state = 8
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR")
                    lexeme = ""  # Reset lexeme to avoid appending invalid values
                    state = 0  # Reset state to recover
            else:
                print("WRONG IN STATE 7")
                state = 1000  # Reset state to recover
                lexeme += token


        elif state == 10:
            lexeme += token
            if token == 'l':
                state = 11
            else:
                print("WRONG IN STATE 10")
                state = 1000  # Reset state to recover
                lexeme += token

        elif state == 11:
            lexeme += token
            if token == 'e':
                state = 12
            else:
                print("WRONG IN STATE 11")
                state = 1000  # Reset state to recover
                lexeme += token

        elif state == 12:
            lexeme += token
            if token == 'l':
                state = 13
            else:
                print("WRONG IN STATE 12")
                state = 1000  # Reset state to recover
                lexeme += token

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
                lexeme += token


        elif state == 16:
            lexeme += token
            if token == 'l':
                state = 17
            elif token == 'o':
                state = 22
            else:
                print("WRONG IN STATE 16")
                state = 1000  # Reset state to recover
                lexeme += token

        elif state == 17:
            lexeme += token
            if token == 'u':
                state = 18
            else:
                print("WRONG IN STATE 17")
                state = 1000  # Reset state to recover
                lexeme += token

        elif state == 18:
            lexeme += token
            if token == 's':
                state = 19
            else:
                print("WRONG IN STATE 18")
                state = 1000  # Reset state to recover
                lexeme += token

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
                lexeme += token

        elif state == 22:
            lexeme += token
            if token == 'n':
                state = 23
            else:
                print("WRONG IN STATE 22")
                state = 1000  # Reset state to recover
                lexeme += token

        elif state == 23:
            lexeme += token
            if token == 't':
                state = 24
            else:
                print("WRONG IN STATE 23")
                state = 1000  # Reset state to recover
                lexeme += token

        elif state == 24:
            lexeme += token
            if token == 'i':
                state = 25
            else:
                print("WRONG IN STATE 24")
                state = 1000  # Reset state to recover
                lexeme += token

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
                    lexeme += token

            else:
                print("WRONG IN STATE 25")
                state = 1000  # Reset state to recover
                lexeme += token

        elif state == 28:
            print("Passed state 28")
            lexeme += token
                 
            if token == 'e':
                state = 29
            elif token == 'o':
                print("Passed state 36")
                state = 36
                if lookahead_char == 'm':  # Lookahead check for 'm'
                    state = 38
                elif lookahead_char == 's':
                    state = 40
                #DO
                else:
                    if lookahead_char in delim_end or lookahead_char is None or lookahead_char == "\n":
                        state = 37
                        tokens.append((lexeme, lexeme))
                        lexeme = ""
                    else:
                        print("ERROR IN STATE 37")
                        state = 1000  # Reset state to recover
                        lexeme += token

            else:
                print("PRINT IN STATE 28")
                state = 1000  # Reset state to recover
                lexeme += token

        elif state == 29:
            lexeme += token
            if token == 's':
                state = 30
            else:
                print("WRONG IN STATE 29")
                state = 1000  # Reset state to recover
                lexeme += token

        elif state == 30:
            lexeme += token
            if token == 't':
                state = 31
            else:
                print("WRONG IN STATE 30")
                state = 1000  # Reset state to recover
                lexeme += token

        elif state == 31:
            lexeme += token
            if token == 'r':
                state = 32
            else:
                print("WRONG IN STATE 31")
                state = 1000  # Reset state to recover
                lexeme += token

        elif state == 32:
            lexeme += token
            if token == 'o':
                state = 33
            else:
                print("WRONG IN STATE 32")
                state = 1000  # Reset state to recover
                lexeme += token

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
                lexeme += token

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
                    lexeme += token

            else:
                print("WRONG IN STATE 38")
                state = 1000  # Reset state to recover
                lexeme += token

        elif state == 40:
            print("Passed state 40")
            lexeme += token
            if token == 's':
                state = 41
            else:
                print("WRONG IN STATE 40")
                state = 1000  # Reset state to recover
                lexeme += token
                
        #DOSE
        elif state == 41:
            print("Passed state 41")
            lexeme += token
            if token == 'e':
                if lookahead_char in delim_end or lookahead_char is None or lookahead_char == "\n":
                    print("Passed state 42")
                    state = 42
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("WRONG IN STATE 42")
                    state = 1000  # Reset state to recover
                    lexeme += token
            else:
                print("WRONG IN STATE 41")
                state = 1000  # Reset state to recover
                lexeme += token

        elif state == 43:
            lexeme += token
            if token == 'l':
                state = 44
            elif token == 'x':
                state = 51
            else:
                print("ERROR IN STATE 43")
                state = 1000  # Reset state to recover

        elif state == 44:
            lexeme += token
            if token == 'i':
                state = 45
            elif token == 's':
                state = 48
            else:
                print("WRONG IN STATE 29")
                state = 1000  # Reset state to recover
                lexeme += token

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
                lexeme += token

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
            else:
                print("WRONG IN STATE 51")
                state = 1000  # Reset state to recover
                lexeme += token

        elif state == 52:
            lexeme += token
            if token == 'r':
                state = 53
            else:
                print("WRONG IN STATE 52")
                state = 1000  # Reset state to recover
                lexeme += token

        elif state == 53:
            lexeme += token
            if token == 'e':
                state = 54
            else:
                print("WRONG IN STATE 53")
                state = 1000  # Reset state to recover
                lexeme += token

        elif state == 54:
            lexeme += token
            if token == 's':
                state = 55
            else:
                print("WRONG IN STATE 54")
                state = 1000  # Reset state to recover
                lexeme += token

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
                    lexeme += token
            else:
                print("WRONG IN STATE 55")
                state = 1000  # Reset state to recover
                lexeme += token

        elif state == 58:
            lexeme += token
            if token == 'o':
                state = 59
            else:
                print("WRONG IN STATE 58")
                state = 1000  # Reset state to recover
                lexeme += token

        #FOR
        elif state == 59:
            lexeme += token
            if token == 'r':
                if lookahead_char in delim_1 or lookahead_char is None or lookahead_char == "\n":
                    state = 60
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 56")
                    state = 1000  # Reset state to recover
                    lexeme += token
            else:
                print("WRONG IN STATE 59")
                state = 1000  # Reset state to recover
                lexeme += token

        elif state == 62:
            lexeme += token
            if token == 'e':
                state = 63
            else:
                print("WRONG IN STATE 62")
                state = 1000  # Reset state to recover
                lexeme += token

        elif state == 63:
            lexeme += token
            if token == 'n':
                state = 64
            else:
                print("WRONG IN STATE 62")
                state = 1000  # Reset state to recover
                lexeme += token

        #GENE
        elif state == 64:
            lexeme += token
            if token == 'e':
                if lookahead_char in delim_1 or lookahead_char is None or lookahead_char == "\n":
                    state = 65
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
                else:
                    print("ERROR IN STATE 65")
                    state = 1000  # Reset state to recover

            else:
                print("WRONG IN STATE 64")
                state = 1000  # Reset state to recover
                lexeme += token

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
                lexeme += token

        elif state == 70:
            lexeme += token
            if token == 'e':
                state = 71
            elif token == 'r':
                state = 76
            else:
                print("ERROR IN STATE 70")
                state = 1000  # Reset state to recover

        elif state == 71:
            lexeme += token
            if token == 'r':
                state = 72
            else:
                print("WRONG IN STATE 71")
                state = 1000  # Reset state to recover
                lexeme += token

        elif state == 72:
            lexeme += token
            if token == 'm':
                state = 73
            else:
                print("WRONG IN STATE 72")
                state = 1000  # Reset state to recover
                lexeme += token

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
            if token == 'u':
                state = 82
            else:
                print("WRONG IN STATE 81")
                state = 1000  # Reset state to recover

        elif state == 82:
            lexeme += token
            if token == 'a':
                state = 83
            else:
                print("WRONG IN STATE 82")
                state = 1000  # Reset state to recover

        elif state == 83:
            lexeme += token
            if token == 'n':
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
            if token == 'e':
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
            else:
                print("WRONG IN STATE 95")
                state = 1000  # Reset state to recover

        elif state == 96:
            lexeme += token
            if token == 'm':
                state = 97  # Transition to the next state
            else:
                print("WRONG IN STATE 96")
                state = 1000  # Error state

        elif state == 97:
            lexeme += token
            if token == 'u':
                state = 98  # Transition to the next state
            else:
                print("WRONG IN STATE 97")
                state = 1000  # Error state

        elif state == 98:
            lexeme += token
            if token == 'l':
                state = 99  # Transition to the next state
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
            else:
                print("WRONG IN STATE 102")
                state = 1000  # Error state

        elif state == 103:
            lexeme += token
            if token == 'i':
                state = 104  # Transition to the next state
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
            else:
                print("WRONG IN STATE 107")
                state = 1000  # Error state

        elif state == 108:
            lexeme += token
            if token == 'i':
                state = 109  # Transition to the next state
            else:
                print("WRONG IN STATE 108")
                state = 1000  # Error state

        elif state == 109:
            lexeme += token
            if token == 'l':
                state = 110  # Transition to the next state
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
                state = 1000  # Error state

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

        #IDENTIFIER (2)
        elif state == 181:
            print("Passed state 181")
            lexeme += token
            if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    print("Passed state 182")
                    tokens.append((lexeme, "identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the identifier
            elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 183  # Continue processing as a valid identifier
            else:
                    print(f"ERROR IN STATE 181")
                    state = 1000  # Error state

        #IDENTIFIER (3)
        elif state == 183:
            print("Passed state 183")
            lexeme += token
            if token in valchar and token in upchar and token in underscore:
                state = 1000  # Error state
            else:
                # Check for valid ending of an identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    print("Passed state 184")
                    state = 184
                    tokens.append((lexeme, "identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 185  # Continue processing as a valid identifier
                else:
                    state = 1000  # Error state

        #IDENTIFIER (4)
        elif state == 185:
            print("Passed state 185")
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for identifier")
                state = 1000  # Error state
            else:
                # Check for valid ending of an identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    print("Passed state 186")
                    state = 186
                    tokens.append((lexeme, "identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 187  # Continue processing as a valid identifier
                else:
                    print(f"ERROR IN STATE 185")
                    state = 1000  # Error state

        #IDENTIFIER (5)
        elif state == 187:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for identifier")
                state = 1000  # Error state
            else:
                # Check for valid ending of an identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 188
                    tokens.append((lexeme, "identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 189  # Continue processing as a valid identifier
                else:
                    print(f"ERROR IN STATE 180")
                    state = 1000  # Error state

        #IDENTIFIER (6)
        elif state == 189:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for identifier")
                state = 1000  # Error state
            else:
                # Check for valid ending of an identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 190
                    tokens.append((lexeme, "identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 191  # Continue processing as a valid identifier
                else:
                    print(f"ERROR IN STATE 189")
                    state = 1000  # Error state

        #IDENTIFIER (7)
        elif state == 191:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for identifier")
                state = 1000  # Error state
            else:
                # Check for valid ending of an identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 192
                    tokens.append((lexeme, "identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 193  # Continue processing as a valid identifier
                else:
                    print(f"ERROR IN STATE 182")
                    state = 1000  # Error state

        #IDENTIFIER (8)
        elif state == 193:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for identifier")
                state = 1000  # Error state
            else:
                # Check for valid ending of an identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 194
                    tokens.append((lexeme, "identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 195  # Continue processing as a valid identifier
                else:
                    print(f"ERROR IN STATE 183")
                    state = 1000  # Error state

        #IDENTIFIER (9)
        elif state == 195:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for identifier")
                state = 1000  # Error state
            else:
                # Check for valid ending of an identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 196
                    tokens.append((lexeme, "identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 197  # Continue processing as a valid identifier
                else:
                    print(f"ERROR IN STATE 184")
                    state = 1000  # Error state

        #IDENTIFIER (10)
        elif state == 197:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for identifier")
                state = 1000  # Error state
            else:
                # Check for valid ending of an identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 198
                    tokens.append((lexeme, "identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 199  # Continue processing as a valid identifier
                else:
                    print(f"ERROR IN STATE 185")
                    state = 1000  # Error state

        #IDENTIFIER (11)
        elif state == 199:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for identifier")
                state = 1000  # Error state
            else:
                # Check for valid ending of an identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 200
                    tokens.append((lexeme, "identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 201  # Continue processing as a valid identifier
                else:
                    print(f"ERROR IN STATE 186")
                    state = 1000  # Error state

        #IDENTIFIER (12)
        elif state == 201:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for identifier")
                state = 1000  # Error state
            else:
                # Check for valid ending of an identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 202
                    tokens.append((lexeme, "identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 203  # Continue processing as a valid identifier
                else:
                    print(f"ERROR IN STATE 187")
                    state = 1000  # Error state

        #IDENTIFIER (13)
        elif state == 203:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for identifier")
                state = 1000  # Error state
            else:
                # Check for valid ending of an identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 204
                    tokens.append((lexeme, "identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 205  # Continue processing as a valid identifier
                else:
                    print(f"ERROR IN STATE 188")
                    state = 1000  # Error state

        #IDENTIFIER (14)
        elif state == 205:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for identifier")
                state = 1000  # Error state
            else:
                # Check for valid ending of an identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 206
                    tokens.append((lexeme, "identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 207  # Continue processing as a valid identifier
                else:
                    print(f"ERROR IN STATE 189")
                    state = 1000  # Error state

        #IDENTIFIER (15)
        elif state == 207:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for identifier")
                state = 1000  # Error state
            else:
                # Check for valid ending of an identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 208
                    tokens.append((lexeme, "identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 209  # Continue processing as a valid identifier
                else:
                    print(f"ERROR IN STATE 190")
                    state = 1000  # Error state

        #IDENTIFIER (16)
        elif state == 209:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for identifier")
                state = 1000  # Error state
            else:
                # Check for valid ending of an identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 210
                    tokens.append((lexeme, "identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 211  # Continue processing as a valid identifier
                else:
                    print(f"ERROR IN STATE 191")
                    state = 1000  # Error state

        #IDENTIFIER (17)
        elif state == 211:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for identifier")
                state = 1000  # Error state
            else:
                # Check for valid ending of an identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 212
                    tokens.append((lexeme, "identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 213  # Continue processing as a valid identifier
                else:
                    print(f"ERROR IN STATE 192")
                    state = 1000  # Error state

        #IDENTIFIER (18)
        elif state == 213:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for identifier")
                state = 1000  # Error state
            else:
                # Check for valid ending of an identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 214
                    tokens.append((lexeme, "identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 215  # Continue processing as a valid identifier
                else:
                    print(f"ERROR IN STATE 192")
                    state = 1000  # Error state

        #IDENTIFIER (19)
        elif state == 215:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for identifier")
                state = 1000  # Error state
            else:
                # Check for valid ending of an identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 216
                    tokens.append((lexeme, "identifier"))
                    lexeme = ""  # Reset lexeme for next token
                # Check if the lookahead is part of the identifier
                elif lookahead_char in valchar or lookahead_char in underscore:
                    state = 217  # Continue processing as a valid identifier
                else:
                    print(f"ERROR IN STATE 194")
                    state = 1000  # Error state

        #IDENTIFIER(20)
        elif state == 217:
            lexeme += token
            if token not in valchar and token not in upchar and token not in underscore:
                print(f"Invalid token '{token}' for identifier")
                state = 1000  # Error state
            else:
                # Check for valid ending of an identifier
                if lookahead_char in delim_id or lookahead_char is None or lookahead_char == "\n":
                    state = 218
                    tokens.append((lexeme, "identifier"))
                    lexeme = ""  # Reset lexeme for next token
                else:
                    print(f"ERROR IN STATE 218")
                    state = 1000  # Error state

        # STRING LITERALS
        elif state == 219:
            print("Passed state 219")
            lexeme += token
            # Check if the next character is within ASCII range and not a double quote
            if lookahead_char in ascii:
                state = 219  # Stay in state 219 to continue processing ASCII characters
            elif lookahead_char == '"':
                state = 220  # Transition to the next state when a double quote is seen
            else:
                print(f"ERROR IN STATE 219: Unexpected character {lookahead_char}")
                state = 1000  # Error state

        elif state == 220:
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


        #DELIM_GEN DELIMITERS
        elif state in {2, 4, 8, 14, 20, 39, 74, 78, 85, 105}:
            print("Passed Final State (delim_gen)")
            if token in delim_gen:
                lexeme = ""  # Reset lexeme
                tokens.append((token, "space"))  # Add delimiter as a token
                state = 0  # Reset state for the next token
            else:
                print("WRONG IN DELIM_GEN")
                state = 1000  # Reset state to recover
                lexeme += token

        #DELIM_END
        elif state in {26, 34, 42 ,89}:
            if token in delim_end:
                lexeme += token
                if token == ' ':
                    tokens.append((token, "space"))
                elif token == ';':
                    tokens.append((token, "semicolon"))
                state = 0  # Reset state for the next token
            else:
                print("WRONG IN DELIM_END")
                state = 1000  # Reset state to recover
                lexeme += token

        #DELIM_1 DELIMITERS
        elif state in {37, 46, 56, 60, 65, 68, 93, 100, 111}:
            if token in delim_1:
                if token == ' ':
                    tokens.append((token, "space"))
                elif token == '(':
                    tokens.append((token, token))
                state = 0  # Reset state for the next token
            else:
                print("WRONG IN DELIM_1")
                state = 1000  # Reset state to recover
                lexeme += token

        #DELIM_2 DELIMITERS
        elif state in {49}:
            if token in delim_2:
                if token == ' ':
                    tokens.append((token, "space"))
                elif token == '{':
                    tokens.append((token, "open curly brace"))
                state = 0  # Reset state for the next token
            else:
                print("WRONG IN DELIM_2")
                state = 1000  # Reset state to recover
                lexeme += token

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
                    tokens.append((token, "comma"))
                elif token == '}':
                    tokens.append((token, "close curly brace"))
                elif token == ')':
                    tokens.append((token, "close parenthesis"))
                elif token == '+':
                    tokens.append((token, "plus"))
                elif token == '\t':
                    tokens.append(("\\t", "tab"))
                state = 0  # Reset state for the next token
            else:
                print("WRONG IN DELIM_STRING")
                state = 1000  # Reset state to recover
                lexeme += token

        #DELIM_ADD DELIMITERS
        elif state in {114, 115}:
            if token in delim_add:
                if token == '"':
                    tokens.append((token, "double quote"))
                elif token == ' ':
                    tokens.append((token, "space"))
                elif token == '^':
                    tokens.append((token, "caret"))
                elif token == '(':
                    tokens.append((token, "open parenthesis"))
                state = 0  # Reset state for the next token
            else:
                print("WRONG IN DELIM_ADD")
                state = 1000  # Reset state to recover
                lexeme += token  # Append token to lexeme to process it in the next cycle

        #DELIM_UPDATE DELIMITERS
        elif state in {116, 122}:
            if token in delim_update:
                if token == ' ':
                    tokens.append((token, "space"))
                elif token == ')':
                    tokens.append((token, "close parenthesis"))
                elif token == ';':
                    tokens.append((token, "semicolon"))
                elif token == "Identifier":
                    tokens.append((token, "identifier"))
                state = 0  # Reset state for the next token
            else:
                print("WRONG IN DELIM_UPDATE")
                state = 1000  # Reset state to recover
                lexeme += token  # Append token to lexeme to process it in the next cycle

        #DELIM_EQUAL DELIMITERS
        elif state in {118, 124, 129, 132, 136, 144, 148}:
            if token in delim_equal:
                if token == ' ':
                    tokens.append((token, "space"))
                elif token == '{':
                    tokens.append((token, "open curly brace"))
                elif token in allval:
                    tokens.append((token, "valid value"))
                elif token in upchar:
                    tokens.append((token, "uppercase character"))
                elif token == '(':
                    tokens.append((token, token))
                elif token == '"':
                    tokens.append((token, "double quote"))
                state = 0  # Reset state for the next token
            else:
                print("WRONG IN DELIM_ADD")
                state = 1000  # Reset state to recover
                lexeme += token  # Append token to lexeme to process it in the next cycle

        #DELIM_ARITH DELIMITERS
        elif state in {120, 126, 130, 134}:
            if token in delim_arith:
                if token == '(':
                    tokens.append((token, token))
                elif token == ' ':
                    tokens.append((token, "space"))
                elif token == '^':
                    tokens.append((token, "caret"))
                elif token in value:
                    tokens.append((token, "value"))
                elif token in upchar:
                    tokens.append((token, "uppercase letter"))
                state = 0  # Reset state for the next token
            else:
                print("WRONG IN DELIM_ADD")
                state = 1000  # Reset state to recover
                lexeme += token  # Append token to lexeme to process it in the next cycle


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
                state = 1000  # Reset state to recover
                lexeme += token  # Append token to lexeme to process it in the next cycle

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
                state = 1000  # Reset state to recover
                lexeme += token  # Append token to lexeme to process it in the next cycle

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
                state = 1000  # Reset state to recover
                lexeme += token  # Append token to lexeme to process it in the next cycle

        #OPEN_PARENTHESIS_DELIM
        elif state in {168}:
            if token in open_parenthesis_delim:
                if token == '\n':
                    tokens.append((token, "newline"))
                elif token == '^':
                    tokens.append((token, "caret"))
                elif token == ' ':
                    tokens.append((token, "space"))
                elif token == '"':
                    tokens.append((token, "quote"))
                elif token == '(':
                    tokens.append((token, "open_paren"))
                elif token == ',':
                    tokens.append((token, "comma"))
                elif token == ')':
                    tokens.append((token, "close_paren"))
                elif token in lowchar:
                    tokens.append((token, "lowchar"))
                state = 0  # Reset state for the next token
            else:
                print("WRONG IN OPEN_PARENTHESIS_DELIM")
                state = 1000  # Reset state to recover
                lexeme += token  # Append token to lexeme to process it in the next cycle

        #CLOSE_PARENTHESIS_DELIM
        elif state in {170}:
            if token in close_parenthesis_delim:
                if token == ')':
                    tokens.append((token, "close_paren"))
                elif token == ' ':
                    tokens.append((token, "space"))
                elif token == '\n':
                    tokens.append((token, "newline"))
                elif token == '{':
                    tokens.append((token, "open_brace"))
                elif token == '}':
                    tokens.append((token, "close_brace"))
                elif token == '^':
                    tokens.append((token, "caret"))
                elif token == '+':
                    tokens.append((token, "plus"))
                elif token == '-':
                    tokens.append((token, "minus"))
                elif token == '/':
                    tokens.append((token, "slash"))
                elif token == '*':
                    tokens.append((token, "asterisk"))
                elif token == '%':
                    tokens.append((token, "percent"))
                elif token == '#':
                    tokens.append((token, "hash"))
                elif token == ';':
                    tokens.append((token, "semicolon"))
                state = 0  # Reset state for the next token
            else:
                print("WRONG IN CLOSE_PARENTHESIS_DELIM")
                state = 1000  # Reset state to recover
                lexeme += token  # Append token to lexeme to process it in the next cycle

        #OPEN_BRACES_DELIM
        elif state in {172}:
            if token in open_braces_delim:
                if token == ' ':
                    tokens.append((token, "space"))
                elif token == '\\':
                    tokens.append((token, "backslash"))
                elif token == '"':
                    tokens.append((token, "double_quote"))
                elif token in value:
                    tokens.append((token, "value"))
                elif token in allchar:
                    tokens.append((token, "allchar"))
                state = 0  # Reset state for the next token
            else:
                print("WRONG IN OPEN_BRACES_DELIM")
                state = 1000  # Reset state to recover
                lexeme += token  # Append token to lexeme to process it in the next cycle

        #CLOSE_BRACES_DELIM
        elif state in {174}:
            if token in close_braces_delim:
                if token == ' ':
                    tokens.append((token, "space"))
                elif token == '\n':
                    tokens.append((token, "newline"))
                elif token == '#':
                    tokens.append((token, "hash"))
                state = 0  # Reset state for the next token
            else:
                print("WRONG IN CLOSE_BRACE_DELIM")
                state = 1000  # Reset state to recover
                lexeme += token  # Append token to lexeme to process it in the next cycle

        #OPEN_BRACKET_DELIM
        elif state in {176}:
            if token in open_bracket_delim:
                if token in value:
                    tokens.append((token, "value"))
            else:
                print("WRONG IN OPEN_BRACKET_DELIM")
                state = 1000  # Reset state to recover
                lexeme += token  # Append token to lexeme to process it in the next cycle

        #CLOSE_BRACKET_DELIM
        elif state in {178}:
            if token in close_bracket_delim:
                if token ==  ' ':
                    tokens.append((token, "SPACE"))
                elif token ==  '=':
                    tokens.append((token, "equals"))
            else:
                print("WRONG IN CLOSE_BRACKET_DELIM")
                state = 1000  # Reset state to recover
                lexeme += token  # Append token to lexeme to process it in the next cycle

        # DELIM_ID DELIMITERS
        elif state in {180, 182, 184, 186, 188, 190, 192, 194, 196, 198, 
                       200, 202, 204, 206, 208, 210, 212, 214, 216, 218}:
            # First, check if we have a complete identifier to add
            if lexeme and (token in delim_id or lookahead_char in delim_id):
                tokens.append((lexeme, "identifier"))
                lexeme = ""

            # Now handle the current token
            if token in delim_id:
                if token == ' ':
                    tokens.append((token, "space"))
                elif token == '=':
                    tokens.append((token, "equals"))
                elif token == '<':
                    tokens.append((token, "less than"))
                elif token == '>':
                    tokens.append((token, "greater than"))
                elif token == ';':
                    tokens.append((token, "semicolon"))
                elif token == '!':
                    tokens.append((token, "exclamation mark"))
                elif token == '+':
                    tokens.append((token, "plus"))
                elif token == '[':
                    tokens.append((token, "open bracket"))
                elif token == '(':
                    tokens.append((token, token))
                elif token == '&':
                    tokens.append((token, "ampersand"))
                elif token == '|':
                    tokens.append((token, "pipe"))
                elif token == '-':
                    tokens.append((token, "minus"))
                elif token == '*':
                    tokens.append((token, "asterisk"))
                elif token == ',':
                    tokens.append((token, "comma"))
                
                state = 0  # Reset state for the next token
            else:
                # If it's not a delimiter, continue building the lexeme
                lexeme += token

        elif state == 1000:  # Error state
            lexeme += token  # Continue capturing invalid token
            if token in {'\n', ' '}:  # End of invalid token
                display_lexical_error(f"Invalid lexeme: {lexeme.strip()} on line {line_number}")
                lexeme = ""  # Reset lexeme
                state = 0  # Recover state

    return tokens

root = tk.Tk()
root.title("GenomeX")

frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

#Lexer Table
lexical_result = ttk.Treeview(frame, columns=('ID', 'Lexeme', 'Token'), show='headings', height=15)
lexical_result.heading('ID', text='ID')
lexical_result.heading('Lexeme', text='Lexeme')
lexical_result.heading('Token', text='Token')

lexical_result.column('ID', width=50, anchor='center')
lexical_result.column('Lexeme', width=150, anchor='center')
lexical_result.column('Token', width=150, anchor='center')

lexical_result.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

def parse_program():
    output_text.delete(1.0, tk.END)
    code = input_text.get("1.0", tk.END).strip()  # Get input code
    tokens = parseLexer(code)  # Run lexer
    
    # Clear previous entries in the Treeview
    for item in lexical_result.get_children():
        lexical_result.delete(item)
    
    # Insert tokens into the Treeview
    for idx, (lexeme, token) in enumerate(tokens, start=1):
        lexical_result.insert('', 'end', values=(idx, lexeme, token))

#Insert Code
input_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=40, height=10)
input_text.pack(side=tk.TOP, padx=10, pady=10)

parse_button = tk.Button(frame, text="Run", command=parse_program)
parse_button.pack(side=tk.TOP, padx=10, pady=5)

#Display Errors
output_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=40, height=15)
output_text.pack(side=tk.TOP, padx=10, pady=10)

root.mainloop()
