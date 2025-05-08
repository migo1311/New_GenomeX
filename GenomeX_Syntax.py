import GenomeX_Lexer as gxl
import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
import sys  # Import the system module
from itertools import chain


def parseSyntax(tokens, output_text):
    def get_line_number(tokens, index):
        """
        Determine the line number for a token at the given index by counting newlines.
        
        Args:
            tokens: The list of tokens
            index: The index of the token to find the line number for
        
        Returns:
            The line number (1-based)
        """
        if index < 0 or index >= len(tokens):
            return -1  # Invalid index
        
        line_number = 1
        for i in range(index):
            if tokens[i][1] == "newline":
                line_number += 1
        
        return line_number

    def skip_spaces(tokens, start_idx):
        # Guard against None
        if start_idx is None:
            return None
            
        while start_idx < len(tokens) and tokens[start_idx][1] in ["space", "comment", "multiline", "tab"]:
            start_idx += 1
        return start_idx

    def is_token(tokens, idx, token_type):
            if idx >= len(tokens):
                return False

            # If token_type is a list or tuple, check if the token's type is in that list
            if isinstance(token_type, (list, tuple)):
                return tokens[idx][1] in token_type

            # Otherwise, check if the token's type matches the expected type
            return tokens[idx][1] == token_type
        
    def check_number_sign(token):
        if not token or not token[0]: 
            return None
        
        value = token[0]

        if value.startswith('^'):
            if '.' in value:
                return "nequantliteral"  
            return "neliteral"  

        if '.' in value:
            return "quantval" 
        return "doseliteral" 

    def validate_syntax_pattern(tokens, pattern, start_idx=0):
        token_idx = start_idx
        pattern_idx = 0
        number_sign = None

        while token_idx < len(tokens) and pattern_idx < len(pattern):
            token_value = tokens[token_idx][1]  # Assuming tokens are tuples like (type, value)

            # Skip spaces
            if token_value == "space":
                token_idx += 1
                continue

            # Get the expected value from the pattern
            expected = pattern[pattern_idx]

            # Check if the expected value is a set or a specific token
            if isinstance(expected, set):
                # If it's a set, check if the token is in the set
                if token_value not in expected:
                    return False, token_idx, None
            else:
                # If it's a specific token, check for exact match
                if token_value != expected:
                    return False, token_idx, None

            # Move to the next token and pattern element
            token_idx += 1
            pattern_idx += 1

        # Return True if the entire pattern was matched
        return True, token_idx, number_sign
    
    class program:
            def body_statements(tokens, start_idx):
                keywords = {"dose", "quant", "seq", "allele"}

                statement_parsers = {
                    'express': statements.express_statement,
                    'if': statements.if_statement,
                    'prod': statements.prod_statement,
                    'Identifier': statements.stimuli_statement,
                    'for': statements.for_loop_statement,
                    'do': statements.do_while_statement,
                    'while': statements.while_statement,
                    'func': statements.func_calling,
                }

                perms_parsers = {
                    'allele': variables.validate_alleleval,
                    'dose': variables.validate_doseval,
                    'seq': variables.validate_seqval,
                    'quant': variables.validate_quantval,
                }

                local_parse = {
                    'allele': variables.validate_alleleval,
                    'dose': variables.validate_doseval,
                    'seq': variables.validate_seqval,
                    'quant': variables.validate_quantval,
                }

                clust_parse = {
                    'dose': clust.validate_clust_doseval,
                    'quant': clust.validate_clust_quantval,
                    'seq': clust.validate_clust_seqval
                }

                check_statements = False

                while start_idx is not None and start_idx < len(tokens):
                    print("<body_statements>")
                    current_token = tokens[start_idx] if start_idx < len(tokens) else None
                        
                    # Get the current line number for this token
                    current_line_number = get_line_number(tokens, start_idx)
                    
                    # Find which display line contains this token
                    matching_line = None
                    for line in display_lines:
                        if current_token in line["tokens"]:
                            matching_line = line
                            break
                        
                    # If we found a matching line, use its line number and text
                    if matching_line:
                        line_number = matching_line["line_number"]
                        line_tokens = matching_line["tokens"]
                        line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])
                    else:
                        # If no matching display line, use the calculated line number
                        line_number = current_line_number
                        line_text = current_token[0] if current_token else ""
                    start_idx = skip_spaces(tokens, start_idx)

                    # List of keywords that require '_L' prefix
                    keywords = ['dose', 'quant', 'seq', 'allele', 'clust', 'perms']

                    # Check if current token is one of the keywords
                    for keyword in keywords:
                        if is_token(tokens, start_idx, keyword):
                            # Get the actual line text for this token
                            token_line = None
                            current_token = tokens[start_idx]
                            for line in display_lines:
                                if current_token in line["tokens"]:
                                    token_line = line
                                    break
                            
                            if token_line:
                                error_line_number = token_line["line_number"]
                                error_line_text = ' '.join([t[0] for t in token_line["tokens"] if t[1] != "space"])
                            else:
                                error_line_number = get_line_number(tokens, start_idx)
                                error_line_text = current_token[0] if current_token else ""

                            output_text.insert(tk.END, f"Syntax Error at line {error_line_number}: Expected '_L' before keyword\n")
                            output_text.insert(tk.END, f"Line {error_line_number}: {error_line_text}\n")
                            print(f"Error: Expected '_L' before keyword at line {error_line_number}")
                            return False, start_idx
                                    
                    # Special handling for *L perms (as a separate case from just *L)
                    if is_token(tokens, start_idx, '_L'):
                        print("<local_perms_declaration>")
                        check_statements = True  # Set to True when a valid *L perms statement is found
                        start_idx += 1  # Move past '*L'
                        start_idx = skip_spaces(tokens, start_idx)

                        # Check for 'perms' or 'clust' keyword
                        if is_token(tokens, start_idx, 'perms'):
                            print("<perms>")
                            start_idx += 1  # Move past 'perms'
                            start_idx = skip_spaces(tokens, start_idx)
                            
                            # Check if 'clust' follows 'perms'
                            if is_token(tokens, start_idx, 'clust'):
                                print("<clust>")
                                start_idx += 1  # Move past 'clust'
                                start_idx = skip_spaces(tokens, start_idx)
                                
                                # Look for a valid clust type
                                if not any(is_token(tokens, start_idx, clust_type) for clust_type in clust_parse):
                                    print("Invalid *clust type")
                                    return False, None
                                    
                                for clust_type, parser_func in clust_parse.items():
                                    if is_token(tokens, start_idx, clust_type):
                                        start_idx += 1  # Move past the type
                                        start_idx = skip_spaces(tokens, start_idx)
                                        
                                        is_valid, new_idx = parser_func(tokens, start_idx)
                                        if not is_valid:
                                            print(f"Invalid *L perms clust {clust_type} statement")
                                            return False, None
                                            
                                        start_idx = new_idx
                                        start_idx = skip_spaces(tokens, start_idx)
                                        print(f"Successfully parsed *L perms clust {clust_type}")
                                        break  # Exit loop after parsing a valid statement
                                        
                                continue  # Continue main loop
                            
                            # Original perms parsing logic
                            # Look for a valid perms type
                            if not any(is_token(tokens, start_idx, perms_type) for perms_type in perms_parsers):
                                print("Invalid perms type")
                                return False, None  # Invalid perms type
                                
                            for perms_type, parser_func in perms_parsers.items():
                                if is_token(tokens, start_idx, perms_type):
                                    start_idx += 1  # Move past the type
                                    start_idx = skip_spaces(tokens, start_idx)
                                    
                                    is_valid, new_idx = parser_func(tokens, start_idx)
                                    if not is_valid:
                                        print(f"Invalid perms {perms_type} statement")
                                        return False, None
                                        
                                    start_idx = new_idx
                                    start_idx = skip_spaces(tokens, start_idx)
                                    print(f"Successfully parsed perms {perms_type}")
                                    break  # Exit loop after parsing a valid perms statement
                                    
                            continue  # Continue main loop
                            
                        elif is_token(tokens, start_idx, 'clust'):
                            print("<clust>")
                            start_idx += 1  # Move past 'clust'
                            start_idx = skip_spaces(tokens, start_idx)
                            
                            # Look for a valid clust type
                            if not any(is_token(tokens, start_idx, clust_type) for clust_type in clust_parse):
                                print("Invalid *clust type")
                                return False, None
                                
                            for clust_type, parser_func in clust_parse.items():
                                if is_token(tokens, start_idx, clust_type):
                                    start_idx += 1  # Move past the type
                                    start_idx = skip_spaces(tokens, start_idx)
                                    
                                    is_valid, new_idx = parser_func(tokens, start_idx)
                                    if not is_valid:
                                        print(f"Invalid *L clust {clust_type} statement")
                                        return False, None
                                        
                                    start_idx = new_idx
                                    start_idx = skip_spaces(tokens, start_idx)
                                    print(f"Successfully parsed *L clust {clust_type}")
                                    break  # Exit loop after parsing a valid statement
                                    
                            continue  # Continue main loop

                        # Look for a valid perms type
                        if not any(is_token(tokens, start_idx, L_type) for L_type in local_parse):
                            print("Invalid *L perms type")
                            output_text.insert(tk.END, f"Expected valid datatype but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None  # Invalid *L perms type

                        for L_type, parser_func in local_parse.items():
                            if is_token(tokens, start_idx, L_type):
                                start_idx += 1  # Move past the type
                                start_idx = skip_spaces(tokens, start_idx)

                                is_valid, new_idx = parser_func(tokens, start_idx)
                                if not is_valid:
                                    print(f"Invalid *L perms {L_type} statement")
                                    return False, None

                                start_idx = new_idx
                                start_idx = skip_spaces(tokens, start_idx)
                                print(f"Successfully parsed *L perms {L_type}")
                                break  # Exit loop after parsing a valid *L perms statement

                        continue  # Continue main loop

                    # Regular statement handling
                    found_statement = False
                    for statement_type, parser_func in statement_parsers.items():
                        if is_token(tokens, start_idx, statement_type):
                            check_statements = True  # Set to True when a valid statement is found
                            found_statement = True
                            start_idx += 1  # Move past statement keyword
                            start_idx = skip_spaces(tokens, start_idx)

                            is_valid, new_idx = parser_func(tokens, start_idx)
                            if not is_valid:
                                print(f"Invalid {statement_type} statement")
                                return False, None

                            start_idx = new_idx
                            start_idx = skip_spaces(tokens, start_idx)
                            print(f"Finished statement: {statement_type}")
                            break  # Exit loop after parsing a valid statement

                    if not found_statement:
                        # If we reach this point and haven't found a valid statement
                        # We might be at the end of the block or have an invalid token
                        if start_idx >= len(tokens):
                            print("Reached end of tokens")
                        else:
                            print(f"Current token: {tokens[start_idx] if start_idx < len(tokens) else 'None'}")
                        return check_statements, start_idx  # Return current state instead of error

                print(f"End of body_statements: check_statements={check_statements}, start_idx={start_idx}")
                output_text.insert(tk.END, f"Expected valid statements but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number + 2}: {line_text}\n")
                return check_statements, start_idx  # Return final state

            # Class variables to track program state
            main_function_seen = False
            user_defined_function_error = False  # Track if any user-defined function has an error            
            def global_statements(tokens, start_idx):

                print("<global_statements>")
                keywords = {"dose", "quant", "seq", "allele"}
                current_token = tokens[start_idx] if start_idx < len(tokens) else None
                matching_line = None
                for line in display_lines:
                    if current_token in line["tokens"]:
                        matching_line = line
                        break
                
                if matching_line:
                    line_number = matching_line["line_number"]
                    line_tokens = matching_line["tokens"]
                    line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])
                else:
                    line_number = get_line_number(tokens, start_idx)
                    line_text = current_token[0] if current_token else "EOF"

                # Early validation - check if we have a valid keyword
                if start_idx >= len(tokens) or not any(is_token(tokens, start_idx, keyword) for keyword in keywords):
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a valid keyword (dose, quant, seq, allele) but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, start_idx  # Return proper tuple instead of None
                perms_parsers = {
                    'allele': variables.validate_alleleval,
                    'dose': variables.validate_doseval,
                    'seq': variables.validate_seqval,
                    'quant': variables.validate_quantval,
                }

                local_parse = {
                    'allele': variables.validate_alleleval,
                    'dose': variables.validate_doseval,
                    'seq': variables.validate_seqval,
                    'quant': variables.validate_quantval,
                }

                clust_parse = {
                    'dose': clust.validate_clust_doseval,
                    'quant': clust.validate_clust_quantval,
                    'seq': clust.validate_clust_seqval
                }

                
                check_statements = False

                while start_idx is not None and start_idx < len(tokens):
                    start_idx = skip_spaces(tokens, start_idx)
                    print("<body_statements>")
                    current_token = tokens[start_idx] if start_idx < len(tokens) else None
                        
                    # Find which display line contains this token
                    matching_line = None
                    for line in display_lines:
                        if current_token in line["tokens"]:
                            matching_line = line
                            break
                        
                    # If we found a matching line, use its line number, otherwise fall back to get_line_number
                    if matching_line:
                        line_number = matching_line["line_number"]
                        line_tokens = matching_line["tokens"]
                        line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])  # Format without spaces
                    else:
                        line_number = get_line_number(tokens, start_idx)
                        line_tokens = []
                        line_text = ""

                    # List of keywords that require '_L' prefix
                    keywords = ['dose', 'quant', 'seq', 'allele', 'clust', 'perms']

                    # Check if current token is one of the keywords
                    for keyword in keywords:
                        if is_token(tokens, start_idx, keyword):
                            # Removed the error about expecting '_L' before keyword
                            # Now we just proceed normally with keyword processing
                            print(f"Found keyword: {keyword}")
                            # Add any keyword processing here if needed
                            # ...
                            
                    # Special handling for perms and clust (removed '_L' requirement)
                    if is_token(tokens, start_idx, 'perms'):
                        print("<perms>")
                        start_idx += 1  # Move past 'perms'
                        start_idx = skip_spaces(tokens, start_idx)
                        
                        # Check if 'clust' follows 'perms'
                        if is_token(tokens, start_idx, 'clust'):
                            print("<clust>")
                            start_idx += 1  # Move past 'clust'
                            start_idx = skip_spaces(tokens, start_idx)
                            
                            # Look for a valid clust type
                            if not any(is_token(tokens, start_idx, clust_type) for clust_type in clust_parse):
                                print("Invalid clust type")
                                return False, None
                                
                            for clust_type, parser_func in clust_parse.items():
                                if is_token(tokens, start_idx, clust_type):
                                    start_idx += 1  # Move past the type
                                    start_idx = skip_spaces(tokens, start_idx)
                                    
                                    is_valid, new_idx = parser_func(tokens, start_idx)
                                    if not is_valid:
                                        print(f"Invalid perms clust {clust_type} statement")
                                        return False, None
                                        
                                    start_idx = new_idx
                                    start_idx = skip_spaces(tokens, start_idx)
                                    print(f"Successfully parsed perms clust {clust_type}")
                                    break  # Exit loop after parsing a valid statement
                                    
                            continue  # Continue main loop
                        
                        # Original perms parsing logic
                        # Look for a valid perms type
                        if not any(is_token(tokens, start_idx, perms_type) for perms_type in perms_parsers):
                            print("Invalid perms type")
                            return False, None  # Invalid perms type
                            
                        for perms_type, parser_func in perms_parsers.items():
                            if is_token(tokens, start_idx, perms_type):
                                start_idx += 1  # Move past the type
                                start_idx = skip_spaces(tokens, start_idx)
                                
                                is_valid, new_idx = parser_func(tokens, start_idx)
                                if not is_valid:
                                    print(f"Invalid perms {perms_type} statement")
                                    return False, None
                                    
                                start_idx = new_idx
                                start_idx = skip_spaces(tokens, start_idx)
                                print(f"Successfully parsed perms {perms_type}")
                                break  # Exit loop after parsing a valid perms statement
                                
                        continue  # Continue main loop
                        
                    elif is_token(tokens, start_idx, 'clust'):
                        print("<clust>")
                        start_idx += 1  # Move past 'clust'
                        start_idx = skip_spaces(tokens, start_idx)
                        
                        # Look for a valid clust type
                        if not any(is_token(tokens, start_idx, clust_type) for clust_type in clust_parse):
                            print("Invalid clust type")
                            return False, None
                            
                        for clust_type, parser_func in clust_parse.items():
                            if is_token(tokens, start_idx, clust_type):
                                start_idx += 1  # Move past the type
                                start_idx = skip_spaces(tokens, start_idx)
                                
                                is_valid, new_idx = parser_func(tokens, start_idx)
                                if not is_valid:
                                    print(f"Invalid clust {clust_type} statement")
                                    return False, None
                                    
                                start_idx = new_idx
                                start_idx = skip_spaces(tokens, start_idx)
                                print(f"Successfully parsed clust {clust_type}")
                                break  # Exit loop after parsing a valid statement
                                
                        continue  # Continue main loop

                    # Direct parsing for other types
                    for L_type, parser_func in local_parse.items():
                        if is_token(tokens, start_idx, L_type):
                            start_idx += 1  # Move past the type
                            start_idx = skip_spaces(tokens, start_idx)

                            is_valid, new_idx = parser_func(tokens, start_idx)
                            if not is_valid:
                                print(f"Invalid {L_type} statement")
                                return False, None

                            start_idx = new_idx
                            start_idx = skip_spaces(tokens, start_idx)
                            print(f"Successfully parsed {L_type}")
                            check_statements = True  # Mark that we've found a valid statement
                            break  # Exit loop after parsing a valid statement

                    print(f"End of body_statements: check_statements={check_statements}, start_idx={start_idx}")
                    output_text.insert(tk.END, f"Expected valid statements but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number + 2}: {line_text}\n")
                    return check_statements, start_idx  # Return final state

            def global_handling(tokens, start_idx):
                print("<global_handling>")
                check_statements, new_idx = program.global_statements(tokens, start_idx)

                if new_idx is None:
                    print("Error in main function body statements")
                    return False, None
                
                if not program.main_function_seen:
                    print("Error: No main function (gene) found in the program")
                    output_text.insert(tk.END, f"Expected main function\n")
                     
                    return False, None
                else:
                    pass
                
                start_idx = new_idx
                return True, start_idx + 1
            
            def user_defined_function(tokens, start_idx):
                print("Parsing user defined function...")
                # Find which display line contains this token
                current_token = tokens[start_idx] if start_idx < len(tokens) else None

                matching_line = None
                for line in display_lines:
                    if current_token in line["tokens"]:
                        matching_line = line
                        break
                
                # If we found a matching line, use its line number, otherwise fall back to get_line_number
                if matching_line:
                    line_number = matching_line["line_number"]
                    line_tokens = matching_line["tokens"]
                    line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])  # Format without spaces
                else:
                    line_number = get_line_number(tokens, start_idx)
                    line_tokens = []
                    line_text = ""
                start_idx = skip_spaces(tokens, start_idx)
                
                # Check if the next token is 'void' (optional)
                if is_token(tokens, start_idx, 'void'):
                    start_idx += 1  # Move past 'void'
                    start_idx = skip_spaces(tokens, start_idx)

                # The function name is now required. We check for an Identifier token.
                if not (start_idx < len(tokens) and tokens[start_idx][1] == "Identifier"):
                    print(f"Error: Expected function name (Identifier) at index {start_idx}")
                    output_text.insert(tk.END, f"Expected function name (Identifier) or gene at index {start_idx} but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    program.user_defined_function_error = True  # Mark that a user-defined function has an error
                    return False, None

                start_idx += 1  # Move past function name
                start_idx = skip_spaces(tokens, start_idx)

                if not is_token(tokens, start_idx, '('):
                    print(f"Error: Expected '(' after function name at index {start_idx}")
                    output_text.insert(tk.END, f"Syntax Error: Expected '(' after function name at index {start_idx}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    program.user_defined_function_error = True  # Mark that a user-defined function has an error
                    return False, None
                start_idx += 1  # Move past '('
                start_idx = skip_spaces(tokens, start_idx)

                # Parse the parameters
                is_valid, params, new_idx = parameters.parse_params(tokens, start_idx)
                if not is_valid:
                    print(f"Error: Invalid parameters in function declaration at index {start_idx}")
                    program.user_defined_function_error = True  # Mark that a user-defined function has an error
                    return False, None

                start_idx = new_idx  # Move to next token
                start_idx = skip_spaces(tokens, start_idx)

                if not is_token(tokens, start_idx, ')'):
                    print(f"Error: Expected ')' at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                    program.user_defined_function_error = True  # Mark that a user-defined function has an error
                    return False, None
                
                start_idx += 1 
                start_idx = skip_spaces(tokens, start_idx)            
                if not is_token(tokens, start_idx, '{'):
                    print("Missing opening brace for function block")
                    program.user_defined_function_error = True  # Mark that a user-defined function has an error
                    return False, None
                
                start_idx += 1  # Move past '{'
                start_idx = skip_spaces(tokens, start_idx)

                # Parse the function body
                check_statements, new_idx = program.body_statements(tokens, start_idx)
                
                if new_idx is None:
                    print("Error in user defined function statements")
                    program.user_defined_function_error = True  # Mark that a user-defined function has an error
                    return False, None
                
                start_idx = new_idx
                
                # Check if a main function exists in the program
                if not program.main_function_seen:
                    print("Error: No main function (gene) found in the program")
                    output_text.insert(tk.END, f"Expected main function\n")
                    return False, None
                else:
                    pass

                # Check for closing brace
                if is_token(tokens, start_idx, '}'):
                    print("Found closing brace for user defined function")
                    # Important: Return False if no statements were found in the function body
                    if not check_statements:
                        print("Error: No statements found in user defined function")
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected '_L' before keyword\n")
                        output_text.insert(tk.END, f"Expected valid statements in user defined\n")

                        program.user_defined_function_error = True  # Mark that a user-defined function has an error
                        return False, None
                    
                    return True, start_idx + 1
                else:


                    program.user_defined_function_error = True  # Mark that a user-defined function has an error
                    return False, None  # Error: Missing closing brace

            def main_function(tokens, start_idx):
                print("Parsing function...")
                current_token = tokens[start_idx] if start_idx < len(tokens) else None
                
                # Find which display line contains this token
                matching_line = None
                for line in display_lines:
                    if current_token in line["tokens"]:
                        matching_line = line
                        break
                
                # If we found a matching line, use its line number, otherwise fall back to get_line_number
                if matching_line:
                    line_number = matching_line["line_number"]
                    line_tokens = matching_line["tokens"]
                    line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])  # Format without spaces
                else:
                    line_number = get_line_number(tokens, start_idx)
                    line_tokens = []
                    line_text = ""
                        
                start_idx = skip_spaces(tokens, start_idx)

                
                # Check if this is the main function (gene)
                if is_token(tokens, start_idx, 'gene'):
                    print("main function")
                    
                    # If any user-defined function has an error, do not proceed with the main function
                    if program.user_defined_function_error:
                        print("Error: Cannot proceed with main function due to errors in user-defined functions")
                        return False, None
                    
                    # Check if we've already seen the main function
                    if program.main_function_seen:
                        print("Error: Multiple main functions (gene) declared")
                        return False, None
                    
                    # Set the flag that we've seen the main function
                    program.main_function_seen = True
                    
                    start_idx += 1  # Move past 'gene'
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    if not is_token(tokens, start_idx, '('):
                        print(f"Error: Expected '(' after 'gene' at index {start_idx}")
                        output_text.insert(tk.END, f"Expected '(' after 'gene' at index {start_idx}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                    start_idx += 1  # Move past '('

                    # Ensure no semicolon is present before ')'
                    if is_token(tokens, start_idx, ';'):
                        print(f"Error: Unexpected ';' at index {start_idx}")
                    
                        return False, None

                    if not is_token(tokens, start_idx, ')'):
                        print(f"Error: Expected ')' at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                        output_text.insert(tk.END, f"Syntax Error: Expected ')' after 'gene' at index {start_idx}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                    
                    start_idx += 1 
                    start_idx = skip_spaces(tokens, start_idx)            
                    if not is_token(tokens, start_idx, '{'):

                        print("Missing opening brace for main function block")
                        output_text.insert(tk.END, f"Syntax Error: Expected '{{' after 'gene' but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                    
                    start_idx += 1  # Move past '{'
                    start_idx = skip_spaces(tokens, start_idx)

                    # Parse the function body
                    check_statements, new_idx = program.body_statements(tokens, start_idx)
                    print("Parsing function...")
                    current_token = tokens[start_idx] if start_idx < len(tokens) else None
                    
                    # Find which display line contains this token
                    matching_line = None
                    for line in display_lines:
                        if current_token in line["tokens"]:
                            matching_line = line
                            break
                    
                    # If we found a matching line, use its line number, otherwise fall back to get_line_number
                    if matching_line:
                        line_number = matching_line["line_number"]
                        line_tokens = matching_line["tokens"]
                        line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])  # Format without spaces
                    else:
                        line_number = get_line_number(tokens, start_idx)
                        line_tokens = []
                        line_text = ""
                        if new_idx is None:
                            print("Error in main function body statements")
                            return False, None
                        
                    start_idx = new_idx
                    
                    # Check for closing brace
                    if is_token(tokens, start_idx, '}'):
                        print("Found closing brace for main function")
                        # Important: Return False if no statements were found in the function body
                        if not check_statements:
                            print("Error: No statements found in main function")
                            output_text.insert(tk.END, f"Expected valid statements in main function\n")

                            return False, None
                        return True, start_idx + 1
                    else:
                        
                        print("Missing closing brace for main function")
                        output_text.insert(tk.END, f"Syntax Error: Expected closing brace '}}' for main function but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                
                # This is a user-defined function
                else:
                    # Check if we've already seen the main function - this is an error
                    if program.main_function_seen:
                        print("Error: User-defined functions must be declared before the main function")
                        output_text.insert(tk.END, f"Syntax Error: User-defined functions must be declared before the main function\n")
                        program.user_defined_function_error = True  # Mark that a user-defined function has an error
                        return False, None
                        
                    print("user defined function")
                    
                    # Call the user_defined_function method to parse the user-defined function
                    # This ensures that errors in user-defined functions are properly detected
                    return program.user_defined_function(tokens, start_idx)
    


    class conditional:
            @staticmethod
            def conditional_block(tokens, start_idx):
                print("<conditional_block>")
                current_token = tokens[start_idx] if start_idx < len(tokens) else None
                
                # Find which display line contains this token
                matching_line = None
                for line in display_lines:
                    if current_token in line["tokens"]:
                        matching_line = line
                        break
                
                # If we found a matching line, use its line number, otherwise fall back to get_line_number
                if matching_line:
                    line_number = matching_line["line_number"]
                    line_tokens = matching_line["tokens"]
                    line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])  # Format without spaces
                else:
                    line_number = get_line_number(tokens, start_idx)
                    line_tokens = []
                    line_text = ""
                        
                start_idx = skip_spaces(tokens, start_idx)
                
                # Parse the conditions base
                is_valid, new_idx = conditional.conditions_base(tokens, start_idx)
                if not is_valid:
                    # Get the token at start_idx to find its position in the original token list
                    current_token = tokens[start_idx] if start_idx < len(tokens) else None
                    
                    # Find which display line contains this token
                    matching_line = None
                    for line in display_lines:
                        if current_token in line["tokens"]:
                            matching_line = line
                            break
                    
                    # If we found a matching line, use its line number, otherwise fall back to get_line_number
                    if matching_line:
                        line_number = matching_line["line_number"]
                        line_tokens = matching_line["tokens"]
                        line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])  # Format without spaces
                    else:
                        line_number = get_line_number(tokens, start_idx)
                        line_tokens = []
                        line_text = ""
                        
                    # output_text.insert(tk.END, f"Syntax Error at line {line_number}: Invalid condition\n")
                    # output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    print(f"Error: Invalid conditions_base at index {start_idx}")
                    return False, None
                return True, new_idx
            
            @staticmethod
            def conditions_base(tokens, start_idx):
                # Get the token at start_idx to find its position in the original token list
                current_token = tokens[start_idx] if start_idx < len(tokens) else None
                    
                # Find which display line contains this token
                matching_line = None
                for line in display_lines:
                    if current_token in line["tokens"]:
                        matching_line = line
                        break
                    
                # If we found a matching line, use its line number, otherwise fall back to get_line_number
                if matching_line:
                    line_number = matching_line["line_number"]
                    line_tokens = matching_line["tokens"]
                    line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])  # Format without spaces
                else:
                    line_number = get_line_number(tokens, start_idx)
                    line_tokens = []
                    line_text = ""
                print("<conditions_base>")
                start_idx = skip_spaces(tokens, start_idx)
                
                # Parse first negation operator (optional)
                has_negation = False
                if start_idx < len(tokens) and tokens[start_idx][0] == '!':
                    print(f"Found negation operator '!' at index {start_idx}")
                    has_negation = True
                    start_idx += 1  # Move past '!'
                    start_idx = skip_spaces(tokens, start_idx)
                
                # Parse first condition value
                is_valid, new_idx = conditional.condition_value(tokens, start_idx)
                if not is_valid:
                    output_text.insert(tk.END, f"Syntax Error: Invalid condition value at line {get_line_number(tokens, start_idx)}\n")
                    print(f"Error: Invalid first condition_value at index {start_idx}")
                    return False, None
                
                start_idx = new_idx
                start_idx = skip_spaces(tokens, start_idx)
                
                has_array_stimuli = False
                if is_token(tokens, start_idx, '['):
                    has_array_stimuli = True
                    start_idx += 1  # Move past '['
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    # Check for array_stimuli_value (Identifier, doseliteral, or empty)
                    if start_idx < len(tokens) and tokens[start_idx][1] in ["Identifier", "numlit"]:
                        # We found a valid array_stimuli_value
                        start_idx += 1  # Move past the value
                    
                    # Skip spaces after the array_stimuli_value
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    # Check for closing bracket
                    if not is_token(tokens, start_idx, ']'):
                        print(f"Error: Expected closing bracket ']' at index {start_idx} (line {line_number})")
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected closing bracket ']' but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                    
                    start_idx += 1  # Move past ']'
                
                # Skip spaces after identifier or array stimuli
                start_idx = skip_spaces(tokens, start_idx)
                # Define relational operators
                relational_operators = {'<', '>', '<=', '>=', '==', '!='}
                logical_operators = {'&&', '||'}

                # Check if there's a conditional operator - REQUIRED
                if start_idx >= len(tokens) or not any(tokens[start_idx][0] in op_set for op_set in [logical_operators, relational_operators] for op in op_set):
                    # output_text.insert(tk.END, f"Syntax Error: Expected relational operator at line {get_line_number(tokens, start_idx)}\n")
                    print(f"Error: Expected relational operator at index {start_idx}, found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}")
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected relational operator but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                
                # Found a relational operator
                print(f"Found relational operator '{tokens[start_idx][0]}' at index {start_idx}")
                start_idx += 1  # Move past operator
                start_idx = skip_spaces(tokens, start_idx)
                
                # Parse second negation operator (optional)
                has_negation = False
                if start_idx < len(tokens) and tokens[start_idx][0] == '!':
                    print(f"Found negation operator '!' at index {start_idx}")
                    has_negation = True
                    start_idx += 1  # Move past '!'
                    start_idx = skip_spaces(tokens, start_idx)
                
                # Parse second condition value
                is_valid, new_idx = conditional.condition_value(tokens, start_idx)
                if not is_valid:
                    output_text.insert(tk.END, f"Syntax Error: Invalid condition value at line {get_line_number(tokens, start_idx)}\n")
                    print(f"Error: Invalid second condition_value at index {start_idx}")
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected conditional value\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                
                start_idx = new_idx
                start_idx = skip_spaces(tokens, start_idx)
                
                has_array_stimuli = False
                if is_token(tokens, start_idx, '['):
                    has_array_stimuli = True
                    start_idx += 1  # Move past '['
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    # Check for array_stimuli_value (Identifier, doseliteral, or empty)
                    if start_idx < len(tokens) and tokens[start_idx][1] in ["Identifier", "numlit"]:
                        # We found a valid array_stimuli_value
                        start_idx += 1  # Move past the value
                    
                    # Skip spaces after the array_stimuli_value
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    # Check for closing bracket
                    if not is_token(tokens, start_idx, ']'):
                        print(f"Error: Expected closing bracket ']' at index {start_idx} (line {line_number})")
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected closing bracket ']' but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                    
                    start_idx += 1  # Move past ']'
                
                # Skip spaces after identifier or array stimuli
                start_idx = skip_spaces(tokens, start_idx)
                # After processing the conditional operator and second value, check for logical operators
                is_valid, new_idx = conditional.condition_value_tail(tokens, start_idx)
                if not is_valid:
                    output_text.insert(tk.END, f"Syntax Error: Invalid condition at line {get_line_number(tokens, start_idx)}\n")
                    print(f"Error: Invalid condition_value_tail at index {start_idx}")
                    return False, None
                
                return True, new_idx
                    
            @staticmethod
            def condition_value(tokens, start_idx):
                # Get the token at start_idx to find its position in the original token list
                current_token = tokens[start_idx] if start_idx < len(tokens) else None
                    
                # Find which display line contains this token
                matching_line = None
                for line in display_lines:
                    if current_token in line["tokens"]:
                        matching_line = line
                        break
                    
                # If we found a matching line, use its line number, otherwise fall back to get_line_number
                if matching_line:
                    line_number = matching_line["line_number"]
                    line_tokens = matching_line["tokens"]
                    line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])  # Format without spaces
                else:
                    line_number = get_line_number(tokens, start_idx)
                    line_tokens = []
                    line_text = ""

                print("<condition_value>")
                start_idx = skip_spaces(tokens, start_idx)
                
                # Case 1: Parenthesized condition
                if start_idx < len(tokens) and tokens[start_idx][0] == '(':
                    print(f"Found opening parenthesis at index {start_idx}")
                    start_idx += 1  # Move past '('
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    # Parse the condition inside parentheses
                    is_valid, new_idx = conditional.conditions_base(tokens, start_idx)
                    if not is_valid:
                        output_text.insert(tk.END, f"Syntax Error: Invalid condition inside parentheses at line {get_line_number(tokens, start_idx)}\n")
                        print(f"Error: Invalid condition inside parentheses at index {start_idx}")
                        return False, None
                    
                    start_idx = new_idx
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    if not is_token(tokens, start_idx, ')'):
                        output_text.insert(tk.END, f"Syntax Error: Expected closing parenthesis at line {get_line_number(tokens, start_idx)}\n")
                        print(f"Error: Expected closing parenthesis at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                        return False, None
                    
                    print(f"Found closing parenthesis at index {start_idx}")
                    return True, start_idx + 1  # Move past ')'
                
                # Case 2: Identifier with possible array access
                if start_idx < len(tokens) and tokens[start_idx][1] == 'Identifier':
                    print(f"Found Identifier '{tokens[start_idx][0]}' at index {start_idx}")
                    current_idx = start_idx
                    start_idx += 1  # Move past identifier
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    # Handle array access
                    while start_idx < len(tokens) and tokens[start_idx][0] == '[':
                        start_idx += 1  # Move past '['
                        start_idx = skip_spaces(tokens, start_idx)
                        
                        # Parse array index (can be identifier or numlit)
                        if not (start_idx < len(tokens) and (tokens[start_idx][1] == "Identifier" or tokens[start_idx][1] == "numlit")):
                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Invalid array index\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None
                        
                        start_idx += 1  # Move past index
                        start_idx = skip_spaces(tokens, start_idx)
                        
                        # Check for closing bracket
                        if not (start_idx < len(tokens) and tokens[start_idx][0] == ']'):
                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected closing bracket\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None
                        
                        start_idx += 1  # Move past ']'
                        start_idx = skip_spaces(tokens, start_idx)
                    
                    # After array access, check if we need to parse arithmetic
                    if start_idx < len(tokens) and tokens[start_idx][0] in math_operator:
                        is_valid, new_idx = arithmetic.arithmetic_sequence(tokens, current_idx)
                        if is_valid:
                            return True, new_idx
                    
                    return True, start_idx
                
                # Case 3: Try to parse as an arithmetic sequence
                if start_idx < len(tokens) and (tokens[start_idx][1] == 'numlit' or tokens[start_idx][1] == 'Identifier'):
                    next_idx = start_idx + 1
                    next_idx = skip_spaces(tokens, next_idx)
                    if next_idx < len(tokens) and tokens[next_idx][0] in math_operator:
                        is_valid, new_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
                        if is_valid:
                            print(f"Found valid arithmetic sequence at index {start_idx}")
                            return True, new_idx
                
                # Case 4: Literals
                conliterals = {'numlit', 'string literal', 'dom', 'rec'}
                if start_idx < len(tokens) and tokens[start_idx][1] in conliterals:
                    print(f"Found literal '{tokens[start_idx][0]}' of type {tokens[start_idx][1]} at index {start_idx}")
                    return True, start_idx + 1  # Move past literal
                
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a condition value but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                print(f"Error: Expected condition value at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None

            @staticmethod
            def condition_value_tail(tokens, start_idx):
                """
                Parse condition value tail according to the CFG:
                <condition_value_tail> → <logical_operator><conditions_base><condition_value_tail>
                <condition_value_tail> → λ
                """
                print("<condition_value_tail>")
                start_idx = skip_spaces(tokens, start_idx)
                
                # Check for logical operators (&&, ||)
                logical_operators = {'&&', '||'}
                relational_operators = {'<', '>', '<=', '>=', '==', '!='}

                # If no logical operator is found, this is the empty (λ) case
                if start_idx >= len(tokens) or not any(tokens[start_idx][0] in op_set for op_set in logical_operators for op in op_set):
                    
                    # Check for semicolon if we're at the end of a statement
                    if start_idx < len(tokens) and tokens[start_idx][0] == ';':
                        print(f"Found semicolon at index {start_idx}")
                        return True, start_idx + 1  # Move past semicolon
                    
                    return True, start_idx  # Return current position
                
                # Found a logical operator
                print(f"Found logical operator '{tokens[start_idx][0]}' at index {start_idx}")
                start_idx += 1  # Move past logical operator
                start_idx = skip_spaces(tokens, start_idx)
                
                # Parse the next conditions_base
                is_valid, new_idx = conditional.conditions_base(tokens, start_idx)
                if not is_valid:
                    output_text.insert(tk.END, f"Syntax Error: Invalid condition after logical operator at line {get_line_number(tokens, start_idx)}\n")
                    print(f"Error: Invalid conditions_base after logical operator at index {start_idx}")
                    return False, None
                
                start_idx = new_idx
                start_idx = skip_spaces(tokens, start_idx)
                
                # Recursively parse more condition_value_tail
                return conditional.condition_value_tail(tokens, start_idx)
        
    class statements:
        @staticmethod
        def func_calling(tokens, start_idx):
            print(f"DEBUG SYNTAX: Starting function_calling at index {start_idx}")
            
            # Get the token at start_idx to find its position in the original token list
            current_token = tokens[start_idx] if start_idx < len(tokens) else None
                    
            # Find which display line contains this token
            matching_line = None
            for line in display_lines:
                if current_token in line["tokens"]:
                    matching_line = line
                    break
                    
            # If we found a matching line, use its line number, otherwise fall back to get_line_number
            if matching_line:
                line_number = matching_line["line_number"]
                line_tokens = matching_line["tokens"]
                line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])  # Format without spaces
            else:
                line_number = get_line_number(tokens, start_idx)
                line_tokens = []
                line_text = ""
                
            start_idx = skip_spaces(tokens, start_idx)

            # Ensure we have a valid identifier
            if not (start_idx < len(tokens) and is_token(tokens, start_idx, "Identifier")):
                print(f"Error: Expected identifier after 'func' at index {start_idx}")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier after 'func' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, start_idx

            func_name = tokens[start_idx]  # Store function name
            start_idx += 1  # Move past identifier
            start_idx = skip_spaces(tokens, start_idx)

            # Check if this is a function with parameters in parentheses
            if start_idx < len(tokens) and is_token(tokens, start_idx, "("):
                print(f"Found function with parameters: {func_name}")
                has_params = True
                start_idx += 1  # Move past '('
                start_idx = skip_spaces(tokens, start_idx)
                
                # Parse parameters
                is_valid, new_idx = parameters.func_params(tokens, start_idx)
                if not is_valid:
                    print(f"Error: Invalid parameters in function definition at index {start_idx}")
                    return False, start_idx
                
                start_idx = new_idx  # Update index after parsing parameters
                start_idx = skip_spaces(tokens, start_idx)
                
                # Check for closing parenthesis
                if not (start_idx < len(tokens) and is_token(tokens, start_idx, ")")):
                    print(f"Error: Expected ')' at index {start_idx}")
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing parenthesis\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, start_idx
                
                start_idx += 1  # Move past ')'
                start_idx = skip_spaces(tokens, start_idx)
            else:
                has_params = False

            # Check if this is a function assignment (either simple reassignment or with parameters)
            if start_idx < len(tokens) and is_token(tokens, start_idx, "="):
                print(f"Found function assignment for {func_name}")
                start_idx += 1  # Move past '='
                start_idx = skip_spaces(tokens, start_idx)

                # Ensure valid identifier after '='
                if not (start_idx < len(tokens) and is_token(tokens, start_idx, "Identifier")):
                    print(f"Error: Expected identifier after '=' at index {start_idx}")
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier after '=' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, start_idx

                assigned_func = tokens[start_idx]
                if has_params:
                    print(f"Valid parameterized function assignment: {func_name}() = {assigned_func}")
                else:
                    print(f"Valid function reassignment: {func_name} -> {assigned_func}")
                start_idx += 1  # Move past assigned identifier
                start_idx = skip_spaces(tokens, start_idx)
            elif has_params:
                # This is a function call with parameters but no assignment
                print(f"Valid function call with parameters: {func_name}()")
            else:
                # This is a bare function identifier with no parameters or assignment
                print(f"Valid function reference: {func_name}")

            # Check for semicolon at the end
            if not (start_idx < len(tokens) and is_token(tokens, start_idx, ";")):
                print(f"Error: Expected ';' at index {start_idx}")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a ';' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, start_idx

            print(f"Valid function statement: {func_name}")
            start_idx += 1  # Move past ';'
            return True, start_idx
        
        @staticmethod
        def if_statement(tokens, start_idx):
            # Get the token at start_idx to find its position in the original token list
            current_token = tokens[start_idx] if start_idx < len(tokens) else None
                    
            # Find which display line contains this token
            matching_line = None
            for line in display_lines:
                if current_token in line["tokens"]:
                    matching_line = line
                    break
                    
            # If we found a matching line, use its line number, otherwise fall back to get_line_number
            if matching_line:
                line_number = matching_line["line_number"]
                line_tokens = matching_line["tokens"]
                line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])  # Format without spaces
            else:
                line_number = get_line_number(tokens, start_idx)
                line_tokens = []
                line_text = ""

            if not is_token(tokens, start_idx, '('):
                print(f"Error: Expected '(' after 'if' at index {start_idx}")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an open parenthesis\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            start_idx += 1  # Move past '('
            start_idx = skip_spaces(tokens, start_idx)

            # Parse the condition using conditional_block
            is_valid, new_idx = conditional.conditional_block(tokens, start_idx)
            if not is_valid:
                print(f"Error: Invalid condition in if statement at index {start_idx}")
                # output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a conditional block\n")
                # output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

            start_idx = new_idx  # Move to next token
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, ')'):
                print(f"Error: Expected ')' at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'} in if statement")
                return False, None

            start_idx += 1  # Move past ')'
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, '{'):
                print(f"Error: Expected '{{' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None

            start_idx += 1  # Move past '{'
            start_idx = skip_spaces(tokens, start_idx)

            # Parse if body statements
            is_valid, new_idx = program.body_statements(tokens, start_idx)
            if not is_valid:
                return False, None
                        
            start_idx = new_idx
            start_idx = skip_spaces(tokens, start_idx)

            is_valid, new_idx = statements.inside_loop_statement(tokens, start_idx)
            if not is_valid:
                return False, None
                    
            start_idx = new_idx
            start_idx = skip_spaces(tokens, start_idx)
            
            # Ensure closing brace
            if not is_token(tokens, start_idx, '}'):
                print(f"Error: Expected '}}' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            
            start_idx += 1  # Move past '}'
            start_idx = skip_spaces(tokens, start_idx)

            # Process optional elif/else statements
            has_else = False
            
            while start_idx < len(tokens):
                if is_token(tokens, start_idx, 'elif'):
                    start_idx += 1  # Move past 'elif'
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    if not is_token(tokens, start_idx, '('):
                        print(f"Error: Expected '(' after 'elif' at index {start_idx}")
                        return False, None
                    
                    start_idx += 1  # Move past '('
                    start_idx = skip_spaces(tokens, start_idx)

                    is_valid, new_idx = conditional.conditional_block(tokens, start_idx)
                    if not is_valid:
                        print(f"Error: Invalid condition in if statement at index {start_idx}")
                        return False, None
                    
                    
                    start_idx = new_idx
                    start_idx = skip_spaces(tokens, start_idx)

                    if not is_token(tokens, start_idx, ')'):
                        print(f"Error: Expected ')' at index {start_idx} in elif statement")
                        return False, None
                    
                    start_idx += 1  # Move past ')'
                    start_idx = skip_spaces(tokens, start_idx)

                    if not is_token(tokens, start_idx, '{'):
                        print(f"Error: Expected '{{' after elif condition at index {start_idx}")
                        return False, None
                    
                    start_idx += 1  # Move past '{'
                    start_idx = skip_spaces(tokens, start_idx)

                    is_valid, new_idx = program.body_statements(tokens, start_idx)
                    if not is_valid:
                        return False, None
                    
                    start_idx = new_idx
                    start_idx = skip_spaces(tokens, start_idx)

                    is_valid, new_idx = statements.inside_loop_statement(tokens, start_idx)
                    if not is_valid:
                        return False, None
                    
                    start_idx = new_idx
                    start_idx = skip_spaces(tokens, start_idx)

                    if not is_token(tokens, start_idx, '}'):
                        print(f"Error: Expected '}}' at index {start_idx}")
                        return False, None
                    
                    start_idx += 1  # Move past '}'
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    # Continue to the next iteration to check for more elif/else
                    # No break here, so we'll continue the loop

                elif is_token(tokens, start_idx, 'else'):
                    if has_else:
                        print("Error: Multiple else statements are not allowed")
                        return False, None
                        
                    has_else = True
                    start_idx += 1  # Move past 'else'
                    start_idx = skip_spaces(tokens, start_idx)

                    if not is_token(tokens, start_idx, '{'):
                        print(f"Error: Expected '{{' after 'else' at index {start_idx}")
                        return False, None
                    
                    start_idx += 1  # Move past '{'
                    start_idx = skip_spaces(tokens, start_idx)

                    is_valid, new_idx = program.body_statements(tokens, start_idx)
                    if not is_valid:
                        return False, None
                    
                    start_idx = new_idx
                    start_idx = skip_spaces(tokens, start_idx)


                    if not is_token(tokens, start_idx, '}'):
                        print(f"Error: Expected '}}' at index {start_idx}")
                        return False, None
                    
                    start_idx += 1  # Move past '}'
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    # No more elif/else allowed after else
                    break

                else:
                    # No more elif or else, exit loop
                    break
            
            return True, start_idx  # Return success

        @staticmethod
        def inside_loop_statement(tokens, start_idx):
            print(f"DEBUG SYNTAX: Starting inside_loop_statement at index {start_idx}")
            start_idx = skip_spaces(tokens, start_idx)
            
            # Check if we have a contig statement
            if start_idx < len(tokens) and is_token(tokens, start_idx, "contig"):
                print("Found contig statement")
                start_idx += 1  # Move past 'contig'
                start_idx = skip_spaces(tokens, start_idx)
                
                # Check for semicolon
                if not is_token(tokens, start_idx, ";"):
                    print(f"Error: Expected ';' after 'contig' at index {start_idx}")
                    return False, start_idx
                
                start_idx += 1  # Move past ';'
                return True, start_idx
            
            # Check if we have a destroy statement
            elif start_idx < len(tokens) and is_token(tokens, start_idx, "destroy"):
                print("Found destroy statement")
                start_idx += 1  # Move past 'destroy'
                start_idx = skip_spaces(tokens, start_idx)
                
                # Check for semicolon
                if not is_token(tokens, start_idx, ";"):
                    print(f"Error: Expected ';' after 'destroy' at index {start_idx}")
                    return False, start_idx
                
                start_idx += 1  # Move past ';'
                return True, start_idx
            
            # If we don't have either, it's a lambda/empty production, which is also valid
            else:
                print(f"Empty inside_loop_statement (lambda) but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return True, start_idx
           
        @staticmethod
        def express_statement(tokens, start_idx):
            print("inside express")
            current_token = tokens[start_idx] if start_idx < len(tokens) else None
                    
            # Find which display line contains this token
            matching_line = None
            for line in display_lines:
                if current_token in line["tokens"]:
                    matching_line = line
                    break
                    
            # If we found a matching line, use its line number, otherwise fall back to get_line_number
            if matching_line:
                line_number = matching_line["line_number"]
                line_tokens = matching_line["tokens"]
                line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])  # Format without spaces
            else:
                line_number = get_line_number(tokens, start_idx)
                line_tokens = []
                line_text = ""

            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, '('):
                print(f"Error: Expected '(' at index {start_idx}")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an open parenthesis in express statement\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            start_idx += 1  # Move past '('
            start_idx = skip_spaces(tokens, start_idx)

            # Debug before parsing express_value
            print(f"Before calling express_value: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Parse express_value
            is_valid , new_idx = express.express_value(tokens, start_idx)
            if not is_valid:
                print(f"Error: Invalid expression at index {start_idx}")
                return False, None

            # Debug: What does express_value return?
            print(f"After express_value, new index: {new_idx}, token: {tokens[new_idx] if new_idx < len(tokens) else 'EOF'}")

            # Update start_idx properly (no extra increment)
            start_idx = new_idx  
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, ')'):
                print(f"Error: Expected ')' at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'} in express statement")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a ',', ')' or math op in express statement but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
                
            start_idx += 1 
            start_idx = skip_spaces(tokens, start_idx)   

            # Get the current line number and token for the semicolon check
            semicolon_token = tokens[start_idx] if start_idx < len(tokens) else None
            semicolon_line = None
            for line in display_lines:
                if semicolon_token in line["tokens"]:
                    semicolon_line = line
                    break
            
            if semicolon_line:
                semicolon_line_number = semicolon_line["line_number"]
                semicolon_line_text = ' '.join([t[0] for t in semicolon_line["tokens"] if t[1] != "space"])
            else:
                semicolon_line_number = get_line_number(tokens, start_idx)
                semicolon_line_text = semicolon_token[0] if semicolon_token else ""

            if is_token(tokens, start_idx, ';'):
                return True, start_idx + 1
            else:
                found_token = tokens[start_idx] if start_idx < len(tokens) else ('EOF', 'EOF')
                print(f"Error: Expected ';' at index {start_idx} (line {semicolon_line_number})")
                output_text.insert(tk.END, f"Syntax Error at line {semicolon_line_number}: Expected a semicolon in express statement but found {found_token}\n")
                output_text.insert(tk.END, f"Line {semicolon_line_number}: {semicolon_line_text}\n")
                return False, None

        @staticmethod
        def stimuli_statement(tokens, start_idx):
            """
            Parses a stimuli statement, ensuring it follows the correct syntax.
            Valid syntax:
            - VAR = stimuli("text");
            - VAR[index] = stimuli("text");
            - VAR = <expression>;
            - VAR[index] = <expression>;
            - VAR += <expression>;
            - VAR[index] += <expression>;
            - VAR -= <expression>;
            - VAR[index] -= <expression>;
            - VAR *= <expression>;
            - VAR[index] *= <expression>;
            - VAR /= <expression>;
            - VAR[index] /= <expression>;
            - VAR %= <expression>;
            - VAR[index] %= <expression>;
            """
            # Helper function to get line info for current token
            def get_current_line_info(idx):
                token = tokens[idx] if idx < len(tokens) else None
                line = None
                for l in display_lines:
                    if token in l["tokens"]:
                        line = l
                        break
                if line:
                    return line["line_number"], ' '.join([t[0] for t in line["tokens"] if t[1] != "space"])
                return get_line_number(tokens, idx), token[0] if token else ""

            start_idx = skip_spaces(tokens, start_idx)
            
            # Get current line number for error reporting
            line_number = get_line_number(tokens, start_idx)
            
            # Check for array index
            has_array_stimuli = False
            if is_token(tokens, start_idx, '['):
                has_array_stimuli = True
                start_idx += 1  # Move past '['
                start_idx = skip_spaces(tokens, start_idx)
                
                # Check for array index value (Identifier or numlit)
                if not (start_idx < len(tokens) and tokens[start_idx][1] in ["Identifier", "numlit"]):
                    line_num, line_txt = get_current_line_info(start_idx)
                    found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                    output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected array index but found {found_token}\n")
                    output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                    return False, None
                
                start_idx += 1  # Move past index value
                start_idx = skip_spaces(tokens, start_idx)
                
                # Check for closing bracket
                if not is_token(tokens, start_idx, ']'):
                    line_num, line_txt = get_current_line_info(start_idx)
                    found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                    output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected closing bracket ']' but found {found_token}\n")
                    output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                    return False, None
                
                start_idx += 1  # Move past ']'
                start_idx = skip_spaces(tokens, start_idx)
                
                # Check for optional second dimension index
                if is_token(tokens, start_idx, '['):
                    start_idx += 1  # Move past second '['
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    # Check for second array index value (Identifier or numlit)
                    if not (start_idx < len(tokens) and tokens[start_idx][1] in ["Identifier", "numlit"]):
                        line_num, line_txt = get_current_line_info(start_idx)
                        found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                        output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected second array index but found {found_token}\n")
                        output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                        return False, None
                    
                    start_idx += 1  # Move past second index value
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    # Check for closing bracket of second dimension
                    if not is_token(tokens, start_idx, ']'):
                        line_num, line_txt = get_current_line_info(start_idx)
                        found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                        output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected closing bracket ']' but found {found_token}\n")
                        output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                        return False, None
                    
                    start_idx += 1  # Move past second ']'
            
            # Skip spaces after identifier or array index
            start_idx = skip_spaces(tokens, start_idx)

            # Check for assignment operator
            if not any(is_token(tokens, start_idx, op) for op in assignment_op):
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected an assignment operator but found QPAL {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                return False, None
            
            # Move past assignment operator
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            
            # Check if this is a 'stimuli' call or a regular assignment
            if is_token(tokens, start_idx, 'stimuli'):
                start_idx += 1  # Move past 'stimuli'
                start_idx = skip_spaces(tokens, start_idx)
                return statements.parse_stimuli_call(tokens, start_idx, line_number)
            else:
                # Process as a regular assignment
                start_idx = skip_spaces(tokens, start_idx)
                return statements.assignment_statement(tokens, start_idx - 2)

        @staticmethod
        def parse_stimuli_call(tokens, start_idx, line_number):
            """
            Parses a valid stimuli call: stimuli("text");
            """

            current_token = tokens[start_idx] if start_idx < len(tokens) else None
                    
            # Find which display line contains this token
            matching_line = None
            for line in display_lines:
                if current_token in line["tokens"]:
                    matching_line = line
                    break
                    
            # If we found a matching line, use its line number, otherwise fall back to get_line_number
            if matching_line:
                line_number = matching_line["line_number"]
                line_tokens = matching_line["tokens"]
                line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])  # Format without spaces
            else:
                line_number = get_line_number(tokens, start_idx)
                line_tokens = []
                line_text = ""
            start_idx = skip_spaces(tokens, start_idx)

            # Check for opening parenthesis
            if not is_token(tokens, start_idx, '('):
                print(f"Error: Expected '(' at index {start_idx} (line {line_number})")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an open parenthesis but found {tokens[start_idx][0]}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            start_idx += 1  # Move past '('
            start_idx = skip_spaces(tokens, start_idx)
            
            # Check for string literal
            if not is_token(tokens, start_idx, 'string literal'):
                print(f"Error: Expected string literal at index {start_idx} (line {line_number})")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a string literal but found {tokens[start_idx][0]}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            start_idx += 1  # Move past string literal
            start_idx = skip_spaces(tokens, start_idx)
            
            # Check for closing parenthesis
            if not is_token(tokens, start_idx, ')'):
                print(f"Error: Expected ')' at index {start_idx} (line {line_number}) in stimuli call")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing parenthesis but found {tokens[start_idx][0]}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            start_idx += 1  # Move past ')'
            start_idx = skip_spaces(tokens, start_idx)
            
            # Check for semicolon
            if is_token(tokens, start_idx, ';'):
                return True, start_idx + 1
            else:
                print(f"Error: Expected ';' at index {start_idx} (line {line_number})")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a semicolon in stimuli call but found {tokens[start_idx][0]}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

    
        @staticmethod
        def assignment_statement(tokens, start_idx):
            # Helper function to get line info for current token
            def get_current_line_info(idx):
                token = tokens[idx] if idx < len(tokens) else None
                line = None
                for l in display_lines:
                    if token in l["tokens"]:
                        line = l
                        break
                if line:
                    return line["line_number"], ' '.join([t[0] for t in line["tokens"] if t[1] != "space"])
                return get_line_number(tokens, idx), token[0] if token else ""

            print(f"DEBUG SYNTAX: Starting assignment_statement at index {start_idx}")
            
            # Skip leading whitespace
            start_idx = skip_spaces(tokens, start_idx)
            
            # Check for assignment operator
            if not any(is_token(tokens, start_idx, op) for op in assignment_op):
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected an assignment operator but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                return False, start_idx

            # Move past assignment operator
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            
            # Directly go to assignment value handling
            is_valid, new_idx = statements.assignment_value(tokens, start_idx)
            if not is_valid:
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected a valid assignment value but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                return False, start_idx
            
            start_idx = new_idx  # Update index after parsing assignment value
            start_idx = skip_spaces(tokens, start_idx)  # Skip any spaces after the value
            
            # Handle multiple assignments (assignment_tail)
            while start_idx < len(tokens) and is_token(tokens, start_idx, ','):
                start_idx += 1  # Move past the comma
                start_idx = skip_spaces(tokens, start_idx)
                
                if not is_token(tokens, start_idx, 'Identifier'):
                    line_num, line_txt = get_current_line_info(start_idx)
                    found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                    output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected an Identifier but found {found_token}\n")
                    output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                    return False, None

                start_idx += 1  # Move past identifier
                start_idx = skip_spaces(tokens, start_idx)

                has_array_stimuli = False
                if is_token(tokens, start_idx, '['):
                    has_array_stimuli = True
                    start_idx += 1  # Move past '['
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    # Check for array_stimuli_value (Identifier, doseliteral, or empty)
                    if start_idx < len(tokens) and tokens[start_idx][1] == "Identifier":
                        start_idx += 1  # Move past the value
                    
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    if not is_token(tokens, start_idx, ']'):
                        line_num, line_txt = get_current_line_info(start_idx)
                        found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                        output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected closing bracket ']' but found {found_token}\n")
                        output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                        return False, None
                    
                    start_idx += 1  # Move past ']'
                    start_idx = skip_spaces(tokens, start_idx)

                if not any(is_token(tokens, start_idx, op) for op in assignment_op):
                    line_num, line_txt = get_current_line_info(start_idx)
                    found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                    output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected an assignment operator but found {found_token}\n")
                    output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                    return False, start_idx
                
                start_idx += 1  # Move past assignment operator
                start_idx = skip_spaces(tokens, start_idx)
                
                # Parse next assignment value
                is_valid, new_idx = statements.assignment_value(tokens, start_idx)
                if not is_valid:
                    line_num, line_txt = get_current_line_info(start_idx)
                    found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                    output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected a valid assignment value but found {found_token}\n")
                    output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                    return False, start_idx
                
                start_idx = new_idx
                start_idx = skip_spaces(tokens, start_idx)

            # Check for array access after the last value
            has_array_stimuli = False
            if is_token(tokens, start_idx, '['):
                has_array_stimuli = True
                start_idx += 1  # Move past '['
                start_idx = skip_spaces(tokens, start_idx)
                
                # Check for array_stimuli_value or slice syntax
                if start_idx < len(tokens):
                    # Check for slice syntax (::)
                    if is_token(tokens, start_idx, '::'):
                        start_idx += 1  # Move past '::'
                        start_idx = skip_spaces(tokens, start_idx)
                        
                        # Check for step value after ::
                        if start_idx < len(tokens) and tokens[start_idx][1] == "numlit":
                            start_idx += 1  # Move past the step value
                        
                    # Regular array_stimuli_value (Identifier or numlit)
                    elif tokens[start_idx][1] in ["Identifier", "numlit"]:
                        start_idx += 1  # Move past the value
                
                start_idx = skip_spaces(tokens, start_idx)
                
                if not is_token(tokens, start_idx, ']'):
                    line_num, line_txt = get_current_line_info(start_idx)
                    found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                    output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected closing bracket ']' but found {found_token}\n")
                    output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                    return False, None
                
                start_idx += 1  # Move past ']'
                start_idx = skip_spaces(tokens, start_idx)

            # Check for semicolon at the end
            if not is_token(tokens, start_idx, ';'):
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected a semicolon in assignment but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                return False, start_idx
            
            start_idx += 1  # Move past semicolon
            return True, start_idx
                            
        @staticmethod
        def for_loop_statement(tokens, start_idx):
            # Get the token at start_idx to find its position in the original token list
            current_token = tokens[start_idx] if start_idx < len(tokens) else None
                
            # Find which display line contains this token
            matching_line = None
            for line in display_lines:
                if current_token in line["tokens"]:
                    matching_line = line
                    break
                
            # If we found a matching line, use its line number, otherwise fall back to get_line_number
            if matching_line:
                line_number = matching_line["line_number"]
                line_tokens = matching_line["tokens"]
                line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])  # Format without spaces
            else:
                line_number = get_line_number(tokens, start_idx)
                line_tokens = []
                line_text = ""

            print(f"DEBUG SYNTAX: Starting for_loop_statement at index {start_idx}")
            print(f"DEBUG SYNTAX: Current tokens: {tokens[start_idx:start_idx+5] if start_idx < len(tokens) else 'end of tokens'}")

            # Skip leading whitespace
            start_idx = skip_spaces(tokens, start_idx)

            # Helper function to get line info for current token
            def get_current_line_info(idx):
                token = tokens[idx] if idx < len(tokens) else None
                line = None
                for l in display_lines:
                    if token in l["tokens"]:
                        line = l
                        break
                if line:
                    return line["line_number"], ' '.join([t[0] for t in line["tokens"] if t[1] != "space"])
                return get_line_number(tokens, idx), token[0] if token else ""

            # Check for opening parenthesis '('
            if not (start_idx < len(tokens) and tokens[start_idx][0] == '('):
                print(f"ERROR: Expected '(' at index {start_idx}")
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected an open parenthesis but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                return False, start_idx
            start_idx += 1  # Move past '('

            start_idx = skip_spaces(tokens, start_idx)

            # **Initialization Parsing**
            if not (start_idx < len(tokens) and tokens[start_idx][0] == 'dose'):
                print(f"ERROR: Expected 'dose' for initialization at index {start_idx}")
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected dose keyword but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                return False, start_idx
            start_idx += 1  # Move past 'dose'

            start_idx = skip_spaces(tokens, start_idx)

            # Check for identifier after 'dose'
            if not (start_idx < len(tokens) and tokens[start_idx][1] == "Identifier"):
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected an Identifier but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                return False, start_idx
            start_idx += 1  # Move past Identifier

            start_idx = skip_spaces(tokens, start_idx)

            # Expect '=' after Identifier
            if not (start_idx < len(tokens) and tokens[start_idx][0] == '='):
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected an equal sign but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                return False, start_idx
            start_idx += 1  # Move past '='

            start_idx = skip_spaces(tokens, start_idx)

            # Initialization value (must be dose literal or Identifier)
            if not (start_idx < len(tokens) and tokens[start_idx][1] in ["Identifier", "numlit"]):
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected Identifier or Numlit but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                return False, start_idx
            start_idx += 1  # Move past init_value

            start_idx = skip_spaces(tokens, start_idx)

            # Check for semicolon (end of initialization)
            if not (start_idx < len(tokens) and tokens[start_idx][0] == ";"):
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected semicolon but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                return False, start_idx
            start_idx += 1  # Move past ';'

            start_idx = skip_spaces(tokens, start_idx)

            # Check for identifier in condition
            if not (start_idx < len(tokens) and tokens[start_idx][1] == "Identifier"):
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected an Identifier but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                return False, start_idx
            start_idx += 1  # Move past Identifier

            start_idx = skip_spaces(tokens, start_idx)

            # Check for conditional operator
            if start_idx >= len(tokens) or tokens[start_idx][0] not in conditional_op:
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected a conditional operator but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_txt}\n")
                return False, start_idx
            start_idx += 1  # Move past conditional operator

            start_idx = skip_spaces(tokens, start_idx)

            # Parse arithmetic sequence for condition value
            is_valid, new_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
            if not is_valid:
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected a valid arithmetic sequence but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                return False, None

            start_idx = new_idx
            start_idx = skip_spaces(tokens, start_idx)

            # Check for semicolon after condition
            if not (start_idx < len(tokens) and tokens[start_idx][0] == ";"):
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected a semicolon in for loop but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                return False, start_idx

            start_idx += 1  # Move past ';'
            start_idx = skip_spaces(tokens, start_idx)

            # Check for identifier or unary operator in update expression
            if not (start_idx < len(tokens) and (tokens[start_idx][1] == "Identifier" or tokens[start_idx][0] in ['++', '--'])):
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected Identifier or unary operator but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                return False, start_idx

            # Handle pre/post increment/decrement
            if tokens[start_idx][1] == "Identifier":
                # Store the identifier token for error reporting
                identifier_token = tokens[start_idx]
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                
                # Get line info for the operator position
                operator_token = tokens[start_idx] if start_idx < len(tokens) else None
                operator_line = None
                for line in display_lines:
                    if operator_token in line["tokens"]:
                        operator_line = line
                        break
                
                if operator_line:
                    operator_line_number = operator_line["line_number"]
                    operator_line_text = ' '.join([t[0] for t in operator_line["tokens"] if t[1] != "space"])
                else:
                    operator_line_number = get_line_number(tokens, start_idx)
                    operator_line_text = operator_token[0] if operator_token else ""

                if not (start_idx < len(tokens) and tokens[start_idx][0] in ['++', '--']):
                    found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                    output_text.insert(tk.END, f"Syntax Error at line {operator_line_number}: Expected increment/decrement operator but found {found_token}\n")
                    output_text.insert(tk.END, f"Line {operator_line_number}: {operator_line_text}\n")
                    return False, start_idx
                start_idx += 1
            else:
                # Pre-increment/decrement case
                operator_token = tokens[start_idx]
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                
                # Get line info for the identifier position
                identifier_token = tokens[start_idx] if start_idx < len(tokens) else None
                identifier_line = None
                for line in display_lines:
                    if identifier_token in line["tokens"]:
                        identifier_line = line
                        break
                
                if identifier_line:
                    identifier_line_number = identifier_line["line_number"]
                    identifier_line_text = ' '.join([t[0] for t in identifier_line["tokens"] if t[1] != "space"])
                else:
                    identifier_line_number = get_line_number(tokens, start_idx)
                    identifier_line_text = identifier_token[0] if identifier_token else ""

                if not (start_idx < len(tokens) and tokens[start_idx][1] == "Identifier"):
                    found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                    output_text.insert(tk.END, f"Syntax Error at line {identifier_line_number}: Expected an Identifier but found {found_token}\n")
                    output_text.insert(tk.END, f"Line {identifier_line_number}: {identifier_line_text}\n")
                    return False, start_idx
                start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)

            # Check for closing parenthesis
            if not (start_idx < len(tokens) and tokens[start_idx][0] == ')'):
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected closing parenthesis for for loop but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                return False, None

            start_idx += 1  # Move past ')'
            start_idx = skip_spaces(tokens, start_idx)

            # Check for opening brace
            if not (start_idx < len(tokens) and tokens[start_idx][0] == '{'):
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected '{{' but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

            start_idx += 1  # Move past '{'
            start_idx = skip_spaces(tokens, start_idx)

            # Parse if body statements
            is_valid, new_idx = program.body_statements(tokens, start_idx)
            if not is_valid:
                return False, None
                        
            start_idx = new_idx
            
            # Ensure closing brace
            if not (start_idx < len(tokens) and tokens[start_idx][0] == '}'):
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected '}}' but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                return False, None
            
            start_idx += 1  # Move past '}'
            return True, start_idx

        @staticmethod
        def prod_statement(tokens, start_idx):
            print("inside prod_statement")

            current_token = tokens[start_idx] if start_idx < len(tokens) else None
                
            # Find which display line contains this token
            matching_line = None
            for line in display_lines:
                if current_token in line["tokens"]:
                    matching_line = line
                    break
                
            # If we found a matching line, use its line number, otherwise fall back to get_line_number
            if matching_line:
                line_number = matching_line["line_number"]
                line_tokens = matching_line["tokens"]
                line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])  # Format without spaces
            else:
                line_number = get_line_number(tokens, start_idx)
                line_tokens = []
                line_text = ""

            # Check if we have just "prod" followed immediately by ";"
            start_idx = skip_spaces(tokens, start_idx)
            if start_idx < len(tokens) and is_token(tokens, start_idx, ';'):
                print(f"Error: Expected ';' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected ';'\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                print(f"Valid empty prod statement at index {start_idx}")
                return True, start_idx + 1  # End of statement
            
            # Otherwise, try to parse a value
            is_valid, new_idx = statements.prod_value(tokens, start_idx)
            if not is_valid:
                print(f"Error: Invalid arithmetic expression at index {start_idx}")
                return False, None

            # Make sure we're using the updated index returned from prod_value
            start_idx = new_idx
            start_idx = skip_spaces(tokens, start_idx)

            # Now, check if the statement properly ends with ';'
            if start_idx < len(tokens) and is_token(tokens, start_idx, ';'):
                print(f"Valid prod statement (ends with ';') at index {start_idx}")
                return True, start_idx + 1  # End of statement

            print(f"Error: Expected literal at prod statement, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected ';'\n")
            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
            return False, None

        @staticmethod
        def prod_value(tokens, start_idx):
            # output_text.insert(tk.END, "<prod_value>➜")
            start_idx = skip_spaces(tokens, start_idx)
            
            # Check for empty prod value (this will be handled at the prod_statement level)
            if start_idx >= len(tokens) or is_token(tokens, start_idx, ';'):
                print("Empty prod value")
                return True, start_idx
            
            # Check for '' (empty string) token
            if is_token(tokens, start_idx, literals) or is_token(tokens, start_idx, ''):
                print(f"Simple literal or identifier at index {start_idx}")
                return True, start_idx + 1  # Move past the literal or identifier
            
            # Try to parse as an arithmetic sequence first
            is_valid, new_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
            if is_valid:
                print(f"ARITH PROD - Successfully parsed arithmetic sequence, new index: {new_idx}")
                return True, new_idx
            
            # Define a list of valid keywords/tokens
            valid_tokens = ['Identifier', 'dom', 'rec', 'ff']
            
            # Check if it's a simple literal
            if is_token(tokens, start_idx, literals):
                print(f"Simple literal at index {start_idx}")
                return True, start_idx + 1  # Move past the literal
            
            # Check if it's one of our valid tokens
            for token in valid_tokens:
                if is_token(tokens, start_idx, token):
                    print(f"{token} token at index {start_idx}")
                    return True, start_idx + 1  # Move past the token
            
            # If we get here, the token is neither a valid arithmetic sequence nor a literal/identifier/keyword
            print(f"Invalid token at index {start_idx}: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            return False, start_idx

        @staticmethod
        def assignment_value(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)

            # Check if the current token is a literal or identifier
            if is_token(tokens, start_idx, literals) or is_token(tokens, start_idx, 'Identifier'):
                # Look ahead to see if the next token is a math_operator
                next_idx = start_idx + 1
                next_idx = skip_spaces(tokens, next_idx)
                
                if next_idx < len(tokens) and any(is_token(tokens, next_idx, op) for op in math_operator):
                    print("ARITH PROD - Starting with literal or identifier")
                    # If the next token is a math_operator, try to parse as an arithmetic sequence
                    is_valid, new_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
                    if is_valid:
                        start_idx = new_idx
                        return True, start_idx
                    else:
                        # If arithmetic sequence parsing fails, fall back to treating it as a simple literal/identifier
                        print("Arithmetic sequence parsing failed, falling back to simple literal/identifier")
                
                # If there's no math operator following, or if arithmetic sequence parsing failed,
                # treat it as a simple literal or identifier
                start_idx += 1  # Move past the literal or identifier
                return True, start_idx
            
            # Try to parse as an arithmetic sequence that might start with something other than a literal or identifier
            is_valid, new_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
            if is_valid:
                print("ARITH PROD - Starting with non-literal/non-identifier")
                start_idx = new_idx
                return True, start_idx
            
            # If we get here, the token is neither a literal, an identifier, nor the start of an arithmetic sequence
            return False, None

        @staticmethod
        def do_while_statement(tokens, start_idx):
            print("<do_while_statement>")
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After initial skip_spaces, start_idx={start_idx}, token={tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            
            
            # Check for opening brace
            if not is_token(tokens, start_idx, '{'):
                print(f"DEBUG SYNTAX: Expected '{{' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            
            # Move past opening brace
            start_idx += 1
            print(f"DEBUG SYNTAX: After opening brace, start_idx={start_idx}")
            
            # Parse if body statements
            is_valid, new_idx = program.body_statements(tokens, start_idx)
            if not is_valid:
                return False, None
                        
            
            start_idx = new_idx
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After body statements, start_idx={start_idx}, token={tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            
            # Check for closing brace
            if not is_token(tokens, start_idx, '}'):
                print(f"DEBUG SYNTAX: Expected '}}' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            
            # Move past closing brace
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After closing brace, start_idx={start_idx}, token={tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            
            # Check for 'while' keyword
            if not is_token(tokens, start_idx, 'while'):
                print(f"DEBUG SYNTAX: Expected 'while' keyword but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            
            # Move past 'while' keyword
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After 'while' keyword, start_idx={start_idx}, token={tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            
            # Check for opening parenthesis
            if not is_token(tokens, start_idx, '('):
                print(f"DEBUG SYNTAX: Expected '(' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            
            # Move past opening parenthesis
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After opening parenthesis, start_idx={start_idx}, token={tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            
            # Parse condition
            is_valid, new_idx = conditional.conditional_block(tokens, start_idx)
            if not is_valid or new_idx is None:
                print(f"DEBUG SYNTAX: Invalid condition at index {start_idx}")
                return False, None
            
            start_idx = new_idx
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After condition, start_idx={start_idx}, token={tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            
            # Check for closing parenthesis
            if not is_token(tokens, start_idx, ')'):
                print(f"DEBUG SYNTAX: Expected ')' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'} in do-while statement")
                return False, None
            
            # Move past closing parenthesis
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After closing parenthesis, start_idx={start_idx}, token={tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            
            # Check for semicolon
            if is_token(tokens, start_idx, ';'):
                start_idx += 1  # Move past semicolon
                print(f"DEBUG SYNTAX: After semicolon, start_idx={start_idx}")
            
            print(f"DEBUG SYNTAX: Successfully parsed do-while statement, returning True, {start_idx}")
            return True, start_idx
  
        @staticmethod
        def while_statement(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, '('):
                print(f"Error: Expected '(' after 'while' at index {start_idx}")
                return False, None
            start_idx += 1  # Move past '('
            
            # Parse the condition using conditional_block
            is_valid, new_idx = conditional.conditional_block(tokens, start_idx)
            if not is_valid:
                print(f"Error: Invalid condition in while statement at index {start_idx}")
                return False, None

            start_idx = new_idx  # Move to next token
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, ')'):
                print(f"Error: Expected ')' at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'} in while statement")
                return False, None

            start_idx += 1  # Move past ')'
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, '{'):
                print(f"Error: Expected '{{' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None

            start_idx += 1  # Move past '{'
            start_idx = skip_spaces(tokens, start_idx)

            # Parse if body statements
            is_valid, new_idx = program.body_statements(tokens, start_idx)
            if not is_valid:
                return False, None
                        

            start_idx = new_idx
            
            # Ensure closing brace
            if not is_token(tokens, start_idx, '}'):
                print(f"Error: Expected '}}' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            
            return True, start_idx + 1
    
    class variables:
        @staticmethod
        def validate_doseval(tokens, start_idx):
            # Get the token at start_idx to find its position in the original token list
            current_token = tokens[start_idx] if start_idx < len(tokens) else None

            # Find which display line contains this token
            matching_line = None
            for line in display_lines:
                if current_token in line["tokens"]:
                    matching_line = line
                    break

            # If we found a matching line, use its line number, otherwise fall back to get_line_number
            if matching_line:
                line_number = matching_line["line_number"]
                line_tokens = matching_line["tokens"]
                line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])  # Format without spaces
            else:
                line_number = get_line_number(tokens, start_idx)
                line_tokens = []
                line_text = ""

            start_idx = skip_spaces(tokens, start_idx)

            # First identifier check
            if not is_token(tokens, start_idx, 'Identifier'):
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            while True:
                # Check if it's an assignment (now optional)
                if is_token(tokens, start_idx, '='):
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    # Always try to parse as an arithmetic sequence first
                    if is_token(tokens, start_idx, 'numlit'):
                        # Validate the number format only if not part of an arithmetic sequence
                        next_idx = start_idx + 1
                        next_idx = skip_spaces(tokens, next_idx)
                        
                        if next_idx < len(tokens) and any(is_token(tokens, next_idx, op) for op in math_operator):
                            # If the next token is a math_operator, try to parse as an arithmetic sequence
                            is_valid, new_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
                            if is_valid:
                                start_idx = new_idx
                            else:
                                # If arithmetic sequence parsing fails, check number sign and use the numlit
                                number_sign = check_number_sign(tokens[start_idx])
                                if number_sign in {"quantval", "nequantliteral"}:
                                    # Update line number tracking for the error message
                                    current_token = tokens[start_idx] if start_idx < len(tokens) else None
                                    matching_line = None
                                    for line in display_lines:
                                        if current_token in line["tokens"]:
                                            matching_line = line
                                            break
                                    if matching_line:
                                        line_number = matching_line["line_number"]
                                        line_tokens = matching_line["tokens"]
                                        line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])
                                    else:
                                        line_number = get_line_number(tokens, start_idx)
                                        line_tokens = []
                                        line_text = ""
                                    
                                    output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected a dose value but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                                    return False, None
                                start_idx += 1
                        else:
                            # If the next token is not a math_operator, check number sign and use the numlit
                            number_sign = check_number_sign(tokens[start_idx])
                            if number_sign in {"quantval", "nequantliteral"}:
                                # Update line number tracking for the error message
                                current_token = tokens[start_idx] if start_idx < len(tokens) else None
                                matching_line = None
                                for line in display_lines:
                                    if current_token in line["tokens"]:
                                        matching_line = line
                                        break
                                if matching_line:
                                    line_number = matching_line["line_number"]
                                    line_tokens = matching_line["tokens"]
                                    line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])
                                else:
                                    line_number = get_line_number(tokens, start_idx)
                                    line_tokens = []
                                    line_text = ""
                                
                                output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected a dose value but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                                return False, None
                            start_idx += 1
                    elif is_token(tokens, start_idx, 'Identifier'):
                        # Get the token at start_idx to find its position in the original token list
                        current_token = tokens[start_idx] if start_idx < len(tokens) else None

                        # Find which display line contains this token
                        matching_line = None
                        for line in display_lines:
                            if current_token in line["tokens"]:
                                matching_line = line
                                break

                        # If we found a matching line, use its line number, otherwise fall back to get_line_number
                        if matching_line:
                            line_number = matching_line["line_number"]
                            line_tokens = matching_line["tokens"]
                            line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])  # Format without spaces
                        else:
                            line_number = get_line_number(tokens, start_idx)
                            line_tokens = []
                            line_text = ""

                        # Look ahead to see if the next token is a math_operator
                        next_idx = start_idx + 1
                        next_idx = skip_spaces(tokens, next_idx)
                        
                        if next_idx < len(tokens) and any(is_token(tokens, next_idx, op) for op in math_operator):
                            # If the next token is a math_operator, try to parse as an arithmetic sequence
                            is_valid, new_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
                            if is_valid:
                                start_idx = new_idx
                            else:
                                # If arithmetic sequence parsing fails, just use the identifier
                                start_idx += 1
                        else:
                            # If the next token is not a math_operator, just use the identifier
                            start_idx += 1
                    else:
                        # Update line number tracking for the error message
                        current_token = tokens[start_idx] if start_idx < len(tokens) else None
                        matching_line = None
                        for line in display_lines:
                            if current_token in line["tokens"]:
                                matching_line = line
                                break
                        if matching_line:
                            line_number = matching_line["line_number"]
                            line_tokens = matching_line["tokens"]
                            line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])
                        else:
                            line_number = get_line_number(tokens, start_idx)
                            line_tokens = []
                            line_text = ""
                        
                        output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected a dose value but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                                            
                    start_idx = skip_spaces(tokens, start_idx)
                
                # Now check for either a semicolon (end of statement) or comma (more assignments)
                if is_token(tokens, start_idx, ';'):
                    return True, start_idx + 1
                
                if not is_token(tokens, start_idx, ','):
                    output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected a comma, math op or semicolon but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                
                # Move past comma
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                
                # Next identifier
                if not is_token(tokens, start_idx, 'Identifier'):
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                start_idx += 1
                
                start_idx = skip_spaces(tokens, start_idx)

        @staticmethod
        def validate_seqval(tokens, start_idx):
            # Get the token at start_idx to find its position in the original token list
            current_token = tokens[start_idx] if start_idx < len(tokens) else None

            # Find which display line contains this token
            matching_line = None
            for line in display_lines:
                if current_token in line["tokens"]:
                    matching_line = line
                    break

            # If we found a matching line, use its line number, otherwise fall back to get_line_number
            if matching_line:
                line_number = matching_line["line_number"]
                line_tokens = matching_line["tokens"]
                line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])  # Format without spaces
            else:
                line_number = get_line_number(tokens, start_idx)
                line_tokens = []
                line_text = ""

            start_idx = skip_spaces(tokens, start_idx)

            # First identifier check
            if not is_token(tokens, start_idx, 'Identifier'):
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            while True:
                # Check if it's an assignment (now optional)
                if is_token(tokens, start_idx, '='):
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    # Check for dom or rec
                    if is_token(tokens, start_idx, 'string literal'):
                        start_idx += 1
                    else:
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected string literal but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                                        
                    start_idx = skip_spaces(tokens, start_idx)
                
                # Now check for either a semicolon (end of statement) or comma (more assignments)
                if is_token(tokens, start_idx, ';'):
                    return True, start_idx + 1
                
                if not is_token(tokens, start_idx, ','):
                    output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected a comma, math op or semicolon but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                
                # Move past comma
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                
                # Next identifier
                if not is_token(tokens, start_idx, 'Identifier'):
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                start_idx += 1
                
                start_idx = skip_spaces(tokens, start_idx)

                        
        @staticmethod
        def validate_alleleval(tokens, start_idx):
            # Get the token at start_idx to find its position in the original token list
            current_token = tokens[start_idx] if start_idx < len(tokens) else None

            # Find which display line contains this token
            matching_line = None
            for line in display_lines:
                if current_token in line["tokens"]:
                    matching_line = line
                    break

            # If we found a matching line, use its line number, otherwise fall back to get_line_number
            if matching_line:
                line_number = matching_line["line_number"]
                line_tokens = matching_line["tokens"]
                line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])  # Format without spaces
            else:
                line_number = get_line_number(tokens, start_idx)
                line_tokens = []
                line_text = ""

            start_idx = skip_spaces(tokens, start_idx)

            # First identifier check
            if not is_token(tokens, start_idx, 'Identifier'):
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            while True:
                # Check if it's an assignment (now optional)
                if is_token(tokens, start_idx, '='):
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    # Check for dom or rec
                    if is_token(tokens, start_idx, 'dom'):
                        start_idx += 1
                    elif is_token(tokens, start_idx, 'rec'):
                        start_idx += 1

                    else:
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected dom, rec or numlit but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                                        
                    start_idx = skip_spaces(tokens, start_idx)
                
                # Now check for either a semicolon (end of statement) or comma (more assignments)
                if is_token(tokens, start_idx, ';'):
                    return True, start_idx + 1
                
                if not is_token(tokens, start_idx, ','):
                    output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected a comma, math op or semicolon but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                
                # Move past comma
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                
                # Next identifier
                if not is_token(tokens, start_idx, 'Identifier'):
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                start_idx += 1
                
                start_idx = skip_spaces(tokens, start_idx)

        @staticmethod
        def validate_quantval(tokens, start_idx):
                    # Get the token at start_idx to find its position in the original token list
                    current_token = tokens[start_idx] if start_idx < len(tokens) else None
                    
                    # Find which display line contains this token
                    matching_line = None
                    for line in display_lines:
                        if current_token in line["tokens"]:
                            matching_line = line
                            break
                    
                    # If we found a matching line, use its line number, otherwise fall back to get_line_number
                    if matching_line:
                        line_number = matching_line["line_number"]
                        line_tokens = matching_line["tokens"]
                        line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])  # Format without spaces
                    else:
                        line_number = get_line_number(tokens, start_idx)
                        line_tokens = []
                        line_text = ""
                    start_idx = skip_spaces(tokens, start_idx)

                    # First identifier check
                    if not is_token(tokens, start_idx, 'Identifier'):
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                    
                    start_idx += 1
                    
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    while True:
                        # Check if it's an assignment (now optional)
                        if is_token(tokens, start_idx, '='):
                            start_idx += 1
                            start_idx = skip_spaces(tokens, start_idx)
                            
                            # Always try to parse as an arithmetic sequence first
                            if is_token(tokens, start_idx, 'numlit'):
                                # Validate the number format only if not part of an arithmetic sequence
                                next_idx = start_idx + 1
                                next_idx = skip_spaces(tokens, next_idx)
                                
                                if next_idx < len(tokens) and any(is_token(tokens, next_idx, op) for op in math_operator):
                                    # If the next token is a math_operator, try to parse as an arithmetic sequence
                                    is_valid, new_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
                                    if is_valid:
                                        start_idx = new_idx
                                    else:
                                        # If arithmetic sequence parsing fails, check number sign and use the numlit
                                        number_sign = check_number_sign(tokens[start_idx])
                                        if number_sign in {"doseliteral", "neliteral"}:
                                            output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected a quant value\n")
                                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                                            return False, None
                                        start_idx += 1
                                else:
                                    # If the next token is not a math_operator, check number sign and use the numlit
                                    number_sign = check_number_sign(tokens[start_idx])
                                    if number_sign in {"doseliteral", "neliteral"}:
                                        output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected a quant value\n")
                                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                                        return False, None
                                    start_idx += 1
                            elif is_token(tokens, start_idx, 'Identifier'):
                                # Look ahead to see if the next token is a math_operator
                                next_idx = start_idx + 1
                                next_idx = skip_spaces(tokens, next_idx)
                                
                                if next_idx < len(tokens) and any(is_token(tokens, next_idx, op) for op in math_operator):
                                    # If the next token is a math_operator, try to parse as an arithmetic sequence
                                    is_valid, new_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
                                    if is_valid:
                                        start_idx = new_idx
                                    else:
                                        # If arithmetic sequence parsing fails, just use the identifier
                                        start_idx += 1
                                else:
                                    # If the next token is not a math_operator, just use the identifier
                                    start_idx += 1
                            else:
                                output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected a quant value but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                                return False, None
                                                    
                            start_idx = skip_spaces(tokens, start_idx)
                        
                        current_token = tokens[start_idx] if start_idx < len(tokens) else None
                        
                        # Find which display line contains this token
                        matching_line = None
                        for line in display_lines:
                            if current_token in line["tokens"]:
                                matching_line = line
                                break
                        
                        # If we found a matching line, use its line number, otherwise fall back to get_line_number
                        if matching_line:
                            line_number = matching_line["line_number"]
                            line_tokens = matching_line["tokens"]
                            line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])  # Format without spaces
                        else:
                            line_number = get_line_number(tokens, start_idx)
                            line_tokens = []
                            line_text = ""

                        # Now check for either a semicolon (end of statement) or comma (more assignments)
                        if is_token(tokens, start_idx, ';'):
                            return True, start_idx + 1
                        
                        if not is_token(tokens, start_idx, ','):
                            output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected a comma, math op or semicolon but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None
                        
                        # Move past comma
                        start_idx += 1
                        start_idx = skip_spaces(tokens, start_idx)
                        
                        # Next identifier
                        if not is_token(tokens, start_idx, 'Identifier'):
                            return False, None
                        start_idx += 1
                        
                        start_idx = skip_spaces(tokens, start_idx)

    class clust:
        @staticmethod
        def validate_clust_quantval(tokens, start_idx):
            # Get the token at start_idx to find its position in the original token list
            current_token = tokens[start_idx] if start_idx < len(tokens) else None
            
            # Find which display line contains this token
            matching_line = None
            for line in display_lines:
                if current_token in line["tokens"]:
                    matching_line = line
                    break
            
            # If we found a matching line, use its line number, otherwise fall back to get_line_number
            if matching_line:
                line_number = matching_line["line_number"]
                line_tokens = matching_line["tokens"]
                line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])  # Format without spaces
            else:
                line_number = get_line_number(tokens, start_idx)
                line_tokens = []
                line_text = ""
            print('<clust_quantval>')
            start_idx = skip_spaces(tokens, start_idx)

            # Check for identifier
            if not is_token(tokens, start_idx, 'Identifier'):
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            # Check for opening bracket
            if not is_token(tokens, start_idx, '['):
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an open bracket but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            # Check for dimension size
            if not is_token(tokens, start_idx, 'numlit'):
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a number but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            
                # Verify the number is a dose literal
            number_sign = check_number_sign(tokens[start_idx])
            if number_sign in {"quantval", "nequantliteral"}:
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a dose value but found {tokens[start_idx][0]}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            # Check for closing bracket
            if not is_token(tokens, start_idx, ']'):
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing bracket but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            # Check for second dimension (optional)
            if is_token(tokens, start_idx, '['):
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                if not is_token(tokens, start_idx, 'numlit'):
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a number but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                
                # Verify the number is a dose literal
                number_sign = check_number_sign(tokens[start_idx])
                if number_sign in {"quantval", "nequantliteral"}:
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a dose value but found {tokens[start_idx][0]}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                if not is_token(tokens, start_idx, ']'):
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing bracket but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

            # Check for initialization (optional)
            if is_token(tokens, start_idx, '='):
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                # Check for opening brace
                if not is_token(tokens, start_idx, '{'):
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an opening brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                # Parse array values
                if is_token(tokens, start_idx, '{'):
                    # 2D array
                    while True:
                        if not is_token(tokens, start_idx, '{'):
                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an opening brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None
                        start_idx += 1
                        start_idx = skip_spaces(tokens, start_idx)

                        # Parse inner array
                        while True:
                            if not is_token(tokens, start_idx, 'numlit'):
                                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a number but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                                return False, None
                            
                            # Verify the number is a dose literal
                            number_sign = check_number_sign(tokens[start_idx])
                            if number_sign in {"neliteral", "doseliteral"}:
                                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a dose value but found {tokens[start_idx][0]}\n")
                                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                                return False, None
                            
                            start_idx += 1
                            start_idx = skip_spaces(tokens, start_idx)

                            if is_token(tokens, start_idx, ','):
                                start_idx += 1
                                start_idx = skip_spaces(tokens, start_idx)
                            elif is_token(tokens, start_idx, '}'):
                                start_idx += 1
                                break
                            else:
                                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                                return False, None

                        start_idx = skip_spaces(tokens, start_idx)

                        if is_token(tokens, start_idx, ','):
                            start_idx += 1
                            start_idx = skip_spaces(tokens, start_idx)
                        elif is_token(tokens, start_idx, '}'):
                            start_idx += 1
                            break
                        else:
                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None
                else:
                    # 1D array
                    while True:
                        if not is_token(tokens, start_idx, 'numlit'):
                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a number but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None
                        
                        # Verify the number is a dose literal
                        number_sign = check_number_sign(tokens[start_idx])
                        if number_sign in {"neliteral", "doseliteral"}:
                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a dose value but found {tokens[start_idx][0]}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None
                        start_idx += 1
                        start_idx = skip_spaces(tokens, start_idx)

                        if is_token(tokens, start_idx, ','):
                            start_idx += 1
                            start_idx = skip_spaces(tokens, start_idx)
                        elif is_token(tokens, start_idx, '}'):
                            start_idx += 1
                            break
                        else:
                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None

            # Check for semicolon
            if not is_token(tokens, start_idx, ';'):
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a semicolon but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

            return True, start_idx + 1

        @staticmethod
        def validate_clust_doseval(tokens, start_idx):
            # Get the token at start_idx to find its position in the original token list
            current_token = tokens[start_idx] if start_idx < len(tokens) else None
            
            # Find which display line contains this token
            matching_line = None
            for line in display_lines:
                if current_token in line["tokens"]:
                    matching_line = line
                    break
            
            # If we found a matching line, use its line number, otherwise fall back to get_line_number
            if matching_line:
                line_number = matching_line["line_number"]
                line_tokens = matching_line["tokens"]
                line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])  # Format without spaces
            else:
                line_number = get_line_number(tokens, start_idx)
                line_tokens = []
                line_text = ""

            print('<clust_dose>')
            start_idx = skip_spaces(tokens, start_idx)

            # Check for identifier
            if not is_token(tokens, start_idx, 'Identifier'):
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            # Check for opening bracket
            if not is_token(tokens, start_idx, '['):
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an open bracket but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            # Check for dimension size
            if not is_token(tokens, start_idx, 'numlit'):
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a number but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

            # Verify the number is a dose literal
            number_sign = check_number_sign(tokens[start_idx])
            if number_sign in {"quantval", "nequantliteral"}:
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a dose value but found {tokens[start_idx][0]}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            # Check for closing bracket
            if not is_token(tokens, start_idx, ']'):
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing bracket but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            # Check for second dimension (optional)
            if is_token(tokens, start_idx, '['):
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                if not is_token(tokens, start_idx, 'numlit'):
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a number but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None

                # Verify the second dimension is also a dose literal
                number_sign = check_number_sign(tokens[start_idx])
                if number_sign in {"quantval", "nequantliteral"}:
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a dose value but found {tokens[start_idx][0]}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None

                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                if not is_token(tokens, start_idx, ']'):
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing bracket but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

            # Check for initialization (optional)
            if is_token(tokens, start_idx, '='):
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                # Check for opening brace
                if not is_token(tokens, start_idx, '{'):
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an opening brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                # Parse array values
                if is_token(tokens, start_idx, '{'):
                    # 2D array
                    while True:
                        if not is_token(tokens, start_idx, '{'):
                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an opening brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None
                        start_idx += 1
                        start_idx = skip_spaces(tokens, start_idx)

                        # Parse inner array
                        while True:
                            if not is_token(tokens, start_idx, 'numlit'):
                                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a number but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                                return False, None

                            # Verify array value is a dose literal
                            number_sign = check_number_sign(tokens[start_idx])
                            if number_sign in {"quantval", "nequantliteral"}:
                                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a dose value but found {tokens[start_idx][0]}\n")
                                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                                return False, None

                            start_idx += 1
                            start_idx = skip_spaces(tokens, start_idx)

                            if is_token(tokens, start_idx, ','):
                                start_idx += 1
                                start_idx = skip_spaces(tokens, start_idx)
                            elif is_token(tokens, start_idx, '}'):
                                start_idx += 1
                                break
                            else:
                                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                                return False, None

                        start_idx = skip_spaces(tokens, start_idx)

                        if is_token(tokens, start_idx, ','):
                            start_idx += 1
                            start_idx = skip_spaces(tokens, start_idx)
                        elif is_token(tokens, start_idx, '}'):
                            start_idx += 1
                            break
                        else:
                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None
                else:
                    # 1D array
                    while True:
                        if not is_token(tokens, start_idx, 'numlit'):
                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a number but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None

                        # Verify array value is a dose literal
                        number_sign = check_number_sign(tokens[start_idx])
                        if number_sign in {"quantval", "nequantliteral"}:
                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a dose value but found {tokens[start_idx][0]}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None

                        start_idx += 1
                        start_idx = skip_spaces(tokens, start_idx)

                        if is_token(tokens, start_idx, ','):
                            start_idx += 1
                            start_idx = skip_spaces(tokens, start_idx)
                        elif is_token(tokens, start_idx, '}'):
                            start_idx += 1
                            break
                        else:
                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None

            # Check for semicolon
            if not is_token(tokens, start_idx, ';'):
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a semicolon but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

            return True, start_idx + 1

        @staticmethod
        def validate_clust_seqval(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After initial skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Helper function to get the current line number and text
            def get_current_line_info(idx):
                current_token = tokens[idx] if idx < len(tokens) else None
                
                # Find which display line contains this token
                matching_line = None
                for line in display_lines:
                    if current_token in line["tokens"]:
                        matching_line = line
                        break
                        
                # If we found a matching line, use its line number, otherwise fall back to get_line_number
                if matching_line:
                    line_number = matching_line["line_number"]
                    line_tokens = matching_line["tokens"]
                    line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])  # Format without spaces
                else:
                    line_number = get_line_number(tokens, idx)
                    line_tokens = []
                    line_text = ""
                
                return line_number, line_text

            # Get initial line info
            line_number, line_text = get_current_line_info(start_idx)

            # Check for identifier
            if not is_token(tokens, start_idx, 'Identifier'):
                print(f"DEBUG SYNTAX: Expected Identifier at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            print(f"DEBUG SYNTAX: Found Identifier: {tokens[start_idx]}")
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check for opening bracket
            if not is_token(tokens, start_idx, '['):
                print(f"DEBUG SYNTAX: Expected '[' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an open bracket\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            print(f"DEBUG SYNTAX: Found opening bracket")
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check for dimension size
            if not is_token(tokens, start_idx, 'numlit'):
                print(f"DEBUG SYNTAX: Expected numlit at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a number\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

            literal = tokens[start_idx]
            number_sign = check_number_sign(literal)
            print(f"DEBUG SYNTAX: Found numlit: {literal}, number_sign: {number_sign}")
            
            if number_sign not in {'doseliteral'}:
                print(f"DEBUG SYNTAX: Invalid number sign: {number_sign}, expected 'doseliteral'")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a dose value\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check for closing bracket
            if not is_token(tokens, start_idx, ']'):
                print(f"DEBUG SYNTAX: Expected ']' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing bracket\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            print(f"DEBUG SYNTAX: Found closing bracket")
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check for second dimension (optional)
            if is_token(tokens, start_idx, '['):
                print(f"DEBUG SYNTAX: Found second dimension opening bracket")
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                print(f"DEBUG SYNTAX: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

                if not is_token(tokens, start_idx, 'numlit') or check_number_sign(tokens[start_idx]) != "doseliteral":
                    print(f"DEBUG SYNTAX: Expected numlit with doseliteral at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a dose value\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                print(f"DEBUG SYNTAX: Found second dimension size: {tokens[start_idx]}")
                start_idx += 1

                start_idx = skip_spaces(tokens, start_idx)
                print(f"DEBUG SYNTAX: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                
                if not is_token(tokens, start_idx, ']'):
                    print(f"DEBUG SYNTAX: Expected ']' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing bracket\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                print(f"DEBUG SYNTAX: Found second dimension closing bracket")
                start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check for initialization (now optional)
            if is_token(tokens, start_idx, '='):
                print(f"DEBUG SYNTAX: Found equals sign, parsing initialization")
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                # Check for opening brace
                if not is_token(tokens, start_idx, '{'):
                    print(f"DEBUG SYNTAX: Expected '{{' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an opening brace\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                print(f"DEBUG SYNTAX: Found opening brace")
                start_idx += 1

                start_idx = skip_spaces(tokens, start_idx)
                print(f"DEBUG SYNTAX: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

                # Check what type of array we're dealing with
                if is_token(tokens, start_idx, '{'):
                    print(f"DEBUG SYNTAX: Detected 2D array (nested braces)")
                    # Handle 2D array case (nested braces)
                    while True:
                        if is_token(tokens, start_idx, '{'):
                            print(f"DEBUG SYNTAX: Found inner opening brace")
                            start_idx += 1
                            start_idx = skip_spaces(tokens, start_idx)
                            print(f"DEBUG SYNTAX: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

                            while True:
                                if not is_token(tokens, start_idx, 'string literal'):
                                    print(f"DEBUG SYNTAX: Expected string literal at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a string literal but found {tokens[start_idx][0]}\n")
                                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                                    return False, None

                                start_idx += 1

                                start_idx = skip_spaces(tokens, start_idx)
                                print(f"DEBUG SYNTAX: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

                                if is_token(tokens, start_idx, ','):
                                    print(f"DEBUG SYNTAX: Found comma in inner array")
                                    start_idx += 1
                                    start_idx = skip_spaces(tokens, start_idx)
                                    print(f"DEBUG SYNTAX: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                                elif is_token(tokens, start_idx, '}'):
                                    print(f"DEBUG SYNTAX: Found inner closing brace")
                                    start_idx += 1
                                    break
                                else:
                                    print(f"DEBUG SYNTAX: Expected ',' or '}}' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a comma or closing brace but found {tokens[start_idx][0]}\n")
                                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                                    return False, None

                            start_idx = skip_spaces(tokens, start_idx)
                            print(f"DEBUG SYNTAX: After inner array, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

                            if is_token(tokens, start_idx, ','):
                                print(f"DEBUG SYNTAX: Found comma after inner array")
                                start_idx += 1
                                start_idx = skip_spaces(tokens, start_idx)
                                print(f"DEBUG SYNTAX: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                            elif is_token(tokens, start_idx, '}'):
                                print(f"DEBUG SYNTAX: Found outer closing brace")
                                start_idx += 1
                                break
                            else:
                                print(f"DEBUG SYNTAX: Expected ',' or '}}' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a comma or closing brace but found {tokens[start_idx][0]}\n")
                                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                                return False, None
                        else:
                            print(f"DEBUG SYNTAX: Expected '{{' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an opening brace but found {tokens[start_idx][0]}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None
                else:
                    print(f"DEBUG SYNTAX: Detected 1D array (direct values)")
                    # Handle 1D array case (direct values)
                    while True:
                        if not is_token(tokens, start_idx, 'string literal'):
                            print(f"DEBUG SYNTAX: Expected string literal at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a string literal but found {tokens[start_idx][0]}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None

                        start_idx += 1

                        start_idx = skip_spaces(tokens, start_idx)
                        print(f"DEBUG SYNTAX: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

                        if is_token(tokens, start_idx, ','):
                            print(f"DEBUG SYNTAX: Found comma in array")
                            start_idx += 1
                            start_idx = skip_spaces(tokens, start_idx)
                            print(f"DEBUG SYNTAX: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                        elif is_token(tokens, start_idx, '}'):
                            print(f"DEBUG SYNTAX: Found closing brace")
                            start_idx += 1
                            break
                        else:
                            print(f"DEBUG SYNTAX: Expected ',' or '}}' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a comma or closing brace but found {tokens[start_idx][0]}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None

            # Check for semicolon (required whether there's initialization or not)
            if not is_token(tokens, start_idx, ';'):
                print(f"DEBUG SYNTAX: Expected ';' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a semicolon but found {tokens[start_idx][0]}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            print(f"DEBUG SYNTAX: Found semicolon, array declaration complete")

            return True, start_idx + 1


    class parameters:
        @staticmethod
        def parse_params(tokens, start_idx):
            print("Parsing parameters...")
            current_token = tokens[start_idx] if start_idx < len(tokens) else None
            
            # Find which display line contains this token
            matching_line = None
            for line in display_lines:
                if current_token in line["tokens"]:
                    matching_line = line
                    break
            
            # If we found a matching line, use its line number, otherwise fall back to get_line_number
            if matching_line:
                line_number = matching_line["line_number"]
                line_tokens = matching_line["tokens"]
                line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])  # Format without spaces
            else:
                line_number = get_line_number(tokens, start_idx)
                line_tokens = []
                line_text = ""
            param_types = {"dose", "quant", "seq", "allele"}
            params = []
            start_idx = skip_spaces(tokens, start_idx)

            # Check if we have a valid parameter type
            if start_idx >= len(tokens) or tokens[start_idx][0] not in param_types:
                print(f"No parameters found at index {start_idx}.")
                return True, [], start_idx

            if tokens[start_idx][0] == ")":
                print(f"No parameters found at index {start_idx}.")
                return True, [], start_idx
            
            while start_idx < len(tokens):
                # Check if the current token is a valid parameter type
                if tokens[start_idx][0] not in param_types:
                    print(f"Error: Expected parameter type at index {start_idx}, found {tokens[start_idx]}")
                    output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected an data type\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None, start_idx

                param_type = tokens[start_idx][0]
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                # Check if Identifier follows the parameter type
                if start_idx >= len(tokens) or tokens[start_idx][1] != "Identifier":
                    print(f"Error: Expected Identifier after parameter type '{param_type}' at index {start_idx}")
                    output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected an Identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None, start_idx

                param_id = tokens[start_idx][0]
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                params.append((param_type, param_id))
                print(f"Added parameter: ({param_type}, {param_id})")

                if start_idx < len(tokens) and is_token(tokens, start_idx, ','):
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)
                else:
                    break

            print(f"Completed parsing parameters: {params}")
            return True, params, start_idx

        @staticmethod
        def func_params(tokens, start_idx):
            print(">> Parsing func parameters...")
            print(f"Initial start index: {start_idx}")
            print(f"Token at start index: {tokens[start_idx] if start_idx < len(tokens) else 'None'}")

            current_token = tokens[start_idx] if start_idx < len(tokens) else None
            
            # Find which display line contains this token
            matching_line = None
            for line in display_lines:
                if current_token in line["tokens"]:
                    matching_line = line
                    break
            
            # If we found a matching line, use its line number, otherwise fall back to get_line_number
            if matching_line:
                line_number = matching_line["line_number"]
                line_tokens = matching_line["tokens"]
                line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])  # Format without spaces
                print(f"Matched display line found at line {line_number}: {line_text}")
            else:
                line_number = get_line_number(tokens, start_idx)
                line_tokens = []
                line_text = ""
                print(f"No matching display line found. Falling back to get_line_number: {line_number}")

            start_idx = skip_spaces(tokens, start_idx)
            print(f"Index after skipping initial spaces: {start_idx}")

            if start_idx < len(tokens) and tokens[start_idx][0] == ")":
                print(f"Empty Parameter List")
                return True, start_idx
            
            if start_idx >= len(tokens):
                print(f">> No parameters found at index {start_idx}.")
                return True, start_idx

            while start_idx < len(tokens):
                print(f"Processing parameter at index: {start_idx}")

                # Check if the current token is an identifier or numlit
                if tokens[start_idx][1] == "Identifier" or tokens[start_idx][1] == "numlit":
                    print(f"Parameter value detected: {tokens[start_idx][0]}")
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)
                    print(f"Index after skipping spaces post-value: {start_idx}")
                else:
                    print(f">> ERROR: Expected identifier or number at index {start_idx}")
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier or numlit but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, start_idx

                if start_idx < len(tokens) and is_token(tokens, start_idx, ','):
                    print("Comma detected, moving to next parameter.")
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)
                else:
                    print("No comma found, assuming end of parameter list.")
                    break

            print(f">> Completed parsing parameters")
            return True, start_idx

    class arithmetic:
        @staticmethod
        def arithmetic_sequence(tokens, start_idx):
            current_token = tokens[start_idx] if start_idx < len(tokens) else None
            
            # Find which display line contains this token
            matching_line = None
            for line in display_lines:
                if current_token in line["tokens"]:
                    matching_line = line
                    break
            
            # If we found a matching line, use its line number, otherwise fall back to get_line_number
            if matching_line:
                line_number = matching_line["line_number"]
                line_tokens = matching_line["tokens"]
                line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])
            else:
                line_number = get_line_number(tokens, start_idx)
                line_tokens = []
                line_text = ""

            print("In arithmetic sequence")
            
            # First, try to parse a single arithmetic value
            is_valid, new_idx = arithmetic.arithmetic_value(tokens, start_idx)
            if not is_valid:    
                return False, start_idx
            
            start_idx = new_idx
            
            # Then try to parse the rest of the sequence (if any)
            is_valid, new_idx = arithmetic.arithmetic_sequence_tail(tokens, start_idx)
            if not is_valid:
                print(f"ERROR: Expected valid arithmetic sequence tail at index {start_idx}")
                return False, start_idx
            
            return True, new_idx

        @staticmethod
        def arithmetic_value(tokens, start_idx):
            current_token = tokens[start_idx] if start_idx < len(tokens) else None
            
            # Find which display line contains this token
            matching_line = None
            for line in display_lines:
                if current_token in line["tokens"]:
                    matching_line = line
                    break
            
            # If we found a matching line, use its line number, otherwise fall back to get_line_number
            if matching_line:
                line_number = matching_line["line_number"]
                line_tokens = matching_line["tokens"]
                line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])
            else:
                line_number = get_line_number(tokens, start_idx)
                line_tokens = []
                line_text = ""

            start_idx = skip_spaces(tokens, start_idx)
            
            if start_idx >= len(tokens):
                print(f"ERROR: Expected token at index {start_idx}, but reached end of input")
                return False, start_idx
            
            # Check for parenthesized expression
            if is_token(tokens, start_idx, '('):
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                
                # Parse the sub-expression
                is_valid, new_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
                if not is_valid:
                    return False, start_idx
                
                start_idx = new_idx
                start_idx = skip_spaces(tokens, start_idx)
                
                # Check for closing parenthesis
                if is_token(tokens, start_idx, ')'):
                    return True, start_idx + 1
                else:
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing parenthesis\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, start_idx
            
            # Check for seq_type_cast
            elif is_token(tokens, start_idx, 'seq'):
                is_valid, cast_value, new_idx = express.seq_type_cast(tokens, start_idx)
                if is_valid:
                    return True, new_idx
                return False, start_idx
            
            # Check for literal or identifier
            elif is_token(tokens, start_idx, 'numlit') or is_token(tokens, start_idx, 'Identifier') or \
                 is_token(tokens, start_idx, 'string literal') or is_token(tokens, start_idx, 'dom') or \
                 is_token(tokens, start_idx, 'rec'):
                return True, start_idx + 1
            

            return False, start_idx

        @staticmethod
        def arithmetic_sequence_tail(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)

            # Check for end of sequence
            if start_idx >= len(tokens) or is_token(tokens, start_idx, ')'):
                return True, start_idx

            # Check for math operator
            if start_idx < len(tokens) and any(is_token(tokens, start_idx, op) for op in (math_operator | conditional_op)):
                operator = tokens[start_idx][0]
                operator_idx = start_idx + 1
                operator_idx = skip_spaces(tokens, operator_idx)

                # Parse the next arithmetic value
                is_valid, new_idx = arithmetic.arithmetic_value(tokens, operator_idx)
                if not is_valid:
                    return False, start_idx

                start_idx = new_idx

                # Parse the rest of the sequence (if any)
                return arithmetic.arithmetic_sequence_tail(tokens, start_idx)

            # If no math operator, this is now OK
            return True, start_idx

    class express:
        @staticmethod
        def express_value(tokens, start_idx):
            current_token = tokens[start_idx] if start_idx < len(tokens) else None
                    
            # Find which display line contains this token
            matching_line = None
            for line in display_lines:
                if current_token in line["tokens"]:
                    matching_line = line
                    break
                    
            # If we found a matching line, use its line number, otherwise fall back to get_line_number
            if matching_line:
                line_number = matching_line["line_number"]
                line_tokens = matching_line["tokens"]
                line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])  # Format without spaces
            else:
                line_number = get_line_number(tokens, start_idx)
                line_tokens = []
                line_text = ""
            print("<express_value>")
            
            exp_literals = {'string literal', 'numlit', 'Identifier', 'dom', 'rec'}
            values = []  # To store parsed literal values
            print(f"Initial start_idx: {start_idx}")
            
            start_idx = skip_spaces(tokens, start_idx)
            print(f"After skipping spaces, start_idx: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            
            # Check if we should parse a seq_type_cast first
            if start_idx < len(tokens) and is_token(tokens, start_idx, 'seq'):
                print("Found 'seq' keyword, parsing as seq_type_cast")
                is_valid, cast_value, next_idx = express.seq_type_cast(tokens, start_idx)
                if is_valid and cast_value:  # Only proceed if we got a valid cast value
                    print(f"Successfully parsed seq_type_cast: {cast_value}")
                    
                    # Check if the next token is a '+' operator
                    lookahead_idx = skip_spaces(tokens, next_idx)
                    if lookahead_idx < len(tokens) and tokens[lookahead_idx][0] == "+":
                        print("Found 'seq' followed by '+', parsing as seq_concat")
                        # We need to handle this as a concatenation
                        # First, we'll parse the seq function call
                        start_idx = skip_spaces(tokens, start_idx)
                        is_valid, concat_value, next_idx = express.seq_concat(tokens, start_idx)
                        if not is_valid:
                            print("Failed to parse seq_concat")
                            return False, start_idx
                        
                        # Successfully parsed a concatenation expression
                        values.append(concat_value)
                        start_idx = next_idx
                    else:
                        # Just a regular seq function call
                        values.append(cast_value)
                        start_idx = next_idx
                else:
                    print("Failed to parse seq_type_cast")
                    print("Syntax Error: Expected valid sequence type")
                    # Continue to other parsing options
            
            elif start_idx < len(tokens) and tokens[start_idx][1] == 'Identifier':
                # Get the identifier
                identifier = tokens[start_idx][0]
                print(f"Found identifier: {identifier}")
                
                # Move past the identifier
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                
                # Check for array access (express_value_id_tail)
                if start_idx < len(tokens) and tokens[start_idx][0] == '[':
                    print("Found '[', parsing as express_value_id_tail")
                    is_valid, id_tail_value, next_idx = express.express_value_id_tail(tokens, start_idx, identifier)
                    if not is_valid:
                        print("Failed to parse express_value_id_tail")
                        print("Syntax Error: Expected valid array index")
                        return False, start_idx
                    
                    values.append(id_tail_value)
                    start_idx = next_idx
                else:
                    # Just a regular identifier
                    values.append(identifier)

            # Try to parse an arithmetic sequence
            elif start_idx < len(tokens) and is_token(tokens, start_idx, 'numlit'):
                lookahead_idx = skip_spaces(tokens, start_idx + 1)
                if lookahead_idx < len(tokens) and tokens[lookahead_idx][0] == "+":  # Check for + operator
                    print("Found 'numlit' followed by '+', trying to parse as arithmetic sequence")
                    # First try arithmetic sequence
                    is_valid, next_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
                    if is_valid:
                        print("Successfully parsed arithmetic sequence")
                        # We don't have a specific value to append since arithmetic_sequence doesn't return one
                        # Just update the start_idx to continue parsing
                        start_idx = next_idx
                    else:
                        # Fall back to seq_concat if arithmetic sequence fails
                        print("Failed to parse arithmetic sequence, trying seq_concat")
                        is_valid, concat_value, next_idx = express.seq_concat(tokens, start_idx)
                        if not is_valid:
                            print("Failed to parse seq_concat")
                            return False, start_idx
                            
                        # Successfully parsed a concatenation expression
                        values.append(concat_value)
                        start_idx = next_idx
                else:
                    # Just a regular literal
                    values.append(tokens[start_idx][0])  # Store the literal value (first element)
                    print(f"Added '{tokens[start_idx][0]}' to values: {values}")
                    start_idx += 1  # Move past the literal
            
            # Check if we should parse a seq_concat
            # We need to look ahead to see if there's a '+' after a literal
            elif start_idx < len(tokens) and is_token(tokens, start_idx, 'string literal'):
                lookahead_idx = skip_spaces(tokens, start_idx + 1)
                if lookahead_idx < len(tokens) and tokens[lookahead_idx][0] == "+":
                    print("Found 'string literal' followed by '+', parsing as seq_concat")
                    is_valid, concat_value, next_idx = express.seq_concat(tokens, start_idx)
                    if not is_valid:
                        print("Failed to parse seq_concat")
                        print("Syntax Error: Expected plus sign")
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a plus sign\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, start_idx
                        
                    # Successfully parsed a concatenation expression
                    values.append(concat_value)
                    start_idx = next_idx
                else:
                    # Just a regular literal
                    values.append(tokens[start_idx][0])  # Store the literal value (first element)
                    print(f"Added '{tokens[start_idx][0]}' to values: {values}")
                    start_idx += 1  # Move past the literal
            # Fixed: Correctly handle token structure where the second element is the token type
            elif start_idx < len(tokens) and tokens[start_idx][1] in exp_literals:
                # Regular literal case
                values.append(tokens[start_idx][0])  # Store the literal value (first element)
                print(f"Added '{tokens[start_idx][0]}' to values: {values}")
                start_idx += 1  # Move past the literal
            else:
                print(f"Error: Expected a literal or seq type cast at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                print("Syntax Error: Expected a literal or sequence type")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a literal but found {tokens[start_idx][0]}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, start_idx  # Return failure
            
            # Now handle the express_value_tail (comma-separated values)
            start_idx = skip_spaces(tokens, start_idx)
            
            # Parse express_value_tail (handling comma-separated values)
            while start_idx < len(tokens) and (is_token(tokens, start_idx, ',') or is_token(tokens, start_idx, '+')):               
                
                start_idx += 1  # Move past the comma
                print(f"Moved past comma, new start_idx: {start_idx}")
                
                start_idx = skip_spaces(tokens, start_idx)
                print(f"After skipping spaces, start_idx: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                
                # Check if we have a seq_type_cast after the comma
                if start_idx < len(tokens) and is_token(tokens, start_idx, 'seq'):
                    print("Found 'seq' keyword after comma, parsing as seq_type_cast")
                    is_valid, cast_value, next_idx = express.seq_type_cast(tokens, start_idx)
                    if is_valid and cast_value:  # Only proceed if we got a valid cast value
                        print(f"Successfully parsed seq_type_cast after comma: {cast_value}")
                        
                        # Check if the next token is a '+' operator
                        lookahead_idx = skip_spaces(tokens, next_idx)
                        if lookahead_idx < len(tokens) and tokens[lookahead_idx][0] == "+":
                            print("Found 'seq' followed by '+' after comma, parsing as seq_concat")
                            # We need to handle this as a concatenation
                            # First, we'll parse the seq function call
                            start_idx = skip_spaces(tokens, start_idx)
                            is_valid, concat_value, next_idx = express.seq_concat(tokens, start_idx)
                            if not is_valid:
                                print("Failed to parse seq_concat after comma")
                                print("Syntax Error: Expected plus sign")
                                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a plus sign\n")
                                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                                return False, start_idx
                            
                            # Successfully parsed a concatenation expression
                            values.append(concat_value)
                            start_idx = next_idx
                            continue
                        else:
                            # Just a regular seq function call
                            values.append(cast_value)
                            start_idx = next_idx
                            continue
                    else:
                        print("Failed to parse seq_type_cast after comma")
                        print("Syntax Error: Expected valid sequence type")
                        return False, start_idx
                
                # Try to parse an arithmetic sequence after the comma
                elif start_idx < len(tokens) and is_token(tokens, start_idx, 'numlit'):
                    lookahead_idx = skip_spaces(tokens, start_idx + 1)
                    if lookahead_idx < len(tokens) and tokens[lookahead_idx][0] == "+":  # Check for + operator
                        print("Found 'numlit' followed by '+' after comma, trying to parse as arithmetic sequence")
                        # First try arithmetic sequence
                        is_valid, next_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
                        if is_valid:
                            print("Successfully parsed arithmetic sequence after comma")
                            # We don't have a specific value to append since arithmetic_sequence doesn't return one
                            # Just update the start_idx to continue parsing
                            start_idx = next_idx
                            continue
                        else:
                            # Fall back to seq_concat if arithmetic sequence fails
                            print("Failed to parse arithmetic sequence after comma, trying seq_concat")
                            is_valid, concat_value, next_idx = express.seq_concat(tokens, start_idx)
                            if not is_valid:
                                print("Failed to parse seq_concat after comma")
                                print("Syntax Error: Expected plus sign")
                                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a plus sign\n")
                                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                                return False, start_idx
                                
                            # Successfully parsed a concatenation expression
                            values.append(concat_value)
                            start_idx = next_idx
                            continue
                    else:
                        # Just a regular literal
                        values.append(tokens[start_idx][0])  # Store the literal value
                        print(f"Added '{tokens[start_idx][0]}' to values: {values}")
                        start_idx += 1  # Move past the literal
                        continue
                
                # Check if we have a seq_concat after the comma
                elif start_idx < len(tokens) and is_token(tokens, start_idx, 'string literal'):
                    lookahead_idx = skip_spaces(tokens, start_idx + 1)
                    if lookahead_idx < len(tokens) and tokens[lookahead_idx][0] == "+":
                        print("Found 'string literal' followed by '+' after comma, parsing as seq_concat")
                        is_valid, concat_value, next_idx = express.seq_concat(tokens, start_idx)
                        if not is_valid:
                            print("Failed to parse seq_concat after comma")
                            print("Syntax Error: Expected plus sign")
                            return False, start_idx
                            
                        # Successfully parsed a concatenation expression
                        values.append(concat_value)
                        start_idx = next_idx
                        continue
                    else:
                        # Just a regular literal
                        values.append(tokens[start_idx][0])  # Store the literal value
                        print(f"Added '{tokens[start_idx][0]}' to values: {values}")
                        start_idx += 1  # Move past the literal
                        continue
                
                # Regular literal after comma
                # Fixed: Check the second element of the token tuple against exp_literals
                if start_idx >= len(tokens) or tokens[start_idx][1] not in exp_literals:
                    print(f"Error: Expected a literal or seq type cast after ',' at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                    print("Syntax Error: Expected a literal or sequence type after comma")
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a literal but found {tokens[start_idx][0]}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, start_idx  # Return failure
                
                values.append(tokens[start_idx][0])  # Store the literal value (first element)
                print(f"Added '{tokens[start_idx][0]}' to values: {values}")
                
                start_idx += 1  # Move past the literal
                start_idx = skip_spaces(tokens, start_idx)  # Skip any spaces after the literal
            
            print("Parsing successful:", values)
            return True, start_idx  # Return success with next index only

        @staticmethod
        def seq_concat(tokens, start_idx):
            current_token = tokens[start_idx] if start_idx < len(tokens) else None
                    
            # Find which display line contains this token
            matching_line = None
            for line in display_lines:
                if current_token in line["tokens"]:
                    matching_line = line
                    break
                    
            # If we found a matching line, use its line number, otherwise fall back to get_line_number
            if matching_line:
                line_number = matching_line["line_number"]
                line_tokens = matching_line["tokens"]
                line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])  # Format without spaces
            else:
                line_number = get_line_number(tokens, start_idx)
                line_tokens = []
                line_text = ""

            print("<seq_concat>")
            start_idx = skip_spaces(tokens, start_idx)
            
            # Parse the first value - now accepting string literal, seq_type_cast, or Identifier
            first_value = None
            
            # Try string literal first
            if is_token(tokens, start_idx, 'string literal'):
                first_value = tokens[start_idx][1]
                print(f"First string literal: {first_value}")
                start_idx += 1
            # Try Identifier
            elif is_token(tokens, start_idx, 'Identifier'):
                first_value = tokens[start_idx][0]  # Get the identifier name
                print(f"First identifier: {first_value}")
                start_idx += 1
            # Try seq_type_cast
            elif is_token(tokens, start_idx, 'seq'):
                is_valid, cast_result, next_idx = express.seq_type_cast(tokens, start_idx)
                if is_valid and cast_result is not None:
                    first_value = cast_result
                    print(f"First seq_type_cast: {first_value}")
                    start_idx = next_idx
                else:
                    print(f"Error: Invalid seq type cast at index {start_idx}")
                    return False, None, start_idx
            else:
                print(f"Error: Expected string literal, identifier, or seq_type_cast at index {start_idx}")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a string literal, identifier, or seq type cast but found {tokens[start_idx][0]}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None, start_idx
            
            start_idx = skip_spaces(tokens, start_idx)
            
            # Check for '+' operator
            if start_idx >= len(tokens) or tokens[start_idx][0] != "+":
                print(f"Error: Expected '+' at index {start_idx}")
                return False, None, start_idx
            
            # Move past the '+' operator
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            
            # Parse the second value - now accepting string literal, seq_type_cast, or Identifier
            second_value = None
            
            # Try string literal first
            if is_token(tokens, start_idx, 'string literal'):
                second_value = tokens[start_idx][1]
                print(f"Second string literal: {second_value}")
                start_idx += 1
            # Try Identifier
            elif is_token(tokens, start_idx, 'Identifier'):
                second_value = tokens[start_idx][0]  # Get the identifier name
                print(f"Second identifier: {second_value}")
                start_idx += 1
            # Try seq_type_cast
            elif is_token(tokens, start_idx, 'seq'):
                is_valid, cast_result, next_idx = express.seq_type_cast(tokens, start_idx)
                if is_valid and cast_result is not None:
                    second_value = cast_result
                    print(f"Second seq_type_cast: {second_value}")
                    start_idx = next_idx
                else:
                    print(f"Error: Invalid seq type cast at index {start_idx}")
                    return False, None, start_idx
            else:
                print(f"Error: Expected string literal, identifier, or seq_type_cast at index {start_idx}")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a string literal, identifier, or seq type cast but found {tokens[start_idx][0]}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None, start_idx
            
            # Concatenate the values
            result = f"{first_value} + {second_value}"  # Changed to keep the + operator visible
            print(f"Concatenated result: {result}")
            
            # Check for additional concatenations in seq_concat_tail
            is_valid, additional_result, next_idx = express.seq_concat_tail(tokens, start_idx, result)
            if not is_valid:
                return False, None, start_idx
            
            # If there was a tail concatenation, update the result
            if additional_result:
                result = additional_result
            
            return True, result, next_idx

        @staticmethod
        def seq_concat_tail(tokens, start_idx, current_value=""):
            current_token = tokens[start_idx] if start_idx < len(tokens) else None
                    
            # Find which display line contains this token
            matching_line = None
            for line in display_lines:
                if current_token in line["tokens"]:
                    matching_line = line
                    break
                    
            # If we found a matching line, use its line number, otherwise fall back to get_line_number
            if matching_line:
                line_number = matching_line["line_number"]
                line_tokens = matching_line["tokens"]
                line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])  # Format without spaces
            else:
                line_number = get_line_number(tokens, start_idx)
                line_tokens = []
                line_text = ""

            print("<seq_concat_tail>")
            
            start_idx = skip_spaces(tokens, start_idx)
            
            if start_idx >= len(tokens) or tokens[start_idx][0] != "+":
                # No '+' found, this is the empty (λ) case
                print(f"No further concatenation at index {start_idx}, final value: {current_value}")
                return True, current_value, start_idx
            
            # Found '+', proceed with concatenation
            print(f"Found '+' at index {start_idx}, proceeding with concatenation")
            
            # Move past '+'
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            
            # Parse the next value (string literal or seq function call)
            next_value = None
            if is_token(tokens, start_idx, 'string literal'):
                # Get the string literal value
                next_value = tokens[start_idx][1]
                print(f"Next value is a string literal: {next_value}")
                start_idx += 1
            elif is_token(tokens, start_idx, 'seq'):
                # Parse the seq function call
                is_valid, cast_value, next_idx = express.seq_type_cast(tokens, start_idx)
                if not is_valid or not cast_value:
                    print(f"Error: Invalid seq function call at index {start_idx}")
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a seq but found {tokens[start_idx][0]}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None, start_idx
                next_value = cast_value
                print(f"Next value is a seq function call: {next_value}")
                start_idx = next_idx
            else:
                print(f"Error: Expected string literal or seq function call at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a string literal or seq type cast but found {tokens[start_idx][0]}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None, start_idx
            
            # Concatenate with current value
            updated_value = current_value + next_value
            print(f"Updated concatenation: {updated_value}")
            
            # Recursively call seq_concat_tail for further concatenation
            return express.seq_concat_tail(tokens, start_idx, updated_value)

        @staticmethod
        def seq_type_cast(tokens, start_idx):
            print("<seq_type_cast>")
            # Check for 'seq' keyword
            if start_idx >= len(tokens) or tokens[start_idx][1] != "seq":
                return False, "Error: Missing 'seq' keyword", start_idx

            start_idx += 1  # Move past 'seq'
            start_idx = skip_spaces(tokens, start_idx)

            # Check for opening parenthesis
            if start_idx >= len(tokens) or tokens[start_idx][0] != '(':
                return False, "Error: Missing '(' after 'seq'", start_idx

            start_idx += 1  # Move past '('
            start_idx = skip_spaces(tokens, start_idx)

            # Get the identifier
            if start_idx >= len(tokens) or tokens[start_idx][1] != "Identifier":
                return False, "Error: Missing Identifier inside 'seq()'", start_idx

            identifier = tokens[start_idx][0]
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            # Check for array access
            array_expr = ""
            while start_idx < len(tokens) and tokens[start_idx][0] == '[':
                array_expr += '['
                start_idx += 1  # Move past '['
                start_idx = skip_spaces(tokens, start_idx)

                # Parse array index (can be identifier or numlit)
                if start_idx >= len(tokens) or (tokens[start_idx][1] != "Identifier" and tokens[start_idx][1] != "numlit"):
                    return False, "Error: Invalid array index", start_idx

                array_expr += tokens[start_idx][0]
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                # Check for closing bracket
                if start_idx >= len(tokens) or tokens[start_idx][0] != ']':
                    return False, "Error: Missing ']'", start_idx

                array_expr += ']'
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

            # Check for closing parenthesis
            if start_idx >= len(tokens) or tokens[start_idx][0] != ')':
                return False, "Error: Missing ')' to close 'seq()'", start_idx

            result = f"seq({identifier}{array_expr})"
            return True, result, start_idx + 1  # Move past ')'



        @staticmethod
        def express_value_id_tail(tokens, start_idx, identifier):
            print("<express_value_id_tail>")
            start_idx = skip_spaces(tokens, start_idx)
            
            # Check if we have an array value
            if start_idx < len(tokens) and tokens[start_idx][0] == '[':
                print("Found '[', parsing as express_array_value")
                is_valid, array_value, next_idx = express.express_array_value(tokens, start_idx, identifier)
                if not is_valid:
                    print("Failed to parse express_array_value")
                    return False, identifier, start_idx
                
                return True, array_value, next_idx
            
            # Empty case (λ)
            print("No array access, returning original identifier")
            return True, identifier, start_idx

        @staticmethod
        def express_array_value(tokens, start_idx, identifier):
            print("<express_array_value>")
            
            # Check for opening bracket '['
            if start_idx >= len(tokens) or tokens[start_idx][0] != '[':
                print(f"Error: Expected '[' at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None, start_idx
            
            # Move past '['
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            
            # Parse express_array_default_value
            default_value = None
            if start_idx < len(tokens) and tokens[start_idx][1] == 'numlit':
                default_value = tokens[start_idx][0]
                print(f"Found default value: {default_value}")
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
            
            # Parse express_array_splice
            splice_operations = []
            if start_idx < len(tokens) and tokens[start_idx][0] == ':':
                print("Found ':', parsing as express_array_splice")
                is_valid, splice_ops, next_idx = express.express_array_splice(tokens, start_idx)
                if not is_valid:
                    print("Failed to parse express_array_splice")
                    return False, None, start_idx
                
                splice_operations = splice_ops
                start_idx = next_idx
            
            # Parse express_array_value_tail
            tail_value = None
            if start_idx < len(tokens) and tokens[start_idx][1] == 'numlit':
                tail_value = tokens[start_idx][0]
                print(f"Found tail value: {tail_value}")
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
            
            # Check for closing bracket ']'
            if start_idx >= len(tokens) or tokens[start_idx][0] != ']':
                print(f"Error: Expected ']' at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None, start_idx
            
            # Move past ']'
            start_idx += 1
            
            # Construct the array access expression
            array_expr = f"{identifier}[{default_value if default_value else ''}"
            
            # Add splice operations
            for splice in splice_operations:
                array_expr += splice
            
            # Add tail value if present
            if tail_value:
                array_expr += f"{tail_value}"
            
            array_expr += "]"
            
            print(f"Constructed array expression: {array_expr}")
            return True, array_expr, start_idx

        @staticmethod
        def express_array_splice(tokens, start_idx):
            print("<express_array_splice>")
            
            # Check for ':'
            if start_idx >= len(tokens) or tokens[start_idx][0] != ':':
                print(f"Error: Expected ':' at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, [], start_idx
            
            # Move past ':'
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            
            # Add this splice operation
            splice_ops = [':']
            
            # Parse express_array_splice_tail
            is_valid, tail_splices, next_idx = express.express_array_splice_tail(tokens, start_idx)
            if not is_valid:
                print("Failed to parse express_array_splice_tail")
                return False, [], start_idx
            
            # Combine splice operations
            splice_ops.extend(tail_splices)
            
            return True, splice_ops, next_idx

        @staticmethod
        def express_array_splice_tail(tokens, start_idx):
            print("<express_array_splice_tail>")
            
            # Check if we have another splice
            if start_idx < len(tokens) and tokens[start_idx][0] == ':':
                print("Found ':', parsing as another express_array_splice")
                is_valid, splice_ops, next_idx = express.express_array_splice(tokens, start_idx)
                if not is_valid:
                    print("Failed to parse nested express_array_splice")
                    return False, [], start_idx
                
                return True, splice_ops, next_idx
            
            # Empty case (λ)
            print("No further splices")
            return True, [], start_idx

    # def reset_parser_state():
    #     global main_function_seen
    #     main_function_seen = False

    # Modify the process_tokens function to call reset_parser_state at the beginning
    def process_tokens(tokens):
        print("\n========== PROCESS TOKENS ==========")  # Big header for debugging
        # reset_parser_state()

        lines = []
        current_statement = []
        current_line = []
        current_line_number = 1
        brace_count = 0  # Track nested braces
        i = 0
        
        # For display purposes only - organize tokens by line
        display_lines = []
        current_display_line = []

        while i < len(tokens):
            token = tokens[i]
            print(f"PROCESS TOKENS Processing token {i}: {token}")  # Debug statement

            if token is None or len(token) < 2:  # Prevents "None" token errors
                print(f"PROCESS TOKENS Skipping invalid token at index {i}")
                i += 1
                continue  # Skip invalid tokens

            # For display purposes - add token to current display line
            if token[1] != "newline":
                current_display_line.append(token)
            
            # If we encounter a newline
            if token[1] == "newline":
                print(f"PROCESS TOKENS Newline found at line {current_line_number}, processing current_line: {current_line}")
                
                # For display purposes - add the current display line to display_lines
                if current_display_line:
                    display_lines.append({
                        'tokens': current_display_line.copy(),
                        'line_number': current_line_number
                    })
                    current_display_line = []
                
                if current_line:  # Only add if there are tokens
                    current_statement.extend(current_line)
                    current_line = []

                current_line_number += 1

                # if current_statement and any(t[1] == ';' for t in current_statement) and brace_count == 0:
                #     print(f"PROCESS TOKENS End of statement found at line {current_line_number - 1}, adding to lines.")
                #     lines.append(current_statement)
                #     current_statement = []
            else:
                if token[1] == '{':
                    brace_count += 1
                    print(f"PROCESS TOKENS Opening brace found, brace_count: {brace_count}")
                elif token[1] == '}':
                    brace_count -= 1
                    print(f"PROCESS TOKENS Closing brace found, brace_count: {brace_count}")

                current_line.append(token)

                # Check if we have a closing brace followed by specific keywords
                if token[1] == '}' and brace_count == 0:
                    print("PROCESS TOKENS Closing brace detected, checking for following keywords.")
                    
                    # Look ahead to see if 'else' or similar keywords follow
                    next_index = i + 1
                    while next_index < len(tokens) and tokens[next_index][1] in ["space", "newline"]:
                        next_index += 1
                    
                    # If we're at the end or the next token isn't a special keyword
                    if next_index >= len(tokens) or tokens[next_index][1] not in ["else", "while", "do", "elif"]:
                        print(f"PROCESS TOKENS Block end detected at index {i}, adding current_line: {current_line}")
                        current_statement.extend(current_line)
                        lines.append(current_statement)
                        current_statement = []
                        current_line = []

            i += 1

        # Add the last display line if it's not empty
        if current_display_line:
            display_lines.append({
                'tokens': current_display_line,
                'line_number': current_line_number
            })

        if current_line:
            print(f"PROCESS TOKENS Processing remaining line at end of input: {current_line}")
            current_statement.extend(current_line)

        if current_statement:
            print(f"PROCESS TOKENS Adding final statement: {current_statement}")
            lines.append(current_statement)

        
        # Print each line for display purposes
        print("\nTokens by Line:")
        for line in display_lines:
            line_number = line['line_number']
            tokens_str = ' '.join([f"{t[0]} ({t[1]})" for t in line['tokens']])
            print(f"Line {line_number}: {tokens_str}")
        
        # Return the original lines for syntax processing
        return lines, display_lines
    
    conditional_op = {'<', '>', '>=', '<=', '==', '!=', '&&', '||', '!'}
    math_operator = {'+', '-', '*', "/", '%', '**', '//'}
    literals = {'string literal', 'dom', 'rec'}
    assignment_op = {'+=', '*=', '-=', '/=', '%=', '=',}

    program_pattern = [
        ['act'],
        ['_G']
    ]

    token_lines, display_lines = process_tokens(tokens)
    valid_syntax = True

    print("\nTokens Received:")
    for idx, (token_id, token_value) in enumerate(tokens, start=1):
        print(f"{idx}. Token: {token_value} (ID: {token_id})")

    for line_num, line_tokens in enumerate(token_lines, start=1):
        line_tokens = [token for token in line_tokens if token[1] != 'newline']

        if not line_tokens:
            continue

        # Extract the first token value
        first_token = line_tokens[0][1] if line_tokens else None
        valid_line = False
        number_sign = None
        start_idx = 0 
        print(f"first token: {first_token}")
            
        if first_token == "act" or first_token == "_G":
            for pattern in program_pattern:
                is_valid, next_idx, _ = validate_syntax_pattern(line_tokens, pattern)
                if is_valid:
                    if first_token == "act":
                        is_valid_program, sign = program.main_function(line_tokens, next_idx)
                    elif first_token == "_G":
                        is_valid_program, sign = program.global_handling(line_tokens, next_idx)
                    
                    if is_valid_program:
                        valid_line = True
                    break

        elif first_token == "comment" or first_token == "multiline" or first_token == "tab":
            continue  # Skip the rest of the loop for this line



        else:
            #DAPAT DI TO NAGPAPAKITA KAHIT ERROR SA USER DEF
            output_text.insert(tk.END, f"Expected global declaration, user defined or main function\n")


    if valid_line:
            # tokens_info = [f"{token[0]} ({token[1]})" for token in line_tokens]
            # sign_msg = f" (Number is {number_sign})" if number_sign else ""
            print(f"ignore")
    else:
            # # Use display_lines to show the error by actual line number
            # error_line = None
            # for dl in display_lines:
            #     if any(t in line_tokens for t in dl['tokens']):
            #         error_line = dl
            #         break
            
            # if error_line:
            #     tokens_info = [f"{token[0]} ({token[1]})" for token in error_line['tokens']]
            #     line_text = ' '.join([t[0] for t in error_line['tokens'] if t[1] != "space"])
            #     print(f"Line {error_line['line_number']}: Syntax Error {tokens_info}")
            #     # output_text.insert(tk.END, f"Syntax Error at line {error_line['line_number']}\n")
            #     # output_text.insert(tk.END, f"Line {error_line['line_number']}: {line_text}\n")
            # else:
            #     tokens_info = [f"{token[0]} ({token[1]})" for token in line_tokens]
            #     line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])
            #     print(f"Statement {line_num}: Syntax Error {tokens_info}")
            #     # output_text.insert(tk.END, f"Syntax Error at line {line_num}\n")
            #     # output_text.insert(tk.END, f"Line {line_num}: {line_text}\n")
                        
            valid_syntax = False
            # break

    syntax_error = False
    if not valid_syntax:
        # output_text.insert(tk.END, "Syntax Error: Invalid statement detected\n")
        output_text.yview(tk.END)
        print("\nSyntax Error!")
        syntax_error = True

    else:
        output_text.insert(tk.END, "You May Push!\n")
        print("\nAll statements are valid!")

    return syntax_error