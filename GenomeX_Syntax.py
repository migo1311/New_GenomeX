import GenomeX_Lexer as gxl
import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
import sys  
from itertools import chain


def parseSyntax(tokens, output_text):
    # Add a set to track lines that have already had errors reported
    reported_error_lines = set()
    
    def get_line_number(tokens, index):
        """
        Determine the line numlit for a token at the given index by counting newlines.
        
        Args:
            tokens: The list of tokens
            index: The index of the token to find the line numlit for
        
        Returns:
            The line numlit (1-based)
        """
        if index < 0 or index >= len(tokens):
            return -1  
        
        line_number = 1
        for i in range(index):
            if tokens[i][1] == "newline":
                line_number += 1
            # We don't count newlines inside multiline comments anymore
            # because the lexer appears to insert separate newline tokens
        
        return line_number

    def skip_spaces(tokens, start_idx):
        
        if start_idx is None:
            return None
            
        while start_idx < len(tokens) and tokens[start_idx][1] in ["space", "comment", "multiline", "tab"]:
            start_idx += 1
        return start_idx

    def is_token(tokens, idx, token_type):
            if idx >= len(tokens):
                return False

            
            if isinstance(token_type, (list, tuple)):
                return tokens[idx][1] in token_type

            
            return tokens[idx][1] == token_type
    
    def find_matching_line(tokens, start_idx, display_lines, get_line_number):
        # Handle the EOF case (when start_idx is at or past the end of tokens)
        if start_idx >= len(tokens):
            print("DEBUG SYNTAX: AT EOF")
            
            # Try to find the last non-empty line in the file
            if display_lines:
                # Sort by line numlit and find the last non-empty line
                sorted_lines = sorted(display_lines, key=lambda line: line["line_number"])
                last_line = sorted_lines[-1]  # Default to absolute last line
                
                # Try to find the line with actual code, not just whitespace
                for line in reversed(sorted_lines):
                    non_space_tokens = [t for t in line["tokens"] if t[1] != "space"]
                    if non_space_tokens:
                        last_line = line
                        break
                        
                line_number = last_line["line_number"]
                line_tokens = last_line["tokens"]
                # Include the line's text in the error message to help users find where the error is
                line_text = "End of file after: " + ' '.join([t[0] for t in line_tokens if t[1] != "space"])
                line_index = start_idx
                return (line_number, line_tokens, line_text, line_index)
            else:
                # If no lines in display_lines, use default
                return (0, [], "End of tokens", start_idx)
        
        # Normal case - we have a valid token
        current_token = (start_idx, tokens[start_idx])
        print(f"DEBUG SYNTAX: CURRENT TOKEN: {current_token}")
        
        # Find matching line by looking for the exact token at exact index
        matching_line = None
        for line in display_lines:
            if current_token[1] in [t for t in line["tokens"]]:
                if "start_idx" in line:
                    # If the line already tracks its starting index in the global tokens list
                    start_of_line = line["start_idx"]
                    end_of_line = start_of_line + len(line["tokens"])
                    if start_of_line <= current_token[0] < end_of_line:
                        matching_line = line
                        print(f"DEBUG SYNTAX: FOUND CURRENT MATCH: {matching_line}")
                        break
                else:
                    # Alternative approach for lines without start_idx
                    for i in range(len(tokens) - len(line["tokens"]) + 1):
                        if all(tokens[i+j] == line["tokens"][j] for j in range(len(line["tokens"]))):
                            if i <= current_token[0] < i + len(line["tokens"]):
                                matching_line = line
                                print(f"DEBUG SYNTAX: FOUND CURRENT MATCH: {matching_line}")
                                break
                    if matching_line:
                        break

        if matching_line:
            line_number = matching_line["line_number"]
            line_tokens = matching_line["tokens"]
            line_index = current_token[0]  # Use the exact index
            line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])
        else:
            line_number = get_line_number(tokens, start_idx)
            line_tokens = []
            line_text = ""
            line_index = start_idx
        
        return (line_number, line_tokens, line_text, line_index)
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
            token_value = tokens[token_idx][1]  

            
            if token_value == "space":
                token_idx += 1
                continue

            
            expected = pattern[pattern_idx]

            
            if isinstance(expected, set):
                
                if token_value not in expected:
                    return False, token_idx, None
            else:
                
                if token_value != expected:
                    return False, token_idx, None

            
            token_idx += 1
            pattern_idx += 1

        
        return True, token_idx, number_sign
    
    def display_error(line_number, line_text, error_message):
        if line_number not in reported_error_lines and not hasattr(display_error, 'error_displayed'):
            output_text.insert(tk.END, f"Syntax Error at line {line_number}: {error_message}\n")
            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
            reported_error_lines.add(line_number)
            display_error.error_displayed = True
            return True
        return False

    class program:
            def body_statements(tokens, start_idx):
                keywords = {"dose", "quant", "seq", "allele"}

                statement_parsers = {
                    'express': statements.express_statement,
                    'if': statements.if_statement,
                    'prod': statements.prod_statement,
                    'Identifier': statements.stimuli_statement,
                    'for': statements.for_loop_statement,
                    'while': statements.while_statement,
                    'func': statements.func_calling,
                    'contig': statements.contig_statement,
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
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    keywords = ['dose', 'quant', 'seq', 'allele', 'clust', 'perms']

                    
                    for keyword in keywords:
                        if is_token(tokens, start_idx, keyword):
                            # line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                            # output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected a valid keyword but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                            # output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None
                                    
                    
                    if is_token(tokens, start_idx, '_L'):
                        print("<local_perms_declaration>")
                        check_statements = True  
                        start_idx += 1  
                        start_idx = skip_spaces(tokens, start_idx)

                        
                        if is_token(tokens, start_idx, 'perms'):
                            print("<perms>")
                            start_idx += 1  
                            start_idx = skip_spaces(tokens, start_idx)
                            
                            
                            if not any(is_token(tokens, start_idx, perms_type) for perms_type in perms_parsers):
                                print("Invalid perms type")
                                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                                display_error(line_number, line_text, f"Expected dose, quant, seq, or allele but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                                return False, None  
                                
                            for perms_type, parser_func in perms_parsers.items():
                                if is_token(tokens, start_idx, perms_type):
                                    start_idx += 1  
                                    start_idx = skip_spaces(tokens, start_idx)
                                    
                                    is_valid, new_idx = parser_func(tokens, start_idx)
                                    if not is_valid:
                                        print(f"Invalid perms {perms_type} statement")
                                        return False, None
                                        
                                    start_idx = new_idx
                                    start_idx = skip_spaces(tokens, start_idx)
                                    print(f"Successfully parsed perms {perms_type}")
                                    break  
                                    
                            continue  
                            
                        elif is_token(tokens, start_idx, 'clust'):
                            print("<clust>")
                            start_idx += 1  
                            start_idx = skip_spaces(tokens, start_idx)
                            
                            
                            if not any(is_token(tokens, start_idx, clust_type) for clust_type in clust_parse):
                                print("Invalid *clust type")
                                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                                display_error(line_number, line_text, f"Expected 'dose', 'quant', 'seq' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                                return False, None
                                
                            for clust_type, parser_func in clust_parse.items():
                                if is_token(tokens, start_idx, clust_type):
                                    start_idx += 1  
                                    start_idx = skip_spaces(tokens, start_idx)
                                    
                                    is_valid, new_idx = parser_func(tokens, start_idx)
                                    if not is_valid:
                                        print(f"Invalid *L clust {clust_type} statement")
                                        return False, None
                                        
                                    start_idx = new_idx
                                    start_idx = skip_spaces(tokens, start_idx)
                                    print(f"Successfully parsed *L clust {clust_type}")
                                    break  
                                    
                            continue  

                        
                        if not any(is_token(tokens, start_idx, L_type) for L_type in local_parse):
                            print("Invalid *L perms type")
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                            display_error(line_number, line_text, f"Expected 'dose', 'quant', 'seq', 'allele', 'clust' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                            return False, None  

                        for L_type, parser_func in local_parse.items():
                            if is_token(tokens, start_idx, L_type):
                                start_idx += 1  
                                start_idx = skip_spaces(tokens, start_idx)

                                is_valid, new_idx = parser_func(tokens, start_idx)
                                if not is_valid:
                                    print(f"Invalid *L perms {L_type} statement")
                                    return False, None

                                start_idx = new_idx
                                start_idx = skip_spaces(tokens, start_idx)
                                print(f"Successfully parsed *L perms {L_type}")
                                break  

                        continue  

                    
                    found_statement = False
                    for statement_type, parser_func in statement_parsers.items():
                        if is_token(tokens, start_idx, statement_type):
                            check_statements = True  
                            found_statement = True
                            start_idx += 1  
                            start_idx = skip_spaces(tokens, start_idx)

                            is_valid, new_idx = parser_func(tokens, start_idx)
                            if not is_valid:
                                print(f"Invalid {statement_type} statement")
                                return False, None

                            start_idx = new_idx
                            start_idx = skip_spaces(tokens, start_idx)
                            print(f"Finished statement: {statement_type}")
                            break  

                    if not found_statement:
                        
                        
                        if start_idx >= len(tokens):
                            print("Reached end of tokens")
                        else:
                            print(f"Current token: {tokens[start_idx] if start_idx < len(tokens) else 'None'}")
                        return check_statements, start_idx  


                return check_statements, start_idx  
            main_function_seen = False
            user_defined_function_error = False  
            def global_handling(tokens, start_idx):
                print("<global_handling> ENTRY: start_idx=", start_idx, "tokens=", tokens)
                
                start_idx = skip_spaces(tokens, start_idx)
                print("[global_handling] After skip_spaces: start_idx=", start_idx)
                
                # Setup parsers for different data types
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

                # Parse perms block
                if is_token(tokens, start_idx, 'perms'):
                    print("[global_handling] <perms> block at idx", start_idx)
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)
                    print("[global_handling] After perms skip_spaces: start_idx=", start_idx)
                    
                    if not any(is_token(tokens, start_idx, perms_type) for perms_type in perms_parsers):
                        print("[global_handling] Invalid perms type at idx", start_idx)
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        display_error(line_number, line_text, f"Expected 'dose', 'quant', 'seq' but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}")
                        return False, None
                        
                    for perms_type, parser_func in perms_parsers.items():
                        if is_token(tokens, start_idx, perms_type):
                            print(f"[global_handling] Parsing perms_type: {perms_type} at idx {start_idx}")
                            start_idx += 1  
                            start_idx = skip_spaces(tokens, start_idx)
                            is_valid, new_idx = parser_func(tokens, start_idx)
                            print(f"[global_handling] perms_type {perms_type} is_valid={is_valid}, new_idx={new_idx}")
                            if not is_valid:
                                print(f"[global_handling] Invalid perms {perms_type} statement at idx {start_idx}")
                                return False, None
                            start_idx = new_idx
                            start_idx = skip_spaces(tokens, start_idx)
                            print(f"[global_handling] Successfully parsed perms {perms_type}, new start_idx={start_idx}")
                            break
                
                # Parse clust block
                elif is_token(tokens, start_idx, 'clust'):
                    print("[global_handling] <clust> block at idx", start_idx)
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)
                    print("[global_handling] After clust skip_spaces: start_idx=", start_idx)
                    
                    if not any(is_token(tokens, start_idx, clust_type) for clust_type in clust_parse):
                        print("[global_handling] Invalid clust type at idx", start_idx)
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        display_error(line_number, line_text, f"Expected 'dose', 'quant', 'seq' but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}")
                        return False, None
                        
                    for clust_type, parser_func in clust_parse.items():
                        if is_token(tokens, start_idx, clust_type):
                            print(f"[global_handling] Parsing clust_type: {clust_type} at idx {start_idx}")
                            start_idx += 1  
                            start_idx = skip_spaces(tokens, start_idx)
                            is_valid, new_idx = parser_func(tokens, start_idx)
                            print(f"[global_handling] clust_type {clust_type} is_valid={is_valid}, new_idx={new_idx}")
                            if not is_valid:
                                print(f"[global_handling] Invalid clust {clust_type} statement at idx {start_idx}")
                                return False, None
                            start_idx = new_idx
                            start_idx = skip_spaces(tokens, start_idx)
                            print(f"[global_handling] Successfully parsed clust {clust_type}, new start_idx={start_idx}")
                            break
                
                # Parse regular data types (dose, quant, seq, allele)
                else:
                    if not any(is_token(tokens, start_idx, L_type) for L_type in local_parse):
                        print("[global_handling] Invalid global data type at idx", start_idx)
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        display_error(line_number, line_text, f"Expected a valid datatype (dose, quant, seq, allele) but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}")
                        return False, None
                        
                    for G_type, parser_func in local_parse.items():
                        if is_token(tokens, start_idx, G_type):
                            print(f"[global_handling] Parsing G_type: {G_type} at idx {start_idx}")
                            start_idx += 1  
                            start_idx = skip_spaces(tokens, start_idx)
                            is_valid, new_idx = parser_func(tokens, start_idx)
                            print(f"[global_handling] G_type {G_type} is_valid={is_valid}, new_idx={new_idx}")
                            if not is_valid:
                                print(f"[global_handling] Invalid {G_type} statement at idx {start_idx}")
                                return False, None
                            start_idx = new_idx
                            start_idx = skip_spaces(tokens, start_idx)
                            print(f"[global_handling] Successfully parsed {G_type}, new start_idx={start_idx}")
                            break
                
                # After processing one global declaration, return the next index
                next_idx = skip_spaces(tokens, start_idx)
                print("[global_handling] Returning after processing one global declaration, next_idx=", next_idx)
                return True, next_idx

            def user_defined_function(tokens, start_idx):
                print("<user_function> ENTRY: start_idx=", start_idx, "tokens=", tokens)
                print("Parsing user defined function...")
                
                start_idx = skip_spaces(tokens, start_idx)
                
                # Handle void return type
                if is_token(tokens, start_idx, 'void'):
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)

                # Check for function name
                if not (start_idx < len(tokens) and tokens[start_idx][1] == "Identifier"):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    print(f"Error: Expected function name (Identifier) ")
                    if display_error(line_number, line_text, f"Expected function name (Identifier)  but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
                    program.user_defined_function_error = True  

                # Store the function name for better error messages
                func_name = tokens[start_idx][0] if start_idx < len(tokens) else "unknown"
                
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)

                # Check for opening parenthesis
                if not is_token(tokens, start_idx, '('):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    print(f"Error: Expected '(' after function name ")
                    if display_error(line_number, line_text, f"Expected '(' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
                    program.user_defined_function_error = True  
                    
                    
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)

                # Parse parameters
                is_valid, params, new_idx = parameters.parse_params(tokens, start_idx)
                if not is_valid:
                    program.user_defined_function_error = True  
                    return False, None

                start_idx = new_idx  
                start_idx = skip_spaces(tokens, start_idx)

                # Check for closing parenthesis
                if not is_token(tokens, start_idx, ')'):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    print(f"Error: Expected ')' , but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}")
                    if display_error(line_number, line_text, f"Expected ')' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
                    program.user_defined_function_error = True  
                    
                
                start_idx += 1 
                start_idx = skip_spaces(tokens, start_idx)

                # Check for opening brace
                if not is_token(tokens, start_idx, '{'):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    print("Missing opening brace for function block")
                    if display_error(line_number, line_text, f"Expected '{{' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
                    program.user_defined_function_error = True  
                    
                
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)

                # Parse function body
                check_statements, new_idx = program.body_statements(tokens, start_idx)
                start_idx = skip_spaces(tokens, new_idx)

                if new_idx is None:
                    print("Error in user defined function statements")
                    program.user_defined_function_error = True  
                    return False, None
                
                start_idx = new_idx
                start_idx = skip_spaces(tokens, start_idx)
                
                # Check for closing brace
                if is_token(tokens, start_idx, '}'):
                    print("Found closing brace for user defined function")
                    
                    if not check_statements:
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        print(f"Error: No statements found in {func_name} function")
                        if display_error(line_number, line_text, f"Expected '}}' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                            return False, None
                        program.user_defined_function_error = True  
                        
                    
                    return True, start_idx + 1
                else:
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    print("Missing closing brace for user defined function")
                    if display_error(line_number, line_text, f"Expected '}}' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
                    program.user_defined_function_error = True  
                   

                
            def main_function(tokens, start_idx):
                print("<main_function> ENTRY: start_idx=", start_idx, "tokens=", tokens)

                start_idx = skip_spaces(tokens, start_idx)
                
                # First check if we're processing an 'act' keyword
                if is_token(tokens, start_idx, 'act'):
                    print("[main_function] Found 'act' keyword")
                    
                    # Check if user-defined function had errors
                    if program.user_defined_function_error:
                        print("[main_function] Error: Cannot proceed with 'act' due to errors in user-defined functions")
                        return False, None
                    
                    start_idx += 1  # Skip 'act' token
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    # Check if there's 'gene' after 'act'
                    if not is_token(tokens, start_idx, 'gene'):
                        print(f"[main_function] Error: Expected 'gene' after 'act' ")
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        if display_error(line_number, line_text, f"Expected gene , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
                
                # Continue with normal main function parsing
                if is_token(tokens, start_idx, 'gene'):
                    print("[main_function] Processing 'gene' function")
                    
                    # Check if user-defined function had errors
                    if program.user_defined_function_error:
                        print("[main_function] Error: Cannot proceed with main function due to errors in user-defined functions")
                        return False, None
                    
                    # Check for multiple main functions
                    if program.main_function_seen:
                        print("[main_function] Error: Multiple main functions (gene) declared")
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        output_text.insert(tk.END, f"Multiple main functions (gene) declared\n")
                        return False, None
                    
                    # Mark main function as seen
                    program.main_function_seen = True
                    
                    start_idx += 1  # Skip 'gene' token
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    # Check for opening parenthesis
                    if not is_token(tokens, start_idx, '('):
                        print(f"[main_function] Error: Expected '(' after 'gene' ")
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        if display_error(line_number, line_text, f"Expected '(' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None

                    start_idx += 1  # Skip '(' token
                    start_idx = skip_spaces(tokens, start_idx)

                    # Check for closing parenthesis
                    if not is_token(tokens, start_idx, ')'):
                        print(f"[main_function] Error: Expected ')' , but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}")
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        if display_error(line_number, line_text, f"Expected ')' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
                    
                    start_idx += 1  # Skip ')' token
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    # Check for opening brace
                    if not is_token(tokens, start_idx, '{'):
                        print("[main_function] Missing opening brace for main function block")
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        if display_error(line_number, line_text, f"Expected '{{' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
                    
                    start_idx += 1  # Skip '{' token
                    start_idx = skip_spaces(tokens, start_idx)

                    # Parse function body statements
                    check_statements, new_idx = program.body_statements(tokens, start_idx)
                    print(f"[main_function] After body_statements: check_statements={check_statements}, new_idx={new_idx}")

                    if new_idx is None:
                        print("[main_function] Error in main function body statements")
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        if display_error(line_number, line_text, f"Expected _L, express, if, prod, Identifier, for, while, func , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
                        
                    start_idx = new_idx
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    # Check for closing brace
                    if is_token(tokens, start_idx, '}'):
                        print("[main_function] Found closing brace for main function")
                        
                        if not check_statements:
                            print("[main_function] Error: No statements found in main function")
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                            if display_error(line_number, line_text, f"Expected _L, express, if, prod, Identifier, for, while, func , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                                return False, None
                            
                        return True, start_idx + 1
                    else:
                        print("[main_function] Missing closing brace for main function")
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        if display_error(line_number, line_text, f"Expected '}}' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
                
                # Handle user-defined functions
                else:
                    if program.main_function_seen:
                        print("[main_function] Error: User-defined functions must be declared before the main function")
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        if display_error(line_number, line_text, f"User defined function must be declared before the main function"):
                         return False, None
                        program.user_defined_function_error = True  
                        
                        
                    print("[main_function] Processing user-defined function")
                    return program.user_defined_function(tokens, start_idx)
    


    class conditional:
            @staticmethod
            def conditional_block(tokens, start_idx):
                print("<conditional_block>")

                start_idx = skip_spaces(tokens, start_idx)
                
                
                is_valid, new_idx = conditional.conditions_base(tokens, start_idx)
                if not is_valid:
                    
                    current_token = tokens[start_idx] if start_idx < len(tokens) else None
                    
                    
                    
                    print(f"Error: Invalid conditions_base ")
                    return False, None
                return True, new_idx
            
            @staticmethod
            def conditions_base(tokens, start_idx):
                
                print("<conditions_base>")
                start_idx = skip_spaces(tokens, start_idx)
                
                
                has_negation = False
                if start_idx < len(tokens) and tokens[start_idx][0] == '!':
                    print(f"Found negation operator '!' ")
                    has_negation = True
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)
                
                
                is_valid, new_idx = conditional.condition_value(tokens, start_idx)
                if not is_valid:
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    if display_error(line_number, line_text, f"Expected 'dom', 'rec', 'numlit', 'string literal' or Identifier , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
                    print(f"Error: Invalid first condition_value ")
                    

                start_idx = new_idx
                start_idx = skip_spaces(tokens, start_idx)
                
                
                has_array_stimuli = False
                if is_token(tokens, start_idx, '['):
                    has_array_stimuli = True
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    
                    if start_idx < len(tokens) and tokens[start_idx][1] in ["Identifier", "numlit"]:
                        
                        start_idx += 1  
                    
                    
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    
                    if not is_token(tokens, start_idx, ']'):
                        print(f"Error: Expected closing bracket ']'  (line {line_number})")
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        if display_error(line_number, line_text, f"Expected  ']' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
                    
                    start_idx += 1  
                
                
                start_idx = skip_spaces(tokens, start_idx)
                
                relational_operators = {'<', '>', '<=', '>=', '==', '!='}
                mathematical_operators = {'+', '-', '*', '/', '%', '**', '//'}
                logical_operators = {'&&', '||'}

                
                if start_idx >= len(tokens) or not any(tokens[start_idx][0] in op_set for op_set in [logical_operators, relational_operators] for op in op_set):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    print(f"Error: Expected relational operator , found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}")
                    if display_error(line_number, line_text, f"Expected '>', '<', '>=', '<=', '==', '!=' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
                
                
                print(f"Found relational operator '{tokens[start_idx][0]}' ")
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
                
                
                has_negation = False
                if start_idx < len(tokens) and tokens[start_idx][0] == '!':
                    print(f"Found negation operator '!' ")
                    has_negation = True
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)
                
                
                is_valid, new_idx = conditional.condition_value(tokens, start_idx)
                if not is_valid:
                    print(f"Error: Invalid second condition_value ")
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    if display_error(line_number, line_text, f"Expected 'dom', 'rec', 'string literal', 'numlit' or Identifiers , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                     return False, None
                    
                
                start_idx = new_idx
                start_idx = skip_spaces(tokens, start_idx)
                
                has_array_stimuli = False
                if is_token(tokens, start_idx, '['):
                    has_array_stimuli = True
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    
                    if start_idx < len(tokens) and tokens[start_idx][1] in ["Identifier", "numlit"]:
                        
                        start_idx += 1  
                    
                    
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    
                    if not is_token(tokens, start_idx, ']'):
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        print(f"Error: Expected closing bracket ']'  (line {line_number})")
                        if display_error(line_number, line_text, f"Expected ']' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None

                    
                    start_idx += 1  
                
                
                start_idx = skip_spaces(tokens, start_idx)
                
                is_valid, new_idx = conditional.condition_value_tail(tokens, start_idx)
                if not is_valid:
                    if display_error(line_number, line_text, f"Invalid condition at line {line_number}"):
                         return False, None
                    print(f"Error: Invalid condition_value_tail ")
                
                return True, new_idx
                    
            @staticmethod
            def condition_value(tokens, start_idx):
                

                print("<condition_value>")
                start_idx = skip_spaces(tokens, start_idx)
                
                
                if start_idx < len(tokens) and tokens[start_idx][0] == '(':
                    print(f"Found opening parenthesis ")
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    
                    is_valid, new_idx = conditional.conditions_base(tokens, start_idx)
                    if not is_valid:
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                        print(f"Error: Invalid condition inside parentheses ")
                        # output_text.insert(tk.END, f"Syntax Error: Invalid condition inside parentheses  but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                        # output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                    
                    start_idx = new_idx
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    if not is_token(tokens, start_idx, ')'):
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        print(f"Error: Expected closing parenthesis , found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                        if display_error(line_number, line_text, f"Expected ')' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
                    
                    print(f"Found closing parenthesis ")
                    return True, start_idx + 1  
                
                
                if start_idx < len(tokens) and tokens[start_idx][1] == 'Identifier':
                    print(f"Found Identifier '{tokens[start_idx][0]}' ")
                    current_idx = start_idx
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    
                    while start_idx < len(tokens) and tokens[start_idx][0] == '[':
                        start_idx += 1  
                        start_idx = skip_spaces(tokens, start_idx)
                        
                        
                        if not (start_idx < len(tokens) and (tokens[start_idx][1] == "Identifier" or tokens[start_idx][1] == "numlit")):
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                            if display_error(line_number, line_text, f"Invalid array index, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                                return False, None
                        
                        start_idx += 1  
                        start_idx = skip_spaces(tokens, start_idx)
                        
                        
                        if not (start_idx < len(tokens) and tokens[start_idx][0] == ']'):
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                            if display_error(line_number, line_text, f"Expected ']' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                                return False, None
                        
                        start_idx += 1  
                        start_idx = skip_spaces(tokens, start_idx)
                    
                    
                    if start_idx < len(tokens) and tokens[start_idx][0] in math_operator:
                        is_valid, new_idx = arithmetic.arithmetic_sequence(tokens, current_idx)
                        if is_valid:
                            return True, new_idx
                    
                    return True, start_idx
                
                
                if start_idx < len(tokens) and (tokens[start_idx][1] == 'numlit' or tokens[start_idx][1] == 'Identifier'):
                    next_idx = start_idx + 1
                    next_idx = skip_spaces(tokens, next_idx)
                    if next_idx < len(tokens) and tokens[next_idx][0] in math_operator:
                        is_valid, new_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
                        if is_valid:
                            print(f"Found valid arithmetic sequence ")
                            return True, new_idx
                
                
                conliterals = {'numlit', 'string literal', 'dom', 'rec'}
                if start_idx < len(tokens) and tokens[start_idx][1] in conliterals:
                    print(f"Found literal '{tokens[start_idx][0]}' of type {tokens[start_idx][1]} ")
                    return True, start_idx + 1  
                
                # line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                # output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a condition value but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                # output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                print(f"Error: Expected condition value , found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
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
                
                
                logical_operators = {'&&', '||'}
                relational_operators = {'<', '>', '<=', '>=', '==', '!='}

                
                if start_idx >= len(tokens) or not any(tokens[start_idx][0] in op_set for op_set in logical_operators for op in op_set):
                    
                    
                    if start_idx < len(tokens) and tokens[start_idx][0] == ';':
                        print(f"Found semicolon ")
                        return True, start_idx + 1  
                    
                    return True, start_idx  
                
                
                print(f"Found logical operator '{tokens[start_idx][0]}' ")
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
                
                
                is_valid, new_idx = conditional.conditions_base(tokens, start_idx)
                if not is_valid:
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    if display_error(line_number, line_text, f"Invalid condition after logical operator at line {line_number}"):
                         return False, None
                    print(f"Error: Invalid conditions_base after logical operator ")
        
                
                start_idx = new_idx
                start_idx = skip_spaces(tokens, start_idx)
                
                
                return conditional.condition_value_tail(tokens, start_idx)
        
    class statements:
        @staticmethod
        def func_calling(tokens, start_idx):
            print(f"DEBUG SYNTAX: Starting function_calling ")
            
            start_idx = skip_spaces(tokens, start_idx)

            # Check for function identifier
            if not (start_idx < len(tokens) and is_token(tokens, start_idx, "Identifier")):
                print(f"Error: Expected identifier after 'func' ")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected Identifier after 'func' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None

            func_name = tokens[start_idx]  
            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)

            # Require parentheses after identifier
            if start_idx < len(tokens) and is_token(tokens, start_idx, "("):
                print(f"Found function with parameters: {func_name}")
                has_params = True
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
                
                # Parse parameters
                is_valid, new_idx = parameters.func_params(tokens, start_idx)
                if not is_valid:
                    print(f"Error: Invalid parameters in function definition ")
                    return False, None
                
                start_idx = new_idx  
                start_idx = skip_spaces(tokens, start_idx)

                # Expect closing parenthesis
                if not (start_idx < len(tokens) and is_token(tokens, start_idx, ")")):
                    print(f"Error: Expected ')' or ',' ")
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    if display_error(line_number, line_text, f"Expected ')' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
                
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
            else:
                # No '(' found after identifier — invalid
                print(f"Error: Expected '(' after function name ")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected '(' after function name , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None

            # Optional assignment
            if start_idx < len(tokens) and is_token(tokens, start_idx, "="):
                print(f"Found function assignment for {func_name}")
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)

                if not (start_idx < len(tokens) and is_token(tokens, start_idx, "Identifier")):
                    print(f"Error: Expected identifier after '=' ")
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    if display_error(line_number, line_text, f"Expected Identifier after =, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None

                assigned_func = tokens[start_idx]
                print(f"Valid parameterized function assignment: {func_name}() = {assigned_func}")
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
            else:
                print(f"Valid function call with parameters: {func_name}()")

            # Expect semicolon at the end
            if not (start_idx < len(tokens) and is_token(tokens, start_idx, ";")):
                print(f"Error: Expected ';' or '=' ")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected ';' or '=' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None

            print(f"Valid function statement: {func_name}")
            start_idx += 1  
            return True, start_idx

        
        @staticmethod
        def if_statement(tokens, start_idx):
            
            if not is_token(tokens, start_idx, '('):
                print(f"Error: Expected '(' after 'if' ")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected '('  , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
        
            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)

            
            is_valid, new_idx = conditional.conditional_block(tokens, start_idx)
            if not is_valid:
                print(f"Error: Invalid condition in if statement ")
                
                
                return False, None

            start_idx = new_idx  
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, ')'):
                print(f"Error: Expected ')' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'} in if statement")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected ')' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None

            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, '{'):
                print(f"Error: Expected '{{' , found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected '{{' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None

            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)
            
            # Check if this is an empty if statement body
            # Empty bodies have a pattern of open brace, possible spaces/newlines, then close brace
            empty_body_check = start_idx
            empty_body_check = skip_spaces(tokens, empty_body_check)
            
            if empty_body_check < len(tokens) and tokens[empty_body_check][0] == '}':
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                # Output the error message
                if display_error(line_number, line_text, f"Empty if statement body is not allowed"):
                         return False, None
                print(f"EMPTY IF STATEMENT DETECTED at line {line_number}")
            
            # Check for invalid if statement body statements BEFORE parsing the body
            check_idx = start_idx
            check_idx = skip_spaces(tokens, check_idx)
            
            # Check for specific invalid tokens that should not be directly inside an if body
            invalid_direct_tokens = ['elif', 'else']
            if check_idx < len(tokens) and any(tokens[check_idx][0] == token for token in invalid_direct_tokens):
                invalid_token = tokens[check_idx][0]
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, check_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected express, if, Identifier, prod, func, for, while, or if , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
            
            # If it's not empty, proceed with normal parsing
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
                print(f"Error: Expected '}}' , found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected '}}' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                    return False, None
            
            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)

            
            has_else = False
            
            while start_idx < len(tokens):
                if is_token(tokens, start_idx, 'elif'):
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    if not is_token(tokens, start_idx, '('):
                        print(f"Error: Expected '(' after 'elif' ")
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        if display_error(line_number, line_text, f"Expected '(' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
                    
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)

                    is_valid, new_idx = conditional.conditional_block(tokens, start_idx)
                    if not is_valid:
                        print(f"Error: Invalid condition in if statement ")
                        return False, None
                    
                    
                    start_idx = new_idx
                    start_idx = skip_spaces(tokens, start_idx)

                    if not is_token(tokens, start_idx, ')'):
                        print(f"Error: Expected ')'  in elif statement")
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        if display_error(line_number, line_text, f"Expected ')' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
                    
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)

                    if not is_token(tokens, start_idx, '{'):
                        print(f"Error: Expected '{{' after elif condition ")
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        if display_error(line_number, line_text, f"Expected '{{' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
                        
                    
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    # Check if this is an empty elif statement body
                    # Empty bodies have a pattern of open brace, possible spaces/newlines, then close brace
                    empty_body_check = start_idx
                    empty_body_check = skip_spaces(tokens, empty_body_check)
                    
                    if empty_body_check < len(tokens) and tokens[empty_body_check][0] == '}':
                        # We found an empty elif statement body!
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        # Output the error message
                        if display_error(line_number, line_text, f"Empty elif statement body is not allowed"):
                         return False, None
                        print(f"EMPTY ELIF STATEMENT DETECTED at line {line_number}")
                        
                    
                    # Check for invalid elif statement body statements BEFORE parsing the body
                    check_idx = start_idx
                    check_idx = skip_spaces(tokens, check_idx)
                    
                    # Check for specific invalid tokens that should not be directly inside an elif body
                    invalid_direct_tokens = ['elif', 'else']
                    if check_idx < len(tokens) and any(tokens[check_idx][0] == token for token in invalid_direct_tokens):
                        invalid_token = tokens[check_idx][0]
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, check_idx, display_lines, get_line_number)
                        if display_error(line_number, line_text, f"Expected express, if, Identifier, prod, func, for, while, or if , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
                        
                    
                    # If it's not empty, proceed with normal parsing
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
                        print(f"Error: Expected '}}' ")
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        if display_error(line_number, line_text, f"Expected '}}' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
                    
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    
                    

                elif is_token(tokens, start_idx, 'else'):
                    if has_else:
                        print("Error: Multiple else statements are not allowed")
                        return False, None
                        
                    has_else = True
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)

                    if not is_token(tokens, start_idx, '{'):
                        print(f"Error: Expected '{{' after 'else' ")
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        if display_error(line_number, line_text, f"Expected '{{' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
                    
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    # Check if this is an empty else statement body
                    # Empty bodies have a pattern of open brace, possible spaces/newlines, then close brace
                    empty_body_check = start_idx
                    empty_body_check = skip_spaces(tokens, empty_body_check)
                    
                    if empty_body_check < len(tokens) and tokens[empty_body_check][0] == '}':
                        # We found an empty else statement body!
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        # Output the error message
                        if display_error(line_number, line_text, f"Empty else statement body is not allowed"):
                         return False, None
                        print(f"EMPTY ELSE STATEMENT DETECTED at line {line_number}")
                    
                    # Check for invalid else statement body statements BEFORE parsing the body
                    check_idx = start_idx
                    check_idx = skip_spaces(tokens, check_idx)
                    
                    # Check for specific invalid tokens that should not be directly inside an else body
                    invalid_direct_tokens = ['elif', 'else']
                    if check_idx < len(tokens) and any(tokens[check_idx][0] == token for token in invalid_direct_tokens):
                        invalid_token = tokens[check_idx][0]
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, check_idx, display_lines, get_line_number)
                        if display_error(line_number, line_text, f"Expected express, if, Identifier, prod, func, for, while, or if , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
                    
                    # If it's not empty, proceed with normal parsing
                    is_valid, new_idx = program.body_statements(tokens, start_idx)
                    if not is_valid:
                        return False, None

                    start_idx = new_idx
                    start_idx = skip_spaces(tokens, start_idx)

                    if not is_token(tokens, start_idx, '}'):
                        print(f"Error: Expected '}}' ")
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        if display_error(line_number, line_text, f"Expected '}}' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
                    
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    
                    break

                else:
                    
                    break
            
            return True, start_idx  

        @staticmethod
        def inside_loop_statement(tokens, start_idx):
            print(f"DEBUG SYNTAX: Starting inside_loop_statement ")
            start_idx = skip_spaces(tokens, start_idx)
            
            
            if start_idx < len(tokens) and is_token(tokens, start_idx, "contig"):
                print("Found contig statement")
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
                
                
                if not is_token(tokens, start_idx, ";"):
                    print(f"Error: Expected ';' after 'contig' ")
                    return False, None
                
                start_idx += 1  
                return True, start_idx
            
            
            elif start_idx < len(tokens) and is_token(tokens, start_idx, "destroy"):
                print("Found destroy statement")
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
                
                
                if not is_token(tokens, start_idx, ";"):
                    print(f"Error: Expected ';' after 'destroy' ")
                    return False, None
                
                start_idx += 1  
                return True, start_idx
            
            
            else:
                print(f"Empty inside_loop_statement (lambda) but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return True, start_idx
           
        @staticmethod
        def express_statement(tokens, start_idx):
            print("inside express")
                    
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, '('):
                print(f"Error: Expected '(' ")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected '(' in express statement but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                    return False, None
                
            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)

            print(f"Before calling express_value: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check if we have a valid arithmetic value after the opening parenthesis
            if not (is_token(tokens, start_idx, 'numlit') or is_token(tokens, start_idx, 'Identifier') or 
                    is_token(tokens, start_idx, 'seq') or tokens[start_idx][0] in {'(', '!'} or 
                    tokens[start_idx][1] == 'string literal'  or 
                    is_token(tokens, start_idx, 'dom') or  
                    is_token(tokens, start_idx, 'rec')):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected numlit, Identifier, string literal, 'dom', 'rec' 'seq' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                    return False, None

            is_valid, new_idx = express.express_value(tokens, start_idx)
            if not is_valid:
                print(f"Error: Invalid expression ")
                return False, None

            print(f"After express_value, new index: {new_idx}, token: {tokens[new_idx] if new_idx < len(tokens) else 'EOF'}")

            start_idx = new_idx  
            start_idx = skip_spaces(tokens, start_idx)
            # Handle array indexing if present
            if is_token(tokens, start_idx, '['):
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                
                # Check for valid array index
                if not (start_idx < len(tokens) and tokens[start_idx][1] in ["Identifier", "numlit"]):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    if display_error(line_number, line_text, f"Expected Identifier or numlit but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
                
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                
                # Check for closing bracket
                if not is_token(tokens, start_idx, ']'):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    if display_error(line_number, line_text, f"Expected ']' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
                
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                
            if not is_token(tokens, start_idx, ')'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                print(f"Error: Expected ')' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'} in express statement")
                if display_error(line_number, line_text, f"Expected ')','==', '!=', '<', '>', '<=', '>=', '&&', '||' ,'+', '-', '*', '/', '%', '//' ,'**'  but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
                
            start_idx += 1 
            start_idx = skip_spaces(tokens, start_idx)

   
            if is_token(tokens, start_idx, ';'):
                return True, start_idx + 1
            else:
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                print(f"Error: Expected ';'  (line {line_number})")
                if display_error(line_number, line_text, f"Expected ';' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
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
        
            start_idx = skip_spaces(tokens, start_idx)
            
            
            has_array_stimuli = False
            if is_token(tokens, start_idx, '['):
                has_array_stimuli = True
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
                
                
                if not (start_idx < len(tokens) and tokens[start_idx][1] in ["Identifier", "numlit"]):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                    if display_error(line_number, line_text, f"Expected array index , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
                
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
                
                
                if not is_token(tokens, start_idx, ']'):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                    if display_error(line_number, line_text, f"Expected ']' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
                
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
                
                
                if is_token(tokens, start_idx, '['):
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    
                    if not (start_idx < len(tokens) and tokens[start_idx][1] in ["Identifier", "numlit"]):
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                        found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                        if display_error(line_number, line_text, f"Expected second array index , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
                    
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    
                    if not is_token(tokens, start_idx, ']'):
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                        found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                        if display_error(line_number, line_text, f"Expected ']' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
                    start_idx += 1  
            
            
            start_idx = skip_spaces(tokens, start_idx)

            
            if not any(is_token(tokens, start_idx, op) for op in assignment_op):

                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected an assignment operator , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
            
            
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            
            
            if is_token(tokens, start_idx, 'stimuli'):
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
                return statements.parse_stimuli_call(tokens, start_idx)
            else:
                
                start_idx = skip_spaces(tokens, start_idx)
                return statements.assignment_statement(tokens, start_idx - 2)

        @staticmethod
        def parse_stimuli_call(tokens, start_idx):


            start_idx = skip_spaces(tokens, start_idx)

            
            if not is_token(tokens, start_idx, '('):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                print(f"Error: Expected '('  (line {line_number})")
                if display_error(line_number, line_text, f"Expected '()' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)
            
            
            if not is_token(tokens, start_idx, 'string literal'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                print(f"Error: Expected string literal  (line {line_number})")
                if display_error(line_number, line_text, f"Expected string literal , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)
            
            
            if not is_token(tokens, start_idx, ')'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                print(f"Error: Expected ')'  (line {line_number}) in stimuli call")
                if display_error(line_number, line_text, f"Expected ')' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
            
            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)
            
            
            if not is_token(tokens, start_idx, ';'):
                print(f"Error: Expected ';'  )")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected ';' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None 

            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)
            return True, start_idx
    
        @staticmethod
        def assignment_statement(tokens, start_idx):
            


            print(f"DEBUG SYNTAX: Starting assignment_statement ")
            
            
            start_idx = skip_spaces(tokens, start_idx)
            
            
            if not any(is_token(tokens, start_idx, op) for op in assignment_op):
                # Check if the token itself is an equals sign (for no space case)
                if start_idx < len(tokens) and tokens[start_idx][0] == '=':
                    # Handle the case with no spaces - we found the equals sign token
                    pass  # Continue processing normally
                else:
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                    if display_error(line_number, line_text, f"Expected an assignment operator , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None

            
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            new_idx = start_idx
            
            is_valid, new_idx = statements.assignment_value(tokens, start_idx)
            if not is_valid:
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                if display_error(line_number, line_text, f"Expected a valid assignment value or stimuli , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
            
            start_idx = new_idx  
            start_idx = skip_spaces(tokens, start_idx)  
            
            
            while start_idx < len(tokens) and is_token(tokens, start_idx, ','):
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
                
                if not is_token(tokens, start_idx, 'Identifier'):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                    if display_error(line_number, line_text, f"Expected and Identifier , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None

                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)

                has_array_stimuli = False
                if is_token(tokens, start_idx, '['):
                    has_array_stimuli = True
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    
                    if start_idx < len(tokens) and tokens[start_idx][1] == "Identifier":
                        start_idx += 1  
                    
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    if not is_token(tokens, start_idx, ']'):
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                        found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                        if display_error(line_number, line_text, f"Expected ']' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
                    
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)

                if not any(is_token(tokens, start_idx, op) for op in assignment_op):
                    # Check if the token itself is an equals sign (for no space case)
                    if start_idx < len(tokens) and tokens[start_idx][0] == '=':
                        # Handle the case with no spaces - we found the equals sign token
                        pass  # Continue processing normally
                    else:
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                        found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                        if display_error(line_number, line_text, f"Expected an assigmnent operator , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                         return False, None
                
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
                
                
                is_valid, new_idx = statements.assignment_value(tokens, start_idx)
                if not is_valid:
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                    if display_error(line_number, line_text, f"Expected a valid assignment value , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
                
                start_idx = new_idx
                start_idx = skip_spaces(tokens, start_idx)

            
            has_array_stimuli = False
            if is_token(tokens, start_idx, '['):
                has_array_stimuli = True
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)

                if start_idx < len(tokens):

                    if is_token(tokens, start_idx, '::') or is_token(tokens, start_idx, ':'):
                        start_idx += 1  
                        start_idx = skip_spaces(tokens, start_idx)

                        # After skipping :: or :, we must now expect Identifier or numlit
                        if not is_token(tokens, start_idx, ["Identifier", "numlit"]):
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                            if display_error(line_number, line_text, f"Expected Identifier or numlit , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                                return False, None
                    elif not is_token(tokens, start_idx, ["Identifier", "numlit"]):
                        # Handles case like: [Identifier] with no colon
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        if display_error(line_number, line_text, f"Expected Identifier or numlit , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                            return False, None
                    
                    elif not is_token(tokens, start_idx, ["Identifier", "numlit"]):
                        start_idx += 1  
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        if display_error(line_number, line_text, f"Expected Identifier or numlit , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                            return False, None
                    
                start_idx += 1    
                start_idx = skip_spaces(tokens, start_idx)
                
                if not is_token(tokens, start_idx, ']'):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                    if display_error(line_number, line_text, f"Expected ']' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
                
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)

            
            if not is_token(tokens, start_idx, ';'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                if display_error(line_number, line_text, f"Expected ';' or arithmetic operator , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
            
            start_idx += 1  
            return True, start_idx
                            
        @staticmethod
        def for_loop_statement(tokens, start_idx):
            print(f"DEBUG SYNTAX: Starting for_loop_statement ")
            print(f"DEBUG SYNTAX: Current tokens: {tokens[start_idx:start_idx+5]}")
            
            # Immediately add an empty for loop check
            # Look for the pattern: '{' followed by spaces/newlines then '}'
            for i in range(start_idx, len(tokens)):
                if tokens[i][0] == '{':
                    brace_index = i
                    next_index = i + 1
                    while next_index < len(tokens) and tokens[next_index][1] in ['space', 'newline', 'tab']:
                        next_index += 1
                    if next_index < len(tokens) and tokens[next_index][0] == '}':
                        # Empty for loop found!
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        output_text.insert(tk.END, f" Syntax Error at line {line_number}: Empty for loop body is not allowed\n")
                        return False, None
                    break

            # ... rest of the code

            start_idx = skip_spaces(tokens, start_idx)

            

            
            if not (start_idx < len(tokens) and tokens[start_idx][0] == '('):
                print(f"ERROR: Expected '(' ")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                if display_error(line_number, line_text, f"Expected '(' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
            start_idx += 1  

            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and tokens[start_idx][0] == 'dose'):
                print(f"ERROR: Expected 'dose' for initialization ")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                if display_error(line_number, line_text, f"Expected dose keyword for initialization , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
            start_idx += 1  

            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and tokens[start_idx][1] == "Identifier"):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                if display_error(line_number, line_text, f"Expected an Identifier , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
            start_idx += 1  

            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and tokens[start_idx][0] == '='):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                if display_error(line_number, line_text, f"Expected an equal sign , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
            start_idx += 1  

            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and tokens[start_idx][1] in ["Identifier", "numlit"]):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                if display_error(line_number, line_text, f"Expected an Identifier or numlit , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                    return False, None
            start_idx += 1  

            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and tokens[start_idx][0] == ";"):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                if display_error(line_number, line_text, f"Expected ';' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
            start_idx += 1  

            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and tokens[start_idx][1] == "Identifier"):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                if display_error(line_number, line_text, f"Expected an Identifier , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
            start_idx += 1  

            start_idx = skip_spaces(tokens, start_idx)

            
            if start_idx >= len(tokens) or tokens[start_idx][0] not in conditional_op:
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                if display_error(line_number, line_text, f"Expected a conditional operator (<, >, <=, >=, !=, ==) , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
            start_idx += 1  

            start_idx = skip_spaces(tokens, start_idx)

            
            is_valid, new_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
            if not is_valid:
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                if display_error(line_number, line_text, f"Expected an Identifier or numlit , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None

            start_idx = new_idx
            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and tokens[start_idx][0] == ";"):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                if display_error(line_number, line_text, f"Expected ';' in for loop , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None

            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and (tokens[start_idx][1] == "Identifier" or tokens[start_idx][0] in ['++', '--'])):
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                if display_error(line_number, line_text, f"Expected Identifier or unary operator (++, --) , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None

            
            if tokens[start_idx][1] == "Identifier":
                
                identifier_token = tokens[start_idx]
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                
                
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
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    if display_error(line_number, line_text, f"Expected increment or decrement operator (++, --) , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
                start_idx += 1
            else:
                
                operator_token = tokens[start_idx]
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                
                
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
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                    if display_error(line_number, line_text, f"Expected an Identifier but found {found_token}"):
                        return False, None
                start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and tokens[start_idx][0] == ')'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                if display_error(line_number, line_text, f"Expected ')' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None

            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and tokens[start_idx][0] == '{'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                if display_error(line_number, line_text, f"Expected '{{' but found {found_token}"):
                        return False, None

            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)

            # Check if this is an empty for loop body
            # Empty bodies have a pattern of open brace, possible spaces/newlines, then close brace
            empty_body_check = start_idx
            empty_body_check = skip_spaces(tokens, empty_body_check)
            
            if empty_body_check < len(tokens) and tokens[empty_body_check][0] == '}':
                # We found an empty for loop body!
                line_number = get_line_number(tokens, empty_body_check)
                # Output the error message
                if display_error(line_number, line_text, f"Empty for loop body is not allowed"):
                        return False, None
                print(f"EMPTY FOR LOOP DETECTED at line {line_number}")
                
            
            # Check for invalid for loop body statements BEFORE parsing the body
            check_idx = start_idx
            check_idx = skip_spaces(tokens, check_idx)
            
            # Check for specific invalid tokens that should not be directly inside a for loop body
            invalid_direct_tokens = ['elif', 'else']
            if check_idx < len(tokens) and any(tokens[check_idx][0] == token for token in invalid_direct_tokens):
                invalid_token = tokens[check_idx][0]
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, check_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected express, Identifier, stimuli, if, prod, while, func, contig, destroy , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
            
            # If it's not empty, proceed with normal parsing
            is_valid, new_idx = program.body_statements(tokens, start_idx)
            if not is_valid:
                return False, None

            start_idx = new_idx    
            
            if not (start_idx < len(tokens) and tokens[start_idx][0] == '}'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                if display_error(line_number, line_text, f"Expected '}}' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
            
            start_idx += 1  
            return True, start_idx

        @staticmethod
        def prod_statement(tokens, start_idx):
            print("inside prod_statement")
            
            start_idx = skip_spaces(tokens, start_idx)
            
            # First check if we have a prod value
            is_valid, new_idx = statements.prod_value(tokens, start_idx)
            if not is_valid:
                return False, None
            
            # Update the index to after the prod value
            start_idx = new_idx
            start_idx = skip_spaces(tokens, start_idx)
            
            # Now check for the required semicolon
            if not is_token(tokens, start_idx, ';'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected ';' after prod value , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
            
            # Return success and the index after the semicolon
            return True, start_idx + 1

        @staticmethod
        def prod_value(tokens, start_idx):
            
            start_idx = skip_spaces(tokens, start_idx)
            
            # Empty prod value
            if start_idx >= len(tokens) or is_token(tokens, start_idx, ';'):
                print("Empty prod value")
                return True, start_idx
            
            # Check if we have an arithmetic operation starting
            if start_idx + 1 < len(tokens):
                next_idx = skip_spaces(tokens, start_idx + 1)
                if next_idx < len(tokens) and any(is_token(tokens, next_idx, op) for op in math_operator):
                    # This is an arithmetic expression
                    is_valid, new_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
                    if not is_valid:
                        # Get the operator that failed
                        op = tokens[next_idx][0] if next_idx < len(tokens) else 'EOF'
                        # line_number, line_tokens, line_text, line_index = find_matching_line(tokens, next_idx, display_lines, get_line_number)
                        # output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected arithmetic value after '{op}'\n")
                        # output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                    print(f"ARITH PROD - Successfully parsed arithmetic sequence, new index: {new_idx}")
                    return True, new_idx
            
            # Simple literals check
            if is_token(tokens, start_idx, literals) or is_token(tokens, start_idx, ''):
                print(f"Simple literal or identifier ")
                return True, start_idx + 1  
            
            # Try general arithmetic sequence
            is_valid, new_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
            if is_valid:
                print(f"ARITH PROD - Successfully parsed arithmetic sequence, new index: {new_idx}")
                return True, new_idx
            
            # Valid identifiers, dom/rec
            valid_tokens = ['Identifier', 'dom', 'rec']
            
            # Literals again (double check)
            if is_token(tokens, start_idx, literals):
                print(f"Simple literal ")
                return True, start_idx + 1  
            
            # Try valid tokens
            for token in valid_tokens:
                if is_token(tokens, start_idx, token):
                    print(f"{token} token ")
                    return True, start_idx + 1  
            
            # If we get here, the token is invalid
            print(f"Invalid token : {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            # Add specific error message for invalid prod value
            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
            if display_error(line_number, line_text, f"Expected prod value, or ';' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None

        @staticmethod
        def assignment_value(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)

            # Check for negation operator at the beginning
            has_negation = False
            if start_idx < len(tokens) and tokens[start_idx][0] == '!':
                print(f"Found negation operator '!' in assignment value ")
                has_negation = True
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
                
                # After negation, check for conditional expression
                if start_idx < len(tokens) and tokens[start_idx][0] == '(':
                    is_valid, new_idx = conditional.conditional_block(tokens, start_idx)
                    if is_valid:
                        print(f"Successfully parsed negated conditional expression")
                        return True, new_idx
            
            if is_token(tokens, start_idx, literals) or is_token(tokens, start_idx, 'Identifier'):
                
                next_idx = start_idx + 1
                next_idx = skip_spaces(tokens, next_idx)
                
                if next_idx < len(tokens) and any(is_token(tokens, next_idx, op) for op in math_operator):
                    print("ARITH PROD - Starting with literal or identifier")
                    
                    is_valid, new_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
                    if is_valid:
                        start_idx = new_idx
                        return True, start_idx
                    else:
                        
                        print("Arithmetic sequence parsing failed, falling back to simple literal/identifier")
                
                
                
                start_idx += 1  
                return True, start_idx
            
            
            is_valid, new_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
            if is_valid:
                print("ARITH PROD - Starting with non-literal/non-identifier")
                start_idx = new_idx
                return True, start_idx
            
            # Try parsing as a conditional expression (like 5 > 3)
            if not has_negation:  # If we already tried with negation, don't try again
                is_valid, new_idx = conditional.conditional_block(tokens, start_idx)
                if is_valid:
                    print("Successfully parsed conditional expression")
                    return True, new_idx
            
            return False, None
  
        @staticmethod
        def while_statement(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, '('):
                print(f"Error: Expected '(' after 'while' ")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected '(' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
            start_idx += 1  
            
            
            is_valid, new_idx = conditional.conditional_block(tokens, start_idx)
            if not is_valid:
                print(f"Error: Invalid condition in while statement ")
                return False, None

            start_idx = new_idx  
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, ')'):
                print(f"Error: Expected ')' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'} in while statement")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected ')' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None

            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, '{'):
                print(f"Error: Expected '{{' , found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected '{{' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None

            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)
            
            # Check if this is an empty while statement body
            # Empty bodies have a pattern of open brace, possible spaces/newlines, then close brace
            empty_body_check = start_idx
            empty_body_check = skip_spaces(tokens, empty_body_check)
            
            if empty_body_check < len(tokens) and tokens[empty_body_check][0] == '}':
                # We found an empty while loop body!
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                # Output the error message
                if display_error(line_number, line_text, f"Empty while statement body is not allowed"):
                        return False, None
                print(f"EMPTY WHILE LOOP DETECTED at line {line_number}")
            
            # Check for invalid while statement body statements BEFORE parsing the body
            check_idx = start_idx
            check_idx = skip_spaces(tokens, check_idx)
            
            # Check for specific invalid tokens that should not be directly inside a while body
            invalid_direct_tokens = ['elif', 'else']
            if check_idx < len(tokens) and any(tokens[check_idx][0] == token for token in invalid_direct_tokens):
                invalid_token = tokens[check_idx][0]
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, check_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected express, if, prod, Identifier, for, while, func, contig, destroy , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
            
            # If it's not empty, proceed with normal parsing
            is_valid, new_idx = program.body_statements(tokens, start_idx)
            if not is_valid:
                return False, None
                        
            start_idx = new_idx
            
            
            if not is_token(tokens, start_idx, '}'):
                print(f"Error: Expected '}}' , found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected '}}' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
            
            return True, start_idx + 1
    
        @staticmethod
        def contig_statement(tokens, start_idx):
            print("<contig_statement>")
            start_idx = skip_spaces(tokens, start_idx)
            
            # Check for semicolon after contig
            if not is_token(tokens, start_idx, ';'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected ';' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
                
            # Move past the semicolon
            start_idx += 1
            print("Successfully parsed contig statement")
            return True, start_idx
            
    class variables:
        @staticmethod
        def validate_doseval(tokens, start_idx):
            # Get line information for initial position

            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, 'Identifier'):
                # Include both token info and line index in error message
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected an Identifier , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None

            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            while True:
                if is_token(tokens, start_idx, '='):
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    if is_token(tokens, start_idx, 'numlit'):
                        number_sign = check_number_sign(tokens[start_idx])
                        if number_sign in {"quantval", "nequantliteral"}:
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                            if display_error(line_number, line_text, f"Expected a dose value , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                                return False, None
                        start_idx += 1
                    elif is_token(tokens, start_idx, 'Identifier'):
                        start_idx += 1
                    else:
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        if display_error(line_number, line_text, f"Expected a dose value , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                            return False, None
                    
                    start_idx = skip_spaces(tokens, start_idx)
                
                if is_token(tokens, start_idx, ';'):
                    return True, start_idx + 1
                
                if not is_token(tokens, start_idx, ','):
                    # Get updated line information for error
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    
                    if display_error(line_number, line_text, f"Expected a ',', '=', or ';' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
                
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                
                if not is_token(tokens, start_idx, 'Identifier'):
                    # Get updated line information for error
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    
                    if display_error(line_number, line_text, f"Expected an Identifier , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
                start_idx += 1
                
                start_idx = skip_spaces(tokens, start_idx)

        @staticmethod
        def validate_seqval(tokens, start_idx):
            
            start_idx = skip_spaces(tokens, start_idx)

            
            if not is_token(tokens, start_idx, 'Identifier'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected an Identifier , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                    return False, None

            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            while True:
                
                if is_token(tokens, start_idx, '='):
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    
                    if is_token(tokens, start_idx, 'string literal') or is_token(tokens, start_idx, 'Identifier'):
                        start_idx += 1

                    else:
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        if display_error(line_number, line_text, f"Expected seq literal or Identifier index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                            return False, None
                                        
                    start_idx = skip_spaces(tokens, start_idx)
                
                
                if is_token(tokens, start_idx, ';'):
                    return True, start_idx + 1
                
                if not is_token(tokens, start_idx, ','):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    if display_error(line_number, line_text, f"Expected a ',', '=', or ';' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
                
                
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                
                
                if not is_token(tokens, start_idx, 'Identifier'):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    if display_error(line_number, line_text, f"Expected an Identifier , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
                start_idx += 1
                
                start_idx = skip_spaces(tokens, start_idx)

                        
        @staticmethod
        def validate_alleleval(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)

            
            if not is_token(tokens, start_idx, 'Identifier'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected an Identifier , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                    return False, None

            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            while True:
                
                if is_token(tokens, start_idx, '='):
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    
                    if is_token(tokens, start_idx, 'dom'):
                        start_idx += 1
                    elif is_token(tokens, start_idx, 'rec'):
                        start_idx += 1
                    elif is_token(tokens, start_idx, 'Identifier'):
                        start_idx += 1
                    elif is_token(tokens, start_idx, 'numlit'):
                        start_idx += 1
                    else:
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        if display_error(line_number, line_text, f"Expected dom, rec, Identifier, or numlit , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                            return False, None
                                        
                    start_idx = skip_spaces(tokens, start_idx)
                
                
                if is_token(tokens, start_idx, ';'):
                    return True, start_idx + 1
                
                if not is_token(tokens, start_idx, ','):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    if display_error(line_number, line_text, f"Expected ',', '=', or ';' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
                
                
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                
                
                if not is_token(tokens, start_idx, 'Identifier'):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    if display_error(line_number, line_text, f"Expected Identifier , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
                start_idx += 1
                
                start_idx = skip_spaces(tokens, start_idx)

        @staticmethod
        def validate_quantval(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, 'Identifier'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected an Identifier , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                 return False, None
            
            start_idx += 1
            
            start_idx = skip_spaces(tokens, start_idx)
            
            while True:
                
                if is_token(tokens, start_idx, '='):
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    if is_token(tokens, start_idx, 'numlit'):
                        number_sign = check_number_sign(tokens[start_idx])
                        if number_sign in {"doseliteral", "neliteral"}:
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                            if display_error(line_number, line_text, f"Expected a quant value , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                                return False, None
                        start_idx += 1
                    elif is_token(tokens, start_idx, 'Identifier'):
                        start_idx += 1
                    else:
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        if display_error(line_number, line_text, f"Expected quant value , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                            return False, None
                    
                    start_idx = skip_spaces(tokens, start_idx)

                if is_token(tokens, start_idx, ';'):
                    return True, start_idx + 1
                
                if not is_token(tokens, start_idx, ','):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    if display_error(line_number, line_text, f"Expected ',', '=', or ';' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
                
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                
                if not is_token(tokens, start_idx, 'Identifier'):
                    return False, None
                start_idx += 1
                
                start_idx = skip_spaces(tokens, start_idx)

    class clust:
        @staticmethod
        def validate_clust_quantval(tokens, start_idx):
            

            print('<clust_quantval>')
            start_idx = skip_spaces(tokens, start_idx)

            
            if not is_token(tokens, start_idx, 'Identifier'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                if display_error(line_number, line_text, f"Expected an Identifier  , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                    return False, None
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            
            if not is_token(tokens, start_idx, '['):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                if display_error(line_number, line_text, f"Expected '[' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                    return False, None
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

                        
            if not (is_token(tokens, start_idx, 'numlit') or is_token(tokens, start_idx, 'Identifier')):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected a numlit or Identifier  , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                    return False, None

            # Only check number_sign if it's a numlit
            if is_token(tokens, start_idx, 'numlit'):
                number_sign = check_number_sign(tokens[start_idx])
                if number_sign in {"quantval", "nequantliteral"}:
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    if display_error(line_number, line_text, f"Expected quant value , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None

            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            
            if not is_token(tokens, start_idx, ']'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                if display_error(line_number, line_text, f"Expected ']' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                    return False, None
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            has_second_dimension = False
            if is_token(tokens, start_idx, '['):
                has_second_dimension = True
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                if not (is_token(tokens, start_idx, 'numlit') or is_token(tokens, start_idx, 'Identifier')):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    if display_error(line_number, line_text, f"Expected a numlit or Identifier , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None

                # Only check number_sign if it's a numlit
                if is_token(tokens, start_idx, 'numlit'):
                    number_sign = check_number_sign(tokens[start_idx])
                    if number_sign in {"quantval", "nequantliteral"}:
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        if display_error(line_number, line_text, f"Expected a quant value , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                            return False, None
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                if not is_token(tokens, start_idx, ']'):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    if display_error(line_number, line_text, f"Expected ']' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

            
            if is_token(tokens, start_idx, '='):
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                
                if not is_token(tokens, start_idx, '{'):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    if display_error(line_number, line_text, f"Expected '{{' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                
                if has_second_dimension:
                    # For 2D arrays, we expect the first token after '{' to be another '{'
                    if not is_token(tokens, start_idx, '{'):
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        if display_error(line_number, line_text, f"Expected '{{' for start of row in 2D array, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                            return False, None
                    
                    
                    while True:
                        if not is_token(tokens, start_idx, '{'):
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                            if display_error(line_number, line_text, f"Expected an '{{' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                                return False, None
                        start_idx += 1
                        start_idx = skip_spaces(tokens, start_idx)

                        
                        while True:
                            if not is_token(tokens, start_idx, 'numlit'):
                                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                                if display_error(line_number, line_text, f"Expected a numlit but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                                    return False, None

                            
                            number_sign = check_number_sign(tokens[start_idx])
                            if number_sign in {"neliteral", "doseliteral"}:
                                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                                if display_error(line_number, line_text, f"Expected a quant value but found {tokens[start_idx][0]}\n"):
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
                                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                                if display_error(line_number, line_text, f"Expected a closing brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                                    return False, None

                        start_idx = skip_spaces(tokens, start_idx)

                        if is_token(tokens, start_idx, ','):
                            start_idx += 1
                            start_idx = skip_spaces(tokens, start_idx)
                        elif is_token(tokens, start_idx, '}'):
                            start_idx += 1
                            break
                        else:
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                            if display_error(line_number, line_text, f"Expected a closing brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                                return False, None
                else:
                    
                    while True:
                        if not is_token(tokens, start_idx, 'numlit'):
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                            if display_error(line_number, line_text, f"Expected a numlit but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                                return False, None
                        
                        
                        number_sign = check_number_sign(tokens[start_idx])
                        if number_sign in {"neliteral", "doseliteral"}:
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                            if display_error(line_number, line_text, f"Expected a quant value but found {tokens[start_idx][0]}\n"):
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
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                            if display_error(line_number, line_text, f"Expected a closing brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                                return False, None

            
            if not is_token(tokens, start_idx, ';'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                if display_error(line_number, line_text, f"Expected a semicolon but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                    return False, None

            return True, start_idx + 1

        @staticmethod
        def validate_clust_doseval(tokens, start_idx):
            print('<clust_dose>')
            start_idx = skip_spaces(tokens, start_idx)

            
            if not is_token(tokens, start_idx, 'Identifier'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                if display_error(line_number, line_text, f"Expected an identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                    return False, None
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            
            if not is_token(tokens, start_idx, '['):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                if display_error(line_number, line_text, f"Expected an open bracket but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                    return False, None
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            
            if not (is_token(tokens, start_idx, 'numlit') or is_token(tokens, start_idx, 'Identifier')):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                if display_error(line_number, line_text, f"Expected a numlit or identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                    return False, None

            # Only check number_sign if it's a numlit
            if is_token(tokens, start_idx, 'numlit'):
                number_sign = check_number_sign(tokens[start_idx])
                if number_sign in {"quantval", "nequantliteral"}:
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    if display_error(line_number, line_text, f"Expected a quant value but found {tokens[start_idx][0]}\n"):
                        return False, None

            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            
            if not is_token(tokens, start_idx, ']'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                if display_error(line_number, line_text, f"Expected a closing bracket but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                    return False, None
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            
            has_second_dimension = False
            if is_token(tokens, start_idx, '['):
                has_second_dimension = True
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                if not (is_token(tokens, start_idx, 'numlit') or is_token(tokens, start_idx, 'Identifier')):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    if display_error(line_number, line_text, f"Expected a numlit or identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                        return False, None

                # Only check number_sign if it's a numlit
                if is_token(tokens, start_idx, 'numlit'):
                    number_sign = check_number_sign(tokens[start_idx])
                    if number_sign in {"quantval", "nequantliteral"}:
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                        if display_error(line_number, line_text, f"Expected a quant value but found {tokens[start_idx][0]}\n"):
                            return False, None
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                if not is_token(tokens, start_idx, ']'):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    if display_error(line_number, line_text, f"Expected a closing bracket but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                        return False, None
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

            
            if is_token(tokens, start_idx, '='):
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                
                if not is_token(tokens, start_idx, '{'):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    if display_error(line_number, line_text, f"Expected an opening brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                        return False, None
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                
                # Check if we should expect nested braces for a 2D array
                if has_second_dimension:
                    # For 2D arrays, we expect the first token after '{' to be another '{'
                    if not is_token(tokens, start_idx, '{'):
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        if display_error(line_number, line_text, f"Expected '{{' for start of row in 2D array, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                            return False, None
                    
                    
                    while True:
                        if not is_token(tokens, start_idx, '{'):
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                            if display_error(line_number, line_text, f"Expected an opening brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                                return False, None
                        start_idx += 1
                        start_idx = skip_spaces(tokens, start_idx)

                        
                        while True:
                            if not is_token(tokens, start_idx, 'numlit'):
                                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                                if display_error(line_number, line_text, f"Expected a numlit but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                                    return False, None

                            
                            number_sign = check_number_sign(tokens[start_idx])
                            if number_sign in {"quantval", "nequantliteral"}:
                                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                                if display_error(line_number, line_text, f"Expected a dose value but found {tokens[start_idx][0]}\n"):
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
                                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                                if display_error(line_number, line_text, f"Expected a closing brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                                    return False, None

                        start_idx = skip_spaces(tokens, start_idx)

                        if is_token(tokens, start_idx, ','):
                            start_idx += 1
                            start_idx = skip_spaces(tokens, start_idx)
                        elif is_token(tokens, start_idx, '}'):
                            start_idx += 1
                            break
                        else:
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                            if display_error(line_number, line_text, f"Expected a closing brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                                return False, None
                else:
                    
                    while True:
                        if not is_token(tokens, start_idx, 'numlit'):
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                            if display_error(line_number, line_text, f"Expected a numlit but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                                return False, None

                        
                        number_sign = check_number_sign(tokens[start_idx])
                        if number_sign in {"quantval", "nequantliteral"}:
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                            if display_error(line_number, line_text, f"Expected a dose value but found {tokens[start_idx][0]}\n"):
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
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                            if display_error(line_number, line_text, f"Expected a closing brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                              return False, None

            start_idx = skip_spaces(tokens, start_idx)
            if not is_token(tokens, start_idx, ';'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                if display_error(line_number, line_text, f"Expected a semicolon but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                    return False, None

            return True, start_idx + 1

        @staticmethod
        def validate_clust_seqval(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After initial skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")


            
            if not is_token(tokens, start_idx, 'Identifier'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                print(f"DEBUG SYNTAX: Expected Identifier , found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                if display_error(line_number, line_text, f"Expected an identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                    return False, None
            print(f"DEBUG SYNTAX: Found Identifier: {tokens[start_idx]}")
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            
            if not is_token(tokens, start_idx, '['):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                print(f"DEBUG SYNTAX: Expected '[' , found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                if display_error(line_number, line_text, f"Expected an open bracket but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                    return False, None
            print(f"DEBUG SYNTAX: Found opening bracket")
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            
            if not (is_token(tokens, start_idx, 'numlit') or is_token(tokens, start_idx, 'Identifier')):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected a numlit or identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                    return False, None

            # Only check number_sign if it's a numlit
            if is_token(tokens, start_idx, 'numlit'):
                number_sign = check_number_sign(tokens[start_idx])
                if number_sign in {"quantval", "nequantliteral"}:
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    if display_error(line_number, line_text, f"Expected a quant value but found {tokens[start_idx][0]}\n"):
                        return False, None
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            
            if not is_token(tokens, start_idx, ']'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                print(f"DEBUG SYNTAX: Expected ']' , found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                if display_error(line_number, line_text, f"Expected a closing bracket\n"):
                    return False, None
            print(f"DEBUG SYNTAX: Found closing bracket")
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            has_second_dimension = False
            if is_token(tokens, start_idx, '['):
                has_second_dimension = True
                print(f"DEBUG SYNTAX: Found second dimension opening bracket")
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                print(f"DEBUG SYNTAX: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

                if not (is_token(tokens, start_idx, 'numlit') or is_token(tokens, start_idx, 'Identifier')):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    if display_error(line_number, line_text, f"Expected a numlit or identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                        return False, None

                # Only check number_sign if it's a numlit
                if is_token(tokens, start_idx, 'numlit'):
                    number_sign = check_number_sign(tokens[start_idx])
                    if number_sign in {"quantval", "nequantliteral"}:
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        if display_error(line_number, line_text, f"Expected a quant value but found {tokens[start_idx][0]}\n"):
                            return False, None
                print(f"DEBUG SYNTAX: Found second dimension size: {tokens[start_idx]}")
                start_idx += 1

                start_idx = skip_spaces(tokens, start_idx)
                print(f"DEBUG SYNTAX: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                
                if not is_token(tokens, start_idx, ']'):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    print(f"DEBUG SYNTAX: Expected ']' , found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                    if display_error(line_number, line_text, f"Expected a closing bracket\n"):
                        return False, None
                print(f"DEBUG SYNTAX: Found second dimension closing bracket")
                start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            
            if is_token(tokens, start_idx, '='):
                print(f"DEBUG SYNTAX: Found equals sign, parsing initialization")
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                
                if not is_token(tokens, start_idx, '{'):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    print(f"DEBUG SYNTAX: Expected '{{' , found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                    if display_error(line_number, line_text, f"Expected an opening brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                     return False, None
                print(f"DEBUG SYNTAX: Found opening brace")
                start_idx += 1

                start_idx = skip_spaces(tokens, start_idx)
                print(f"DEBUG SYNTAX: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

                
                if has_second_dimension:
                    # For 2D arrays, we expect the first token after '{' to be another '{'
                    if not is_token(tokens, start_idx, '{'):
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        if display_error(line_number, line_text, f"Expected '{{' for start of row in 2D array, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                            return False, None
                    
                    
                    while True:
                        if not is_token(tokens, start_idx, '{'):
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                            if display_error(line_number, line_text, f"Expected an opening brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                                return False, None
                        start_idx += 1
                        start_idx = skip_spaces(tokens, start_idx)

                        
                        while True:
                            if not is_token(tokens, start_idx, 'string literal') :
                                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                                if display_error(line_number, line_text, f"Expected a string literal but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
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
                                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                                if display_error(line_number, line_text, f"Expected a closing brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                                    return False, None

                        start_idx = skip_spaces(tokens, start_idx)

                        if is_token(tokens, start_idx, ','):
                            start_idx += 1
                            start_idx = skip_spaces(tokens, start_idx)
                        elif is_token(tokens, start_idx, '}'):
                            start_idx += 1
                            break
                        else:
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                            if display_error(line_number, line_text, f"Expected a closing brace , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                                return False, None
                else:
                    print(f"DEBUG SYNTAX: Detected 1D array (direct values)")
                    
                    while True:
                        if not is_token(tokens, start_idx, 'string literal') :
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                            print(f"DEBUG SYNTAX: Expected string literal or Identifier , found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                            if display_error(line_number, line_text, f"Expected a string literal but found {tokens[start_idx][0]}\n"):
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
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                            print(f"DEBUG SYNTAX: Expected ',' or '}}' , found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                            if display_error(line_number, line_text, f"Expected a comma or closing brace but found {tokens[start_idx][0]}\n"):
                                return False, None

            
            if not is_token(tokens, start_idx, ';'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                print(f"DEBUG SYNTAX: Expected ';' , found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                if display_error(line_number, line_text, f"Expected a semicolon but found {tokens[start_idx][0]}\n"):
                    return False, None
            print(f"DEBUG SYNTAX: Found semicolon, array declaration complete")

            return True, start_idx + 1

    class parameters:
        @staticmethod
        def parse_params(tokens, start_idx):
            print("Parsing parameters...")
            current_token = tokens[start_idx] if start_idx < len(tokens) else None
            
            

            param_types = {"dose", "quant", "seq", "allele"}
            params = []
            start_idx = skip_spaces(tokens, start_idx)

            
            if start_idx >= len(tokens) or tokens[start_idx][0] not in param_types:
                print(f"No parameters found .")
                return True, [], start_idx

            if tokens[start_idx][0] == ")":
                print(f"No parameters found .")
                return True, [], start_idx
            
            while start_idx < len(tokens):
                
                if tokens[start_idx][0] not in param_types:
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    print(f"Error: Expected parameter type , found {tokens[start_idx]}")
                    if display_error(line_number, line_text, f"Expected a 'dose', 'quant', 'seq', or 'allele' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                        return False, None, start_idx

                param_type = tokens[start_idx][0]
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                
                if start_idx >= len(tokens) or tokens[start_idx][1] != "Identifier":
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    print(f"Error: Expected Identifier after parameter type '{param_type}' ")
                    if display_error(line_number, line_text, f"Expected an Identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
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


            start_idx = skip_spaces(tokens, start_idx)
            print(f"Index after skipping initial spaces: {start_idx}")

            if start_idx < len(tokens) and tokens[start_idx][0] == ")":
                print(f"Empty Parameter List")
                return True, start_idx
            
            if start_idx >= len(tokens):
                print(f">> No parameters found .")
                return True, start_idx

            while start_idx < len(tokens):
                print(f"Processing parameter at index: {start_idx}")

                
                if tokens[start_idx][1] == "Identifier" or tokens[start_idx][1] == "numlit":
                    print(f"Parameter value detected: {tokens[start_idx][0]}")
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)
                    print(f"Index after skipping spaces post-value: {start_idx}")
                else:
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    print(f">> ERROR: Expected identifier or numlit ")
                    if display_error(line_number, line_text, f"Expected an identifier or numlit but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                        return False, None

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


            print("In arithmetic sequence")
            
            
            is_valid, new_idx = arithmetic.arithmetic_value(tokens, start_idx)
            if not is_valid:    
                return False, None
            
            start_idx = new_idx
            start_idx = skip_spaces(tokens, start_idx)

            
            
            is_valid, new_idx = arithmetic.arithmetic_sequence_tail(tokens, start_idx)
            if not is_valid:
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected numlit, '(' or Identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                    return False, None
                
            return True, new_idx

        @staticmethod
        def arithmetic_value(tokens, start_idx):


            start_idx = skip_spaces(tokens, start_idx)
            
            if start_idx >= len(tokens):
                print(f"ERROR: Expected token , but reached end of input")
                return False, None
            
            
            if is_token(tokens, start_idx, '('):
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                
                
                is_valid, new_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
                if not is_valid:
                    return False, None
                
                start_idx = new_idx
                start_idx = skip_spaces(tokens, start_idx)
                
                
                if is_token(tokens, start_idx, ')'):
                    return True, start_idx + 1
                else:
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    if display_error(line_number, line_text, f"Expected a closing parenthesis or math operator but found {tokens[start_idx][0]}\n"):
                        return False, None
            
            
            elif is_token(tokens, start_idx, 'seq'):
                is_valid, cast_value, new_idx = express.seq_type_cast(tokens, start_idx)
                if is_valid:
                    return True, new_idx
                return False, None
            
            
            elif is_token(tokens, start_idx, 'numlit') or is_token(tokens, start_idx, 'Identifier') or \
                 is_token(tokens, start_idx, 'string literal') or is_token(tokens, start_idx, 'dom') or \
                 is_token(tokens, start_idx, 'rec'):
                return True, start_idx + 1
            

            return False, None

        @staticmethod
        def arithmetic_sequence_tail(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)

            
            if start_idx >= len(tokens) or is_token(tokens, start_idx, ')'):
                return True, start_idx

            
            if start_idx < len(tokens) and any(is_token(tokens, start_idx, op) for op in (math_operator | conditional_op)):
                operator = tokens[start_idx][0]
                operator_idx = start_idx + 1
                operator_idx = skip_spaces(tokens, operator_idx)

                
                is_valid, new_idx = arithmetic.arithmetic_value(tokens, operator_idx)
                if not is_valid:
                    return False, None

                start_idx = new_idx

                
                return arithmetic.arithmetic_sequence_tail(tokens, start_idx)

            
            return True, start_idx

    class express:
        @staticmethod
        def express_value(tokens, start_idx):
                    print("<express_value>")
                    exp_literals = {'string literal', 'numlit', 'Identifier', 'dom', 'rec'}
                    values = []  
                    print(f"Initial start_idx: {start_idx}")
                    start_idx = skip_spaces(tokens, start_idx)
                    print(f"After skipping spaces, start_idx: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

                    if start_idx < len(tokens) and tokens[start_idx][1] == 'Identifier':

                        
                        # Use lookahead to determine what kind of expression we're parsing
                        lookahead_idx = skip_spaces(tokens, start_idx + 1)
                        
                        # Case 1: Array reference (identifier followed by '[')
                        if lookahead_idx < len(tokens) and tokens[lookahead_idx][0] == '[':
                            print("Found '[', parsing as express_value_id_tail")
                            is_valid, next_idx = express.express_value_id_tail(tokens, start_idx + 1)
                            if not is_valid:
                                print("Failed to parse express_value_id_tail")
                                print("Syntax Error: Expected valid array index")
                                return False, None
                            
                            start_idx = next_idx
                        
                        # Case 2: Part of arithmetic (followed by arithmetic operators)
                        elif lookahead_idx < len(tokens) and tokens[lookahead_idx][0] in {'+', '-', '*', '/', '%', '//' ,'**'}:
                            print("Identifier followed by arithmetic operator, parsing as arithmetic_sequence")
                            is_valid, new_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
                            if is_valid:
                                print("Parsed arithmetic sequence in express_value.")
                                return True, new_idx
                            else:
                                print("Failed to parse as arithmetic, falling back to simple identifier")
                                values.append(identifier)
                                start_idx = lookahead_idx
                        
                        # Case 3: Part of conditional expression
                        elif lookahead_idx < len(tokens) and tokens[lookahead_idx][0] in {'==', '!=', '<', '>', '<=', '>=', '&&', '||'}:
                            print("Identifier followed by conditional operator, parsing as conditional_block")
                            is_valid, new_idx = conditional.conditional_block(tokens, start_idx)
                            if is_valid:
                                print("Parsed conditional block in express_value.")
                                return True, new_idx
                            else:
                                print("Failed to parse as conditional, falling back to simple identifier")
                                values.append(identifier)
                                start_idx = lookahead_idx
                        
                        # Case 4: Simple identifier
                        elif lookahead_idx < len(tokens) and tokens[lookahead_idx][0] == ")":
                            start_idx = lookahead_idx
                            
                        else:
                            start_idx += 1  
                            start_idx = skip_spaces(tokens, start_idx)
                            
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                            if display_error(line_number, line_text, f"Expected ')', '==', '!=', '<', '>', '<=', '>=', '&&', '||' ,'+', '-', '*', '/', '%', '//' ,'**' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                                return False, None
                    
                    
                    # Only try parsing conditional/arithmetic if we haven't already handled the token
                    elif start_idx < len(tokens) and (
                        tokens[start_idx][0] in {'(', '!'} or 
                        tokens[start_idx][1] == 'numlit'
                        ):

                        if tokens[start_idx][0] in {'('}:
                            is_valid, new_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
                            if is_valid:
                                print("Parsed arithmetic sequence in express_value.")
                                return True, new_idx      
                            else:
                                # Handle invalid arithmetic sequence case
                                return False, None
                            
                            
                        # Use lookahead to determine what kind of expression we're parsing
                        lookahead_idx = skip_spaces(tokens, start_idx + 1)
                    
                                  
                        # Case 2: Part of arithmetic (followed by arithmetic operators)
                        if lookahead_idx < len(tokens) and tokens[lookahead_idx][0] in {'+', '-', '*', '/', '%', '//' ,'**'}:
                            print("Identifier followed by arithmetic operator, parsing as arithmetic_sequence")
                            is_valid, new_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
                            if is_valid:
                                print("Parsed arithmetic sequence in express_value.")
                                return True, new_idx
                            else:
                                print("Failed to parse as arithmetic, falling back to simple identifier")
                                values.append(identifier)
                                start_idx = lookahead_idx
                        
                        # Case 3: Part of conditional expression
                        elif lookahead_idx < len(tokens) and tokens[lookahead_idx][0] in {'==', '!=', '<', '>', '<=', '>=', '&&', '||'}:
                            print("Identifier followed by conditional operator, parsing as conditional_block")
                            is_valid, new_idx = conditional.conditional_block(tokens, start_idx)
                            if is_valid:
                                print("Parsed conditional block in express_value.")
                                return True, new_idx
                            else:
                                print("Failed to parse as conditional, falling back to simple identifier")
                                values.append(identifier)
                                start_idx = lookahead_idx
                        
                        # Case 4: Simple identifier
                        elif lookahead_idx < len(tokens) and tokens[lookahead_idx][0] == ")":
                            start_idx = lookahead_idx

                        else:
                            start_idx += 1  
                            start_idx = skip_spaces(tokens, start_idx)
                            
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                            if display_error(line_number, line_text, f"Expected '==', '!=', '<', '>', '<=', '>=', '&&', '||' ,'+', '-', '*', '/', '%', '//' ,'**' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n"):
                                return False, None

                    elif start_idx < len(tokens) and is_token(tokens, start_idx, 'string literal'):
                        lookahead_idx = skip_spaces(tokens, start_idx + 1)
                        if lookahead_idx < len(tokens) and tokens[lookahead_idx][0] == "+":
                            print("Found 'string literal' followed by '+', parsing as seq_concat")
                            is_valid, concat_value, next_idx = express.seq_concat(tokens, start_idx)
                            if not is_valid:
                                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                                print("Failed to parse seq_concat")
                                print("Syntax Error: Expected plus sign")
                                if display_error(line_number, line_text, f"Expected a plus sign but found {tokens[start_idx][0]}\n"):
                                    return False, None
                            values.append(concat_value)
                            start_idx = next_idx
                        else:
                            values.append(tokens[start_idx][0])  
                            print(f"Added '{tokens[start_idx][0]}' to values: {values}")
                            start_idx += 1  
                    
                    elif start_idx < len(tokens) and tokens[start_idx][1] in exp_literals:
                        
                        values.append(tokens[start_idx][0])  
                        print(f"Added '{tokens[start_idx][0]}' to values: {values}")
                        start_idx += 1  
                    else:
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                        print(f"Error: Expected a literal or seq type cast at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                        print("Syntax Error: Expected a literal or sequence type")
                        if display_error(line_number, line_text, f"Expected a literal but found {tokens[start_idx][0]}\n"):
                            return False, None
                    
                    
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    
                    while start_idx < len(tokens) and (is_token(tokens, start_idx, ',') or is_token(tokens, start_idx, '+')):               
                        
                        start_idx += 1  
                        print(f"Moved past comma, new start_idx: {start_idx}")
                        
                        start_idx = skip_spaces(tokens, start_idx)
                        print(f"After skipping spaces, start_idx: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                        
                        
                        if start_idx < len(tokens) and is_token(tokens, start_idx, 'seq'):
                            print("Found 'seq' keyword after comma, parsing as seq_type_cast")
                            is_valid, cast_value, next_idx = express.seq_type_cast(tokens, start_idx)
                            if is_valid and cast_value:  
                                print(f"Successfully parsed seq_type_cast after comma: {cast_value}")
                                
                                
                                lookahead_idx = skip_spaces(tokens, next_idx)
                                if lookahead_idx < len(tokens) and tokens[lookahead_idx][0] == "+":
                                    print("Found 'seq' followed by '+' after comma, parsing as seq_concat")
                                    
                                    
                                    start_idx = skip_spaces(tokens, start_idx)
                                    is_valid, concat_value, next_idx = express.seq_concat(tokens, start_idx)
                                    if not is_valid:
                                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                                        print("Failed to parse seq_concat after comma")
                                        print("Syntax Error: Expected plus sign")
                                        if display_error(line_number, line_text, f"Expected a plus sign but found {tokens[start_idx][0]}\n"):
                                            return False, None
                                    
                                    
                                    values.append(concat_value)
                                    start_idx = next_idx
                                    continue
                                else:
                                    
                                    values.append(cast_value)
                                    start_idx = next_idx
                                    continue
                            else:
                                print("Failed to parse seq_type_cast after comma")
                                print("Syntax Error: Expected valid sequence type")
                                return False, None
                        
                        # Modified: Handle Identifier after comma the same way as numlit
                        elif start_idx < len(tokens) and tokens[start_idx][1] == 'Identifier':
                            identifier = tokens[start_idx][0]
                            print(f"Found identifier after comma: {identifier}")
                            
                            lookahead_idx = skip_spaces(tokens, start_idx + 1)
                            
                            # Check for operators after identifier (same as numlit behavior)
                            if lookahead_idx < len(tokens) and tokens[lookahead_idx][0] in ('+', '-', '*', '/', '%', '='):  
                                print("Found 'Identifier' followed by operator after comma, trying to parse as arithmetic sequence")
                                
                                is_valid, next_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
                                if is_valid:
                                    print("Successfully parsed arithmetic sequence after comma")
                                    start_idx = next_idx
                                    continue
                                else:
                                    print("Failed to parse arithmetic sequence after comma, trying seq_concat")
                                    is_valid, concat_value, next_idx = express.seq_concat(tokens, start_idx)
                                    if not is_valid:
                                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                                        print("Failed to parse seq_concat after comma")
                                        print("Syntax Error: Expected plus sign")
                                        if display_error(line_number, line_text, f"Expected a plus sign but found {tokens[start_idx][0]}\n"):
                                            return False, None
                                    values.append(concat_value)
                                    start_idx = next_idx
                                    continue
                            # Check for array reference
                            elif lookahead_idx < len(tokens) and tokens[lookahead_idx][0] == '[':
                                print("Found '[' after comma, parsing as express_value_id_tail")
                                is_valid, id_tail_value, next_idx = express.express_value_id_tail(tokens, start_idx + 1, identifier)
                                if not is_valid:
                                    print("Failed to parse express_value_id_tail after comma")
                                    print("Syntax Error: Expected valid array index")
                                    return False, None
                                values.append(id_tail_value)
                                start_idx = next_idx
                                continue
                            else:
                                # Simple identifier (same as numlit behavior)
                                values.append(tokens[start_idx][0])  
                                print(f"Added '{tokens[start_idx][0]}' to values: {values}")
                                start_idx += 1  
                                continue
                        
                        elif start_idx < len(tokens) and is_token(tokens, start_idx, 'numlit'):
                            lookahead_idx = skip_spaces(tokens, start_idx + 1)
                            if lookahead_idx < len(tokens) and tokens[lookahead_idx][0] == "+":  
                                print("Found 'numlit' followed by '+' after comma, trying to parse as arithmetic sequence")
                                
                                is_valid, next_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
                                if is_valid:
                                    print("Successfully parsed arithmetic sequence after comma")
                                    
                                    
                                    start_idx = next_idx
                                    continue
                                else:
                                    
                                    print("Failed to parse arithmetic sequence after comma, trying seq_concat")
                                    is_valid, concat_value, next_idx = express.seq_concat(tokens, start_idx)
                                    if not is_valid:
                                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                                        print("Failed to parse seq_concat after comma")
                                        print("Syntax Error: Expected plus sign")
                                        if display_error(line_number, line_text, f"Expected a plus sign but found {tokens[start_idx][0]}\n"):
                                            return False, None
                                        
                                    
                                    values.append(concat_value)
                                    start_idx = next_idx
                                    continue
                            else:
                                
                                values.append(tokens[start_idx][0])  
                                print(f"Added '{tokens[start_idx][0]}' to values: {values}")
                                start_idx += 1  
                                continue
                        
                        
                        elif start_idx < len(tokens) and is_token(tokens, start_idx, 'string literal'):
                            lookahead_idx = skip_spaces(tokens, start_idx + 1)
                            if lookahead_idx < len(tokens) and tokens[lookahead_idx][0] == "+":
                                print("Found 'string literal' followed by '+' after comma, parsing as seq_concat")
                                is_valid, concat_value, next_idx = express.seq_concat(tokens, start_idx)
                                if not is_valid:
                                    print("Failed to parse seq_concat after comma")
                                    print("Syntax Error: Expected plus sign")
                                    return False, None
                                    
                                
                                values.append(concat_value)
                                start_idx = next_idx
                                continue
                            else:
                                
                                values.append(tokens[start_idx][0])  
                                print(f"Added '{tokens[start_idx][0]}' to values: {values}")
                                start_idx += 1  
                                continue
                        
                        
                        
                        if start_idx >= len(tokens) or tokens[start_idx][1] not in exp_literals:
                            print(f"Error: Expected a literal or seq type cast after ',' at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                            print("Syntax Error: Expected a literal or sequence type after comma")
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                            if display_error(line_number, line_text, f"Expected a literal but found {tokens[start_idx][0]}\n"):
                                return False, None
                        
                        values.append(tokens[start_idx][0])  
                        print(f"Added '{tokens[start_idx][0]}' to values: {values}")
                        
                        start_idx += 1  
                        start_idx = skip_spaces(tokens, start_idx)  
                    
                    print("Parsing successful:", values)
                    return True, start_idx

        @staticmethod
        def seq_concat(tokens, start_idx):

            print("<seq_concat>")
            start_idx = skip_spaces(tokens, start_idx)
            
            
            first_value = None
            
            
            if is_token(tokens, start_idx, 'string literal'):
                first_value = tokens[start_idx][1]
                print(f"First string literal: {first_value}")
                start_idx += 1
            
            elif is_token(tokens, start_idx, 'Identifier'):
                first_value = tokens[start_idx][0]  
                print(f"First identifier: {first_value}")
                start_idx += 1
            
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
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                print(f"Error: Expected string literal, identifier, or seq_type_cast at index {start_idx}")
                if display_error(line_number, line_text, f"Expected a string literal, Identifier or seq but found {tokens[start_idx][0]}\n"):
                    return False, None
            
            start_idx = skip_spaces(tokens, start_idx)
            
            
            if start_idx >= len(tokens) or tokens[start_idx][0] != "+":
                print(f"Error: Expected '+' at index {start_idx}")
                return False, None, start_idx
            
            
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            
            
            second_value = None
            
            
            if is_token(tokens, start_idx, 'string literal'):
                second_value = tokens[start_idx][1]
                print(f"Second string literal: {second_value}")
                start_idx += 1
            
            elif is_token(tokens, start_idx, 'Identifier'):
                second_value = tokens[start_idx][0]  
                print(f"Second identifier: {second_value}")
                start_idx += 1
            
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
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                print(f"Error: Expected string literal, identifier, or seq_type_cast at index {start_idx}")
                if display_error(line_number, line_text, f"Expected a string literal, Identifier or seq but found {tokens[start_idx][0]}\n"):
                    return False, None
            
            
            result = f"{first_value} + {second_value}"  
            print(f"Concatenated result: {result}")
            
            
            is_valid, additional_result, next_idx = express.seq_concat_tail(tokens, start_idx, result)
            if not is_valid:
                return False, None, start_idx
            
            
            if additional_result:
                result = additional_result
            
            return True, result, next_idx

        @staticmethod
        def seq_concat_tail(tokens, start_idx, current_value=""):

            print("<seq_concat_tail>")
            
            start_idx = skip_spaces(tokens, start_idx)
            
            if start_idx >= len(tokens) or tokens[start_idx][0] != "+":
                
                print(f"No further concatenation at index {start_idx}, final value: {current_value}")
                return True, current_value, start_idx
            
            
            print(f"Found '+' at index {start_idx}, proceeding with concatenation")
            
            
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            
            
            next_value = None
            if is_token(tokens, start_idx, 'string literal'):
                
                next_value = tokens[start_idx][1]
                print(f"Next value is a string literal: {next_value}")
                start_idx += 1
            elif is_token(tokens, start_idx, 'seq'):
                
                is_valid, cast_value, next_idx = express.seq_type_cast(tokens, start_idx)
                if not is_valid or not cast_value:
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    print(f"Error: Invalid seq function call at index {start_idx}")
                    if display_error(line_number, line_text, f"Expected 'seq' but found {tokens[start_idx][0]}\n"):
                        return False, None
                next_value = cast_value
                print(f"Next value is a seq function call: {next_value}")
                start_idx = next_idx
            else:
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                print(f"Error: Expected string literal or seq function call at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                if display_error(line_number, line_text, f"Expected a string literal or seq but found {tokens[start_idx][0]}\n"):
                    return False, None
            
            
            updated_value = current_value + next_value
            print(f"Updated concatenation: {updated_value}")
            
            
            return express.seq_concat_tail(tokens, start_idx, updated_value)

        @staticmethod
        def seq_type_cast(tokens, start_idx):
            print("<seq_type_cast>")
            
            if start_idx >= len(tokens) or tokens[start_idx][1] != "seq":
                return False, "Error: Missing 'seq' keyword", start_idx

            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)

            
            if start_idx >= len(tokens) or tokens[start_idx][0] != '(':
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected '(' but found {tokens[start_idx][0]}\n"):
                    return False, None

            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)

            
            if start_idx >= len(tokens) or tokens[start_idx][1] != "Identifier":
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected an Identifier but found {tokens[start_idx][0]}\n"):
                    return False, None

            identifier = tokens[start_idx][0]
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            
            array_expr = ""
            while start_idx < len(tokens) and tokens[start_idx][0] == '[':
                array_expr += '['
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)

                
                if start_idx >= len(tokens) or (tokens[start_idx][1] != "Identifier" and tokens[start_idx][1] != "numlit"):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    if display_error(line_number, line_text, f"Expected Identifier or numlit but found {tokens[start_idx][0]}\n"):
                        return False, None

                array_expr += tokens[start_idx][0]
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                
                if start_idx >= len(tokens) or tokens[start_idx][0] != ']':
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    if display_error(line_number, line_text, f"Expected ']' but found {tokens[start_idx][0]}\n"):
                        return False, None

                array_expr += ']'
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

            
            if start_idx >= len(tokens) or tokens[start_idx][0] != ')':
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected a ')' but found {tokens[start_idx][0]}\n"):
                    return False, None
            result = f"seq({identifier}{array_expr})"
            return True, result, start_idx + 1  



        @staticmethod
        def express_value_id_tail(tokens, start_idx):
            print("<express_value_id_tail>")
            start_idx = skip_spaces(tokens, start_idx)
            
            
            if start_idx < len(tokens) and tokens[start_idx][0] == '[':
                print("Found '[', parsing as express_array_value")
                is_valid,  next_idx = express.express_array_value(tokens, start_idx)
                if not is_valid:
                    print("Failed to parse express_array_value")
                    return False,  start_idx
                
                return True,  next_idx
            
            
            print("No array access, returning original identifier")
            return True,  start_idx

        
        @staticmethod
        def express_array_value(tokens, start_idx, dimension=0):
            print(f"<express_array_value> dimension={dimension}")

            if start_idx >= len(tokens) or tokens[start_idx][0] != '[':
                print(f"Error: Expected '[' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None, start_idx

            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            start_index = None
            end_index = None
            step_value = None
            has_slice = False
            found_content = False  # Track if we found at least one numlit or Identifier

            # Special case: Check for a slice that starts with ':' or '::' directly
            if start_idx < len(tokens) and tokens[start_idx][0] in (':', '::'):
                has_slice = True
                
                print("Found '::' token for start of slice with step")
                start_idx += 1  # Skip the '::' token
                start_idx = skip_spaces(tokens, start_idx)
                
                # Parse step value if present
                if start_idx < len(tokens) and tokens[start_idx][1] in ('numlit', 'Identifier'):
                    step_value = tokens[start_idx][0]
                    found_content = True  # Mark that we found content
                    print(f"Found step value: {step_value}")
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)
                else:
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    if display_error(line_number, line_text, f"Expected 'numlit' or 'Identifier' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None
                
            else:
                # Standard case: starts with an index or is empty
                # Parse start index (could be empty)
                if start_idx < len(tokens) and tokens[start_idx][1] in ('numlit', 'Identifier'):
                    start_index = tokens[start_idx][0]
                    found_content = True  # Mark that we found content
                    print(f"Found start index: {start_index}")
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)

                # Check if it's a slice
                if is_token(tokens, start_idx, '::') or is_token(tokens, start_idx, ':'):
                    has_slice = True
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)

                    # Parse end index
                    if start_idx < len(tokens) and tokens[start_idx][1] in ('numlit', 'Identifier'):
                        end_index = tokens[start_idx][0]
                        found_content = True  # Mark that we found content
                        print(f"Found end index: {end_index}")
                        start_idx += 1
                        start_idx = skip_spaces(tokens, start_idx)

                    # Check for second colon for step
                    if start_idx < len(tokens) and tokens[start_idx][0] == ':':
                        start_idx += 1
                        start_idx = skip_spaces(tokens, start_idx)

                        if start_idx < len(tokens) and tokens[start_idx][1] in ('numlit', 'Identifier'):
                            step_value = tokens[start_idx][0]
                            found_content = True  # Mark that we found content
                            print(f"Found step value: {step_value}")
                            start_idx += 1
                            start_idx = skip_spaces(tokens, start_idx)

            # Check if we found at least one numlit or Identifier
            if not found_content:
                print("Error: Array access requires at least one 'numlit' or 'Identifier'")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected ':', '::', 'numlit' or 'Identifier' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                    return False, None

            # Check for closing bracket
            if start_idx >= len(tokens) or tokens[start_idx][0] != ']':
                print(f"Error: Expected ']' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected ']' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, None

            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            return True, start_idx


        @staticmethod
        def express_array_splice(tokens, start_idx):
            print("<express_array_splice>")

            # Check for first colon
            if start_idx >= len(tokens) or tokens[start_idx][0] not in (':', '::'):
                print(f"Error: Expected ':' or '::' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                if display_error(line_number, line_text, f"Expected ':' or '::' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                    return False, [], start_idx

            # Save the initial colon
            splice_ops = [tokens[start_idx][0]]  # either ':' or '::'
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            # Check for optional second colon (for step)
            if start_idx < len(tokens) and tokens[start_idx][0] in (':', '::'):
                print("Found double colon '::' for step value")
                splice_ops[0] = '::'  # Replace ':' with '::' to reflect full slice notation
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                # Check for step value (must be numlit or Identifier)
                if start_idx < len(tokens) and tokens[start_idx][1] in ('numlit', 'Identifier'):
                    step_value = tokens[start_idx][0]
                    print(f"Found step value: {step_value}")
                    splice_ops.append(f":{step_value}")
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)
                else:
                    # Step value is expected but not found
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    if display_error(line_number, line_text, f"Expected step value after '::' , but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}"):
                        return False, [], start_idx

            return True, splice_ops, start_idx

        @staticmethod
        def express_array_splice_tail(tokens, start_idx):
            print("<express_array_splice_tail>")
            
            # This method is no longer needed since we handle the double colon directly in express_array_splice
            # Keeping it for compatibility but it just returns empty
            print("No further splices")
            return True, [], start_idx

    def process_tokens(tokens):
        print("\n========== PROCESS TOKENS ==========")  

        lines = []
        current_statement = []
        current_line = []
        current_line_number = 1
        brace_count = 0  
        i = 0
        display_lines = []
        current_display_line = []

        while i < len(tokens):
            token = tokens[i]
            print(f"PROCESS TOKENS Processing token {i}: {token}")  

            if token is None or len(token) < 2:  
                print(f"PROCESS TOKENS Skipping invalid token at index {i}")
                i += 1
                continue  

            # If we encounter 'act' when brace_count is 0, start a new statement
            if token[1] == 'act' and brace_count == 0 and current_statement:
                print(f"PROCESS TOKENS Found 'act' at index {i} with brace_count={brace_count}, ending current statement and starting new one")
                lines.append(current_statement)
                current_statement = []
                # Don't clear current_line because we still need to add the current token to it

            if token[1] != "newline":
                current_display_line.append(token)

            if token[1] == "newline":
                print(f"PROCESS TOKENS Newline found at line {current_line_number}, processing current_line: {current_line}")
                if current_display_line:
                    display_lines.append({
                        'tokens': current_display_line.copy(),
                        'line_number': current_line_number
                    })
                    current_display_line = []
                if current_line:  
                    current_statement.extend(current_line)
                    current_line = []
                current_line_number += 1
            else:
                if token[1] == '{':
                    brace_count += 1
                    print(f"PROCESS TOKENS Opening brace found, brace_count: {brace_count}")
                elif token[1] == '}':
                    brace_count -= 1
                    print(f"PROCESS TOKENS Closing brace found, brace_count: {brace_count}")
                current_line.append(token)

                # Only split at '}' if not followed by a semicolon
                if token[1] == '}' and brace_count == 0:
                    print("PROCESS TOKENS Closing brace detected, checking for following keywords or semicolon.")
                    next_index = i + 1

                    # Skip spaces and newlines
                    while next_index < len(tokens) and tokens[next_index][1] in ["space", "newline"]:
                        next_index += 1

                    # Debug: print what token is after the closing brace
                    if next_index < len(tokens):
                        print(f"PROCESS TOKENS Next token after '}}' is: {tokens[next_index]}")
                    else:
                        print("PROCESS TOKENS No token after '}' (end of tokens)")

                    # If next token is a semicolon, include it in current_line
                    if next_index < len(tokens) and tokens[next_index][1] == ';':
                        print("PROCESS TOKENS Found semicolon after '}', including it in current_line.")
                        i = next_index  # move index to semicolon
                        token = tokens[i]
                        current_line.append(token)  # add ';' to current_line

                    if next_index >= len(tokens) or tokens[next_index][1] not in ["else", "while", "do", "elif"]:
                        print(f"PROCESS TOKENS Block end detected at index {i}, adding current_line: {current_line}")
                        current_statement.extend(current_line)
                        lines.append(current_statement)
                        current_statement = []
                        current_line = []
            i += 1

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

        print("\nTokens by Line:")
        for i, line in enumerate(display_lines):
            line_number = line['line_number']
            tokens_str = ' '.join([f"{t[0]} ({t[1]})" for t in line['tokens']])
            print(f"Line {line_number} [{i}]: {tokens_str}")

        print("\nStatements:")
        for i, statement in enumerate(lines):
            if not statement:
                continue
                
            # Show the first few tokens
            tokens_str = ' '.join([f"{t[0]} ({t[1]})" for t in statement[:min(10, len(statement))]])
            
            # Identify function statements
            if statement[0][1] == 'act':
                if len(statement) > 2 and statement[2][1] == 'Identifier':
                    print(f"Statement {i}: FUNCTION '{statement[2][0]}' - {tokens_str}...")
                elif len(statement) > 2 and statement[2][1] == 'gene':
                    print(f"Statement {i}: MAIN FUNCTION - {tokens_str}...")
                else:
                    print(f"Statement {i}: FUNCTION (unknown) - {tokens_str}...")
            else:
                print(f"Statement {i}: {tokens_str}...")

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

    # Process all program elements (global declarations and functions) in a unified way
    print("\nProcessing program declarations and functions:")
    for line_num, line_tokens in enumerate(token_lines, start=1):
        line_tokens = [token for token in line_tokens if token[1] != 'newline']

        if not line_tokens:
            continue

        first_token = line_tokens[0][1] if line_tokens else None
        print(f"Checking line {line_num}: First token: {first_token}")
        
        # Print the first few tokens to help with debugging
        first_few = line_tokens[:min(10, len(line_tokens))]
        print(f"  First few tokens: {[(t[0], t[1]) for t in first_few]}")
            
        # Handle comments and multiline comments
        if first_token in ["comment", "multiline_comment"]:
            print(f"Found {first_token} in line {line_num}")
            
            # Skip this line if it's just a comment
            valid_tokens_after_comment = {"space", "newline", "token", "tab", "_G", "act"}
            
            # Check next tokens until we find something meaningful
            next_token_idx = 1
            while next_token_idx < len(line_tokens):
                next_token = line_tokens[next_token_idx][1]
                
                # If we find _G or act, process them accordingly
                if next_token in ["_G", "act"]:
                    # Update first_token and continue with normal processing
                    first_token = next_token
                    line_tokens = line_tokens[next_token_idx:]
                    break
                    
                # If we find invalid tokens after comments, report error
                if next_token not in valid_tokens_after_comment:
                    line_text = ' '.join([t[0] for t in line_tokens])
                    if display_error(line_num, line_text, f"Unexpected token '{next_token}' after comment\n"):
                        valid_syntax = False
                    break
                    
                next_token_idx += 1
                
            # If we've reached the end but didn't find _G or act, just continue to next line
            if next_token_idx >= len(line_tokens) or not first_token in ["_G", "act"]:
                continue
                
        if first_token in ["_G", "act"]:
            print(f"Found {first_token} in line {line_num}")
            
            # For global declarations, collect tokens up to semicolon 
            tokens_to_validate = line_tokens
            if first_token == "_G":
                # Check for missing semicolon in global declaration
                has_semicolon = any(token[1] == ';' for token in line_tokens)
                if not has_semicolon and line_num < len(token_lines):
                    next_line = token_lines[line_num]
                    if next_line and next_line[0][1] == 'act':
                        # Found act without semicolon - report error
                        line_text = ' '.join([t[0] for t in line_tokens])
                        # Use line_num directly instead of find_matching_line since we already know the line numlit
                        output_text.insert(tk.END, f"Syntax error at line {line_num}: Expected a semicolon but found '{next_line[0][0]}'\n")
                        output_text.insert(tk.END, f"Line {line_num}: {line_text}\n")
                        valid_syntax = False
                        break
 
            for pattern in program_pattern:
                is_valid, next_idx, _ = validate_syntax_pattern(tokens_to_validate, pattern)
                print(f"  Pattern validation: is_valid={is_valid}, next_idx={next_idx}")
                if is_valid:
                    if first_token == "_G":
                        # Process global declarations
                        global_tokens = []
                        for token in line_tokens:
                            global_tokens.append(token)
                            if token[1] == ';':
                                break
                        
                        is_valid_program, sign = program.global_handling(global_tokens, next_idx)
                    else:
                        # Process function declarations
                        is_valid_program, sign = program.main_function(line_tokens, next_idx)
                    
                    print(f"  {first_token} processing result: is_valid_program={is_valid_program}")
                    if not is_valid_program:
                        valid_syntax = False
                    break
        
        else:
            output_text.insert(tk.END, f"Syntax Error: Unexpected token, expected _G or act\n")


            valid_syntax = False
            break
    if valid_syntax:
        output_text.delete('1.0', tk.END)
        # Check if a main function was found in the code
        if not program.main_function_seen:
            output_text.insert(tk.END, "Syntax Error: No main function (gene) found in the program. A valid GenomeX program must have a main function.\n")
            print("\nSyntax Error: No main function found!")
            return True
        output_text.insert(tk.END, "You May Push!\n")
        print("\nAll statements are valid!")
    else:
        output_text.yview(tk.END)
        print("\nSyntax Error!")

    return not valid_syntax
