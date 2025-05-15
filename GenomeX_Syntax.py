import GenomeX_Lexer as gxl
import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
import sys  
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
            return -1  
        
        line_number = 1
        for i in range(index):
            if tokens[i][1] == "newline":
                line_number += 1
        
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
                # Sort by line number and find the last non-empty line
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
                            return False, start_idx
                                    
                    
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
                                output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected dose, quant, seq, or allele but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
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
                                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected valid clust datatype but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
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
                            output_text.insert(tk.END, f"Expected valid datatype but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
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

            def global_statements(tokens, start_idx):
                print("<global_statements> ENTRY: start_idx=", start_idx, "tokens=", tokens)
                keywords = {"dose", "quant", "seq", "allele"}
                
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
                
                # Process a single global statement
                start_idx = skip_spaces(tokens, start_idx)
                print("[global_statements] After skip_spaces: start_idx=", start_idx)
                keywords = ['dose', 'quant', 'seq', 'allele', 'clust', 'perms']

                # First check if we have reached 'act' - this should be handled specially
                if is_token(tokens, start_idx, "act"):
                    print("[global_statements] Found 'act' keyword at idx", start_idx)
                    # We'll handle 'act' as a special case and return to the caller
                    check_statements = True
                    return check_statements, start_idx
                    
                # Handle _G token - this should NOT be present here as it should be handled by global_handling
                if is_token(tokens, start_idx, "_G"):
                    print("[global_statements] Found unexpected '_G' token at idx", start_idx)
                    # We've found another _G token - this is valid, but should be handled by global_handling
                    check_statements = True
                    return check_statements, start_idx

                for keyword in keywords:
                    if is_token(tokens, start_idx, keyword):
                        print(f"[global_statements] Found keyword: {keyword} at idx {start_idx}")
                
                if is_token(tokens, start_idx, 'perms'):
                    print("[global_statements] <perms> block at idx", start_idx)
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)
                    print("[global_statements] After perms skip_spaces: start_idx=", start_idx)
                    if not any(is_token(tokens, start_idx, perms_type) for perms_type in perms_parsers):
                        print("[global_statements] Invalid perms type at idx", start_idx)
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected an valid datatype but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None  
                    for perms_type, parser_func in perms_parsers.items():
                        if is_token(tokens, start_idx, perms_type):
                            print(f"[global_statements] Parsing perms_type: {perms_type} at idx {start_idx}")
                            start_idx += 1  
                            start_idx = skip_spaces(tokens, start_idx)
                            is_valid, new_idx = parser_func(tokens, start_idx)
                            print(f"[global_statements] perms_type {perms_type} is_valid={is_valid}, new_idx={new_idx}")
                            if not is_valid:
                                print(f"[global_statements] Invalid perms {perms_type} statement at idx {start_idx}")
                                return False, None
                            start_idx = new_idx
                            start_idx = skip_spaces(tokens, start_idx)
                            print(f"[global_statements] Successfully parsed perms {perms_type}, new start_idx={start_idx}")
                            break  
                    # Successfully parsed, mark statement as checked
                    check_statements = True
                    return check_statements, start_idx
                elif is_token(tokens, start_idx, 'clust'):
                    print("[global_statements] <clust> block at idx", start_idx)
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)
                    print("[global_statements] After clust skip_spaces: start_idx=", start_idx)
                    if not any(is_token(tokens, start_idx, clust_type) for clust_type in clust_parse):
                        print("[global_statements] Invalid clust type at idx", start_idx)
                        return False, None
                    for clust_type, parser_func in clust_parse.items():
                        if is_token(tokens, start_idx, clust_type):
                            print(f"[global_statements] Parsing clust_type: {clust_type} at idx {start_idx}")
                            start_idx += 1  
                            start_idx = skip_spaces(tokens, start_idx)
                            is_valid, new_idx = parser_func(tokens, start_idx)
                            print(f"[global_statements] clust_type {clust_type} is_valid={is_valid}, new_idx={new_idx}")
                            if not is_valid:
                                print(f"[global_statements] Invalid clust {clust_type} statement at idx {start_idx}")
                                return False, None
                            start_idx = new_idx
                            start_idx = skip_spaces(tokens, start_idx)
                            print(f"[global_statements] Successfully parsed clust {clust_type}, new start_idx={start_idx}")
                            break  
                    # Successfully parsed, mark statement as checked
                    check_statements = True
                    return check_statements, start_idx
                if not any(is_token(tokens, start_idx, L_type) for L_type in local_parse):
                    print("[global_statements] Invalid global data type at idx", start_idx)
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a valid datatype (dose, quant, seq, allele) but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None   
                for G_type, parser_func in local_parse.items():
                    if is_token(tokens, start_idx, G_type):
                        print(f"[global_statements] Parsing G_type: {G_type} at idx {start_idx}")
                        start_idx += 1  
                        start_idx = skip_spaces(tokens, start_idx)
                        is_valid, new_idx = parser_func(tokens, start_idx)
                        print(f"[global_statements] G_type {G_type} is_valid={is_valid}, new_idx={new_idx}")
                        if not is_valid:
                            print(f"[global_statements] Invalid {G_type} statement at idx {start_idx}")
                            return False, None
                        start_idx = new_idx
                        start_idx = skip_spaces(tokens, start_idx)
                        print(f"[global_statements] Successfully parsed {G_type}, new start_idx={start_idx}")
                        break
                
                # Successfully parsed, mark statement as checked
                check_statements = True
                return check_statements, start_idx

            def global_handling(tokens, start_idx):
                print("<global_handling> ENTRY: start_idx=", start_idx, "tokens=", tokens)
                
                # Skip the _G token if present
                if is_token(tokens, start_idx, "_G"):
                    start_idx += 1  # Skip '_G' token
                    start_idx = skip_spaces(tokens, start_idx)
                
                # Process the global statement
                check_statements, new_idx = program.global_statements(tokens, start_idx)
                print("[global_handling] After global_statements: check_statements=", check_statements, "new_idx=", new_idx)
                if new_idx is None:
                    print("[global_handling] Error in global statements")
                    return False, None
                
                # Check next non-space token for 'act' or '_G'
                next_idx = skip_spaces(tokens, new_idx)
                print(f"[global_handling] Next index after global_statements: {next_idx}")
                
                if next_idx < len(tokens):
                    if is_token(tokens, next_idx, "act"):
                        print("[global_handling] Found 'act' keyword, dispatching to main_function...")
                        result, end_idx = program.main_function(tokens, next_idx)
                        # Propagate error status from main_function/user_defined_function
                        if program.user_defined_function_error:
                            print("[global_handling] Error detected in user_defined_function")
                            return False, None
                        return result, end_idx
                    elif is_token(tokens, next_idx, "_G"):
                        print("[global_handling] Found '_G' token, dispatching to global_handling recursively...")
                        result, end_idx = program.global_handling(tokens, next_idx)
                        # Propagate error status from recursive call
                        if program.user_defined_function_error:
                            print("[global_handling] Error detected in user_defined_function (from recursive call)")
                            return False, None
                        return result, end_idx
                    else:
                        print(f"[global_handling] Expected '_G' or 'act' but found '{tokens[next_idx][0]}' at idx {next_idx}")
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, next_idx, display_lines, get_line_number)
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected '_G' or 'act' after global statement but found {tokens[next_idx][0]}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                else:
                    print("[global_handling] End of tokens reached, expected 'act' keyword")
                    output_text.insert(tk.END, f"Syntax Error: Expected 'act' keyword after global statements but reached end of file\n")
                    return False, None
                
                print("[global_handling] Returning True, start_idx=", next_idx)
                return True, next_idx

            def user_defined_function(tokens, start_idx):
                print("Parsing user defined function...")
                
                start_idx = skip_spaces(tokens, start_idx)
                
                # Handle void return type
                if is_token(tokens, start_idx, 'void'):
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)

                # Check for function name
                if not (start_idx < len(tokens) and tokens[start_idx][1] == "Identifier"):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    print(f"Error: Expected function name (Identifier) at index {start_idx}")
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected function name (Identifier) at index {start_idx} but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    program.user_defined_function_error = True  
                    return False, None

                # Store the function name for better error messages
                func_name = tokens[start_idx][0] if start_idx < len(tokens) else "unknown"
                
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)

                # Check for opening parenthesis
                if not is_token(tokens, start_idx, '('):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    print(f"Error: Expected '(' after function name at index {start_idx}")
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected '(' after function name but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    program.user_defined_function_error = True  
                    return False, None
                    
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)

                # Parse parameters
                is_valid, params, new_idx = parameters.parse_params(tokens, start_idx)
                if not is_valid:
                    # line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    # print(f"Error: Invalid parameters in function declaration at index {start_idx}")
                    # output_text.insert(tk.END, f"Syntax Error at line {line_number}: Invalid parameters in function declaration\n")
                    # output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    program.user_defined_function_error = True  
                    return False, None

                start_idx = new_idx  
                start_idx = skip_spaces(tokens, start_idx)

                # Check for closing parenthesis
                if not is_token(tokens, start_idx, ')'):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    print(f"Error: Expected ')' at index {start_idx}, but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}")
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected ')' but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    program.user_defined_function_error = True  
                    return False, None
                
                start_idx += 1 
                start_idx = skip_spaces(tokens, start_idx)

                # Check for opening brace
                if not is_token(tokens, start_idx, '{'):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    print("Missing opening brace for function block")
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected '{{' for function block but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    program.user_defined_function_error = True  
                    return False, None
                
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)

                # Parse function body
                check_statements, new_idx = program.body_statements(tokens, start_idx)
                
                if new_idx is None:
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    print("Error in user defined function statements")
                    # output_text.insert(tk.END, f"Syntax Error at line {line_number}: Invalid statement in function body\n")
                    # output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
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
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Function '{func_name}' has incomplete implementation\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        program.user_defined_function_error = True  
                        return False, None
                    
                    return True, start_idx + 1
                else:
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    print("Missing closing brace for user defined function")
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected closing brace '}}', '_L' or valid statement but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    program.user_defined_function_error = True  
                    return False, None

                
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
                        print(f"[main_function] Error: Expected 'gene' after 'act' at index {start_idx}")
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected 'gene' or Identifier after 'act' but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
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
                        print(f"[main_function] Error: Expected '(' after 'gene' at index {start_idx}")
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected '(' after 'gene' but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                    
                    start_idx += 1  # Skip '(' token
                    start_idx = skip_spaces(tokens, start_idx)

                    # Check for unexpected semicolon
                    if is_token(tokens, start_idx, ';'):
                        print(f"[main_function] Error: Unexpected ';' at index {start_idx}")
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Unexpected ';' in function parameters\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None

                    # Check for closing parenthesis
                    if not is_token(tokens, start_idx, ')'):
                        print(f"[main_function] Error: Expected ')' at index {start_idx}, but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}")
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected ')' after 'gene' parameters but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                    
                    start_idx += 1  # Skip ')' token
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    # Check for opening brace
                    if not is_token(tokens, start_idx, '{'):
                        print("[main_function] Missing opening brace for main function block")
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected '{{' for main function block but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                    
                    start_idx += 1  # Skip '{' token
                    start_idx = skip_spaces(tokens, start_idx)

                    # Parse function body statements
                    check_statements, new_idx = program.body_statements(tokens, start_idx)
                    print(f"[main_function] After body_statements: check_statements={check_statements}, new_idx={new_idx}")

                    if new_idx is None:
                        print("[main_function] Error in main function body statements")
                        return False, None
                        
                    start_idx = new_idx
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    # Check for closing brace
                    if is_token(tokens, start_idx, '}'):
                        print("[main_function] Found closing brace for main function")
                        
                        if not check_statements:
                            print("[main_function] Error: No statements found in main function")
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected valid statements in main function\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None
                            
                        return True, start_idx + 1
                    else:
                        print("[main_function] Missing closing brace for main function")
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected closing brace '}}', '_L' or valid statement for main function but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                
                # Handle user-defined functions
                else:
                    if program.main_function_seen:
                        print("[main_function] Error: User-defined functions must be declared before the main function")
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: User-defined functions must be declared before the main function\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        program.user_defined_function_error = True  
                        return False, None
                        
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
                    
                    
                    
                    print(f"Error: Invalid conditions_base at index {start_idx}")
                    return False, None
                return True, new_idx
            
            @staticmethod
            def conditions_base(tokens, start_idx):
                
                print("<conditions_base>")
                start_idx = skip_spaces(tokens, start_idx)
                
                
                has_negation = False
                if start_idx < len(tokens) and tokens[start_idx][0] == '!':
                    print(f"Found negation operator '!' at index {start_idx}")
                    has_negation = True
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)
                
                
                is_valid, new_idx = conditional.condition_value(tokens, start_idx)
                if not is_valid:
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    output_text.insert(tk.END, f"Syntax Error at {line_number}: Expected condition value but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    print(f"Error: Invalid first condition_value at index {start_idx}")
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
                        print(f"Error: Expected closing bracket ']' at index {start_idx} (line {line_number})")
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected closing bracket ']' but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                    
                    start_idx += 1  
                
                
                start_idx = skip_spaces(tokens, start_idx)
                
                relational_operators = {'<', '>', '<=', '>=', '==', '!='}
                mathematical_operators = {'+', '-', '*', '/', '%', '**', '//'}
                logical_operators = {'&&', '||'}

                
                if start_idx >= len(tokens) or not any(tokens[start_idx][0] in op_set for op_set in [logical_operators, relational_operators] for op in op_set):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    print(f"Error: Expected relational operator at index {start_idx}, found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}")
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected relational operator but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                
                
                print(f"Found relational operator '{tokens[start_idx][0]}' at index {start_idx}")
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
                
                
                has_negation = False
                if start_idx < len(tokens) and tokens[start_idx][0] == '!':
                    print(f"Found negation operator '!' at index {start_idx}")
                    has_negation = True
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)
                
                
                is_valid, new_idx = conditional.condition_value(tokens, start_idx)
                if not is_valid:
                    print(f"Error: Invalid second condition_value at index {start_idx}")
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected conditional value but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
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
                        print(f"Error: Expected closing bracket ']' at index {start_idx} (line {line_number})")
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected closing bracket ']' but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                    
                    start_idx += 1  
                
                
                start_idx = skip_spaces(tokens, start_idx)
                
                is_valid, new_idx = conditional.condition_value_tail(tokens, start_idx)
                if not is_valid:
                    output_text.insert(tk.END, f"Syntax Error: Invalid condition at line {get_line_number(tokens, start_idx)}\n")
                    print(f"Error: Invalid condition_value_tail at index {start_idx}")
                    return False, None
                
                return True, new_idx
                    
            @staticmethod
            def condition_value(tokens, start_idx):
                

                print("<condition_value>")
                start_idx = skip_spaces(tokens, start_idx)
                
                
                if start_idx < len(tokens) and tokens[start_idx][0] == '(':
                    print(f"Found opening parenthesis at index {start_idx}")
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    
                    is_valid, new_idx = conditional.conditions_base(tokens, start_idx)
                    if not is_valid:
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                        print(f"Error: Invalid condition inside parentheses at index {start_idx}")
                        # output_text.insert(tk.END, f"Syntax Error: Invalid condition inside parentheses at index {start_idx} but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                        # output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                    
                    start_idx = new_idx
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    if not is_token(tokens, start_idx, ')'):
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        print(f"Error: Expected closing parenthesis at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                        output_text.insert(tk.END, f"Syntax Error: Expected closing parenthesis at index {start_idx} but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                    
                    print(f"Found closing parenthesis at index {start_idx}")
                    return True, start_idx + 1  
                
                
                if start_idx < len(tokens) and tokens[start_idx][1] == 'Identifier':
                    print(f"Found Identifier '{tokens[start_idx][0]}' at index {start_idx}")
                    current_idx = start_idx
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    
                    while start_idx < len(tokens) and tokens[start_idx][0] == '[':
                        start_idx += 1  
                        start_idx = skip_spaces(tokens, start_idx)
                        
                        
                        if not (start_idx < len(tokens) and (tokens[start_idx][1] == "Identifier" or tokens[start_idx][1] == "numlit")):
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Invalid array index but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None
                        
                        start_idx += 1  
                        start_idx = skip_spaces(tokens, start_idx)
                        
                        
                        if not (start_idx < len(tokens) and tokens[start_idx][0] == ']'):
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected closing bracket but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
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
                            print(f"Found valid arithmetic sequence at index {start_idx}")
                            return True, new_idx
                
                
                conliterals = {'numlit', 'string literal', 'dom', 'rec'}
                if start_idx < len(tokens) and tokens[start_idx][1] in conliterals:
                    print(f"Found literal '{tokens[start_idx][0]}' of type {tokens[start_idx][1]} at index {start_idx}")
                    return True, start_idx + 1  
                
                # line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                # output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a condition value but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                # output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
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
                
                
                logical_operators = {'&&', '||'}
                relational_operators = {'<', '>', '<=', '>=', '==', '!='}

                
                if start_idx >= len(tokens) or not any(tokens[start_idx][0] in op_set for op_set in logical_operators for op in op_set):
                    
                    
                    if start_idx < len(tokens) and tokens[start_idx][0] == ';':
                        print(f"Found semicolon at index {start_idx}")
                        return True, start_idx + 1  
                    
                    return True, start_idx  
                
                
                print(f"Found logical operator '{tokens[start_idx][0]}' at index {start_idx}")
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
                
                
                is_valid, new_idx = conditional.conditions_base(tokens, start_idx)
                if not is_valid:
                    output_text.insert(tk.END, f"Syntax Error: Invalid condition after logical operator at line {get_line_number(tokens, start_idx)}\n")
                    print(f"Error: Invalid conditions_base after logical operator at index {start_idx}")
                    return False, None
                
                start_idx = new_idx
                start_idx = skip_spaces(tokens, start_idx)
                
                
                return conditional.condition_value_tail(tokens, start_idx)
        
    class statements:
        @staticmethod
        def func_calling(tokens, start_idx):
            print(f"DEBUG SYNTAX: Starting function_calling at index {start_idx}")
            
                
            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and is_token(tokens, start_idx, "Identifier")):
                print(f"Error: Expected identifier after 'func' at index {start_idx}")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier after 'func' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, start_idx

            func_name = tokens[start_idx]  
            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)

            
            if start_idx < len(tokens) and is_token(tokens, start_idx, "("):
                print(f"Found function with parameters: {func_name}")
                has_params = True
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
                
                
                is_valid, new_idx = parameters.func_params(tokens, start_idx)
                if not is_valid:
                    print(f"Error: Invalid parameters in function definition at index {start_idx}")
                    return False, start_idx
                
                start_idx = new_idx  
                start_idx = skip_spaces(tokens, start_idx)
                
                
                if not (start_idx < len(tokens) and is_token(tokens, start_idx, ")")):
                    print(f"Error: Expected ')' at index {start_idx}")
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing parenthesis but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, start_idx
                
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
            else:
                has_params = False

            
            if start_idx < len(tokens) and is_token(tokens, start_idx, "="):
                print(f"Found function assignment for {func_name}")
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)

                
                if not (start_idx < len(tokens) and is_token(tokens, start_idx, "Identifier")):
                    print(f"Error: Expected identifier after '=' at index {start_idx}")
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, start_idx

                assigned_func = tokens[start_idx]
                if has_params:
                    print(f"Valid parameterized function assignment: {func_name}() = {assigned_func}")
                else:
                    print(f"Valid function reassignment: {func_name} -> {assigned_func}")
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
            elif has_params:
                
                print(f"Valid function call with parameters: {func_name}()")
            else:
                
                print(f"Valid function reference: {func_name}")

            
            if not (start_idx < len(tokens) and is_token(tokens, start_idx, ";")):
                print(f"Error: Expected ';' at index {start_idx}")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a ';' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, start_idx

            print(f"Valid function statement: {func_name}")
            start_idx += 1  
            return True, start_idx
        
        @staticmethod
        def if_statement(tokens, start_idx):
            
            if not is_token(tokens, start_idx, '('):
                print(f"Error: Expected '(' after 'if' at index {start_idx}")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an open parenthesis but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)

            
            is_valid, new_idx = conditional.conditional_block(tokens, start_idx)
            if not is_valid:
                print(f"Error: Invalid condition in if statement at index {start_idx}")
                
                
                return False, None

            start_idx = new_idx  
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, ')'):
                print(f"Error: Expected ')' at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'} in if statement")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing parenthesis, math operator or conditional operator but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, '{'):
                print(f"Error: Expected '{{' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a '{{' after if condition but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)

            
            is_valid, new_idx = program.body_statements(tokens, start_idx)
            if not is_valid:
                return False, None

            if new_idx == start_idx:  # No tokens were consumed, meaning empty body
                print(f"DEBUG SYNTAX: Empty if statement body at index {start_idx}")
                try:
                    # Try to get line information
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                except Exception as e:
                    # If line information can't be found, use fallback values
                    print(f"Error finding line information: {e}")
                    line_number = get_line_number(tokens, start_idx)
                    line_text = "line with empty if block"
                
                # Always insert error messages to ensure they're displayed in the GUI
                output_text.insert(tk.END, "❌ Error: ", "error")
                output_text.insert(tk.END, f"Empty if statement body is not allowed at line {line_number}\n", "output")
                output_text.insert(tk.END, f"You must include at least one statement inside the if block\n", "output")
                return False, None
 
            start_idx = new_idx
            start_idx = skip_spaces(tokens, start_idx)

            is_valid, new_idx = statements.inside_loop_statement(tokens, start_idx)
            if not is_valid:
                return False, None
                    
            start_idx = new_idx
            start_idx = skip_spaces(tokens, start_idx)
            
            
            if not is_token(tokens, start_idx, '}'):
                print(f"Error: Expected '}}' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a '}}' after if statement but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            
            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)

            
            has_else = False
            
            while start_idx < len(tokens):
                if is_token(tokens, start_idx, 'elif'):
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    if not is_token(tokens, start_idx, '('):
                        print(f"Error: Expected '(' after 'elif' at index {start_idx}")
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a '(' after 'elif' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                    
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)

                    is_valid, new_idx = conditional.conditional_block(tokens, start_idx)
                    if not is_valid:
                        print(f"Error: Invalid condition in if statement at index {start_idx}")
                        return False, None
                    
                    
                    start_idx = new_idx
                    start_idx = skip_spaces(tokens, start_idx)

                    if not is_token(tokens, start_idx, ')'):
                        print(f"Error: Expected ')' at index {start_idx} in elif statement")
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a ')' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                    
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)

                    if not is_token(tokens, start_idx, '{'):
                        print(f"Error: Expected '{{' after elif condition at index {start_idx}")
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a '{{' after elif condition but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                    
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)

                    is_valid, new_idx = program.body_statements(tokens, start_idx)
                    if not is_valid:
                        return False, None
                    
                    if new_idx == start_idx:  # No tokens were consumed, meaning empty body
                        print(f"DEBUG SYNTAX: Empty elif statement body at index {start_idx}")
                        try:
                            # Try to get line information
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        except Exception as e:
                            # If line information can't be found, use fallback values
                            print(f"Error finding line information: {e}")
                            line_number = get_line_number(tokens, start_idx)
                            line_text = "line with empty elif block"
                        
                        # Always insert error messages to ensure they're displayed in the GUI
                        output_text.insert(tk.END, "❌ Error: ", "error")
                        output_text.insert(tk.END, f"Empty elif statement body is not allowed at line {line_number}\n", "output")
                        output_text.insert(tk.END, f"You must include at least one statement inside the elif block\n", "output")
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
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a '}}' after elif statement but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
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
                        print(f"Error: Expected '{{' after 'else' at index {start_idx}")
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a '{{' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                    
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)

                    is_valid, new_idx = program.body_statements(tokens, start_idx)
                    if not is_valid:
                        return False, None
                    

                    if new_idx == start_idx:  # No tokens were consumed, meaning empty body
                        print(f"DEBUG SYNTAX: Empty else statement body at index {start_idx}")
                        try:
                            # Try to get line information
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        except Exception as e:
                            # If line information can't be found, use fallback values
                            print(f"Error finding line information: {e}")
                            line_number = get_line_number(tokens, start_idx)
                            line_text = "line with empty else block"
                        
                        # Always insert error messages to ensure they're displayed in the GUI
                        output_text.insert(tk.END, "❌ Error: ", "error")
                        output_text.insert(tk.END, f"Empty else statement body is not allowed at line {line_number}\n", "output")
                        output_text.insert(tk.END, f"You must include at least one statement inside the else block\n", "output")
                        return False, None

                    start_idx = new_idx
                    start_idx = skip_spaces(tokens, start_idx)

                    if not is_token(tokens, start_idx, '}'):
                        print(f"Error: Expected '}}' at index {start_idx}")
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a '}}' after else statement but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                    
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    
                    break

                else:
                    
                    break
            
            return True, start_idx  

        @staticmethod
        def inside_loop_statement(tokens, start_idx):
            print(f"DEBUG SYNTAX: Starting inside_loop_statement at index {start_idx}")
            start_idx = skip_spaces(tokens, start_idx)
            
            
            if start_idx < len(tokens) and is_token(tokens, start_idx, "contig"):
                print("Found contig statement")
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
                
                
                if not is_token(tokens, start_idx, ";"):
                    print(f"Error: Expected ';' after 'contig' at index {start_idx}")
                    return False, start_idx
                
                start_idx += 1  
                return True, start_idx
            
            
            elif start_idx < len(tokens) and is_token(tokens, start_idx, "destroy"):
                print("Found destroy statement")
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
                
                
                if not is_token(tokens, start_idx, ";"):
                    print(f"Error: Expected ';' after 'destroy' at index {start_idx}")
                    return False, start_idx
                
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
                print(f"Error: Expected '(' at index {start_idx}")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an open parenthesis in express statement but found {tokens[start_idx][0]}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)

            
            print(f"Before calling express_value: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            
            is_valid , new_idx = express.express_value(tokens, start_idx)
            if not is_valid:
                print(f"Error: Invalid expression at index {start_idx}")
                return False, None

            
            print(f"After express_value, new index: {new_idx}, token: {tokens[new_idx] if new_idx < len(tokens) else 'EOF'}")

            
            start_idx = new_idx  
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, ')'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                print(f"Error: Expected ')' at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'} in express statement")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a ',', ')' or math op in express statement but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
                
            start_idx += 1 
            start_idx = skip_spaces(tokens, start_idx)   
            if is_token(tokens, start_idx, ';'):
                return True, start_idx + 1
            else:
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx] if start_idx < len(tokens) else ('EOF', 'EOF')
                print(f"Error: Expected ';' at index {start_idx} (line {line_number})")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a semicolon in express statement but found {tokens[start_idx][0]}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
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
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected array index but found {found_token}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
                
                
                if not is_token(tokens, start_idx, ']'):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected closing bracket ']' but found {found_token}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
                
                
                if is_token(tokens, start_idx, '['):
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    
                    if not (start_idx < len(tokens) and tokens[start_idx][1] in ["Identifier", "numlit"]):
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                        found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected second array index but found {found_token}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                    
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    
                    if not is_token(tokens, start_idx, ']'):
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                        found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected closing bracket ']' but found {found_token}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                    
                    start_idx += 1  
            
            
            start_idx = skip_spaces(tokens, start_idx)

            
            if not any(is_token(tokens, start_idx, op) for op in assignment_op):

                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an assignment operator but found  {tokens[start_idx][0]}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
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
            """
            Parses a valid stimuli call: stimuli("text");
            """


            start_idx = skip_spaces(tokens, start_idx)

            
            if not is_token(tokens, start_idx, '('):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                print(f"Error: Expected '(' at index {start_idx} (line {line_number})")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an open parenthesis but found {tokens[start_idx][0]}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)
            
            
            if not is_token(tokens, start_idx, 'string literal'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                print(f"Error: Expected string literal at index {start_idx} (line {line_number})")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a string literal but found {tokens[start_idx][0]}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)
            
            
            if not is_token(tokens, start_idx, ')'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                print(f"Error: Expected ')' at index {start_idx} (line {line_number}) in stimuli call")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing parenthesis but found {tokens[start_idx][0]}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)
            
            
            if is_token(tokens, start_idx, ';'):
                return True, start_idx + 1
            else:
                print("ASAN NA UNG SA STIMULI CALL");
                print(f"Error: Expected ';' at index {start_idx} (line {line_number})")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a semicolon in stimuli call but found {tokens[start_idx][0]}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

    
        @staticmethod
        def assignment_statement(tokens, start_idx):
            


            print(f"DEBUG SYNTAX: Starting assignment_statement at index {start_idx}")
            
            
            start_idx = skip_spaces(tokens, start_idx)
            
            
            if not any(is_token(tokens, start_idx, op) for op in assignment_op):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an assignment operator but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, start_idx

            
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            new_idx = start_idx
            
            is_valid, new_idx = statements.assignment_value(tokens, start_idx)
            if not is_valid:
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a valid assignment value or stimuli but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, start_idx
            
            start_idx = new_idx  
            start_idx = skip_spaces(tokens, start_idx)  
            
            
            while start_idx < len(tokens) and is_token(tokens, start_idx, ','):
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
                
                if not is_token(tokens, start_idx, 'Identifier'):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an Identifier but found {found_token}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
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
                    
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    if not is_token(tokens, start_idx, ']'):
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                        found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected closing bracket ']' but found {found_token}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                    
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)

                if not any(is_token(tokens, start_idx, op) for op in assignment_op):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an assignment operator but found {found_token}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, start_idx
                
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
                
                
                is_valid, new_idx = statements.assignment_value(tokens, start_idx)
                if not is_valid:
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a valid assignment value but found {found_token}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, start_idx
                
                start_idx = new_idx
                start_idx = skip_spaces(tokens, start_idx)

            
            has_array_stimuli = False
            if is_token(tokens, start_idx, '['):
                has_array_stimuli = True
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
                
                
                if start_idx < len(tokens):
                    
                    if is_token(tokens, start_idx, '::'):
                        start_idx += 1  
                        start_idx = skip_spaces(tokens, start_idx)
                        
                        
                        if start_idx < len(tokens) and tokens[start_idx][1] == "numlit":
                            start_idx += 1  
                    
                    elif tokens[start_idx][1] in ["Identifier", "numlit"]:
                        start_idx += 1  
                
                start_idx = skip_spaces(tokens, start_idx)
                
                if not is_token(tokens, start_idx, ']'):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected closing bracket ']' but found {found_token}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)

            
            if not is_token(tokens, start_idx, ';'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a semicolon or arithmetic operator in assignment but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, start_idx
            
            start_idx += 1  
            return True, start_idx
                            
        @staticmethod
        def for_loop_statement(tokens, start_idx):
            


            print(f"DEBUG SYNTAX: Starting for_loop_statement at index {start_idx}")
            print(f"DEBUG SYNTAX: Current tokens: {tokens[start_idx:start_idx+5] if start_idx < len(tokens) else 'end of tokens'}")

            
            start_idx = skip_spaces(tokens, start_idx)

            

            
            if not (start_idx < len(tokens) and tokens[start_idx][0] == '('):
                print(f"ERROR: Expected '(' at index {start_idx}")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an open parenthesis but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, start_idx
            start_idx += 1  

            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and tokens[start_idx][0] == 'dose'):
                print(f"ERROR: Expected 'dose' for initialization at index {start_idx}")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected dose keyword but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, start_idx
            start_idx += 1  

            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and tokens[start_idx][1] == "Identifier"):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an Identifier but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, start_idx
            start_idx += 1  

            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and tokens[start_idx][0] == '='):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an equal sign but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, start_idx
            start_idx += 1  

            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and tokens[start_idx][1] in ["Identifier", "numlit"]):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected Identifier or Numlit but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, start_idx
            start_idx += 1  

            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and tokens[start_idx][0] == ";"):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected semicolon but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, start_idx
            start_idx += 1  

            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and tokens[start_idx][1] == "Identifier"):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an Identifier but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, start_idx
            start_idx += 1  

            start_idx = skip_spaces(tokens, start_idx)

            
            if start_idx >= len(tokens) or tokens[start_idx][0] not in conditional_op:
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a conditional operator but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, start_idx
            start_idx += 1  

            start_idx = skip_spaces(tokens, start_idx)

            
            is_valid, new_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
            if not is_valid:
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an Identifier or numlit but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

            start_idx = new_idx
            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and tokens[start_idx][0] == ";"):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a semicolon in for loop but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, start_idx

            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and (tokens[start_idx][1] == "Identifier" or tokens[start_idx][0] in ['++', '--'])):
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected Identifier or unary operator but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, start_idx

            
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

                    output_text.insert(tk.END, f"Syntax Error at line {operator_line_number}: Expected increment/decrement operator but found {found_token}\n")
                    output_text.insert(tk.END, f"Line {operator_line_number}: {operator_line_text}\n")
                    return False, start_idx
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
                    output_text.insert(tk.END, f"Syntax Error at line {identifier_line_number}: Expected an Identifier but found {found_token}\n")
                    output_text.insert(tk.END, f"Line {identifier_line_number}: {identifier_line_text}\n")
                    return False, start_idx
                start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and tokens[start_idx][0] == ')'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected closing parenthesis for for loop but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and tokens[start_idx][0] == '{'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected '{{' but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)

            
            is_valid, new_idx = program.body_statements(tokens, start_idx)
            if not is_valid:
                return False, None
                        
            if new_idx == start_idx:  # No tokens were consumed, meaning empty body
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Empty if statement body is not allowed\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

            start_idx = new_idx    
            
            if not (start_idx < len(tokens) and tokens[start_idx][0] == '}'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected '}}' in for loop but found {found_token} \n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            
            start_idx += 1  
            return True, start_idx

        @staticmethod
        def prod_statement(tokens, start_idx):
            print("inside prod_statement")
            
            start_idx = skip_spaces(tokens, start_idx)
            if not is_token(tokens, start_idx, ';'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected ';' or a prod value but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            
            
            is_valid, new_idx = statements.prod_value(tokens, start_idx)
            if not is_valid:
                print(f"Error: Invalid arithmetic expression at index {start_idx}")
                return False, None

            
            start_idx = new_idx
            start_idx = skip_spaces(tokens, start_idx)

            
            if not is_token(tokens, start_idx, ';'):
                print(f"Valid prod statement (ends with ';') at index {start_idx}")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected ';' or a prod value but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

            print(f"Error: Expected literal at prod statement, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected ';' or a prod value but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
            return False, None

        @staticmethod
        def prod_value(tokens, start_idx):
            
            start_idx = skip_spaces(tokens, start_idx)
            
            
            if start_idx >= len(tokens) or is_token(tokens, start_idx, ';'):
                print("Empty prod value")
                return True, start_idx
            
            
            if is_token(tokens, start_idx, literals) or is_token(tokens, start_idx, ''):
                print(f"Simple literal or identifier at index {start_idx}")
                return True, start_idx + 1  
            
            
            is_valid, new_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
            if is_valid:
                print(f"ARITH PROD - Successfully parsed arithmetic sequence, new index: {new_idx}")
                return True, new_idx
            
            
            valid_tokens = ['Identifier', 'dom', 'rec']
            
            
            if is_token(tokens, start_idx, literals):
                print(f"Simple literal at index {start_idx}")
                return True, start_idx + 1  
            
            
            for token in valid_tokens:
                if is_token(tokens, start_idx, token):
                    print(f"{token} token at index {start_idx}")
                    return True, start_idx + 1  
            
            
            print(f"Invalid token at index {start_idx}: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            return False, start_idx

        @staticmethod
        def assignment_value(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)

            # Check for negation operator at the beginning
            has_negation = False
            if start_idx < len(tokens) and tokens[start_idx][0] == '!':
                print(f"Found negation operator '!' in assignment value at index {start_idx}")
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
                print(f"Error: Expected '(' after 'while' at index {start_idx}")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected '(' after 'while' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")    
                return False, None
            start_idx += 1  
            
            
            is_valid, new_idx = conditional.conditional_block(tokens, start_idx)
            if not is_valid:
                print(f"Error: Invalid condition in while statement at index {start_idx}")
                return False, None

            start_idx = new_idx  
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, ')'):
                print(f"Error: Expected ')' at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'} in while statement")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected ')' after 'while' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, '{'):
                print(f"Error: Expected '{{' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected '{{' after 'while' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)

            
            is_valid, new_idx = program.body_statements(tokens, start_idx)
            if not is_valid:
                return False, None
                        

            start_idx = new_idx
            
            
            if not is_token(tokens, start_idx, '}'):
                print(f"Error: Expected '}}' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected '}}' after while statement but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            
            return True, start_idx + 1
    
    class variables:
        @staticmethod
        def validate_doseval(tokens, start_idx):
            # Get line information for initial position

            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, 'Identifier'):
                # Include both token info and line index in error message
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected an Identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
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
                            output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected a dose value but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None
                        start_idx += 1
                    elif is_token(tokens, start_idx, 'Identifier'):
                        start_idx += 1
                    else:
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected a dose value but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                    
                    start_idx = skip_spaces(tokens, start_idx)
                
                if is_token(tokens, start_idx, ';'):
                    return True, start_idx + 1
                
                if not is_token(tokens, start_idx, ','):
                    # Get updated line information for error
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    
                    output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected a comma, equals or semicolon but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                
                if not is_token(tokens, start_idx, 'Identifier'):
                    # Get updated line information for error
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                start_idx += 1
                
                start_idx = skip_spaces(tokens, start_idx)

        @staticmethod
        def validate_seqval(tokens, start_idx):
            
            start_idx = skip_spaces(tokens, start_idx)

            
            if not is_token(tokens, start_idx, 'Identifier'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
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
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected string literal or Identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                                        
                    start_idx = skip_spaces(tokens, start_idx)
                
                
                if is_token(tokens, start_idx, ';'):
                    return True, start_idx + 1
                
                if not is_token(tokens, start_idx, ','):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected a comma, equals or semicolon but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                
                
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                
                
                if not is_token(tokens, start_idx, 'Identifier'):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                start_idx += 1
                
                start_idx = skip_spaces(tokens, start_idx)

                        
        @staticmethod
        def validate_alleleval(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)

            
            if not is_token(tokens, start_idx, 'Identifier'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
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
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected dom, rec, Identifier or numlit but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                                        
                    start_idx = skip_spaces(tokens, start_idx)
                
                
                if is_token(tokens, start_idx, ';'):
                    return True, start_idx + 1
                
                if not is_token(tokens, start_idx, ','):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected a comma, equals or semicolon but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                
                
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                
                
                if not is_token(tokens, start_idx, 'Identifier'):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                start_idx += 1
                
                start_idx = skip_spaces(tokens, start_idx)

        @staticmethod
        def validate_quantval(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, 'Identifier'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
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
                            output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected a quant value but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None
                        start_idx += 1
                    elif is_token(tokens, start_idx, 'Identifier'):
                        start_idx += 1
                    else:
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected a quant value but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                    
                    start_idx = skip_spaces(tokens, start_idx)

                if is_token(tokens, start_idx, ';'):
                    return True, start_idx + 1
                
                if not is_token(tokens, start_idx, ','):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected a comma, equals or semicolon but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
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

                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            
            if not is_token(tokens, start_idx, '['):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an open bracket but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

                        
            if not (is_token(tokens, start_idx, 'numlit') or is_token(tokens, start_idx, 'Identifier')):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a number or identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

            # Only check number_sign if it's a numlit
            if is_token(tokens, start_idx, 'numlit'):
                number_sign = check_number_sign(tokens[start_idx])
                if number_sign in {"quantval", "nequantliteral"}:
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a quant value but found {tokens[start_idx][0]}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None

            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            
            if not is_token(tokens, start_idx, ']'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing bracket but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
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
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a number or identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None

                # Only check number_sign if it's a numlit
                if is_token(tokens, start_idx, 'numlit'):
                    number_sign = check_number_sign(tokens[start_idx])
                    if number_sign in {"quantval", "nequantliteral"}:
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a quant value but found {tokens[start_idx][0]}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                if not is_token(tokens, start_idx, ']'):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing bracket but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

            
            if is_token(tokens, start_idx, '='):
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                
                if not is_token(tokens, start_idx, '{'):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an opening brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                
                if has_second_dimension:
                    # For 2D arrays, we expect the first token after '{' to be another '{'
                    if not is_token(tokens, start_idx, '{'):
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected '{{' for start of row in 2D array, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                    
                    
                    while True:
                        if not is_token(tokens, start_idx, '{'):
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an opening brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None
                        start_idx += 1
                        start_idx = skip_spaces(tokens, start_idx)

                        
                        while True:
                            if not is_token(tokens, start_idx, 'numlit'):
                                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a number but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                                return False, None

                            
                            number_sign = check_number_sign(tokens[start_idx])
                            if number_sign in {"neliteral", "doseliteral"}:
                                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a quant value but found {tokens[start_idx][0]}\n")
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
                                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

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
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None
                else:
                    
                    while True:
                        if not is_token(tokens, start_idx, 'numlit'):
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a number but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None
                        
                        
                        number_sign = check_number_sign(tokens[start_idx])
                        if number_sign in {"neliteral", "doseliteral"}:
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a quant value but found {tokens[start_idx][0]}\n")
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
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None

            
            if not is_token(tokens, start_idx, ';'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a semicolon but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

            return True, start_idx + 1

        @staticmethod
        def validate_clust_doseval(tokens, start_idx):
            print('<clust_dose>')
            start_idx = skip_spaces(tokens, start_idx)

            
            if not is_token(tokens, start_idx, 'Identifier'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            
            if not is_token(tokens, start_idx, '['):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an open bracket but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            
            if not (is_token(tokens, start_idx, 'numlit') or is_token(tokens, start_idx, 'Identifier')):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a number or identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

            # Only check number_sign if it's a numlit
            if is_token(tokens, start_idx, 'numlit'):
                number_sign = check_number_sign(tokens[start_idx])
                if number_sign in {"quantval", "nequantliteral"}:
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a quant value but found {tokens[start_idx][0]}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None

            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            
            if not is_token(tokens, start_idx, ']'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing bracket but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
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
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a number or identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None

                # Only check number_sign if it's a numlit
                if is_token(tokens, start_idx, 'numlit'):
                    number_sign = check_number_sign(tokens[start_idx])
                    if number_sign in {"quantval", "nequantliteral"}:
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a quant value but found {tokens[start_idx][0]}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                if not is_token(tokens, start_idx, ']'):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing bracket but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

            
            if is_token(tokens, start_idx, '='):
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                
                if not is_token(tokens, start_idx, '{'):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an opening brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                
                # Check if we should expect nested braces for a 2D array
                if has_second_dimension:
                    # For 2D arrays, we expect the first token after '{' to be another '{'
                    if not is_token(tokens, start_idx, '{'):
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected '{{' for start of row in 2D array, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                    
                    
                    while True:
                        if not is_token(tokens, start_idx, '{'):
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an opening brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None
                        start_idx += 1
                        start_idx = skip_spaces(tokens, start_idx)

                        
                        while True:
                            if not is_token(tokens, start_idx, 'numlit'):
                                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a number but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                                return False, None

                            
                            number_sign = check_number_sign(tokens[start_idx])
                            if number_sign in {"quantval", "nequantliteral"}:
                                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

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
                                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

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
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None
                else:
                    
                    while True:
                        if not is_token(tokens, start_idx, 'numlit'):
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a numlit but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None

                        
                        number_sign = check_number_sign(tokens[start_idx])
                        if number_sign in {"quantval", "nequantliteral"}:
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

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
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None

            start_idx = skip_spaces(tokens, start_idx)
            if not is_token(tokens, start_idx, ';'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a semicolon but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

            return True, start_idx + 1

        @staticmethod
        def validate_clust_seqval(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After initial skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")


            
            if not is_token(tokens, start_idx, 'Identifier'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                print(f"DEBUG SYNTAX: Expected Identifier at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            print(f"DEBUG SYNTAX: Found Identifier: {tokens[start_idx]}")
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            
            if not is_token(tokens, start_idx, '['):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                print(f"DEBUG SYNTAX: Expected '[' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an open bracket but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            print(f"DEBUG SYNTAX: Found opening bracket")
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            
            if not (is_token(tokens, start_idx, 'numlit') or is_token(tokens, start_idx, 'Identifier')):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a number or identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

            # Only check number_sign if it's a numlit
            if is_token(tokens, start_idx, 'numlit'):
                number_sign = check_number_sign(tokens[start_idx])
                if number_sign in {"quantval", "nequantliteral"}:
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a quant value but found {tokens[start_idx][0]}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            
            if not is_token(tokens, start_idx, ']'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                print(f"DEBUG SYNTAX: Expected ']' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing bracket\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
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
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a number or identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None

                # Only check number_sign if it's a numlit
                if is_token(tokens, start_idx, 'numlit'):
                    number_sign = check_number_sign(tokens[start_idx])
                    if number_sign in {"quantval", "nequantliteral"}:
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a quant value but found {tokens[start_idx][0]}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                print(f"DEBUG SYNTAX: Found second dimension size: {tokens[start_idx]}")
                start_idx += 1

                start_idx = skip_spaces(tokens, start_idx)
                print(f"DEBUG SYNTAX: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                
                if not is_token(tokens, start_idx, ']'):
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    print(f"DEBUG SYNTAX: Expected ']' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing bracket\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
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

                    print(f"DEBUG SYNTAX: Expected '{{' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an opening brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                print(f"DEBUG SYNTAX: Found opening brace")
                start_idx += 1

                start_idx = skip_spaces(tokens, start_idx)
                print(f"DEBUG SYNTAX: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

                
                if has_second_dimension:
                    # For 2D arrays, we expect the first token after '{' to be another '{'
                    if not is_token(tokens, start_idx, '{'):
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected '{{' for start of row in 2D array, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                    
                    
                    while True:
                        if not is_token(tokens, start_idx, '{'):
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an opening brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None
                        start_idx += 1
                        start_idx = skip_spaces(tokens, start_idx)

                        
                        while True:
                            if not is_token(tokens, start_idx, 'string literal') :
                                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a string literal but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
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
                                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

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
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None
                else:
                    print(f"DEBUG SYNTAX: Detected 1D array (direct values)")
                    
                    while True:
                        if not is_token(tokens, start_idx, 'string literal') :
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                            print(f"DEBUG SYNTAX: Expected string literal or Identifier at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
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
                            line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                            print(f"DEBUG SYNTAX: Expected ',' or '}}' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a comma or closing brace but found {tokens[start_idx][0]}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None

            
            if not is_token(tokens, start_idx, ';'):
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

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
            
            

            param_types = {"dose", "quant", "seq", "allele"}
            params = []
            start_idx = skip_spaces(tokens, start_idx)

            
            if start_idx >= len(tokens) or tokens[start_idx][0] not in param_types:
                print(f"No parameters found at index {start_idx}.")
                return True, [], start_idx

            if tokens[start_idx][0] == ")":
                print(f"No parameters found at index {start_idx}.")
                return True, [], start_idx
            
            while start_idx < len(tokens):
                
                if tokens[start_idx][0] not in param_types:
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    print(f"Error: Expected parameter type at index {start_idx}, found {tokens[start_idx]}")
                    output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected an data type\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None, start_idx

                param_type = tokens[start_idx][0]
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                
                if start_idx >= len(tokens) or tokens[start_idx][1] != "Identifier":
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

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

                
                if tokens[start_idx][1] == "Identifier" or tokens[start_idx][1] == "numlit":
                    print(f"Parameter value detected: {tokens[start_idx][0]}")
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)
                    print(f"Index after skipping spaces post-value: {start_idx}")
                else:
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

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


            print("In arithmetic sequence")
            
            
            is_valid, new_idx = arithmetic.arithmetic_value(tokens, start_idx)
            if not is_valid:    
                return False, start_idx
            
            start_idx = new_idx
            
            
            is_valid, new_idx = arithmetic.arithmetic_sequence_tail(tokens, start_idx)
            if not is_valid:
                print(f"ERROR: Expected valid arithmetic sequence tail at index {start_idx}")
                return False, start_idx
            
            return True, new_idx

        @staticmethod
        def arithmetic_value(tokens, start_idx):


            start_idx = skip_spaces(tokens, start_idx)
            
            if start_idx >= len(tokens):
                print(f"ERROR: Expected token at index {start_idx}, but reached end of input")
                return False, start_idx
            
            
            if is_token(tokens, start_idx, '('):
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                
                
                is_valid, new_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
                if not is_valid:
                    return False, start_idx
                
                start_idx = new_idx
                start_idx = skip_spaces(tokens, start_idx)
                
                
                if is_token(tokens, start_idx, ')'):
                    return True, start_idx + 1
                else:
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing parenthesis\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, start_idx
            
            
            elif is_token(tokens, start_idx, 'seq'):
                is_valid, cast_value, new_idx = express.seq_type_cast(tokens, start_idx)
                if is_valid:
                    return True, new_idx
                return False, start_idx
            
            
            elif is_token(tokens, start_idx, 'numlit') or is_token(tokens, start_idx, 'Identifier') or \
                 is_token(tokens, start_idx, 'string literal') or is_token(tokens, start_idx, 'dom') or \
                 is_token(tokens, start_idx, 'rec'):
                return True, start_idx + 1
            

            return False, start_idx

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
                    return False, start_idx

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
                identifier = tokens[start_idx][0]
                print(f"Found identifier: {identifier}")
                
                # Use lookahead to determine what kind of expression we're parsing
                lookahead_idx = skip_spaces(tokens, start_idx + 1)
                
                # Case 1: Array reference (identifier followed by '[')
                if lookahead_idx < len(tokens) and tokens[lookahead_idx][0] == '[':
                    print("Found '[', parsing as express_value_id_tail")
                    is_valid, id_tail_value, next_idx = express.express_value_id_tail(tokens, start_idx + 1, identifier)
                    if not is_valid:
                        print("Failed to parse express_value_id_tail")
                        print("Syntax Error: Expected valid array index")
                        return False, start_idx
                    
                    values.append(id_tail_value)
                    start_idx = next_idx
                
                # Case 2: Part of arithmetic (followed by arithmetic operators)
                elif lookahead_idx < len(tokens) and tokens[lookahead_idx][0] in {'+', '-', '*', '/', '%', '='}:
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
                else:
                    values.append(identifier)
                    start_idx = lookahead_idx
            
            # Only try parsing conditional/arithmetic if we haven't already handled the token
            elif start_idx < len(tokens) and (
                tokens[start_idx][0] in {'(', '!', '+', '-'} or 
                tokens[start_idx][1] == 'numlit'
            ):
                # Try conditional block first
                cond_start_tokens = {'(', '!', 'numlit'}
                if tokens[start_idx][0] in cond_start_tokens or tokens[start_idx][1] in cond_start_tokens:
                    print("Trying conditional_block from express_value...")
                    is_valid, new_idx = conditional.conditional_block(tokens, start_idx)
                    if is_valid:
                        print("Parsed conditional block in express_value.")
                        return True, new_idx
                    
                # Try arithmetic sequence if conditional didn't succeed
                print("Trying arithmetic_sequence from express_value...")
                is_valid, new_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
                if is_valid:
                    print("Parsed arithmetic sequence in express_value.")
                    return True, new_idx
                else:
                    print("Not a valid arithmetic/conditional, will try literal/seq/concat.")
            
            # Existing logic for seq, identifier, numlit, string literal, etc.
            elif start_idx < len(tokens) and is_token(tokens, start_idx, 'seq'):
                print("Found 'seq' keyword, parsing as seq_type_cast")
                is_valid, cast_value, next_idx = express.seq_type_cast(tokens, start_idx)
                if is_valid and cast_value:  
                    print(f"Successfully parsed seq_type_cast: {cast_value}")
                    lookahead_idx = skip_spaces(tokens, next_idx)
                    if lookahead_idx < len(tokens) and tokens[lookahead_idx][0] == "+":
                        print("Found 'seq' followed by '+', parsing as seq_concat")
                        start_idx = skip_spaces(tokens, start_idx)
                        is_valid, concat_value, next_idx = express.seq_concat(tokens, start_idx)
                        if not is_valid:
                            print("Failed to parse seq_concat")
                            return False, start_idx
                        values.append(concat_value)
                        start_idx = next_idx
                    else:
                        values.append(cast_value)
                        start_idx = next_idx
                else:
                    print("Failed to parse seq_type_cast")
                    print("Syntax Error: Expected valid sequence type")


            


            elif start_idx < len(tokens) and is_token(tokens, start_idx, 'numlit'):
                lookahead_idx = skip_spaces(tokens, start_idx + 1)
                if lookahead_idx < len(tokens) and tokens[lookahead_idx][0] == "+":  
                    print("Found 'numlit' followed by '+', trying to parse as arithmetic sequence")
                    is_valid, next_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
                    if is_valid:
                        print("Successfully parsed arithmetic sequence")
                        start_idx = next_idx
                    else:
                        print("Failed to parse arithmetic sequence, trying seq_concat")
                        is_valid, concat_value, next_idx = express.seq_concat(tokens, start_idx)
                        if not is_valid:
                            print("Failed to parse seq_concat")
                            return False, start_idx
                        values.append(concat_value)
                        start_idx = next_idx
                else:
                    values.append(tokens[start_idx][0])  
                    print(f"Added '{tokens[start_idx][0]}' to values: {values}")
                    start_idx += 1  
            elif start_idx < len(tokens) and is_token(tokens, start_idx, 'string literal'):
                lookahead_idx = skip_spaces(tokens, start_idx + 1)
                if lookahead_idx < len(tokens) and tokens[lookahead_idx][0] == "+":
                    print("Found 'string literal' followed by '+', parsing as seq_concat")
                    is_valid, concat_value, next_idx = express.seq_concat(tokens, start_idx)
                    if not is_valid:
                        line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                        print("Failed to parse seq_concat")
                        print("Syntax Error: Expected plus sign")
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a plus sign but found {tokens[start_idx][0]}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, start_idx
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
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a literal but found {tokens[start_idx][0]}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, start_idx  
            
            
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
                                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a plus sign but found {tokens[start_idx][0]}\n")
                                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                                return False, start_idx
                            
                            
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
                        return False, start_idx
                
                
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
                                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a plus sign but found {tokens[start_idx][0]}\n")
                                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                                return False, start_idx
                                
                            
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
                            return False, start_idx
                            
                        
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

                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a literal but found {tokens[start_idx][0]}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, start_idx  
                
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
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a string literal, identifier, or seq type cast but found {tokens[start_idx][0]}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None, start_idx
            
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
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a string literal, identifier, or seq type cast but found {tokens[start_idx][0]}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None, start_idx
            
            
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
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a seq but found {tokens[start_idx][0]}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None, start_idx
                next_value = cast_value
                print(f"Next value is a seq function call: {next_value}")
                start_idx = next_idx
            else:
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)

                print(f"Error: Expected string literal or seq function call at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a string literal or seq type cast but found {tokens[start_idx][0]}\n")
                return False, None, start_idx
            
            
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
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected '(' after 'seq' but found {tokens[start_idx][0]}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, start_idx

            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)

            
            if start_idx >= len(tokens) or tokens[start_idx][1] != "Identifier":
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected Identifier inside 'seq()' but found {tokens[start_idx][0]}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, start_idx

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
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected Identifier or numlit inside 'seq()' but found {tokens[start_idx][0]}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False,  start_idx

                array_expr += tokens[start_idx][0]
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                
                if start_idx >= len(tokens) or tokens[start_idx][0] != ']':
                    line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected ']' after array index but found {tokens[start_idx][0]}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False,  start_idx

                array_expr += ']'
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

            
            if start_idx >= len(tokens) or tokens[start_idx][0] != ')':
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected ')' after array index but found {tokens[start_idx][0]}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False,  start_idx

            result = f"seq({identifier}{array_expr})"
            return True, result, start_idx + 1  



        @staticmethod
        def express_value_id_tail(tokens, start_idx, identifier):
            print("<express_value_id_tail>")
            start_idx = skip_spaces(tokens, start_idx)
            
            
            if start_idx < len(tokens) and tokens[start_idx][0] == '[':
                print("Found '[', parsing as express_array_value")
                is_valid, array_value, next_idx = express.express_array_value(tokens, start_idx, identifier)
                if not is_valid:
                    print("Failed to parse express_array_value")
                    return False, identifier, start_idx
                
                return True, array_value, next_idx
            
            
            print("No array access, returning original identifier")
            return True, identifier, start_idx

        @staticmethod
        def express_array_value(tokens, start_idx, identifier, dimension=0):
            print(f"<express_array_value> dimension={dimension}")

            if start_idx >= len(tokens) or tokens[start_idx][0] != '[':
                print(f"Error: Expected '[' at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None, start_idx

            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            start_index = None
            end_index = None
            step_value = None
            has_slice = False

            # Special case: Check for a slice that starts with ':' or '::' directly
            if start_idx < len(tokens) and tokens[start_idx][0] in (':', '::'):
                has_slice = True
                
                # Handle the case where the token is '::'
                if tokens[start_idx][0] == '::':
                    print("Found '::' token for start of slice with step")
                    start_idx += 1  # Skip the '::' token
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    # Parse step value if present
                    if start_idx < len(tokens) and tokens[start_idx][1] in ('numlit', 'Identifier'):
                        step_value = tokens[start_idx][0]
                        print(f"Found step value: {step_value}")
                        start_idx += 1
                        start_idx = skip_spaces(tokens, start_idx)
                
                # Handle the case where the token is ':'
                else:
                    start_idx += 1  # Skip the ':' token
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    # Parse end index if present
                    if start_idx < len(tokens) and tokens[start_idx][1] in ('numlit', 'Identifier'):
                        end_index = tokens[start_idx][0]
                        print(f"Found end index: {end_index}")
                        start_idx += 1
                        start_idx = skip_spaces(tokens, start_idx)
                    
                    # Check if the next token is another colon (for step)
                    if start_idx < len(tokens) and tokens[start_idx][0] == ':':
                        start_idx += 1
                        start_idx = skip_spaces(tokens, start_idx)
                        
                        # Parse step value if present
                        if start_idx < len(tokens) and tokens[start_idx][1] in ('numlit', 'Identifier'):
                            step_value = tokens[start_idx][0]
                            print(f"Found step value: {step_value}")
                            start_idx += 1
                            start_idx = skip_spaces(tokens, start_idx)
                    else:
                    # Parse end index if present
                        if start_idx < len(tokens) and tokens[start_idx][1] in ('numlit', 'Identifier'):
                            end_index = tokens[start_idx][0]
                            print(f"Found end index: {end_index}")
                            start_idx += 1
                            start_idx = skip_spaces(tokens, start_idx)

                            # Check for second colon for step
                            if start_idx < len(tokens) and tokens[start_idx][0] == ':':
                                start_idx += 1
                                start_idx = skip_spaces(tokens, start_idx)

                                # Parse step value if present
                                if start_idx < len(tokens) and tokens[start_idx][1] in ('numlit', 'Identifier'):
                                    step_value = tokens[start_idx][0]
                                    print(f"Found step value: {step_value}")
                                    start_idx += 1
                                    start_idx = skip_spaces(tokens, start_idx)
            else:
                # Standard case: starts with an index or is empty
                # Parse start index (could be empty)
                if start_idx < len(tokens) and tokens[start_idx][1] in ('numlit', 'Identifier'):
                    start_index = tokens[start_idx][0]
                    print(f"Found start index: {start_index}")
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)

                # Check if it's a slice
                if start_idx < len(tokens) and tokens[start_idx][0] == ':':
                    has_slice = True
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)

                    # Parse end index
                    if start_idx < len(tokens) and tokens[start_idx][1] in ('numlit', 'Identifier'):
                        end_index = tokens[start_idx][0]
                        print(f"Found end index: {end_index}")
                        start_idx += 1
                        start_idx = skip_spaces(tokens, start_idx)

                    # Check for second colon for step
                    if start_idx < len(tokens) and tokens[start_idx][0] == ':':
                        start_idx += 1
                        start_idx = skip_spaces(tokens, start_idx)

                        if start_idx < len(tokens) and tokens[start_idx][1] in ('numlit', 'Identifier'):
                            step_value = tokens[start_idx][0]
                            print(f"Found step value: {step_value}")
                            start_idx += 1
                            start_idx = skip_spaces(tokens, start_idx)

            # Check for closing bracket
            if start_idx >= len(tokens) or tokens[start_idx][0] != ']':
                print(f"Error: Expected ']' at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                line_number, line_tokens, line_text, line_index = find_matching_line(tokens, start_idx, display_lines, get_line_number)
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected ']' but found {tokens[start_idx][0]}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None, start_idx

            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            # Build the array access expression
            array_expr = f"{identifier if dimension == 0 else ''}["
            if has_slice:
                array_expr += (start_index if start_index is not None else '') + ":"
                array_expr += (end_index if end_index is not None else '')
                if step_value is not None:
                    array_expr += f":{step_value}"
            else:
                if start_index is not None:
                    array_expr += start_index
            array_expr += "]"

            print(f"Constructed array expression: {array_expr}")
            return True, array_expr, start_idx


        @staticmethod
        def express_array_splice(tokens, start_idx):
            print("<express_array_splice>")
            
            # Check for first colon
            if start_idx >= len(tokens) or tokens[start_idx][0] not in (':', '::'):
                print(f"Error: Expected ':' or '::' at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, [], start_idx
            
            # Skip the first colon
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            
            # Initialize with just the first colon
            splice_ops = [':']
            
            # Check for double colon (step indicator)
            if start_idx < len(tokens) and tokens[start_idx][0] == ':':
                print("Found double colon '::' for step value")
                # Skip the second colon
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                
                # Check for step value
                step_value = None
                if start_idx < len(tokens) and (tokens[start_idx][1] == 'numlit' or tokens[start_idx][1] == 'Identifier'):
                    step_value = tokens[start_idx][0]
                    print(f"Found step value: {step_value}")
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)
                
                # Add the step part to splice operations
                splice_ops.append(f":{step_value if step_value else ''}")
                
                return True, splice_ops, start_idx
            
            # If no double colon, check for end value in the next token
            # This is handled in express_array_value, so we just return the current state
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
        for line in display_lines:
            line_number = line['line_number']
            tokens_str = ' '.join([f"{t[0]} ({t[1]})" for t in line['tokens']])
            print(f"Line {line_number}: {tokens_str}")

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
            continue  
        else:
            output_text.insert(tk.END, f"Expected global declaration, user defined or main function but found {first_token}\n")


    if valid_line: 
            print(f"ignore")
    else:    
            valid_syntax = False
            

    syntax_error = False
    if not valid_syntax:
        
        output_text.yview(tk.END)
        print("\nSyntax Error!")
        syntax_error = True

    else:
        output_text.delete('1.0', tk.END)
        output_text.insert(tk.END, "You May Push!\n")
        print("\nAll statements are valid!")

    # ADD THIS CHECK BEFORE FINAL ERROR/SUCCESS HANDLING
    if not program.main_function_seen:
        output_text.insert(tk.END, "Syntax Error: No main function (gene) found in the program.\n")
        return False, None

    return syntax_error