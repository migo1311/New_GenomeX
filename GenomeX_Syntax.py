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
                        
                    
                    current_line_number = get_line_number(tokens, start_idx)
                    
                    
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
                        
                        line_number = current_line_number
                        line_text = current_token[0] if current_token else ""
                    start_idx = skip_spaces(tokens, start_idx)

                    
                    keywords = ['dose', 'quant', 'seq', 'allele', 'clust', 'perms']

                    
                    for keyword in keywords:
                        if is_token(tokens, start_idx, keyword):
                            
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
                                    
                    
                    if is_token(tokens, start_idx, '_L'):
                        print("<local_perms_declaration>")
                        check_statements = True  
                        start_idx += 1  
                        start_idx = skip_spaces(tokens, start_idx)

                        
                        if is_token(tokens, start_idx, 'perms'):
                            print("<perms>")
                            start_idx += 1  
                            start_idx = skip_spaces(tokens, start_idx)
                            
                            
                            if is_token(tokens, start_idx, 'clust'):
                                print("<clust>")
                                start_idx += 1  
                                start_idx = skip_spaces(tokens, start_idx)
                                
                                
                                if not any(is_token(tokens, start_idx, clust_type) for clust_type in clust_parse):
                                    print("Invalid *clust type")
                                    return False, None
                                    
                                for clust_type, parser_func in clust_parse.items():
                                    if is_token(tokens, start_idx, clust_type):
                                        start_idx += 1  
                                        start_idx = skip_spaces(tokens, start_idx)
                                        
                                        is_valid, new_idx = parser_func(tokens, start_idx)
                                        if not is_valid:
                                            print(f"Invalid *L perms clust {clust_type} statement")
                                            return False, None
                                            
                                        start_idx = new_idx
                                        start_idx = skip_spaces(tokens, start_idx)
                                        print(f"Successfully parsed *L perms clust {clust_type}")
                                        break  
                                        
                                continue  
                            
                            
                            
                            if not any(is_token(tokens, start_idx, perms_type) for perms_type in perms_parsers):
                                print("Invalid perms type")
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
                                output_text.insert(tk.END, f"Expected valid statements inside {statement_type} statement \n")
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

                print(f"End of body_statements: check_statements={check_statements}, start_idx={start_idx}")
                output_text.insert(tk.END, f"Expected valid statements but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number + 2}: {line_text}\n")
                return check_statements, start_idx  

            
            main_function_seen = False
            user_defined_function_error = False  
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

                
                if start_idx >= len(tokens) or not any(is_token(tokens, start_idx, keyword) for keyword in keywords):
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a valid keyword (dose, quant, seq, allele) but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, start_idx  
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

                    
                    keywords = ['dose', 'quant', 'seq', 'allele', 'clust', 'perms']

                    
                    for keyword in keywords:
                        if is_token(tokens, start_idx, keyword):
                            
                            
                            print(f"Found keyword: {keyword}")
                            
                            
                            
                    
                    if is_token(tokens, start_idx, 'perms'):
                        print("<perms>")
                        start_idx += 1  
                        start_idx = skip_spaces(tokens, start_idx)
                        
                        
                        if is_token(tokens, start_idx, 'clust'):
                            print("<clust>")
                            start_idx += 1  
                            start_idx = skip_spaces(tokens, start_idx)
                            
                            
                            if not any(is_token(tokens, start_idx, clust_type) for clust_type in clust_parse):
                                print("Invalid clust type")
                                return False, None
                                
                            for clust_type, parser_func in clust_parse.items():
                                if is_token(tokens, start_idx, clust_type):
                                    start_idx += 1  
                                    start_idx = skip_spaces(tokens, start_idx)
                                    
                                    is_valid, new_idx = parser_func(tokens, start_idx)
                                    if not is_valid:
                                        print(f"Invalid perms clust {clust_type} statement")
                                        return False, None
                                        
                                    start_idx = new_idx
                                    start_idx = skip_spaces(tokens, start_idx)
                                    print(f"Successfully parsed perms clust {clust_type}")
                                    break  
                                    
                            continue  
                        
                        
                        
                        if not any(is_token(tokens, start_idx, perms_type) for perms_type in perms_parsers):
                            print("Invalid perms type")
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
                            print("Invalid clust type")
                            return False, None
                            
                        for clust_type, parser_func in clust_parse.items():
                            if is_token(tokens, start_idx, clust_type):
                                start_idx += 1  
                                start_idx = skip_spaces(tokens, start_idx)
                                
                                is_valid, new_idx = parser_func(tokens, start_idx)
                                if not is_valid:
                                    print(f"Invalid clust {clust_type} statement")
                                    return False, None
                                    
                                start_idx = new_idx
                                start_idx = skip_spaces(tokens, start_idx)
                                print(f"Successfully parsed clust {clust_type}")
                                break  
                                
                        continue  

                    
                    for L_type, parser_func in local_parse.items():
                        if is_token(tokens, start_idx, L_type):
                            start_idx += 1  
                            start_idx = skip_spaces(tokens, start_idx)

                            is_valid, new_idx = parser_func(tokens, start_idx)
                            if not is_valid:
                                print(f"Invalid {L_type} statement")
                                return False, None

                            start_idx = new_idx
                            start_idx = skip_spaces(tokens, start_idx)
                            print(f"Successfully parsed {L_type}")
                            check_statements = True  
                            break  

                    print(f"End of body_statements: check_statements={check_statements}, start_idx={start_idx}")
                    output_text.insert(tk.END, f"Expected valid statements but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number + 2}: {line_text}\n")
                    return check_statements, start_idx  

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
                start_idx = skip_spaces(tokens, start_idx)
                
                
                if is_token(tokens, start_idx, 'void'):
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)

                
                if not (start_idx < len(tokens) and tokens[start_idx][1] == "Identifier"):
                    print(f"Error: Expected function name (Identifier) at index {start_idx}")
                    output_text.insert(tk.END, f"Expected function name (Identifier) or gene at index {start_idx} but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    program.user_defined_function_error = True  
                    return False, None

                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)

                if not is_token(tokens, start_idx, '('):
                    print(f"Error: Expected '(' after function name at index {start_idx}")
                    output_text.insert(tk.END, f"Syntax Error: Expected '(' after function name at index {start_idx}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    program.user_defined_function_error = True  
                    return False, None
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)

                
                is_valid, params, new_idx = parameters.parse_params(tokens, start_idx)
                if not is_valid:
                    print(f"Error: Invalid parameters in function declaration at index {start_idx}")
                    program.user_defined_function_error = True  
                    return False, None

                start_idx = new_idx  
                start_idx = skip_spaces(tokens, start_idx)

                if not is_token(tokens, start_idx, ')'):
                    print(f"Error: Expected ')' at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                    program.user_defined_function_error = True  
                    return False, None
                
                start_idx += 1 
                start_idx = skip_spaces(tokens, start_idx)            
                if not is_token(tokens, start_idx, '{'):
                    print("Missing opening brace for function block")
                    program.user_defined_function_error = True  
                    return False, None
                
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)

                
                check_statements, new_idx = program.body_statements(tokens, start_idx)
                
                if new_idx is None:
                    print("Error in user defined function statements")
                    program.user_defined_function_error = True  
                    return False, None
                
                start_idx = new_idx
                
                
                if not program.main_function_seen:
                    print("Error: No main function (gene) found in the program")
                    output_text.insert(tk.END, f"Expected main function\n")
                    return False, None
                else:
                    pass

                
                if is_token(tokens, start_idx, '}'):
                    print("Found closing brace for user defined function")
                    
                    if not check_statements:
                        print("Error: No statements found in user defined function")
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected '_L' before keyword\n")
                        output_text.insert(tk.END, f"Expected valid statements in user defined\n")

                        program.user_defined_function_error = True  
                        return False, None
                    
                    return True, start_idx + 1
                else:


                    program.user_defined_function_error = True  
                    return False, None  

            def main_function(tokens, start_idx):
                print("Parsing function...")
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
                        
                start_idx = skip_spaces(tokens, start_idx)

                
                
                if is_token(tokens, start_idx, 'gene'):
                    print("main function")
                    
                    
                    if program.user_defined_function_error:
                        print("Error: Cannot proceed with main function due to errors in user-defined functions")
                        return False, None
                    
                    
                    if program.main_function_seen:
                        print("Error: Multiple main functions (gene) declared")
                        return False, None
                    
                    
                    program.main_function_seen = True
                    
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    if not is_token(tokens, start_idx, '('):
                        print(f"Error: Expected '(' after 'gene' at index {start_idx}")
                        output_text.insert(tk.END, f"Expected '(' after 'gene' at index {start_idx}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                    start_idx += 1  

                    
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
                    
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)

                    
                    check_statements, new_idx = program.body_statements(tokens, start_idx)
                    print("Parsing function...")
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
                        if new_idx is None:
                            print("Error in main function body statements")
                            return False, None
                        
                    start_idx = new_idx
                    
                    
                    if is_token(tokens, start_idx, '}'):
                        print("Found closing brace for main function")
                        
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
                
                
                else:
                    
                    if program.main_function_seen:
                        print("Error: User-defined functions must be declared before the main function")
                        output_text.insert(tk.END, f"Syntax Error: User-defined functions must be declared before the main function\n")
                        program.user_defined_function_error = True  
                        return False, None
                        
                    print("user defined function")
                    
                    
                    
                    return program.user_defined_function(tokens, start_idx)
    


    class conditional:
            @staticmethod
            def conditional_block(tokens, start_idx):
                print("<conditional_block>")
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
                        
                start_idx = skip_spaces(tokens, start_idx)
                
                
                is_valid, new_idx = conditional.conditions_base(tokens, start_idx)
                if not is_valid:
                    
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
                        
                    
                    
                    print(f"Error: Invalid conditions_base at index {start_idx}")
                    return False, None
                return True, new_idx
            
            @staticmethod
            def conditions_base(tokens, start_idx):
                
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
                    output_text.insert(tk.END, f"Syntax Error: Invalid condition value at line {get_line_number(tokens, start_idx)}\n")
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
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected closing bracket ']' but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                    
                    start_idx += 1  
                
                
                start_idx = skip_spaces(tokens, start_idx)
                
                relational_operators = {'<', '>', '<=', '>=', '==', '!='}
                logical_operators = {'&&', '||'}

                
                if start_idx >= len(tokens) or not any(tokens[start_idx][0] in op_set for op_set in [logical_operators, relational_operators] for op in op_set):
                    
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
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    
                    if start_idx < len(tokens) and tokens[start_idx][1] in ["Identifier", "numlit"]:
                        
                        start_idx += 1  
                    
                    
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    
                    if not is_token(tokens, start_idx, ']'):
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

                print("<condition_value>")
                start_idx = skip_spaces(tokens, start_idx)
                
                
                if start_idx < len(tokens) and tokens[start_idx][0] == '(':
                    print(f"Found opening parenthesis at index {start_idx}")
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    
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
                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Invalid array index\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None
                        
                        start_idx += 1  
                        start_idx = skip_spaces(tokens, start_idx)
                        
                        
                        if not (start_idx < len(tokens) and tokens[start_idx][0] == ']'):
                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected closing bracket\n")
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
                
            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and is_token(tokens, start_idx, "Identifier")):
                print(f"Error: Expected identifier after 'func' at index {start_idx}")
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
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing parenthesis\n")
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
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier after '=' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
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
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a ';' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, start_idx

            print(f"Valid function statement: {func_name}")
            start_idx += 1  
            return True, start_idx
        
        @staticmethod
        def if_statement(tokens, start_idx):
            
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

            if not is_token(tokens, start_idx, '('):
                print(f"Error: Expected '(' after 'if' at index {start_idx}")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an open parenthesis\n")
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
                return False, None

            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, '{'):
                print(f"Error: Expected '{{' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None

            start_idx += 1  
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
                print(f"Error: Expected '}}' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
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
                        return False, None
                    
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)

                    if not is_token(tokens, start_idx, '{'):
                        print(f"Error: Expected '{{' after elif condition at index {start_idx}")
                        return False, None
                    
                    start_idx += 1  
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
                        return False, None
                    
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)

                    is_valid, new_idx = program.body_statements(tokens, start_idx)
                    if not is_valid:
                        return False, None
                    
                    start_idx = new_idx
                    start_idx = skip_spaces(tokens, start_idx)


                    if not is_token(tokens, start_idx, '}'):
                        print(f"Error: Expected '}}' at index {start_idx}")
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

            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, '('):
                print(f"Error: Expected '(' at index {start_idx}")
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
                print(f"Error: Expected ')' at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'} in express statement")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a ',', ')' or math op in express statement but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
                
            start_idx += 1 
            start_idx = skip_spaces(tokens, start_idx)   

            
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
            
            
            line_number = get_line_number(tokens, start_idx)
            
            
            has_array_stimuli = False
            if is_token(tokens, start_idx, '['):
                has_array_stimuli = True
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
                
                
                if not (start_idx < len(tokens) and tokens[start_idx][1] in ["Identifier", "numlit"]):
                    line_num, line_txt = get_current_line_info(start_idx)
                    found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                    output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected array index but found {found_token}\n")
                    output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                    return False, None
                
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
                
                
                if not is_token(tokens, start_idx, ']'):
                    line_num, line_txt = get_current_line_info(start_idx)
                    found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                    output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected closing bracket ']' but found {found_token}\n")
                    output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                    return False, None
                
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
                
                
                if is_token(tokens, start_idx, '['):
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    
                    if not (start_idx < len(tokens) and tokens[start_idx][1] in ["Identifier", "numlit"]):
                        line_num, line_txt = get_current_line_info(start_idx)
                        found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                        output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected second array index but found {found_token}\n")
                        output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                        return False, None
                    
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    
                    if not is_token(tokens, start_idx, ']'):
                        line_num, line_txt = get_current_line_info(start_idx)
                        found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                        output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected closing bracket ']' but found {found_token}\n")
                        output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                        return False, None
                    
                    start_idx += 1  
            
            
            start_idx = skip_spaces(tokens, start_idx)

            
            if not any(is_token(tokens, start_idx, op) for op in assignment_op):
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected an assignment operator but found  {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                return False, None
            
            
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            
            
            if is_token(tokens, start_idx, 'stimuli'):
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
                return statements.parse_stimuli_call(tokens, start_idx, line_number)
            else:
                
                start_idx = skip_spaces(tokens, start_idx)
                return statements.assignment_statement(tokens, start_idx - 2)

        @staticmethod
        def parse_stimuli_call(tokens, start_idx, line_number):
            """
            Parses a valid stimuli call: stimuli("text");
            """

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
            start_idx = skip_spaces(tokens, start_idx)

            
            if not is_token(tokens, start_idx, '('):
                print(f"Error: Expected '(' at index {start_idx} (line {line_number})")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an open parenthesis but found {tokens[start_idx][0]}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)
            
            
            if not is_token(tokens, start_idx, 'string literal'):
                print(f"Error: Expected string literal at index {start_idx} (line {line_number})")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a string literal but found {tokens[start_idx][0]}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)
            
            
            if not is_token(tokens, start_idx, ')'):
                print(f"Error: Expected ')' at index {start_idx} (line {line_number}) in stimuli call")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing parenthesis but found {tokens[start_idx][0]}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)
            
            
            if is_token(tokens, start_idx, ';'):
                return True, start_idx + 1
            else:
                print(f"Error: Expected ';' at index {start_idx} (line {line_number})")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a semicolon in stimuli call but found {tokens[start_idx][0]}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

    
        @staticmethod
        def assignment_statement(tokens, start_idx):
            
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
            
            
            start_idx = skip_spaces(tokens, start_idx)
            
            
            if not any(is_token(tokens, start_idx, op) for op in assignment_op):
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected an assignment operator but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                return False, start_idx

            
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            
            
            is_valid, new_idx = statements.assignment_value(tokens, start_idx)
            if not is_valid:
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected a valid assignment value but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                return False, start_idx
            
            start_idx = new_idx  
            start_idx = skip_spaces(tokens, start_idx)  
            
            
            while start_idx < len(tokens) and is_token(tokens, start_idx, ','):
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
                
                if not is_token(tokens, start_idx, 'Identifier'):
                    line_num, line_txt = get_current_line_info(start_idx)
                    found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                    output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected an Identifier but found {found_token}\n")
                    output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
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
                        line_num, line_txt = get_current_line_info(start_idx)
                        found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                        output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected closing bracket ']' but found {found_token}\n")
                        output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                        return False, None
                    
                    start_idx += 1  
                    start_idx = skip_spaces(tokens, start_idx)

                if not any(is_token(tokens, start_idx, op) for op in assignment_op):
                    line_num, line_txt = get_current_line_info(start_idx)
                    found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                    output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected an assignment operator but found {found_token}\n")
                    output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                    return False, start_idx
                
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)
                
                
                is_valid, new_idx = statements.assignment_value(tokens, start_idx)
                if not is_valid:
                    line_num, line_txt = get_current_line_info(start_idx)
                    found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                    output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected a valid assignment value but found {found_token}\n")
                    output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
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
                    line_num, line_txt = get_current_line_info(start_idx)
                    found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                    output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected closing bracket ']' but found {found_token}\n")
                    output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                    return False, None
                
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)

            
            if not is_token(tokens, start_idx, ';'):
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected a semicolon or arithmetic operator in assignment but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                return False, start_idx
            
            start_idx += 1  
            return True, start_idx
                            
        @staticmethod
        def for_loop_statement(tokens, start_idx):
            
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

            print(f"DEBUG SYNTAX: Starting for_loop_statement at index {start_idx}")
            print(f"DEBUG SYNTAX: Current tokens: {tokens[start_idx:start_idx+5] if start_idx < len(tokens) else 'end of tokens'}")

            
            start_idx = skip_spaces(tokens, start_idx)

            
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

            
            if not (start_idx < len(tokens) and tokens[start_idx][0] == '('):
                print(f"ERROR: Expected '(' at index {start_idx}")
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected an open parenthesis but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                return False, start_idx
            start_idx += 1  

            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and tokens[start_idx][0] == 'dose'):
                print(f"ERROR: Expected 'dose' for initialization at index {start_idx}")
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected dose keyword but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                return False, start_idx
            start_idx += 1  

            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and tokens[start_idx][1] == "Identifier"):
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected an Identifier but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                return False, start_idx
            start_idx += 1  

            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and tokens[start_idx][0] == '='):
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected an equal sign but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                return False, start_idx
            start_idx += 1  

            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and tokens[start_idx][1] in ["Identifier", "numlit"]):
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected Identifier or Numlit but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                return False, start_idx
            start_idx += 1  

            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and tokens[start_idx][0] == ";"):
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected semicolon but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                return False, start_idx
            start_idx += 1  

            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and tokens[start_idx][1] == "Identifier"):
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected an Identifier but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                return False, start_idx
            start_idx += 1  

            start_idx = skip_spaces(tokens, start_idx)

            
            if start_idx >= len(tokens) or tokens[start_idx][0] not in conditional_op:
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected a conditional operator but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_txt}\n")
                return False, start_idx
            start_idx += 1  

            start_idx = skip_spaces(tokens, start_idx)

            
            is_valid, new_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
            if not is_valid:
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected an Identifier or numlit but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                return False, None

            start_idx = new_idx
            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and tokens[start_idx][0] == ";"):
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected a semicolon in for loop but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                return False, start_idx

            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and (tokens[start_idx][1] == "Identifier" or tokens[start_idx][0] in ['++', '--'])):
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected Identifier or unary operator but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
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
                    found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                    output_text.insert(tk.END, f"Syntax Error at line {identifier_line_number}: Expected an Identifier but found {found_token}\n")
                    output_text.insert(tk.END, f"Line {identifier_line_number}: {identifier_line_text}\n")
                    return False, start_idx
                start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and tokens[start_idx][0] == ')'):
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected closing parenthesis for for loop but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                return False, None

            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)

            
            if not (start_idx < len(tokens) and tokens[start_idx][0] == '{'):
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected '{{' but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)

            
            is_valid, new_idx = program.body_statements(tokens, start_idx)
            if not is_valid:
                return False, None
                        
            start_idx = new_idx
            
            
            if not (start_idx < len(tokens) and tokens[start_idx][0] == '}'):
                line_num, line_txt = get_current_line_info(start_idx)
                found_token = tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'
                output_text.insert(tk.END, f"Syntax Error at line {line_num}: Expected '}}' but found {found_token}\n")
                output_text.insert(tk.END, f"Line {line_num}: {line_txt}\n")
                return False, None
            
            start_idx += 1  
            return True, start_idx

        @staticmethod
        def prod_statement(tokens, start_idx):
            print("inside prod_statement")

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

            
            start_idx = skip_spaces(tokens, start_idx)
            if start_idx < len(tokens) and is_token(tokens, start_idx, ';'):
                print(f"Error: Expected ';' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected ';'\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                print(f"Valid empty prod statement at index {start_idx}")
                return True, start_idx + 1  
            
            
            is_valid, new_idx = statements.prod_value(tokens, start_idx)
            if not is_valid:
                print(f"Error: Invalid arithmetic expression at index {start_idx}")
                return False, None

            
            start_idx = new_idx
            start_idx = skip_spaces(tokens, start_idx)

            
            if start_idx < len(tokens) and is_token(tokens, start_idx, ';'):
                print(f"Valid prod statement (ends with ';') at index {start_idx}")
                return True, start_idx + 1  

            print(f"Error: Expected literal at prod statement, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected ';'\n")
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
            
            
            valid_tokens = ['Identifier', 'dom', 'rec', 'ff']
            
            
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
            
            
            return False, None

        @staticmethod
        def do_while_statement(tokens, start_idx):
            print("<do_while_statement>")
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After initial skip_spaces, start_idx={start_idx}, token={tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            
            
            
            if not is_token(tokens, start_idx, '{'):
                print(f"DEBUG SYNTAX: Expected '{{' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            
            
            start_idx += 1
            print(f"DEBUG SYNTAX: After opening brace, start_idx={start_idx}")
            
            
            is_valid, new_idx = program.body_statements(tokens, start_idx)
            if not is_valid:
                return False, None
                        
            
            start_idx = new_idx
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After body statements, start_idx={start_idx}, token={tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            
            
            if not is_token(tokens, start_idx, '}'):
                print(f"DEBUG SYNTAX: Expected '}}' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            
            
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After closing brace, start_idx={start_idx}, token={tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            
            
            if not is_token(tokens, start_idx, 'while'):
                print(f"DEBUG SYNTAX: Expected 'while' keyword but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            
            
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After 'while' keyword, start_idx={start_idx}, token={tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            
            
            if not is_token(tokens, start_idx, '('):
                print(f"DEBUG SYNTAX: Expected '(' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            
            
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After opening parenthesis, start_idx={start_idx}, token={tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            
            
            is_valid, new_idx = conditional.conditional_block(tokens, start_idx)
            if not is_valid or new_idx is None:
                print(f"DEBUG SYNTAX: Invalid condition at index {start_idx}")
                return False, None
            
            start_idx = new_idx
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After condition, start_idx={start_idx}, token={tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            
            
            if not is_token(tokens, start_idx, ')'):
                print(f"DEBUG SYNTAX: Expected ')' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'} in do-while statement")
                return False, None
            
            
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After closing parenthesis, start_idx={start_idx}, token={tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            
            
            if is_token(tokens, start_idx, ';'):
                start_idx += 1  
                print(f"DEBUG SYNTAX: After semicolon, start_idx={start_idx}")
            
            print(f"DEBUG SYNTAX: Successfully parsed do-while statement, returning True, {start_idx}")
            return True, start_idx
  
        @staticmethod
        def while_statement(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, '('):
                print(f"Error: Expected '(' after 'while' at index {start_idx}")
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
                return False, None

            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, '{'):
                print(f"Error: Expected '{{' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None

            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)

            
            is_valid, new_idx = program.body_statements(tokens, start_idx)
            if not is_valid:
                return False, None
                        

            start_idx = new_idx
            
            
            if not is_token(tokens, start_idx, '}'):
                print(f"Error: Expected '}}' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            
            return True, start_idx + 1
    
    class variables:
        @staticmethod
        def validate_doseval(tokens, start_idx):
            
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

            start_idx = skip_spaces(tokens, start_idx)

            
            if not is_token(tokens, start_idx, 'Identifier'):
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
                        
                        next_idx = start_idx + 1
                        next_idx = skip_spaces(tokens, next_idx)
                        
                        if next_idx < len(tokens) and any(is_token(tokens, next_idx, op) for op in math_operator):
                            
                            is_valid, new_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
                            if is_valid:
                                start_idx = new_idx
                            else:
                                
                                number_sign = check_number_sign(tokens[start_idx])
                                if number_sign in {"quantval", "nequantliteral"}:
                                    
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
                            
                            number_sign = check_number_sign(tokens[start_idx])
                            if number_sign in {"quantval", "nequantliteral"}:
                                
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

                        
                        next_idx = start_idx + 1
                        next_idx = skip_spaces(tokens, next_idx)
                        
                        if next_idx < len(tokens) and any(is_token(tokens, next_idx, op) for op in math_operator):
                            
                            is_valid, new_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
                            if is_valid:
                                start_idx = new_idx
                            else:
                                
                                start_idx += 1
                        else:
                            
                            start_idx += 1
                    else:
                        
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
                
                
                if is_token(tokens, start_idx, ';'):
                    return True, start_idx + 1
                
                if not is_token(tokens, start_idx, ','):
                    output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected a comma, math op or semicolon but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                
                
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                
                
                if not is_token(tokens, start_idx, 'Identifier'):
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                start_idx += 1
                
                start_idx = skip_spaces(tokens, start_idx)

        @staticmethod
        def validate_seqval(tokens, start_idx):
            
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

            start_idx = skip_spaces(tokens, start_idx)

            
            if not is_token(tokens, start_idx, 'Identifier'):
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            while True:
                
                if is_token(tokens, start_idx, '='):
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    
                    if is_token(tokens, start_idx, 'string literal'):
                        start_idx += 1
                    else:
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected string literal but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                                        
                    start_idx = skip_spaces(tokens, start_idx)
                
                
                if is_token(tokens, start_idx, ';'):
                    return True, start_idx + 1
                
                if not is_token(tokens, start_idx, ','):
                    output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected a comma, math op or semicolon but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                
                
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                
                
                if not is_token(tokens, start_idx, 'Identifier'):
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                start_idx += 1
                
                start_idx = skip_spaces(tokens, start_idx)

                        
        @staticmethod
        def validate_alleleval(tokens, start_idx):
            
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

            start_idx = skip_spaces(tokens, start_idx)

            
            if not is_token(tokens, start_idx, 'Identifier'):
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

                    else:
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected dom, rec or numlit but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                        return False, None
                                        
                    start_idx = skip_spaces(tokens, start_idx)
                
                
                if is_token(tokens, start_idx, ';'):
                    return True, start_idx + 1
                
                if not is_token(tokens, start_idx, ','):
                    output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected a comma, math op or semicolon but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                
                
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                
                
                if not is_token(tokens, start_idx, 'Identifier'):
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                start_idx += 1
                
                start_idx = skip_spaces(tokens, start_idx)

        @staticmethod
        def validate_quantval(tokens, start_idx):
                    
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
                    start_idx = skip_spaces(tokens, start_idx)

                    
                    if not is_token(tokens, start_idx, 'Identifier'):
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
                                
                                next_idx = start_idx + 1
                                next_idx = skip_spaces(tokens, next_idx)
                                
                                if next_idx < len(tokens) and any(is_token(tokens, next_idx, op) for op in math_operator):
                                    
                                    is_valid, new_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
                                    if is_valid:
                                        start_idx = new_idx
                                    else:
                                        
                                        number_sign = check_number_sign(tokens[start_idx])
                                        if number_sign in {"doseliteral", "neliteral"}:
                                            output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected a quant value\n")
                                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                                            return False, None
                                        start_idx += 1
                                else:
                                    
                                    number_sign = check_number_sign(tokens[start_idx])
                                    if number_sign in {"doseliteral", "neliteral"}:
                                        output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected a quant value\n")
                                        output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                                        return False, None
                                    start_idx += 1
                            elif is_token(tokens, start_idx, 'Identifier'):
                                
                                next_idx = start_idx + 1
                                next_idx = skip_spaces(tokens, next_idx)
                                
                                if next_idx < len(tokens) and any(is_token(tokens, next_idx, op) for op in math_operator):
                                    
                                    is_valid, new_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
                                    if is_valid:
                                        start_idx = new_idx
                                    else:
                                        
                                        start_idx += 1
                                else:
                                    
                                    start_idx += 1
                            else:
                                output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected a quant value but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                                return False, None
                                                    
                            start_idx = skip_spaces(tokens, start_idx)
                        
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

                        
                        if is_token(tokens, start_idx, ';'):
                            return True, start_idx + 1
                        
                        if not is_token(tokens, start_idx, ','):
                            output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected a comma, math op or semicolon but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
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
            print('<clust_quantval>')
            start_idx = skip_spaces(tokens, start_idx)

            
            if not is_token(tokens, start_idx, 'Identifier'):
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            
            if not is_token(tokens, start_idx, '['):
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an open bracket but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            
            if not is_token(tokens, start_idx, 'numlit'):
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a number but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            
                
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

            
            if is_token(tokens, start_idx, '['):
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                if not is_token(tokens, start_idx, 'numlit'):
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a number but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                
                
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

            
            if is_token(tokens, start_idx, '='):
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                
                if not is_token(tokens, start_idx, '{'):
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an opening brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                
                if is_token(tokens, start_idx, '{'):
                    
                    while True:
                        if not is_token(tokens, start_idx, '{'):
                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an opening brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None
                        start_idx += 1
                        start_idx = skip_spaces(tokens, start_idx)

                        
                        while True:
                            if not is_token(tokens, start_idx, 'numlit'):
                                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a number but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                                return False, None
                            
                            
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
                    
                    while True:
                        if not is_token(tokens, start_idx, 'numlit'):
                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a number but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None
                        
                        
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

            
            if not is_token(tokens, start_idx, ';'):
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a semicolon but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

            return True, start_idx + 1

        @staticmethod
        def validate_clust_doseval(tokens, start_idx):
            
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

            print('<clust_dose>')
            start_idx = skip_spaces(tokens, start_idx)

            
            if not is_token(tokens, start_idx, 'Identifier'):
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            
            if not is_token(tokens, start_idx, '['):
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an open bracket but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            
            if not is_token(tokens, start_idx, 'numlit'):
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a number but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

            
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

            
            if is_token(tokens, start_idx, '['):
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                if not is_token(tokens, start_idx, 'numlit'):
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a number but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None

                
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

            
            if is_token(tokens, start_idx, '='):
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                
                if not is_token(tokens, start_idx, '{'):
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an opening brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                
                if is_token(tokens, start_idx, '{'):
                    
                    while True:
                        if not is_token(tokens, start_idx, '{'):
                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an opening brace but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None
                        start_idx += 1
                        start_idx = skip_spaces(tokens, start_idx)

                        
                        while True:
                            if not is_token(tokens, start_idx, 'numlit'):
                                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a number but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                                return False, None

                            
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
                    
                    while True:
                        if not is_token(tokens, start_idx, 'numlit'):
                            output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a number but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                            output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                            return False, None

                        
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

            
            if not is_token(tokens, start_idx, ';'):
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a semicolon but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None

            return True, start_idx + 1

        @staticmethod
        def validate_clust_seqval(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After initial skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            
            def get_current_line_info(idx):
                current_token = tokens[idx] if idx < len(tokens) else None
                
                
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
                    line_number = get_line_number(tokens, idx)
                    line_tokens = []
                    line_text = ""
                
                return line_number, line_text

            
            line_number, line_text = get_current_line_info(start_idx)

            
            if not is_token(tokens, start_idx, 'Identifier'):
                print(f"DEBUG SYNTAX: Expected Identifier at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an identifier but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            print(f"DEBUG SYNTAX: Found Identifier: {tokens[start_idx]}")
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            
            if not is_token(tokens, start_idx, '['):
                print(f"DEBUG SYNTAX: Expected '[' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an open bracket\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            print(f"DEBUG SYNTAX: Found opening bracket")
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            
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

            
            if not is_token(tokens, start_idx, ']'):
                print(f"DEBUG SYNTAX: Expected ']' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a closing bracket\n")
                output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                return False, None
            print(f"DEBUG SYNTAX: Found closing bracket")
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG SYNTAX: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            
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

            
            if is_token(tokens, start_idx, '='):
                print(f"DEBUG SYNTAX: Found equals sign, parsing initialization")
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                
                if not is_token(tokens, start_idx, '{'):
                    print(f"DEBUG SYNTAX: Expected '{{' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                    output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected an opening brace\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None
                print(f"DEBUG SYNTAX: Found opening brace")
                start_idx += 1

                start_idx = skip_spaces(tokens, start_idx)
                print(f"DEBUG SYNTAX: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

                
                if is_token(tokens, start_idx, '{'):
                    print(f"DEBUG SYNTAX: Detected 2D array (nested braces)")
                    
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
                    print(f"Error: Expected parameter type at index {start_idx}, found {tokens[start_idx]}")
                    output_text.insert(tk.END, f"Syntax error at line {line_number}: Expected an data type\n")
                    output_text.insert(tk.END, f"Line {line_number}: {line_text}\n")
                    return False, None, start_idx

                param_type = tokens[start_idx][0]
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                
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
            
            
            matching_line = None
            for line in display_lines:
                if current_token in line["tokens"]:
                    matching_line = line
                    break
            
            
            if matching_line:
                line_number = matching_line["line_number"]
                line_tokens = matching_line["tokens"]
                line_text = ' '.join([t[0] for t in line_tokens if t[1] != "space"])  
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
            print("<express_value>")
            
            exp_literals = {'string literal', 'numlit', 'Identifier', 'dom', 'rec'}
            values = []  
            print(f"Initial start_idx: {start_idx}")
            
            start_idx = skip_spaces(tokens, start_idx)
            print(f"After skipping spaces, start_idx: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            
            
            if start_idx < len(tokens) and is_token(tokens, start_idx, 'seq'):
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
                    
            
            elif start_idx < len(tokens) and tokens[start_idx][1] == 'Identifier':
                
                identifier = tokens[start_idx][0]
                print(f"Found identifier: {identifier}")
                
                
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                
                
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
                    
                    values.append(identifier)

            
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
                        print("Failed to parse seq_concat")
                        print("Syntax Error: Expected plus sign")
                        output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a plus sign\n")
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
                                print("Failed to parse seq_concat after comma")
                                print("Syntax Error: Expected plus sign")
                                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a plus sign\n")
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
                                print("Failed to parse seq_concat after comma")
                                print("Syntax Error: Expected plus sign")
                                output_text.insert(tk.END, f"Syntax Error at line {line_number}: Expected a plus sign\n")
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
                return False, "Error: Missing '(' after 'seq'", start_idx

            start_idx += 1  
            start_idx = skip_spaces(tokens, start_idx)

            
            if start_idx >= len(tokens) or tokens[start_idx][1] != "Identifier":
                return False, "Error: Missing Identifier inside 'seq()'", start_idx

            identifier = tokens[start_idx][0]
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            
            array_expr = ""
            while start_idx < len(tokens) and tokens[start_idx][0] == '[':
                array_expr += '['
                start_idx += 1  
                start_idx = skip_spaces(tokens, start_idx)

                
                if start_idx >= len(tokens) or (tokens[start_idx][1] != "Identifier" and tokens[start_idx][1] != "numlit"):
                    return False, "Error: Invalid array index", start_idx

                array_expr += tokens[start_idx][0]
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                
                if start_idx >= len(tokens) or tokens[start_idx][0] != ']':
                    return False, "Error: Missing ']'", start_idx

                array_expr += ']'
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

            
            if start_idx >= len(tokens) or tokens[start_idx][0] != ')':
                return False, "Error: Missing ')' to close 'seq()'", start_idx

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
        def express_array_value(tokens, start_idx, identifier):
            print("<express_array_value>")
            
            
            if start_idx >= len(tokens) or tokens[start_idx][0] != '[':
                print(f"Error: Expected '[' at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None, start_idx
            
            
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            
            
            default_value = None
            if start_idx < len(tokens) and tokens[start_idx][1] == 'numlit':
                default_value = tokens[start_idx][0]
                print(f"Found default value: {default_value}")
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
            
            
            splice_operations = []
            if start_idx < len(tokens) and tokens[start_idx][0] == ':':
                print("Found ':', parsing as express_array_splice")
                is_valid, splice_ops, next_idx = express.express_array_splice(tokens, start_idx)
                if not is_valid:
                    print("Failed to parse express_array_splice")
                    return False, None, start_idx
                
                splice_operations = splice_ops
                start_idx = next_idx
            
            
            tail_value = None
            if start_idx < len(tokens) and tokens[start_idx][1] == 'numlit':
                tail_value = tokens[start_idx][0]
                print(f"Found tail value: {tail_value}")
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
            
            
            if start_idx >= len(tokens) or tokens[start_idx][0] != ']':
                print(f"Error: Expected ']' at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None, start_idx
            
            
            start_idx += 1
            
            
            array_expr = f"{identifier}[{default_value if default_value else ''}"
            
            
            for splice in splice_operations:
                array_expr += splice
            
            
            if tail_value:
                array_expr += f"{tail_value}"
            
            array_expr += "]"
            
            print(f"Constructed array expression: {array_expr}")
            return True, array_expr, start_idx

        @staticmethod
        def express_array_splice(tokens, start_idx):
            print("<express_array_splice>")
            
            
            if start_idx >= len(tokens) or tokens[start_idx][0] != ':':
                print(f"Error: Expected ':' at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, [], start_idx
            
            
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            
            
            splice_ops = [':']
            
            
            is_valid, tail_splices, next_idx = express.express_array_splice_tail(tokens, start_idx)
            if not is_valid:
                print("Failed to parse express_array_splice_tail")
                return False, [], start_idx
            
            
            splice_ops.extend(tail_splices)
            
            return True, splice_ops, next_idx

        @staticmethod
        def express_array_splice_tail(tokens, start_idx):
            print("<express_array_splice_tail>")
            
            
            if start_idx < len(tokens) and tokens[start_idx][0] == ':':
                print("Found ':', parsing as another express_array_splice")
                is_valid, splice_ops, next_idx = express.express_array_splice(tokens, start_idx)
                if not is_valid:
                    print("Failed to parse nested express_array_splice")
                    return False, [], start_idx
                
                return True, splice_ops, next_idx
            
            
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

                
                if token[1] == '}' and brace_count == 0:
                    print("PROCESS TOKENS Closing brace detected, checking for following keywords.")
                    
                    
                    next_index = i + 1
                    while next_index < len(tokens) and tokens[next_index][1] in ["space", "newline"]:
                        next_index += 1
                    
                    
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
            
            output_text.insert(tk.END, f"Expected global declaration, user defined or main function\n")


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
        output_text.insert(tk.END, "You May Push!\n")
        print("\nAll statements are valid!")

    return syntax_error