import GenomeX_Lexer as gxl
import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk

def parseSyntax(tokens, output_text):
    def skip_spaces(tokens, start_idx):
        while start_idx < len(tokens) and tokens[start_idx][1] == "space":
            start_idx += 1
        return start_idx

    def is_token(tokens, start_idx, predict_set):
        return start_idx < len(tokens) and tokens[start_idx][1] == predict_set

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

            if token_value != pattern[pattern_idx]:
                return False, token_idx, None

            token_idx += 1
            pattern_idx += 1

        return True, token_idx, number_sign
    
    class program:
        def validate_program(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)

            # Check for 'Identifier'
            if not is_token(tokens, start_idx, 'Identifier'):
                return False, None
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)

            # Check for '='
            if not is_token(tokens, start_idx, '='):
                return False, None
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)

            # Check for 'numlit'
            if not is_token(tokens, start_idx, 'numlit'):
                return False, None

            number_sign = check_number_sign(tokens[start_idx])
            if number_sign in {"quantval", "nequantliteral"}:
                return False, None
            start_idx += 1

            while True:
                start_idx = skip_spaces(tokens, start_idx)

                # Check for end of statement with ';'
                if is_token(tokens, start_idx, ';'):
                    start_idx += 1
                    break
                
                # Check for multiple declarations separated by ','
                elif is_token(tokens, start_idx, ','):
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)

                    # Check for 'Identifier'
                    if not is_token(tokens, start_idx, 'Identifier'):
                        return False, None
                    start_idx += 1

                    start_idx = skip_spaces(tokens, start_idx)

                    # Check for '='
                    if not is_token(tokens, start_idx, '='):
                        return False, None
                    start_idx += 1

                    start_idx = skip_spaces(tokens, start_idx)

                    # Check for 'numlit'
                    if not is_token(tokens, start_idx, 'numlit'):
                        return False, None

                    number_sign = check_number_sign(tokens[start_idx])
                    if number_sign in {"quantval", "nequantliteral"}:
                        return False, None
                    start_idx += 1

                else:
                    return False, None

            start_idx = skip_spaces(tokens, start_idx)

            # Check for closing '}'
            if not is_token(tokens, start_idx, '}'):
                return False, None
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)

            # Final check for statement termination with ';'
            if not is_token(tokens, start_idx, ';'):
                return False, None
            start_idx += 1

            return True, number_sign
    
    class if_else_statement:
        def ifelse_statement(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, 'if'):
                return False, None
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, '('):
                return False, None
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            # Assuming condition is a single token for simplicity
            if not is_token(tokens, start_idx, 'condition'):
                return False, None
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, ')'):
                return False, None
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, '{'):
                return False, None
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            # Assuming body is a single token for simplicity
            if not is_token(tokens, start_idx, 'body'):
                return False, None
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, '}'):
                return False, None
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            if is_token(tokens, start_idx, 'else'):
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                if not is_token(tokens, start_idx, '{'):
                    return False, None
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                # Assuming body is a single token for simplicity
                if not is_token(tokens, start_idx, 'body'):
                    return False, None
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                if not is_token(tokens, start_idx, '}'):
                    return False, None
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

            return True, None
    class express: #Print statement
        def express_statement(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, 'string literal'):
                return False, None
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, ')'):
                return False, None
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, ';'):
                return False, None
            start_idx += 1

            return True, None
    
    class inside_loop_statement:
        def destroy_statement(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, ';'):
                return False, None
            start_idx += 1

            return True, None
        
        def contig_statement(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, ';'):
                return False, None
            start_idx += 1

            return True, None

    class perms_variables:
        def perms_validate_doseval(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)

            # Check for identifier
            if not is_token(tokens, start_idx, 'Identifier'):
                return False, None
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)

            # Check for equals sign
            if not is_token(tokens, start_idx, '='):
                return False, None
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)

            # Check for 'numlit'
            if not is_token(tokens, start_idx, 'numlit'):
                return False, None

            number_sign = check_number_sign(tokens[start_idx])
            if number_sign in {"quantval", "nequantliteral"}:  # Boolean not allowed for dose
                return False, None

            start_idx += 1

            while True:
                start_idx = skip_spaces(tokens, start_idx)

                # Check for end of statement
                if is_token(tokens, start_idx, ';'):
                    return True, number_sign
                
                # Check for comma for more initializations
                elif not is_token(tokens, start_idx, ','):
                    return False, None

                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                # Check for identifier
                if not is_token(tokens, start_idx, 'Identifier'):
                    return False, None
                start_idx += 1

                start_idx = skip_spaces(tokens, start_idx)

                # Check for equals sign
                if not is_token(tokens, start_idx, '='):
                    return False, None
                start_idx += 1

                start_idx = skip_spaces(tokens, start_idx)

                # Check for 'numlit'
                if not is_token(tokens, start_idx, 'numlit'):
                    return False, None

                number_sign = check_number_sign(tokens[start_idx])
                if number_sign in {"quantval", "nequantliteral"}:
                    return False, None

                start_idx += 1
        
        def perms_validate_seqval(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, 'Identifier'):
                return False, None 
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            if not is_token(tokens, start_idx, '='):
                return False, None
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            if not is_token(tokens, start_idx, 'string literal'):
                return False, None  
            start_idx += 1

            while True:
                start_idx = skip_spaces(tokens, start_idx)

                if is_token(tokens, start_idx, ';'):
                    return True, None  
                elif not is_token(tokens, start_idx, ','):
                    return False, None

                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                if not is_token(tokens, start_idx, 'Identifier'):
                    return False, None
                start_idx += 1

                start_idx = skip_spaces(tokens, start_idx)
                if not is_token(tokens, start_idx, '='):
                    return False, None
                start_idx += 1

                start_idx = skip_spaces(tokens, start_idx)
                if not is_token(tokens, start_idx, 'string literal'):
                    return False, None
                start_idx += 1


        def perms_validate_alleleval(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)

            print("Starting allele validation at index:", start_idx)
            sign = None

            # Check for identifier
            if not is_token(tokens, start_idx, 'Identifier'):
                print("Expected Identifier, got:", tokens[start_idx])
                return False, sign
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)

            # Check for equals sign
            if not is_token(tokens, start_idx, '='):
                print("Expected '=', got:", tokens[start_idx])
                return False, sign
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)

            # Check for 'dom' or 'rec'
            if not is_token(tokens, start_idx, 'dom') and not is_token(tokens, start_idx, 'rec'):
                print("Expected 'dom' or 'rec', got:", tokens[start_idx])
                return False, sign
            start_idx += 1

            while True:
                start_idx = skip_spaces(tokens, start_idx)

                # Check for end of statement
                if is_token(tokens, start_idx, ';'):
                    print("Valid alleleval found.")
                    return True, sign
                
                # Check for comma for more initializations
                elif not is_token(tokens, start_idx, ','):
                    print("Expected ',', got:", tokens[start_idx])
                    return False, sign

                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                # Check for identifier
                if not is_token(tokens, start_idx, 'Identifier'):
                    print("Expected Identifier, got:", tokens[start_idx])
                    return False, sign
                start_idx += 1

                start_idx = skip_spaces(tokens, start_idx)

                # Check for equals sign
                if not is_token(tokens, start_idx, '='):
                    print("Expected '=', got:", tokens[start_idx])
                    return False, sign
                start_idx += 1

                start_idx = skip_spaces(tokens, start_idx)

                # Check for 'dom' or 'rec'
                if not is_token(tokens, start_idx, 'dom') and not is_token(tokens, start_idx, 'rec'):
                    print("Expected 'dom' or 'rec', got:", tokens[start_idx])
                    return False, sign
                start_idx += 1

        def perms_validate_quantval(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)
            if not is_token(tokens, start_idx, 'Identifier'):
                return False, None
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            if not is_token(tokens, start_idx, '='):
                return False, None
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            if not is_token(tokens, start_idx, 'numlit'):
                return False, None

            number_sign = check_number_sign(tokens[start_idx])
            if number_sign in {"doseval", "neliteral"}:
                return False, None
            start_idx += 1

            while True:
                start_idx = skip_spaces(tokens, start_idx)
                if is_token(tokens, start_idx, ';'):
                    return True, number_sign
                elif not is_token(tokens, start_idx, ','):
                    return False, None

                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                if not is_token(tokens, start_idx, 'Identifier'):
                    return False, None
                start_idx += 1

                start_idx = skip_spaces(tokens, start_idx)
                if not is_token(tokens, start_idx, '='):
                    return False, None
                start_idx += 1

                start_idx = skip_spaces(tokens, start_idx)
                if not is_token(tokens, start_idx, 'numlit'):
                    return False, None

                number_sign = check_number_sign(tokens[start_idx])
                if number_sign in {"doseval", "neliteral"}:
                    return False, None
                start_idx += 1
  
    class variables:
        def validate_doseval(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)

            print(f"Starting validation at index {start_idx}, token: {tokens[start_idx]}")

            # Check for the first identifier
            if not is_token(tokens, start_idx, 'Identifier'):
                print("Expected Identifier, got:", tokens[start_idx])
                return False, None
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"After first identifier, index {start_idx}, token: {tokens[start_idx]}")

            while True:
                # Case 1: End of statement (semicolon)
                if is_token(tokens, start_idx, ';'):
                    print("Valid statement (semicolon found)")
                    return True, None

                # Case 2: Comma separator (more variables)
                elif is_token(tokens, start_idx, ','):
                    print("Comma found, expecting another identifier")
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)

                    # Check for the next identifier
                    if not is_token(tokens, start_idx, 'Identifier'):
                        print("Expected Identifier after comma, got:", tokens[start_idx])
                        return False, None
                    start_idx += 1

                    start_idx = skip_spaces(tokens, start_idx)
                    print(f"After identifier, index {start_idx}, token: {tokens[start_idx]}")

                # Check if the next token is an assignment or another comma/semicolon
                if is_token(tokens, start_idx, '='):
                    print("Equals sign found, expecting a numeric literal")
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)

                    # Check for 'numlit' after the equals sign
                    if not is_token(tokens, start_idx, 'numlit'):
                        print("Expected numeric literal after equals sign, got:", tokens[start_idx])
                        return False, None

                    number_sign = check_number_sign(tokens[start_idx])
                    if number_sign in {"quantval", "nequantliteral"}:
                        print("Invalid numeric literal type:", number_sign)
                        return False, None
                    start_idx += 1

                    start_idx = skip_spaces(tokens, start_idx)
                    print(f"After numeric literal, index {start_idx}, token: {tokens[start_idx]}")

                # Case 3: Assignment without a preceding comma (e.g., `C = 13`)
                elif is_token(tokens, start_idx, '='):
                    print("Equals sign found, expecting a numeric literal")
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)

                    # Check for 'numlit' after the equals sign
                    if not is_token(tokens, start_idx, 'numlit'):
                        print("Expected numeric literal after equals sign, got:", tokens[start_idx])
                        return False, None

                    number_sign = check_number_sign(tokens[start_idx])
                    if number_sign in {"quantval", "nequantliteral"}:
                        print("Invalid numeric literal type:", number_sign)
                        return False, None
                    start_idx += 1

                    start_idx = skip_spaces(tokens, start_idx)
                    print(f"After numeric literal, index {start_idx}, token: {tokens[start_idx]}")

                # Case 4: Invalid token
                else:
                    print("Unexpected token:", tokens[start_idx])
                    return False, None
                
        def validate_seqval(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, 'Identifier'):
                return False
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            if not is_token(tokens, start_idx, '='):
                return False
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            if not is_token(tokens, start_idx, 'string literal'):
                return False
            start_idx += 1

            while True:
                start_idx = skip_spaces(tokens, start_idx)

                if is_token(tokens, start_idx, ';'):
                    return True
                elif not is_token(tokens, start_idx, ','):
                    return False

                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                if not is_token(tokens, start_idx, 'Identifier'):
                    return False
                start_idx += 1

                start_idx = skip_spaces(tokens, start_idx)
                if not is_token(tokens, start_idx, '='):
                    return False
                start_idx += 1

                start_idx = skip_spaces(tokens, start_idx)
                if not is_token(tokens, start_idx, 'string literal'):
                    return False
                start_idx += 1

        def validate_alleleval(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)

            # Check for identifier
            if not is_token(tokens, start_idx, 'Identifier'):
                return False
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)

            # Check for equals sign
            if not is_token(tokens, start_idx, '='):
                return False
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)

            # Check for 'dom' or 'rec'
            if not is_token(tokens, start_idx, 'dom') and not is_token(tokens, start_idx, 'rec'):
                return False
            start_idx += 1

            while True:
                start_idx = skip_spaces(tokens, start_idx)

                # Check for end of statement
                if is_token(tokens, start_idx, ';'):
                    return True
                
                # Check for comma for more initializations
                elif not is_token(tokens, start_idx, ','):
                    return False

                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                # Check for identifier
                if not is_token(tokens, start_idx, 'Identifier'):
                    return False
                start_idx += 1

                start_idx = skip_spaces(tokens, start_idx)

                # Check for equals sign
                if not is_token(tokens, start_idx, '='):
                    return False
                start_idx += 1

                start_idx = skip_spaces(tokens, start_idx)

                # Check for 'dom' or 'rec'
                if not is_token(tokens, start_idx, 'dom') and not is_token(tokens, start_idx, 'rec'):
                    return False
                start_idx += 1

        def validate_quantval(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)

            print(f"Starting validation at index {start_idx}, token: {tokens[start_idx]}")

            # Check for the first identifier
            if not is_token(tokens, start_idx, 'Identifier'):
                print("Expected Identifier, got:", tokens[start_idx])
                return False, None
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"After first identifier, index {start_idx}, token: {tokens[start_idx]}")

            while True:
                # Case 1: End of statement (semicolon)
                if is_token(tokens, start_idx, ';'):
                    print("Valid statement (semicolon found)")
                    return True, None

                # Case 2: Comma separator (more variables)
                elif is_token(tokens, start_idx, ','):
                    print("Comma found, expecting another identifier")
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)

                    # Check for the next identifier
                    if not is_token(tokens, start_idx, 'Identifier'):
                        print("Expected Identifier after comma, got:", tokens[start_idx])
                        return False, None
                    start_idx += 1

                    start_idx = skip_spaces(tokens, start_idx)
                    print(f"After identifier, index {start_idx}, token: {tokens[start_idx]}")

                # Check if the next token is an assignment or another comma/semicolon
                if is_token(tokens, start_idx, '='):
                    print("Equals sign found, expecting a numeric literal")
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)

                    # Check for 'numlit' after the equals sign
                    if not is_token(tokens, start_idx, 'numlit'):
                        print("Expected numeric literal after equals sign, got:", tokens[start_idx])
                        return False, None

                    number_sign = check_number_sign(tokens[start_idx])
                    if number_sign == "doseliteral":  # Check if it's a whole number
                        print("Invalid numeric literal type: whole number not allowed")
                        return False, None
                    elif number_sign in {"neliteral"}:
                        print("Invalid numeric literal type:", number_sign)
                        return False, None
                    start_idx += 1

                    start_idx = skip_spaces(tokens, start_idx)
                    print(f"After numeric literal, index {start_idx}, token: {tokens[start_idx]}")

                # Case 3: Assignment without a preceding comma (e.g., `C = 13`)
                elif is_token(tokens, start_idx, '='):
                    print("Equals sign found, expecting a numeric literal")
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)

                    # Check for 'numlit' after the equals sign
                    if not is_token(tokens, start_idx, 'numlit'):
                        print("Expected numeric literal after equals sign, got:", tokens[start_idx])
                        return False, None

                    number_sign = check_number_sign(tokens[start_idx])
                    if number_sign in {"doseval", "neliteral"}:
                        print("Invalid numeric literal type:", number_sign)
                        return False, None
                    start_idx += 1

                    start_idx = skip_spaces(tokens, start_idx)
                    print(f"After numeric literal, index {start_idx}, token: {tokens[start_idx]}")

                # Case 4: Invalid token
                else:
                    print("Unexpected token:", tokens[start_idx])
                    return False, None

    class clust:
        def validate_clust_quantval(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)

            # Check for identifier
            if not is_token(tokens, start_idx, 'Identifier'):
                return False, None
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)

            # Check for opening bracket
            if not is_token(tokens, start_idx, '['):
                return False, None
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)

            # Check for dimension size
            if not is_token(tokens, start_idx, 'numlit'):
                return False, None

            literal = tokens[start_idx]
            number_sign = check_number_sign(literal)
            if number_sign not in {'doseliteral'}:
                return False, None
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)

            # Check for closing bracket
            if not is_token(tokens, start_idx, ']'):
                return False, None
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)

            # Check for second dimension (optional)
            if is_token(tokens, start_idx, '['):
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                if not is_token(tokens, start_idx, 'numlit') or check_number_sign(tokens[start_idx]) != "doseliteral":
                    return False, None
                start_idx += 1

                start_idx = skip_spaces(tokens, start_idx)
                if not is_token(tokens, start_idx, ']'):
                    return False, None

                start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)

            # Check for equals sign
            if not is_token(tokens, start_idx, '='):
                return False, None
            
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            # Check for opening brace
            if not is_token(tokens, start_idx, '{'):
                return False, None
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)

            # Check what type of array we're dealing with
            if is_token(tokens, start_idx, '{'):
                # Handle 2D array case (nested braces)
                while True:
                    if is_token(tokens, start_idx, '{'):
                        start_idx += 1
                        start_idx = skip_spaces(tokens, start_idx)

                        while True:
                            if not is_token(tokens, start_idx, 'numlit'):
                                return False, None

                            literal = tokens[start_idx]
                            number_sign = check_number_sign(literal)

                            if number_sign not in {'quantval', 'nequantliteral'}:
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
                                return False, None

                        start_idx = skip_spaces(tokens, start_idx)

                        if is_token(tokens, start_idx, ','):
                            start_idx += 1
                            start_idx = skip_spaces(tokens, start_idx)
                        elif is_token(tokens, start_idx, '}'):
                            start_idx += 1
                            break
                        else:
                            return False, None
                    else:
                        return False, None
            else:
                # Handle 1D array case (direct values)
                while True:
                    if not is_token(tokens, start_idx, 'numlit'):
                        return False, None

                    literal = tokens[start_idx]
                    number_sign = check_number_sign(literal)

                    if number_sign not in {'quantval', 'nequantliteral'}:
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
                        return False, None

            start_idx = skip_spaces(tokens, start_idx)

            # Check for semicolon
            if not is_token(tokens, start_idx, ';'):
                return False, None

            return True, number_sign
        
        def validate_clust_doseval(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)

            # Check for identifier
            if not is_token(tokens, start_idx, 'Identifier'):
                return False, None
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)

            # Check for opening bracket
            if not is_token(tokens, start_idx, '['):
                return False, None
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)

            # Check for dimension size
            if not is_token(tokens, start_idx, 'numlit'):
                return False, None

            literal = tokens[start_idx]
            number_sign = check_number_sign(literal)
            if number_sign not in {'doseliteral'}:
                return False, None
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)

            # Check for closing bracket
            if not is_token(tokens, start_idx, ']'):
                return False, None
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)

            # Check for second dimension (optional)
            if is_token(tokens, start_idx, '['):
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                if not is_token(tokens, start_idx, 'numlit') or check_number_sign(tokens[start_idx]) != "doseliteral":
                    return False, None
                start_idx += 1

                start_idx = skip_spaces(tokens, start_idx)
                if not is_token(tokens, start_idx, ']'):
                    return False, None

                start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)

            # Check for equals sign
            if not is_token(tokens, start_idx, '='):
                return False, None
            
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            # Check for opening brace
            if not is_token(tokens, start_idx, '{'):
                return False, None
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)

            # Check what type of array we're dealing with
            if is_token(tokens, start_idx, '{'):
                # Handle 2D array case (nested braces)
                while True:
                    if is_token(tokens, start_idx, '{'):
                        start_idx += 1
                        start_idx = skip_spaces(tokens, start_idx)

                        while True:
                            if not is_token(tokens, start_idx, 'numlit'):
                                return False, None

                            literal = tokens[start_idx]
                            number_sign = check_number_sign(literal)

                            if number_sign not in {'doseliteral', 'neliteral'}:
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
                                return False, None

                        start_idx = skip_spaces(tokens, start_idx)

                        if is_token(tokens, start_idx, ','):
                            start_idx += 1
                            start_idx = skip_spaces(tokens, start_idx)
                        elif is_token(tokens, start_idx, '}'):
                            start_idx += 1
                            break
                        else:
                            return False, None
                    else:
                        return False, None
            else:
                # Handle 1D array case (direct values)
                while True:
                    if not is_token(tokens, start_idx, 'numlit'):
                        return False, None

                    literal = tokens[start_idx]
                    number_sign = check_number_sign(literal)

                    if number_sign not in {'doseliteral', 'neliteral'}:
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
                        return False, None

            start_idx = skip_spaces(tokens, start_idx)

            # Check for semicolon
            if not is_token(tokens, start_idx, ';'):
                return False, None

            return True, number_sign

        def validate_clust_seqval(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)

            # Check for identifier
            if not is_token(tokens, start_idx, 'Identifier'):
                return False, None
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)

            # Check for opening bracket
            if not is_token(tokens, start_idx, '['):
                return False, None
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)

            # Check for dimension size
            if not is_token(tokens, start_idx, 'numlit'):
                return False, None

            literal = tokens[start_idx]
            number_sign = check_number_sign(literal)
            if number_sign not in {'doseliteral'}:
                return False, None
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)

            # Check for closing bracket
            if not is_token(tokens, start_idx, ']'):
                return False, None
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)

            # Check for second dimension (optional)
            if is_token(tokens, start_idx, '['):
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                if not is_token(tokens, start_idx, 'numlit') or check_number_sign(tokens[start_idx]) != "doseliteral":
                    return False, None
                start_idx += 1

                start_idx = skip_spaces(tokens, start_idx)
                if not is_token(tokens, start_idx, ']'):
                    return False, None

                start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)

            # Check for equals sign
            if not is_token(tokens, start_idx, '='):
                return False, None
            
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)

            # Check for opening brace
            if not is_token(tokens, start_idx, '{'):
                return False, None
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)

            # Check what type of array we're dealing with
            if is_token(tokens, start_idx, '{'):
                # Handle 2D array case (nested braces)
                while True:
                    if is_token(tokens, start_idx, '{'):
                        start_idx += 1
                        start_idx = skip_spaces(tokens, start_idx)

                        while True:
                            start_idx = skip_spaces(tokens, start_idx)
                            if not is_token(tokens, start_idx, 'string literal'):
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
                                return False, None

                        start_idx = skip_spaces(tokens, start_idx)

                        if is_token(tokens, start_idx, ','):
                            start_idx += 1
                            start_idx = skip_spaces(tokens, start_idx)
                        elif is_token(tokens, start_idx, '}'):
                            start_idx += 1
                            break
                        else:
                            return False, None
                    else:
                        return False, None
            else:
                while True:
                    if not is_token(tokens, start_idx, 'string literal'):
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
                        return False, None

            start_idx = skip_spaces(tokens, start_idx)

            # Check for semicolon
            if not is_token(tokens, start_idx, ';'):
                return False, None

            return True, number_sign

    def end_semicolon(tokens):
        lines = []
        current_line = []
        
        for token in tokens:
            if token[1] == "newline":
                continue

            current_line.append(token)

            if token[1] == ';':
                while current_line and current_line[0][1] == "space":
                    current_line.pop(0)

                lines.append(current_line)
                current_line = []

        if current_line:
            while current_line and current_line[0][1] == "space":
                current_line.pop(0)
            lines.append(current_line)

        return lines

    program_pattern = [
        ['act', 'gene', '(', ')', '{']
    ]
    express_pattern = [

        ['express', '(']
    ]
    global_pattern = [
        ['_G', 'quant'],
        ['_G', 'dose'],
        ['_G', 'seq'],
        ['_G', 'allele'],
        ['_G', 'clust', 'dose'],
        ['_G', 'clust', 'quant'],
        ['_G', 'clust', 'seq'],
        ['_G', 'perms', 'dose'],
        ['_G', 'perms', 'quant'],
        ['_G', 'perms', 'seq'],
        ['_G', 'perms', 'allele']
    ]

    local_pattern = [
        ['_L', 'quant'],
        ['_L', 'dose'],
        ['_L', 'seq'],
        ['_L', 'allele'],
        ['_L', 'clust', 'dose'],
        ['_L', 'clust', 'quant'],
        ['_L', 'clust', 'seq'],
        ['_L', 'perms', 'dose'],
        ['_L', 'perms', 'quant'],
        ['_L', 'perms', 'seq'],
        ['_L', 'perms', 'allele']
    ]

    #<variables_dose> LAHAT TO UNDER TYPE
    dose_pattern = [
        ['dose']
    ]

    #<variables_seq>
    seq_pattern = [
        ['seq']
    ]

    #<variables_quant>
    quant_pattern = [
        ['quant']
    ]

    #<variables_quant>
    allele_pattern = [
        ['allele']
    ]

    #<variables_perms>
    perms_pattern = [
        ['perms', 'dose'],
        ['perms', 'seq'],
        ['perms', 'allele'],
        ['perms', 'quant'],
    ]

    #<variables_perms>
    clust_pattern = [
        ['clust', 'dose'],
        ['clust', 'seq'],
        ['clust', 'allele'],
        ['clust', 'quant'],
    ]
    destroy_pattern = [
        ['destroy']
    ]

    contig_pattern = [
        ['contig']
    ]

    token_lines = end_semicolon(tokens)
    valid_syntax = True

    print("\nTokens Received:")
    for idx, (token_id, token_value) in enumerate(tokens, start=1):
        print(f"{idx}. Token: {token_value} (ID: {token_id})")

    for line_num, line_tokens in enumerate(token_lines, start=1):
        if not line_tokens:
            continue

        first_token = line_tokens[0][1] if line_tokens else None
        valid_line = False
        number_sign = None

        if first_token == "act":
            for pattern in program_pattern:
                is_valid, next_idx, _ = validate_syntax_pattern(line_tokens, pattern)
                if is_valid:
                    is_valid_program, sign = program.validate_program(line_tokens, next_idx)
                    if is_valid_program:
                        valid_line = True
                        print("Valid program syntax!")
                    else:
                        print("Invalid program body!")
                    break

        elif first_token == "express":
            for pattern in express_pattern:
                is_valid, next_idx, _ = validate_syntax_pattern(line_tokens, pattern)
                if is_valid:
                    is_valid_express, _ = express.express_statement(line_tokens, next_idx)
                    if is_valid_express:
                        valid_line = True
                    break
        
        elif first_token == "destroy":
            for pattern in destroy_pattern:
                is_valid, next_idx, _ = validate_syntax_pattern(line_tokens, pattern)
                if is_valid:
                    is_valid_express, _ = inside_loop_statement.destroy_statement(line_tokens, next_idx)
                    if is_valid_express:
                        valid_line = True
                    break

        elif first_token == "contig":
            for pattern in contig_pattern:
                is_valid, next_idx, _ = validate_syntax_pattern(line_tokens, pattern)
                if is_valid:
                    is_valid_express, _ = inside_loop_statement.contig_statement(line_tokens, next_idx)
                    if is_valid_express:
                        valid_line = True
                    break

        elif first_token == "_G":
            is_valid_perms = False  
            sign = None 

            for pattern in global_pattern:
                print(f"Checking pattern: {pattern}")
                is_valid, next_idx, _ = validate_syntax_pattern(line_tokens, pattern)
                print(f"Is pattern valid? {is_valid}")

                if is_valid:
                    data_type = pattern[1]
                    print(f"Data type identified: {data_type}")
                    
                    if data_type == 'quant':
                        if is_valid:
                            is_valid_quantval, sign = variables.validate_quantval(line_tokens, next_idx)
                            if is_valid_quantval:
                                valid_line = True
                                number_sign = sign
                            break

                    elif data_type == 'dose':
                        if is_valid:
                            is_valid_doseval, sign = variables.validate_doseval(line_tokens, next_idx)
                            if is_valid_doseval:
                                valid_line = True
                                number_sign = sign
                            break

                    elif data_type == 'allele':
                        if is_valid:
                            is_valid_alleleval = variables.validate_alleleval(line_tokens, next_idx)
                            if is_valid_alleleval:
                                valid_line = True
                            break

                    elif data_type == 'seq':
                        if is_valid:
                            is_valid_seqval = variables.validate_seqval(line_tokens, next_idx)
                            if is_valid_seqval:
                                valid_line = True
                            break

                    elif data_type == 'clust':
                        print("pasok sa global clust")
                        print(f"Checking pattern: {pattern}")
                        is_valid, next_idx, _ = validate_syntax_pattern(line_tokens, pattern)
                        print(f"Is pattern valid? {is_valid}")

                        if is_valid:
                            data_type = pattern[2]
                            print(f"Data type identified: {data_type}")
                            
                            if data_type == 'quant':
                                print("PASOK SA GLOBAL CLUST QUANT")
                                is_valid_perms, sign = clust.validate_clust_quantval(line_tokens, next_idx)

                            elif data_type == 'dose':
                                print("PASOK SA DOSE")
                                is_valid_perms, sign = clust.validate_clust_doseval(line_tokens, next_idx)

                            elif data_type == 'seq':
                                print("PASOK SA SEQ")
                                is_valid_perms, sign = clust.validate_clust_seqval(line_tokens, next_idx)
                                
                            if is_valid_perms:
                                valid_line = True
                                number_sign = sign
                            break  
  
                    elif data_type == 'perms':
                        print("pasok sa global clust")
                        print(f"Checking pattern: {pattern}")
                        is_valid, next_idx, _ = validate_syntax_pattern(line_tokens, pattern)
                        print(f"Is pattern valid? {is_valid}")

                        if is_valid:
                            data_type = pattern[2]
                            print(f"Data type identified: {data_type}")
                            
                            if data_type == 'quant':
                                print("PASOK SA GLOBAL CLUST QUANT")
                                is_valid_perms, sign = perms_variables.perms_validate_quantval(line_tokens, next_idx)

                            elif data_type == 'dose':
                                print("PASOK SA DOSE")
                                is_valid_perms, sign = perms_variables.perms_validate_doseval(line_tokens, next_idx)

                            elif data_type == 'seq':
                                print("PASOK SA SEQ")
                                is_valid_perms, sign = perms_variables.perms_validate_seqval(line_tokens, next_idx)

                            elif data_type == 'allele':
                                print("PASOK SA allele")
                                is_valid_perms, sign = perms_variables.perms_validate_alleleval(line_tokens, next_idx)
                                
                            if is_valid_perms:
                                valid_line = True
                                number_sign = sign
                            break

        elif first_token == "_L":
            is_valid_perms = False  
            sign = None 

            for pattern in local_pattern:
                print(f"Checking pattern: {pattern}")
                is_valid, next_idx, _ = validate_syntax_pattern(line_tokens, pattern)
                print(f"Is pattern valid? {is_valid}")

                if is_valid:
                    data_type = pattern[1]
                    print(f"Data type identified: {data_type}")
                    
                    if data_type == 'quant':
                        if is_valid:
                            is_valid_quantval, sign = variables.validate_quantval(line_tokens, next_idx)
                            if is_valid_quantval:
                                valid_line = True
                                number_sign = sign
                            break

                    elif data_type == 'dose':
                        if is_valid:
                            is_valid_doseval, sign = variables.validate_doseval(line_tokens, next_idx)
                            if is_valid_doseval:
                                valid_line = True
                                number_sign = sign
                            break

                    elif data_type == 'allele':
                        if is_valid:
                            is_valid_alleleval = variables.validate_alleleval(line_tokens, next_idx)
                            if is_valid_alleleval:
                                valid_line = True
                            break

                    elif data_type == 'seq':
                        if is_valid:
                            is_valid_seqval = variables.validate_seqval(line_tokens, next_idx)
                            if is_valid_seqval:
                                valid_line = True
                            break

                    elif data_type == 'clust':
                        print("pasok sa global clust")
                        print(f"Checking pattern: {pattern}")
                        is_valid, next_idx, _ = validate_syntax_pattern(line_tokens, pattern)
                        print(f"Is pattern valid? {is_valid}")

                        if is_valid:
                            data_type = pattern[2]
                            print(f"Data type identified: {data_type}")
                            
                            if data_type == 'quant':
                                print("PASOK SA GLOBAL CLUST QUANT")
                                is_valid_perms, sign = clust.validate_clust_quantval(line_tokens, next_idx)

                            elif data_type == 'dose':
                                print("PASOK SA DOSE")
                                is_valid_perms, sign = clust.validate_clust_doseval(line_tokens, next_idx)

                            elif data_type == 'seq':
                                print("PASOK SA SEQ")
                                is_valid_perms, sign = clust.validate_clust_seqval(line_tokens, next_idx)
                                
                            if is_valid_perms:
                                valid_line = True
                                number_sign = sign
                            break  
  
                    elif data_type == 'perms':
                        print("pasok sa global clust")
                        print(f"Checking pattern: {pattern}")
                        is_valid, next_idx, _ = validate_syntax_pattern(line_tokens, pattern)
                        print(f"Is pattern valid? {is_valid}")

                        if is_valid:
                            data_type = pattern[2]
                            print(f"Data type identified: {data_type}")
                            
                            if data_type == 'quant':
                                print("PASOK SA GLOBAL CLUST QUANT")
                                is_valid_perms, sign = perms_variables.perms_validate_quantval(line_tokens, next_idx)

                            elif data_type == 'dose':
                                print("PASOK SA DOSE")
                                is_valid_perms, sign = perms_variables.perms_validate_doseval(line_tokens, next_idx)

                            elif data_type == 'seq':
                                print("PASOK SA SEQ")
                                is_valid_perms, sign = perms_variables.perms_validate_seqval(line_tokens, next_idx)

                            elif data_type == 'allele':
                                print("PASOK SA allele")
                                is_valid_perms, sign = perms_variables.perms_validate_alleleval(line_tokens, next_idx)
                                
                            if is_valid_perms:
                                valid_line = True
                                number_sign = sign
                            break    
  
        elif first_token == "dose":
            for pattern in dose_pattern:
                is_valid, next_idx, _ = validate_syntax_pattern(line_tokens, pattern)
                if is_valid:
                    is_valid_doseval, sign = variables.validate_doseval(line_tokens, next_idx)
                    if is_valid_doseval:
                        valid_line = True
                        number_sign = sign
                    break

        elif first_token == "seq":
            for pattern in seq_pattern:
                is_valid, next_idx, _ = validate_syntax_pattern(line_tokens, pattern)
                if is_valid:
                    is_valid_seqval = variables.validate_seqval(line_tokens, next_idx)
                    if is_valid_seqval:
                        valid_line = True
                    break

        elif first_token == "quant":
            for pattern in quant_pattern:
                is_valid, next_idx, _ = validate_syntax_pattern(line_tokens, pattern)
                if is_valid:
                    is_valid_quantval, sign = variables.validate_quantval(line_tokens, next_idx)
                    if is_valid_quantval:
                        valid_line = True
                        number_sign = sign
                    break

        elif first_token == "allele":
            for pattern in allele_pattern:
                is_valid, next_idx, _ = validate_syntax_pattern(line_tokens, pattern)
                if is_valid:
                    is_valid_alleleval = variables.validate_alleleval(line_tokens, next_idx)
                    if is_valid_alleleval:
                        valid_line = True
                    break

        elif first_token == "perms":
            is_valid_perms = False  
            sign = None 

            for pattern in perms_pattern:
                print(f"Checking pattern: {pattern}")
                is_valid, next_idx, _ = validate_syntax_pattern(line_tokens, pattern)
                print(f"Is pattern valid? {is_valid}")

                if is_valid:
                    data_type = pattern[1]
                    print(f"Data type identified: {data_type}")
                    
                    if data_type == 'quant':
                        print("PASOK SA QUANT")
                        is_valid_perms, sign = perms_variables.perms_validate_quantval(line_tokens, next_idx)

                    elif data_type == 'dose':
                        print("PASOK SA DOSE")
                        is_valid_perms, sign = perms_variables.perms_validate_doseval(line_tokens, next_idx)

                    elif data_type == 'allele':
                        print("PASOK SA ALLELE")
                        is_valid_perms, sign = perms_variables.perms_validate_alleleval(line_tokens, next_idx)

                    elif data_type == 'seq':
                        print("PASOK SA SEQ")
                        is_valid_perms, sign = perms_variables.perms_validate_seqval(line_tokens, next_idx)
                        
                    if is_valid_perms:
                        valid_line = True
                        number_sign = sign
                    break  

        elif first_token == "clust":
            is_valid_perms = False  
            sign = None 

            for pattern in clust_pattern:
                print(f"Checking pattern: {pattern}")
                is_valid, next_idx, _ = validate_syntax_pattern(line_tokens, pattern)
                print(f"Is pattern valid? {is_valid}")

                if is_valid:
                    data_type = pattern[1]
                    print(f"Data type identified: {data_type}")
                    
                    if data_type == 'quant':
                        print("PASOK SA CLUST QUANT")
                        is_valid_perms, sign = clust.validate_clust_quantval(line_tokens, next_idx)

                    elif data_type == 'dose':
                        print("PASOK SA DOSE")
                        is_valid_perms, sign = clust.validate_clust_doseval(line_tokens, next_idx)

                    elif data_type == 'seq':
                        print("PASOK SA SEQ")
                        is_valid_perms, sign = clust.validate_clust_seqval(line_tokens, next_idx)
                        
                    if is_valid_perms:
                        valid_line = True
                        number_sign = sign
                    break  


        if valid_line:
            tokens_info = [f"{token[0]} ({token[1]})" for token in line_tokens]
            sign_msg = f" (Number is {number_sign})" if number_sign else ""
            print(f"Line {line_num}: Valid syntax {tokens_info}{sign_msg}")
    
        else:
            tokens_info = [f"{token[0]} ({token[1]})" for token in line_tokens]
            print(f"Line {line_num}: Syntax Error {tokens_info}")
            valid_syntax = False
            break

    if not valid_syntax:
        output_text.insert(tk.END, "Syntax Error: Invalid statement detected\n")
        output_text.yview(tk.END)
        print("\nSyntax Error!")
    else:
        output_text.insert(tk.END, "You May Push!\n")
        print("\nAll statements are valid!")
