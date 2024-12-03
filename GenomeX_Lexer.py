import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk

def handle_state():
    state = 1000  # Example: Simulating that state is 1000

    if state == 1000:
        # Clear both the Treeview and the output text when there is a lexical error
        for item in lexical_result.get_children():
            lexical_result.delete(item)  # Clear Treeview items
        
        output_text.delete(1.0, tk.END)  # Clear output text
        
        # Display the lexical error
        display_lexical_error(f"Lexical error: Invalid token ")

def display_lexical_error(message):
    output_text.insert(tk.END, message + '\n')
    output_text.yview(tk.END)  # Scroll to the end

def getRelop(input_stream):
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

    delim_gen = {' ', '\n'} 
    delim_end = {' ', ';'} 
    delim_1 = {' ', '('} 

    lookahead_char = None
    
    while True:
        if lookahead_char is not None:
            token = lookahead_char  # Use cached lookahead character
            lookahead_char = None  # Clear the cache
        else:
            try:
                token = next(char_iter)
            except StopIteration:
                break  # End of input stream

        try:
            lookahead_char = next(char_iter)  # Peek the next character
        except StopIteration:
            lookahead_char = None  # No more characters to process
        
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
            elif token == '\n':
                state = 999
                lexeme = token  
            else:
                state = 1000  # Reset state to recover
        
        elif state == 1:
            lexeme += token
            
            #State 2
            if token == 'G':
                if len(lexeme) > 1 and lexeme[-2] == '_':  # Check if the previous character is '_'
                    state = 2
                else:
                    print("ERROR IN STATE 1: Invalid sequence before 'G'")
                    lexeme = ""  # Reset lexeme to avoid appending invalid values
                    state = 1000  # Reset state to recover
        
            elif token == 'L':
                if len(lexeme) > 1 and lexeme[-2] == '_':  # Check if the previous character is '_'
                    state = 4
                else:
                    print("ERROR IN STATE 1: Invalid sequence before 'L'")
                    lexeme = ""  # Reset lexeme to avoid appending invalid values
                    state = 1000  # Reset state to recover

            if state == 2 or state == 4:
                tokens.append((lexeme, lexeme))  # Append the valid token

            else:
                print("ERROR IN STATE 1: Unexpected character")
                lexeme = ""  # Reset lexeme to avoid appending invalid values
                state = 1000  # Reset state to recover

        #DELIM_GEN DELIMITERS
        elif state in {2, 4, 8, 14, 20, 39}:
            if token in delim_gen:
                lexeme = ""  # Reset lexeme
                tokens.append((token, "space"))  # Add delimiter as a token
                state = 0  # Reset state for the next token
            else:
                print("WRONG")
                lexeme = ""  # Reset lexeme to avoid appending invalid values
                state = 1000  # Reset state to recover

        elif state == 6:
            if token == 'c':
                lexeme += token
                state = 7
                
            elif token == 'l':
                lexeme += token
                state = 10
            else:
                print("WRONG")
                lexeme = ""  # Reset lexeme to avoid appending invalid values
                state = 1000  # Reset state to recover
                
        #ACT
        elif state == 7:
            if token == 't':
                    lexeme += token
                    state = 14
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
            else:
                print("WRONG")
                lexeme = ""  # Reset lexeme to avoid appending invalid values
                state = 1000  # Reset state to recover

        elif state == 10:
            lexeme += token
            if token == 'l':
                state = 11
            else:
                print("WRONG")
                lexeme = ""  # Reset lexeme to avoid appending invalid values
                state = 1000  # Reset state to recover

        elif state == 11:
            lexeme += token
            if token == 'e':
                state = 12
            else:
                print("WRONG")
                lexeme = ""  # Reset lexeme to avoid appending invalid values
                state = 1000  # Reset state to recover

        elif state == 12:
            lexeme += token
            if token == 'l':
                state = 13
            else:
                print("WRONG")
                lexeme = ""  # Reset lexeme to avoid appending invalid values
                state = 1000  # Reset state to recover

        #ALLELE
        elif state == 13:
            lexeme += token
            if token == 'e':
                if not lexeme:  # No valid subsequent character
                    state = 0
                    lexeme = ""
                else:
                    state = 14
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
            else:
                print("WRONG")
                lexeme = ""  # Reset lexeme to avoid appending invalid values
                state = 1000  # Reset state to recover

        elif state == 16:
            lexeme += token
            if token == 'l':
                state = 17
            elif token == 'o':
                state = 22
            else:
                print("WRONG")
                lexeme = ""  # Reset lexeme to avoid appending invalid values
                state = 1000  # Reset state to recover

        elif state == 17:
            lexeme += token
            if token == 'u':
                state = 18
            else:
                print("WRONG")
                lexeme = ""  # Reset lexeme to avoid appending invalid values
                state = 1000  # Reset state to recover

        elif state == 18:
            lexeme += token
            if token == 's':
                state = 19
            else:
                print("WRONG")
                lexeme = ""  # Reset lexeme to avoid appending invalid values
                state = 1000  # Reset state to recover

        #CLUST
        elif state == 19:
            lexeme += token
            if token == 't':
                if not lexeme:  # No valid subsequent character
                    state = 0
                    lexeme = ""
                else:
                    state = 20
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
            else:
                print("WRONG")
                lexeme = ""  # Reset lexeme to avoid appending invalid values
                state = 1000  # Reset state to recover

        elif state == 22:
            lexeme += token
            if token == 'n':
                state = 23
            else:
                print("WRONG")
                lexeme = ""  # Reset lexeme to avoid appending invalid values
                state = 1000  # Reset state to recover

        elif state == 23:
            lexeme += token
            if token == 't':
                state = 24
            else:
                print("WRONG")
                lexeme = ""  # Reset lexeme to avoid appending invalid values
                state = 1000  # Reset state to recover

        elif state == 24:
            lexeme += token
            if token == 'i':
                state = 25
            else:
                print("WRONG")
                lexeme = ""  # Reset lexeme to avoid appending invalid values
                state = 1000  # Reset state to recover

        #CONTIG
        elif state == 25:
            lexeme += token
            if token == 'g':
                if not lexeme:  # No valid subsequent character
                    state = 0
                    lexeme = ""
                else:
                    state = 26
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
            else:
                print("WRONG")
                lexeme = ""  # Reset lexeme to avoid appending invalid values
                state = 1000  # Reset state to recover

        #DELIM_END
        elif state in {26, 34}:
            if token in delim_end:
                # Process the accumulated lexeme before the delimiter
                if lexeme:  # Check if lexeme is non-empty
                    tokens.append((lexeme, "kups"))  # Add the lexeme as a token
                    lexeme = ""  # Reset lexeme
                # Add the delimiter itself as a token
                if token == ' ':
                    tokens.append((token, "space"))
                elif token == ';':
                    tokens.append((token, "semicolon"))
                state = 0  # Reset state for the next token
            else:
                print("WRONG")
                lexeme = ""  # Reset lexeme to avoid appending invalid values
                state = 1000  # Reset state to recover

        elif state in {36}:
            if token in delim_1:
                if token == ' ':
                    tokens.append((token, "space"))
                elif token == '(':
                    tokens.append((token, "open parenthesis"))
                state = 0  # Reset state for the next token
            else:
                print("WRONG")
                lexeme = ""  # Reset lexeme to avoid appending invalid values
                state = 1000  # Reset state to recover

        elif state == 28:
            lexeme += token
          
            if token == 'o':
                if lookahead_char == 'm':  # Lookahead check for 'm'
                    state = 38
                else:
                    tokens.append((lexeme, "do"))
                    state = 0
                    lexeme = ""
            elif token == 'e':
                state = 29

            else:
                print("YAAA")
                lexeme = ""  # Reset lexeme to avoid appending invalid values
                state = 1000
                

        elif state == 29:
            lexeme += token
            if token == 's':
                state = 30
            else:
                print("WRONG")
                lexeme = ""  # Reset lexeme to avoid appending invalid values
                state = 1000  # Reset state to recover

        elif state == 30:
            lexeme += token
            if token == 't':
                state = 31
            else:
                print("WRONG")
                lexeme = ""  # Reset lexeme to avoid appending invalid values
                state = 1000  # Reset state to recover

        elif state == 31:
            lexeme += token
            if token == 'r':
                state = 32
            else:
                print("WRONG")
                lexeme = ""  # Reset lexeme to avoid appending invalid values
                state = 1000  # Reset state to recover

        elif state == 32:
            lexeme += token
            if token == 'o':
                state = 33
            else:
                print("WRONG")
                lexeme = ""  # Reset lexeme to avoid appending invalid values
                state = 1000  # Reset state to recover

        #DESTROY
        elif state == 33:
            lexeme += token
            if token == 'y':
                if not lexeme:  # No valid subsequent character
                    state = 0
                    lexeme = ""
                else:
                    state = 34
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
            else:
                print("WRONG")
                lexeme = ""  # Reset lexeme to avoid appending invalid values
                state = 1000  # Reset state to recover

        elif state == 36:
            lexeme += token
            if token == 'm':
                if not lexeme:  # No valid subsequent character
                    state = 0
                    lexeme = ""
                else:
                    tokens.append((lexeme, lexeme))
                    lexeme = ""
            else:
                print("WRONG")
                lexeme = ""  # Reset lexeme to avoid appending invalid values
                state = 1000  # Reset state to recover


        #DOM
        # DOM state (processes the 'dom' keyword)
        elif state == 36:
            lexeme += 'o'  # Add the letter 'o' explicitly to the lexeme
            tokens.append((lexeme, lexeme))

        elif state == 38:
            lexeme += token
            if token == 'm':
                tokens.append((lexeme, "dom"))
                state = 0
                lexeme = ""

        elif state == 999:  # Handle newline state
            tokens.append(('"\\n"', "newline"))
            id_counter += 1
            lexeme = ""  # Reset lexeme
            state = 0  # Reset to initial state

        elif state == 1000:
            display_lexical_error(f"Lexical error: Invalid token '{lexeme}'")

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
    tokens = getRelop(code)  # Run lexer
    
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