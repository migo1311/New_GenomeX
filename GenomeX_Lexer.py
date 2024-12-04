import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk

def display_lexical_error(message):
    output_text.insert(tk.END, message + '\n')
    output_text.yview(tk.END)  # Scroll to the end

def parseLexer(input_stream):
    """
    Lexical analyzer function to identify '_G' (greater-than) and '_L' (less-than) as relational operators.
    
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

    #DELIMITERS
    delim_gen = {' '} 
    delim_end = {' ', ';'} 
    delim_1 = {' ', '('} 
    delim_add = {'"', ' ', '^', '(', } 

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
                state = 37
                lexeme = token  
            else:
                state = 1000  # Reset state to recover
                lexeme += token

        
        elif state == 1:
            lexeme += token
    
            if token == 'G':
                if lookahead_char in delim_gen or lookahead_char is None or lookahead_char == '\n':  # Lookahead check for 'm'
                    if len(lexeme) > 1 and lexeme[-2] == '_':  # Check if the previous character is '_'
                        state = 2
                    else:
                        print("ERROR IN STATE 2: Invalid sequence before 'G'")
                        state = 1000  # Reset state to recover
                        lexeme += token


                else:
                    print("ERROR IN STATE 1: Invalid sequence before 'G'")
                    state = 1000  # Reset state to recover
                    lexeme += token

            #L
            elif token == 'L':
                if lookahead_char in delim_gen or lookahead_char is None or lookahead_char == '\n':  # Lookahead check for 'm'
                    if len(lexeme) > 1 and lexeme[-2] == '_':  # Check if the previous character is '_'
                        state = 4
                    else:
                        print("ERROR IN STATE 4: Invalid sequence before 'G'")
                        state = 1000  # Reset state to recover
                        lexeme += token

                else:
                    print("ERROR IN STATE 1: Invalid sequence before 'G'")
                    state = 1000  # Reset state to recover
                    lexeme += token


            if state == 2 or state == 4:
                tokens.append((lexeme, lexeme))  # Append the valid token

            else:
                print("ERROR IN STATE 1: Unexpected character")
                state = 1000  # Reset state to recover
                lexeme += token


        #DELIM_GEN DELIMITERS
        elif state in {2, 4, 8, 14, 20, 39, 42}:
            if token in delim_gen:
                lexeme = ""  # Reset lexeme
                tokens.append((token, "space"))  # Add delimiter as a token
                state = 0  # Reset state for the next token
            else:
                print("WRONG IN DELIM_GEN")
                state = 1000  # Reset state to recover
                lexeme += token


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


        #DELIM_END
        elif state in {26, 34}:
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


        elif state in {37}:
            if token in delim_1:
                if token == ' ':
                    tokens.append((token, "space"))
                elif token == '(':
                    tokens.append((token, "open parenthesis"))
                state = 0  # Reset state for the next token
            else:
                print("WRONG IN DELIM_1")
                state = 1000  # Reset state to recover
                lexeme += token


        elif state == 28:
            lexeme += token
                 
            if token == 'e':
                state = 29
            elif token == 'o':
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
            lexeme += token
            if token == 's':
                state = 41
            else:
                print("WRONG IN STATE 40")
                state = 1000  # Reset state to recover
                lexeme += token
                
        #DOSE
        elif state == 41:
            lexeme += token
            if token == 'e':
                if lookahead_char in delim_end or lookahead_char is None or lookahead_char == "\n":
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

        elif state == 1000:  # Error state
            lexeme += token  # Continue capturing invalid token
            if token in {'\n', ' '} or lookahead_char in delim_gen:  # End of invalid token
                display_lexical_error(f"Invalid lexeme: {lexeme.strip()} on line {line_number}")
                lexeme = ""  # Reset lexeme
                state = 0  # Recover state

    return tokens

root = tk.Tk()
root.title("GenomeX")

frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

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

input_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=40, height=10)
input_text.pack(side=tk.TOP, padx=10, pady=10)

parse_button = tk.Button(frame, text="Run", command=parse_program)
parse_button.pack(side=tk.TOP, padx=10, pady=5)

output_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=40, height=15)
output_text.pack(side=tk.TOP, padx=10, pady=10)

root.mainloop()
