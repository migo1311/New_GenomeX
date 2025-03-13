import GenomeX_Lexer as gxl
import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
import sys  # Import the system module
from itertools import chain


def parseSyntax(tokens, output_text):
    def get_line_number(tokens, idx):
        """
        Calculate the line number for a given token index by counting newlines.
        Returns 1-based line number.
        """
        if idx is None or idx >= len(tokens):
            return 0
            
        line_count = 1
        for i in range(idx):
            if tokens[i][1] == "newline":
                line_count += 1
        return line_count
    
    def skip_spaces(tokens, start_idx):
        # Guard against None
        if start_idx is None:
            return None
            
        while start_idx < len(tokens) and tokens[start_idx][1] in ["space", "newline","comment", "multiline"]:
            start_idx += 1
        return start_idx

    def is_token(tokens, idx, expected):
        if idx >= len(tokens):
            return False  # Prevent index errors
        token_value, token_type = tokens[idx]  # Unpack tuple
        if isinstance(expected, set):  
            return token_type in expected  # Check if token type is in the set
        return token_type == expected
    
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
            print("<body_statements>")
            statement_parsers = {
                'express': statements.express_statement,
                'dose': variables.validate_doseval,
                'seq': variables.validate_seqval,
                'quant': variables.validate_quantval,
                'allele': variables.validate_alleleval,
                'if': statements.if_statement,
                'prod': statements.prod_statement,
                'Identifier': statements.stimuli_statement,
                'for': statements.for_loop_statement,
                'do': statements.do_while_statement,
                'while': statements.while_statement
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
                start_idx = skip_spaces(tokens, start_idx)
                
                # Special handling for perms
                if is_token(tokens, start_idx, 'perms'):
                    check_statements = True  # Set to True when a valid perms statement is found
                    start_idx += 1  # Move past 'perms'
                    start_idx = skip_spaces(tokens, start_idx)

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

                # Special handling for *L (same logic as perms)
                if is_token(tokens, start_idx, '_L'):
                    print("<local_declaration>")
                    check_statements = True  # Set to True when a valid *L statement is found
                    start_idx += 1  # Move past '*L'
                    start_idx = skip_spaces(tokens, start_idx)

                    # Look for a valid L type
                    if not any(is_token(tokens, start_idx, l_type) for l_type in local_parse):
                        print("Invalid *L type")
                        return False, None  # Invalid *L type

                    for l_type, parser_func in local_parse.items():
                        if is_token(tokens, start_idx, l_type):
                            start_idx += 1  # Move past the type
                            start_idx = skip_spaces(tokens, start_idx)

                            is_valid, new_idx = parser_func(tokens, start_idx)
                            if not is_valid:
                                print(f"Invalid *L {l_type} statement")
                                return False, None

                            start_idx = new_idx
                            start_idx = skip_spaces(tokens, start_idx)
                            print(f"Successfully parsed *L {l_type}")
                            break  # Exit loop after parsing a valid *L statement

                    continue  # Continue main loop

                if is_token(tokens, start_idx, 'clust'):
                    print("<clust>")
                    check_statements = True  # Set to True when a valid *L statement is found
                    start_idx += 1  # Move past '*L'
                    start_idx = skip_spaces(tokens, start_idx)

                    # Look for a valid L type
                    if not any(is_token(tokens, start_idx, clust_type) for clust_type in clust_parse):
                        print("Invalid *clust type")
                        return False, None  

                    for clust_type, parser_func in clust_parse.items():
                        if is_token(tokens, start_idx, clust_type):
                            start_idx += 1  # Move past the type
                            start_idx = skip_spaces(tokens, start_idx)

                            is_valid, new_idx = parser_func(tokens, start_idx)
                            if not is_valid:
                                print(f"Invalid *L {clust_type} statement")
                                return False, None

                            start_idx = new_idx
                            start_idx = skip_spaces(tokens, start_idx)
                            print(f"Successfully parsed *L {clust_type}")
                            break  # Exit loop after parsing a valid *L statement

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
                        print(f"tapos act: {statement_type}")
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
            return check_statements, start_idx  # Return final state
        
        def global_declaration(tokens, start_idx):
            print("Parsing global declarations...")

            while start_idx < len(tokens) and is_token(tokens, start_idx, "_G"):
                start_idx += 1  # Move past '_G'
                start_idx = skip_spaces(tokens, start_idx)

                # Expect a datatype
                param_types = {"dose", "quant", "seq", "allele"}
                if not is_token(tokens, start_idx, param_types):
                    print(f"Error: Expected datatype after '_G' at index {start_idx}, found {tokens[start_idx]}")
                    return False, None
                
                start_idx += 1  # Move past datatype
                start_idx = skip_spaces(tokens, start_idx)

                # Expect a semicolon
                if not is_token(tokens, start_idx, ";"):
                    print(f"Error: Expected ';' at index {start_idx}, found {tokens[start_idx]}")
                    return False, None
                
                start_idx += 1  # Move past semicolon
                start_idx = skip_spaces(tokens, start_idx)

            return True, start_idx  # Finished parsing global declarations
        
        def main_function(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)
            is_main_function = is_token(tokens, start_idx, 'gene')
            
            # Check for 'gene' to identify main function
            if is_token(tokens, start_idx, 'gene'):
                print("main function")
                start_idx = skip_spaces(tokens, start_idx)
                
                if not is_token(tokens, start_idx, 'gene'):
                    print(f"Error: Expected '(' after 'if' at index {start_idx}")
                    return False, None
                start_idx += 1  # Move past '('
                
                start_idx = skip_spaces(tokens, start_idx)

                if not is_token(tokens, start_idx, '('):
                    print(f"Error: Expected '(' after 'if' at index {start_idx}")
                    return False, None
                start_idx += 1  # Move past '('

                # Ensure no semicolon is present before ')'
                if is_token(tokens, start_idx, ';'):
                    print(f"Error: Unexpected ';' at index {start_idx}")
                    return False, None

                if not is_token(tokens, start_idx, ')'):
                    print(f"Error: Expected ')' at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                    return False, None
                
                start_idx += 1 
                start_idx = skip_spaces(tokens, start_idx)            
                if not is_token(tokens, start_idx, '{'):
                    print("Missing opening brace for act block")
                    return False, None
                
                start_idx += 1  # Move past '{'
                start_idx = skip_spaces(tokens, start_idx)

                # Use the modified body_statements function
                check_statements, new_idx = program.body_statements(tokens, start_idx)
                
                if new_idx is None:
                    print("Error in body statements")
                    return False, None
                
                start_idx = new_idx
                
                # Check for closing brace
                if is_token(tokens, start_idx, '}'):
                    print("Found closing brace")
                    return (True, start_idx + 1) if check_statements else (False, None)  # Error if no statements found
                else:
                    print("Missing closing brace")
                    return False, None  # Error: Missing closing brace
                
            else:
                print("user defined function")
                
                # Check if the next token is 'void' (optional)
                if is_token(tokens, start_idx, 'void'):
                    start_idx += 1  # Move past 'void'
                    start_idx = skip_spaces(tokens, start_idx)

                if not is_token(tokens, start_idx, 'Identifier'):
                    print(f"Error: Expected function name (Identifier) at index {start_idx}")
                    return False, None

                start_idx += 1  # Move past function name
                start_idx = skip_spaces(tokens, start_idx)

                if not is_token(tokens, start_idx, '('):
                    print(f"Error: Expected '(' after 'if' at index {start_idx}")
                    return False, None
                start_idx += 1  # Move past '('

                # Parse the condition using condition_value_tail
                is_valid, params, new_idx = parameters.parse_params(tokens, start_idx)
                if not is_valid:
                    print(f"Error: Invalid condition in if statement at index {start_idx}")
                    return False, None

                start_idx = new_idx  # Move to next token
                start_idx = skip_spaces(tokens, start_idx)

                if not is_token(tokens, start_idx, ')'):
                    print(f"Error: Expected ')' at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                    return False, None
                
                start_idx += 1 
                start_idx = skip_spaces(tokens, start_idx)            
                if not is_token(tokens, start_idx, '{'):
                    print("Missing opening brace for act block")
                    return False, None
                
                start_idx += 1  # Move past '{'
                start_idx = skip_spaces(tokens, start_idx)

                # Use the modified body_statements function
                check_statements, new_idx = program.body_statements(tokens, start_idx)
                
                if new_idx is None:
                    print("Error in user def statements")
                    return False, None
                
                start_idx = new_idx
                
                # Check for closing brace
                if is_token(tokens, start_idx, '}'):
                    print("Found closing brace")
                    return (True, start_idx + 1) if check_statements else (False, None)  # Error if no statements found
                else:
                    print("Missing closing brace")
                    return False, None  # Error: Missing closing brace
                
    class conditional:
        @staticmethod
        def conditional_block(tokens, start_idx):
            """
            Parse a conditional block according to the CFG:
            <conditional_block> → <conditions_base>
            """
            print("<conditional_block>")
            start_idx = skip_spaces(tokens, start_idx)
            
            # Parse the conditions base
            is_valid, new_idx = conditional.conditions_base(tokens, start_idx)
            if not is_valid:
                output_text.insert(tk.END, f"Syntax Error: Invalid condition at line {get_line_number(tokens, start_idx)}\n")
                print(f"Error: Invalid conditions_base at index {start_idx}")
                return False, None
            
            return True, new_idx
        
        @staticmethod
        def conditions_base(tokens, start_idx):
            """
            Parse conditions base according to the CFG:
            <conditions_base> → <negation_operator><condition_value><conditional_operator><negation_operator><condition_value><condition_value_tail>
            """
            print("<conditions_base>")
            start_idx = skip_spaces(tokens, start_idx)
            
            # Parse first negation operator (optional)
            has_negation1 = False
            if start_idx < len(tokens) and tokens[start_idx][0] == '!':
                print(f"Found first negation operator '!' at index {start_idx}")
                has_negation1 = True
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
            
            # Parse conditional operator
            relational_operators = {'<', '>', '<=', '>=', '==', '!='}
            if not any(is_token(tokens, start_idx, op) for op in relational_operators):
                output_text.insert(tk.END, f"Syntax Error: Expected relational operator at line {get_line_number(tokens, start_idx)}\n")
                print(f"Error: Expected relational operator at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            
            print(f"Found conditional operator '{tokens[start_idx][0]}' at index {start_idx}")
            start_idx += 1  # Move past operator
            start_idx = skip_spaces(tokens, start_idx)
            
            # Parse second negation operator (optional)
            has_negation2 = False
            if start_idx < len(tokens) and tokens[start_idx][0] == '!':
                print(f"Found second negation operator '!' at index {start_idx}")
                has_negation2 = True
                start_idx += 1  # Move past '!'
                start_idx = skip_spaces(tokens, start_idx)
            
            # Parse second condition value
            is_valid, new_idx = conditional.condition_value(tokens, start_idx)
            if not is_valid:
                output_text.insert(tk.END, f"Syntax Error: Invalid condition value at line {get_line_number(tokens, start_idx)}\n")
                print(f"Error: Invalid second condition_value at index {start_idx}")
                return False, None
            
            start_idx = new_idx
            start_idx = skip_spaces(tokens, start_idx)
            
            # Parse condition value tail (optional logical operators and more conditions)
            is_valid, new_idx = conditional.condition_value_tail(tokens, start_idx)
            if not is_valid:
                output_text.insert(tk.END, f"Syntax Error: Invalid condition at line {get_line_number(tokens, start_idx)}\n")
                print(f"Error: Invalid condition_value_tail at index {start_idx}")
                return False, None
            
            return True, new_idx
        
        @staticmethod
        def condition_value(tokens, start_idx):
            """
            Parse condition value according to the CFG:
            <condition_value> → <arithmetic_sequence>
            <condition_value> → Identifier
            <condition_value> → <literals>
            <condition_value> → (<condition_base>)
            """
            print("<condition_value>")
            start_idx = skip_spaces(tokens, start_idx)
            
            # Case 1: Identifier
            if is_token(tokens, start_idx, 'Identifier'):
                print(f"Found Identifier '{tokens[start_idx][0]}' at index {start_idx}")
                return True, start_idx + 1  # Move past identifier
            
            # Case 2: Literal
            if is_token(tokens, start_idx, literals):
                print(f"Found literal '{tokens[start_idx][0]}' at index {start_idx}")
                return True, start_idx + 1  # Move past literal
            
            # Case 3: Parenthesized condition
            if is_token(tokens, start_idx, '('):
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
            
            # Case 4: Arithmetic sequence
            is_valid, new_idx = arithmetic.arithmetic_expression(tokens, start_idx)
            if is_valid:
                print(f"Found valid arithmetic expression at index {start_idx}")
                return True, new_idx
            
            output_text.insert(tk.END, f"Syntax Error: Expected condition value at line {get_line_number(tokens, start_idx)}\n")
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
            
            # If no logical operator is found, this is the empty (λ) case
            if start_idx >= len(tokens) or not any(tokens[start_idx][0] == op for op in logical_operators):
                print(f"No logical operator found at index {start_idx}, returning λ")
                
                # Check for semicolon if we're at the end of a statement
                if start_idx < len(tokens) and is_token(tokens, start_idx, ';'):
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
        def if_statement(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, '('):
                print(f"Error: Expected '(' after 'if' at index {start_idx}")
                return False, None
            start_idx += 1  # Move past '('
            
            # Parse the condition using conditional_block
            is_valid, new_idx = conditional.conditional_block(tokens, start_idx)
            if not is_valid:
                print(f"Error: Invalid condition in if statement at index {start_idx}")
                return False, None

            start_idx = new_idx  # Move to next token
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, ')'):
                print(f"Error: Expected ')' at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None

            start_idx += 1  # Move past ')'
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, '{'):
                print(f"Error: Expected '{{' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None

            start_idx += 1  # Move past '{'
            start_idx = skip_spaces(tokens, start_idx)

            # Parse if body statements
            statements_found, new_idx = program.body_statements(tokens, start_idx)
            if new_idx is None:
                print("Error parsing if body statements")
                return False, None

            start_idx = new_idx
            
            # Ensure closing brace
            if not is_token(tokens, start_idx, '}'):
                print(f"Error: Expected '}}' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            
            start_idx += 1  # Move past '}'
            start_idx = skip_spaces(tokens, start_idx)

            # Process optional elif/else statements
            while start_idx < len(tokens):
                if is_token(tokens, start_idx, 'elif'):
                    start_idx += 1  # Move past 'elif'
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    if not is_token(tokens, start_idx, '('):
                        print(f"Error: Expected '(' after 'elif' at index {start_idx}")
                        return False, None
                    
                    start_idx += 1  # Move past '('
                    start_idx = skip_spaces(tokens, start_idx)

                    is_valid, new_idx = conditional.condition_value_tail(tokens, start_idx)
                    if not is_valid:
                        print(f"Error: Invalid condition in elif statement at index {start_idx}")
                        return False, None
                    
                    start_idx = new_idx
                    start_idx = skip_spaces(tokens, start_idx)

                    if not is_token(tokens, start_idx, ')'):
                        print(f"Error: Expected ')' at index {start_idx}")
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

                    if not is_token(tokens, start_idx, '}'):
                        print(f"Error: Expected '}}' at index {start_idx}")
                        return False, None
                    
                    start_idx += 1  # Move past '}'
                    start_idx = skip_spaces(tokens, start_idx)

                elif is_token(tokens, start_idx, 'else'):
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
                    break  # No more elif/else allowed after else

                else:
                    break  # No more elif or else, exit loop
            
            return True, start_idx  # Return success if it ends with '}'
   
        @staticmethod
        def if_tail(tokens, start_idx):
            print('inside tail')
            if is_token(tokens, start_idx, 'elif'):
                print("tail elif")
                # return parse_elif_clause(tokens, start_idx)
            elif is_token(tokens, start_idx, 'else'):
                print("tail else")

                # return parse_else_clause(tokens, start_idx)
            
            # If there's nothing, it's the empty (lambda) case, so return success
            return True, start_idx
                
        @staticmethod
        def express_statement(tokens, start_idx):
            print("inside express")
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, '('):
                print(f"Error: Expected '(' at index {start_idx}")
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
                print(f"Error: Expected ')' at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
                
            start_idx += 1 
            start_idx = skip_spaces(tokens, start_idx)   

            print("abot dulo ng express")
            if is_token(tokens, start_idx, ';'):
                return True, start_idx + 1

        @staticmethod
        def stimuli_statement(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)
            if is_token(tokens, start_idx, '='):
                print("Detected stimuli statement")
                start_idx += 1  # Move past '='
                start_idx = skip_spaces(tokens, start_idx)

                # Rest of stimuli statement parsing
                if not is_token(tokens, start_idx, 'stimuli'):
                    print(f"Error: Expected 'stimuli' at index {start_idx}")
                    return False, None
                start_idx += 1  # Move past 'stimuli'
                start_idx = skip_spaces(tokens, start_idx)

                # Check for opening parenthesis
                if not is_token(tokens, start_idx, '('):
                    print(f"Error: Expected '(' at index {start_idx}")
                    return False, None
                start_idx += 1  # Move past '('
                start_idx = skip_spaces(tokens, start_idx)

                # Check for string literal
                if not is_token(tokens, start_idx, 'string literal'):
                    print(f"Error: Expected string literal at index {start_idx}")
                    return False, None
                start_idx += 1  # Move past string literal
                start_idx = skip_spaces(tokens, start_idx)

                # Check for closing parenthesis
                if not is_token(tokens, start_idx, ')'):
                    print(f"Error: Expected ')' at index {start_idx}")
                    return False, None
                start_idx += 1  # Move past ')'
                start_idx = skip_spaces(tokens, start_idx)

                # Check for semicolon
                if is_token(tokens, start_idx, ';'):
                    return True, start_idx + 1
                else:
                    print(f"Error: Expected ';' at index {start_idx}")
                    return False, None

            else:
                start_idx = skip_spaces(tokens, start_idx)

                is_valid, new_idx = statements.assignment_statement(tokens, start_idx)
                if not is_valid:
                    print(f"Error: Invalid condition in if statement at index {start_idx}")
                    return False, None  

                return True, new_idx + 1 

        @staticmethod
        def assignment_statement(tokens, start_idx):
            print(f"DEBUG: Starting assignment_statement at index {start_idx}")
            print(f"DEBUG: Current tokens: {tokens[start_idx:start_idx+5] if start_idx < len(tokens) else 'end of tokens'}")
            
            # Skip leading whitespace
            start_idx = skip_spaces(tokens, start_idx)
            
            # Check for += operator
            if any(is_token(tokens, idx, op) for op in assignment_op ):  # Works if they are sets
                token_at_idx = tokens[start_idx] if start_idx < len(tokens) else "end of tokens"
                print(f"ERROR: Expected '+=' at index {start_idx}, found '{token_at_idx}'")
                return False, start_idx
            else:
                print(f"DEBUG: Found '+=' at index {start_idx}")

            # Move past closing brace
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After closing brace, start_idx={start_idx}, token={tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            
            # Use arithmetic_expression directly to handle the entire expression including parentheses
            is_valid, new_idx = arithmetic.arithmetic_expression(tokens, start_idx)
            if not is_valid:
                print(f"Error: Invalid arithmetic expression at index {start_idx}")
                return False, None

            # Use the returned new_idx to avoid skipping tokens
            start_idx = new_idx
            start_idx = skip_spaces(tokens, start_idx)

            # Now, check if the statement properly ends with ';'
            if is_token(tokens, start_idx, ';'):
                print("Valid prod statement (ends with ';')")
                return True, start_idx + 1  # End of statement

            print(f"Error: Invalid token after arithmetic expression {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            return False, None     

        @staticmethod
        def for_loop_statement(tokens, start_idx):
            print(f"DEBUG: Starting for_loop_statement at index {start_idx}")
            print(f"DEBUG: Current tokens: {tokens[start_idx:start_idx+5] if start_idx < len(tokens) else 'end of tokens'}")

            # Skip leading whitespace
            start_idx = skip_spaces(tokens, start_idx)

            # Check for opening parenthesis '('
            if not (start_idx < len(tokens) and tokens[start_idx][0] == '('):
                print(f"ERROR: Expected '(' at index {start_idx}")
                return False, start_idx
            print(f"DEBUG: Found '(' at index {start_idx}")
            start_idx += 1  # Move past '('

            start_idx = skip_spaces(tokens, start_idx)

            # **Initialization Parsing**
            if not (start_idx < len(tokens) and tokens[start_idx][0] == 'dose'):
                print(f"ERROR: Expected 'dose' for initialization at index {start_idx}")
                return False, start_idx
            print(f"DEBUG: Found 'dose' keyword for initialization at index {start_idx}")
            start_idx += 1  # Move past 'dose'

            start_idx = skip_spaces(tokens, start_idx)

            # Identifier after 'dose'
            if not (start_idx < len(tokens) and tokens[start_idx][1] == "Identifier"):
                print(f"ERROR: Expected Identifier after 'dose' at index {start_idx}")
                return False, start_idx
            print(f"DEBUG: Found Identifier '{tokens[start_idx][0]}' for initialization at index {start_idx}")
            start_idx += 1  # Move past Identifier

            start_idx = skip_spaces(tokens, start_idx)

            # Expect '=' after Identifier
            if not (start_idx < len(tokens) and tokens[start_idx][0] == '='):
                print(f"ERROR: Expected '=' at index {start_idx}")
                return False, start_idx
            print(f"DEBUG: Found '=' at index {start_idx}")
            start_idx += 1  # Move past '='

            start_idx = skip_spaces(tokens, start_idx)

            # Initialization value (must be dose literal or Identifier)
            if start_idx < len(tokens) and tokens[start_idx][1] in ["Number", "Identifier", "numlit"]:
                print(f"DEBUG: Found initialization value '{tokens[start_idx][0]}' at index {start_idx}")
                start_idx += 1  # Move past init_value
            else:
                print(f"ERROR: Expected a valid initialization value at index {start_idx}")
                return False, start_idx

            start_idx = skip_spaces(tokens, start_idx)

            # **Check for semicolon (end of initialization)**
            if not (start_idx < len(tokens) and tokens[start_idx][0] == ";"):
                print(f"ERROR: Expected ';' after initialization at index {start_idx}")
                return False, start_idx
            print(f"DEBUG: Found ';' after initialization at index {start_idx}")
            start_idx += 1  # Move past ';'

            start_idx = skip_spaces(tokens, start_idx)

            # **Condition Parsing**
            if not (start_idx < len(tokens) and tokens[start_idx][1] == "Identifier"):
                print(f"ERROR: Expected Identifier in condition at index {start_idx}")
                return False, start_idx
            print(f"DEBUG: Found Identifier '{tokens[start_idx][0]}' for condition at index {start_idx}")
            start_idx += 1  # Move past Identifier

            start_idx = skip_spaces(tokens, start_idx)

            # Expect conditional operator (e.g., <, >, ==, etc.)
            # Fix the conditional operator check
            if start_idx >= len(tokens) or tokens[start_idx][0] not in conditional_op:
                print(f"ERROR: Expected conditional operator at index {start_idx}")
                return False, start_idx
            print(f"DEBUG: Found conditional operator '{tokens[start_idx][0]}' at index {start_idx}")
            start_idx += 1  # Move past conditional operator

            start_idx = skip_spaces(tokens, start_idx)

            # Condition value (dose literal or Identifier)
            if start_idx < len(tokens) and tokens[start_idx][1] in ["numlit", "Identifier"]:
                print(f"DEBUG: Found condition value '{tokens[start_idx][0]}' at index {start_idx}")
                start_idx += 1  # Move past condition_value
            else:
                print(f"ERROR: Expected a valid condition value at index {start_idx}")
                return False, start_idx

            start_idx = skip_spaces(tokens, start_idx)

            # **Check for semicolon (end of condition)**
            if not (start_idx < len(tokens) and tokens[start_idx][0] == ";"):
                print(f"ERROR: Expected ';' after condition at index {start_idx}")
                return False, start_idx
            print(f"DEBUG: Found ';' after condition at index {start_idx}")
            start_idx += 1  # Move past ';'

            start_idx = skip_spaces(tokens, start_idx)

            # **Update Parsing** - Fixed to properly handle both pre and post increment/decrement
            # Case 1: Pre-increment/decrement (++Id or --Id)
            if start_idx < len(tokens) and tokens[start_idx][0] in unary_op:
                print(f"DEBUG: Found pre-unary operator '{tokens[start_idx][0]}' at index {start_idx}")
                start_idx += 1  # Move past unary operator
                
                start_idx = skip_spaces(tokens, start_idx)
                
                if not (start_idx < len(tokens) and tokens[start_idx][1] == "Identifier"):
                    print(f"ERROR: Expected Identifier after unary operator at index {start_idx}")
                    return False, start_idx
                print(f"DEBUG: Found Identifier '{tokens[start_idx][0]}' after pre-unary operator at index {start_idx}")
                start_idx += 1  # Move past Identifier
            
            # Case 2: Post-increment/decrement (Id++ or Id--)
            elif start_idx < len(tokens) and tokens[start_idx][1] == "Identifier":
                print(f"DEBUG: Found Identifier '{tokens[start_idx][0]}' in update at index {start_idx}")
                start_idx += 1  # Move past Identifier
                
                start_idx = skip_spaces(tokens, start_idx)
                
                if start_idx >= len(tokens) or tokens[start_idx][0] not in unary_op:
                    print(f"ERROR: Expected unary operator after Identifier at index {start_idx}")
                    return False, start_idx
                print(f"DEBUG: Found post-unary operator '{tokens[start_idx][0]}' at index {start_idx}")
                start_idx += 1  # Move past unary operator

                start_idx = skip_spaces(tokens, start_idx)

            
            # Neither pre nor post increment/decrement found
            else:
                print(f"ERROR: Expected Identifier or unary operator for update at index {start_idx}")
                return False, start_idx

            start_idx = skip_spaces(tokens, start_idx)
            start_idx += 1  # Move past unary operator

            # Check for closing parenthesis
            if not (start_idx < len(tokens) and tokens[start_idx][0] == ')'):
                print(f"Error: Expected ')' at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None

            start_idx += 1  # Move past ')'
            start_idx = skip_spaces(tokens, start_idx)

            # Check for opening brace
            if not (start_idx < len(tokens) and tokens[start_idx][0] == '{'):
                print(f"Error: Expected '{{' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None

            start_idx += 1  # Move past '{'
            start_idx = skip_spaces(tokens, start_idx)

            # Parse if body statements
            statements_found, new_idx = program.body_statements(tokens, start_idx)
            if new_idx is None:
                print("Error parsing for loop body statements")
                return False, None

            start_idx = new_idx
            
            # Ensure closing brace
            if not (start_idx < len(tokens) and tokens[start_idx][0] == '}'):
                print(f"Error: Expected '}}' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            
            start_idx += 1  # Move past '}'
            return True, start_idx

        @staticmethod
        def prod_statement(tokens, start_idx):
            print("inside prod_statement")

            # Use arithmetic_expression directly to handle the entire expression including parentheses
            is_valid, new_idx = arithmetic.arithmetic_expression(tokens, start_idx)
            if not is_valid:
                print(f"Error: Invalid arithmetic expression at index {start_idx}")
                return False, None

            # Use the returned new_idx to avoid skipping tokens
            start_idx = new_idx
            start_idx = skip_spaces(tokens, start_idx)

            # Now, check if the statement properly ends with ';'
            if is_token(tokens, start_idx, ';'):
                print("Valid prod statement (ends with ';')")
                return True, start_idx + 1  # End of statement

            print(f"Error: Invalid token after arithmetic expression {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            return False, None


        @staticmethod
        def do_while_statement(tokens, start_idx):
            print("<do_while_statement>")
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After initial skip_spaces, start_idx={start_idx}, token={tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            
            
            # Check for opening brace
            if not is_token(tokens, start_idx, '{'):
                print(f"DEBUG: Expected '{{' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            
            # Move past opening brace
            start_idx += 1
            print(f"DEBUG: After opening brace, start_idx={start_idx}")
            
            # Parse the body statements
            statements_found, new_idx = program.body_statements(tokens, start_idx)
            if new_idx is None:
                print("DEBUG: Error parsing do-while body statements")
                return False, None
            
            start_idx = new_idx
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After body statements, start_idx={start_idx}, token={tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            
            # Check for closing brace
            if not is_token(tokens, start_idx, '}'):
                print(f"DEBUG: Expected '}}' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            
            # Move past closing brace
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After closing brace, start_idx={start_idx}, token={tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            
            # Check for 'while' keyword
            if not is_token(tokens, start_idx, 'while'):
                print(f"DEBUG: Expected 'while' keyword but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            
            # Move past 'while' keyword
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After 'while' keyword, start_idx={start_idx}, token={tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            
            # Check for opening parenthesis
            if not is_token(tokens, start_idx, '('):
                print(f"DEBUG: Expected '(' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            
            # Move past opening parenthesis
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After opening parenthesis, start_idx={start_idx}, token={tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            
            # Parse condition
            is_valid, new_idx = conditional.condition_value_tail(tokens, start_idx)
            if not is_valid or new_idx is None:
                print(f"DEBUG: Invalid condition at index {start_idx}")
                return False, None
            
            start_idx = new_idx
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After condition, start_idx={start_idx}, token={tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            
            # Check for closing parenthesis
            if not is_token(tokens, start_idx, ')'):
                print(f"DEBUG: Expected ')' but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            
            # Move past closing parenthesis
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After closing parenthesis, start_idx={start_idx}, token={tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
            
            # Check for semicolon
            if is_token(tokens, start_idx, ';'):
                start_idx += 1  # Move past semicolon
                print(f"DEBUG: After semicolon, start_idx={start_idx}")
            
            print(f"DEBUG: Successfully parsed do-while statement, returning True, {start_idx}")
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
                print(f"Error: Expected ')' at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None

            start_idx += 1  # Move past ')'
            start_idx = skip_spaces(tokens, start_idx)

            if not is_token(tokens, start_idx, '{'):
                print(f"Error: Expected '{{' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None

            start_idx += 1  # Move past '{'
            start_idx = skip_spaces(tokens, start_idx)

            # Parse if body statements
            statements_found, new_idx = program.body_statements(tokens, start_idx)
            if new_idx is None:
                print("Error parsing if body statements")
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
            start_idx = skip_spaces(tokens, start_idx)
            
            # First identifier check
            if not is_token(tokens, start_idx, 'Identifier'):
                output_text.insert(tk.END, f"Syntax Error: Expected an identifier at line {get_line_number(tokens, start_idx)}\n")
                return False, None
            start_idx += 1
            
            start_idx = skip_spaces(tokens, start_idx)
            
            while True:
                # Check if it's an assignment
                if is_token(tokens, start_idx, '='):
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    # Expect a number literal after '='
                    if not is_token(tokens, start_idx, 'numlit'):
                        return False, None
                    
                    # Validate the number format
                    number_sign = check_number_sign(tokens[start_idx])
                    if number_sign in {"quantval", "nequantliteral"}:
                        return False, None
                    start_idx += 1
                
                start_idx = skip_spaces(tokens, start_idx)
                
                # Now check for either a semicolon (end of statement) or comma (more assignments)
                if is_token(tokens, start_idx, ';'):
                    return True, start_idx + 1
                
                if not is_token(tokens, start_idx, ','):
                    return False, None
                
                # Move past comma
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                
                # Next identifier
                if not is_token(tokens, start_idx, 'Identifier'):
                    return False, None
                start_idx += 1
                
                start_idx = skip_spaces(tokens, start_idx)


        @staticmethod
        def validate_seqval(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)
            
            # First identifier check
            if not is_token(tokens, start_idx, 'Identifier'):
                output_text.insert(tk.END, f"Syntax Error: Expected an identifier at line {get_line_number(tokens, start_idx)}\n")
                return False, None
            start_idx += 1
            
            start_idx = skip_spaces(tokens, start_idx)
            
            while True:
                # Check if it's an assignment
                if is_token(tokens, start_idx, '='):
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    # Expect only a string literal after '='
                    if not is_token(tokens, start_idx, 'string literal'):
                        output_text.insert(tk.END, f"Syntax Error: Expected a string literal at line {get_line_number(tokens, start_idx)} but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                        return False, None
                    start_idx += 1
                
                start_idx = skip_spaces(tokens, start_idx)
                
                # Now check for either a semicolon (end of statement) or comma (more assignments)
                if is_token(tokens, start_idx, ';'):
                    return True, start_idx + 1
                
                if not is_token(tokens, start_idx, ','):
                    output_text.insert(tk.END, f"Syntax Error: Expected ',' at line {get_line_number(tokens, start_idx)} but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                    return False, None
                
                # Move past comma
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                
                # Next identifier
                if not is_token(tokens, start_idx, 'Identifier'):
                    output_text.insert(tk.END, f"Syntax Error: Expected Identifier at line {get_line_number(tokens, start_idx)} but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                    return False, None
                start_idx += 1
                
                start_idx = skip_spaces(tokens, start_idx)
                
                # Next equals sign
                if not is_token(tokens, start_idx, '='):
                    output_text.insert(tk.END, f"Syntax Error: Expected '=' at line {get_line_number(tokens, start_idx)} but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                    return False, None
                start_idx += 1
                
                start_idx = skip_spaces(tokens, start_idx)
                
                # Next string literal (no numbers allowed)
                if not is_token(tokens, start_idx, 'string literal'):
                    output_text.insert(tk.END, f"Syntax Error: Expected string literal at line {get_line_number(tokens, start_idx)} but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                    return False, None
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                        
        @staticmethod
        def validate_alleleval(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)
            
            # First identifier check
            if not is_token(tokens, start_idx, 'Identifier'):
                output_text.insert(tk.END, f"Syntax Error: Expected an identifier at line {get_line_number(tokens, start_idx)}\n")
                return False, None
            start_idx += 1
            
            start_idx = skip_spaces(tokens, start_idx)
            
            while True:
                # Check if it's an assignment
                if is_token(tokens, start_idx, '='):
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    # Expect only a string literal after '='
                    if not is_token(tokens, start_idx, {'dom', 'rec'}):
                        output_text.insert(tk.END, f"Syntax Error: Expected allele literal at line {get_line_number(tokens, start_idx)} but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                        return False, None
                    start_idx += 1
                
                start_idx = skip_spaces(tokens, start_idx)
                
                # Now check for either a semicolon (end of statement) or comma (more assignments)
                if is_token(tokens, start_idx, ';'):
                    return True, start_idx + 1
                
                if not is_token(tokens, start_idx, ','):
                    output_text.insert(tk.END, f"Syntax Error: Expected ',' at line {get_line_number(tokens, start_idx)} but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                    return False, None
                
                # Move past comma
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                
                # Next identifier
                if not is_token(tokens, start_idx, 'Identifier'):
                    output_text.insert(tk.END, f"Syntax Error: Expected Identifier at line {get_line_number(tokens, start_idx)} but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                    return False, None
                start_idx += 1
                
                start_idx = skip_spaces(tokens, start_idx)
                
                # Next equals sign
                if not is_token(tokens, start_idx, '='):
                    output_text.insert(tk.END, f"Syntax Error: Expected '=' at line {get_line_number(tokens, start_idx)} but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                    return False, None
                start_idx += 1
                
                start_idx = skip_spaces(tokens, start_idx)
                
                # Next string literal (no numbers allowed)
                if not is_token(tokens, start_idx, {'dom', 'rec'}):
                    output_text.insert(tk.END, f"Syntax Error: Expected allele literal at line {get_line_number(tokens, start_idx)} but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                    return False, None
                start_idx += 1
                
                start_idx = skip_spaces(tokens, start_idx)

        @staticmethod
        def validate_quantval(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)

            # First identifier check
            if not is_token(tokens, start_idx, 'Identifier'):
                output_text.insert(tk.END, f"Syntax Error: Expected an identifier at line {get_line_number(tokens, start_idx)}\n")
                return False, None
            start_idx += 1
            
            start_idx = skip_spaces(tokens, start_idx)
            
            while True:
                # Check if it's an assignment
                if is_token(tokens, start_idx, '='):
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    # Expect a number literal after '='
                    if not is_token(tokens, start_idx, 'numlit'):
                        return False, None
                    
                    # Validate the number format
                    number_sign = check_number_sign(tokens[start_idx])
                    if number_sign in {"neliteral", "doseliteral"}:
                        return False, None
                    start_idx += 1
                
                start_idx = skip_spaces(tokens, start_idx)
                
                # Now check for either a semicolon (end of statement) or comma (more assignments)
                if is_token(tokens, start_idx, ';'):
                    return True, start_idx + 1
                
                if not is_token(tokens, start_idx, ','):
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
            print('<clust_dose>')
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After initial skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check for identifier
            if not is_token(tokens, start_idx, 'Identifier'):
                print(f"DEBUG: Expected Identifier at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            print(f"DEBUG: Found Identifier: {tokens[start_idx]}")
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check for opening bracket
            if not is_token(tokens, start_idx, '['):
                print(f"DEBUG: Expected '[' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            print(f"DEBUG: Found opening bracket")
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check for dimension size
            if not is_token(tokens, start_idx, 'numlit'):
                print(f"DEBUG: Expected numlit at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None

            literal = tokens[start_idx]
            number_sign = check_number_sign(literal)
            print(f"DEBUG: Found numlit: {literal}, number_sign: {number_sign}")
            
            if number_sign not in {'doseliteral'}:
                print(f"DEBUG: Invalid number sign: {number_sign}, expected 'doseliteral'")
                return False, None
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check for closing bracket
            if not is_token(tokens, start_idx, ']'):
                print(f"DEBUG: Expected ']' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            print(f"DEBUG: Found closing bracket")
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check for second dimension (optional)
            if is_token(tokens, start_idx, '['):
                print(f"DEBUG: Found second dimension opening bracket")
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

                if not is_token(tokens, start_idx, 'numlit') or check_number_sign(tokens[start_idx]) != "doseliteral":
                    print(f"DEBUG: Expected numlit with doseliteral at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                    return False, None
                print(f"DEBUG: Found second dimension size: {tokens[start_idx]}")
                start_idx += 1

                start_idx = skip_spaces(tokens, start_idx)
                print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                
                if not is_token(tokens, start_idx, ']'):
                    print(f"DEBUG: Expected ']' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                    return False, None
                print(f"DEBUG: Found second dimension closing bracket")
                start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check for equals sign
            if not is_token(tokens, start_idx, '='):
                print(f"DEBUG: Expected '=' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            print(f"DEBUG: Found equals sign")
            
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check for opening brace
            if not is_token(tokens, start_idx, '{'):
                print(f"DEBUG: Expected '{{' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            print(f"DEBUG: Found opening brace")
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check what type of array we're dealing with
            if is_token(tokens, start_idx, '{'):
                print(f"DEBUG: Detected 2D array (nested braces)")
                # Handle 2D array case (nested braces)
                while True:
                    if is_token(tokens, start_idx, '{'):
                        print(f"DEBUG: Found inner opening brace")
                        start_idx += 1
                        start_idx = skip_spaces(tokens, start_idx)
                        print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

                        while True:
                            if not is_token(tokens, start_idx, 'numlit'):
                                print(f"DEBUG: Expected numlit at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                                return False, None

                            literal = tokens[start_idx]
                            number_sign = check_number_sign(literal)
                            print(f"DEBUG: Found inner array value: {literal}, number_sign: {number_sign}")

                            if number_sign not in {'quantval', 'nequantliteral'}:
                                print(f"DEBUG: Invalid number sign: {number_sign}, expected 'doseliteral' or 'neliteral'")
                                return False, None
                            start_idx += 1

                            start_idx = skip_spaces(tokens, start_idx)
                            print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

                            if is_token(tokens, start_idx, ','):
                                print(f"DEBUG: Found comma in inner array")
                                start_idx += 1
                                start_idx = skip_spaces(tokens, start_idx)
                                print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                            elif is_token(tokens, start_idx, '}'):
                                print(f"DEBUG: Found inner closing brace")
                                start_idx += 1
                                break
                            else:
                                print(f"DEBUG: Expected ',' or '}}' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                                return False, None

                        start_idx = skip_spaces(tokens, start_idx)
                        print(f"DEBUG: After inner array, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

                        if is_token(tokens, start_idx, ','):
                            print(f"DEBUG: Found comma after inner array")
                            start_idx += 1
                            start_idx = skip_spaces(tokens, start_idx)
                            print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                        elif is_token(tokens, start_idx, '}'):
                            print(f"DEBUG: Found outer closing brace")
                            start_idx += 1
                            break
                        else:
                            print(f"DEBUG: Expected ',' or '}}' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                            return False, None
                    else:
                        print(f"DEBUG: Expected '{{' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                        return False, None
            else:
                print(f"DEBUG: Detected 1D array (direct values)")
                # Handle 1D array case (direct values)
                while True:
                    if not is_token(tokens, start_idx, 'numlit'):
                        print(f"DEBUG: Expected numlit at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                        return False, None

                    literal = tokens[start_idx]
                    number_sign = check_number_sign(literal)
                    print(f"DEBUG: Found array value: {literal}, number_sign: {number_sign}")

                    if number_sign not in {'quantval', 'nequantliteral'}:
                        print(f"DEBUG: Invalid number sign: {number_sign}, expected 'doseliteral' or 'neliteral'")
                        return False, None
                    start_idx += 1

                    start_idx = skip_spaces(tokens, start_idx)
                    print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

                    if is_token(tokens, start_idx, ','):
                        print(f"DEBUG: Found comma in array")
                        start_idx += 1
                        start_idx = skip_spaces(tokens, start_idx)
                        print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                    elif is_token(tokens, start_idx, '}'):
                        print(f"DEBUG: Found closing brace")
                        start_idx += 1
                        break
                    else:
                        print(f"DEBUG: Expected ',' or '}}' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                        return False, None

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After array parsing, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check for semicolon
            if not is_token(tokens, start_idx, ';'):
                print(f"DEBUG: Expected ';' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            print(f"DEBUG: Found semicolon, array declaration complete")

            return True, start_idx + 1

        @staticmethod
        def validate_clust_doseval(tokens, start_idx):
            print('<clust_dose>')
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After initial skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check for identifier
            if not is_token(tokens, start_idx, 'Identifier'):
                print(f"DEBUG: Expected Identifier at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            print(f"DEBUG: Found Identifier: {tokens[start_idx]}")
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check for opening bracket
            if not is_token(tokens, start_idx, '['):
                print(f"DEBUG: Expected '[' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            print(f"DEBUG: Found opening bracket")
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check for dimension size
            if not is_token(tokens, start_idx, 'numlit'):
                print(f"DEBUG: Expected numlit at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None

            literal = tokens[start_idx]
            number_sign = check_number_sign(literal)
            print(f"DEBUG: Found numlit: {literal}, number_sign: {number_sign}")
            
            if number_sign not in {'doseliteral'}:
                print(f"DEBUG: Invalid number sign: {number_sign}, expected 'doseliteral'")
                return False, None
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check for closing bracket
            if not is_token(tokens, start_idx, ']'):
                print(f"DEBUG: Expected ']' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            print(f"DEBUG: Found closing bracket")
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check for second dimension (optional)
            if is_token(tokens, start_idx, '['):
                print(f"DEBUG: Found second dimension opening bracket")
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

                if not is_token(tokens, start_idx, 'numlit') or check_number_sign(tokens[start_idx]) != "doseliteral":
                    print(f"DEBUG: Expected numlit with doseliteral at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                    return False, None
                print(f"DEBUG: Found second dimension size: {tokens[start_idx]}")
                start_idx += 1

                start_idx = skip_spaces(tokens, start_idx)
                print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                
                if not is_token(tokens, start_idx, ']'):
                    print(f"DEBUG: Expected ']' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                    return False, None
                print(f"DEBUG: Found second dimension closing bracket")
                start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check for equals sign
            if not is_token(tokens, start_idx, '='):
                print(f"DEBUG: Expected '=' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            print(f"DEBUG: Found equals sign")
            
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check for opening brace
            if not is_token(tokens, start_idx, '{'):
                print(f"DEBUG: Expected '{{' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            print(f"DEBUG: Found opening brace")
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check what type of array we're dealing with
            if is_token(tokens, start_idx, '{'):
                print(f"DEBUG: Detected 2D array (nested braces)")
                # Handle 2D array case (nested braces)
                while True:
                    if is_token(tokens, start_idx, '{'):
                        print(f"DEBUG: Found inner opening brace")
                        start_idx += 1
                        start_idx = skip_spaces(tokens, start_idx)
                        print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

                        while True:
                            if not is_token(tokens, start_idx, 'numlit'):
                                print(f"DEBUG: Expected numlit at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                                return False, None

                            literal = tokens[start_idx]
                            number_sign = check_number_sign(literal)
                            print(f"DEBUG: Found inner array value: {literal}, number_sign: {number_sign}")

                            if number_sign not in {'doseliteral', 'neliteral'}:
                                print(f"DEBUG: Invalid number sign: {number_sign}, expected 'doseliteral' or 'neliteral'")
                                return False, None
                            start_idx += 1

                            start_idx = skip_spaces(tokens, start_idx)
                            print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

                            if is_token(tokens, start_idx, ','):
                                print(f"DEBUG: Found comma in inner array")
                                start_idx += 1
                                start_idx = skip_spaces(tokens, start_idx)
                                print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                            elif is_token(tokens, start_idx, '}'):
                                print(f"DEBUG: Found inner closing brace")
                                start_idx += 1
                                break
                            else:
                                print(f"DEBUG: Expected ',' or '}}' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                                return False, None

                        start_idx = skip_spaces(tokens, start_idx)
                        print(f"DEBUG: After inner array, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

                        if is_token(tokens, start_idx, ','):
                            print(f"DEBUG: Found comma after inner array")
                            start_idx += 1
                            start_idx = skip_spaces(tokens, start_idx)
                            print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                        elif is_token(tokens, start_idx, '}'):
                            print(f"DEBUG: Found outer closing brace")
                            start_idx += 1
                            break
                        else:
                            print(f"DEBUG: Expected ',' or '}}' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                            return False, None
                    else:
                        print(f"DEBUG: Expected '{{' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                        return False, None
            else:
                print(f"DEBUG: Detected 1D array (direct values)")
                # Handle 1D array case (direct values)
                while True:
                    if not is_token(tokens, start_idx, 'numlit'):
                        print(f"DEBUG: Expected numlit at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                        return False, None

                    literal = tokens[start_idx]
                    number_sign = check_number_sign(literal)
                    print(f"DEBUG: Found array value: {literal}, number_sign: {number_sign}")

                    if number_sign not in {'doseliteral', 'neliteral'}:
                        print(f"DEBUG: Invalid number sign: {number_sign}, expected 'doseliteral' or 'neliteral'")
                        return False, None
                    start_idx += 1

                    start_idx = skip_spaces(tokens, start_idx)
                    print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

                    if is_token(tokens, start_idx, ','):
                        print(f"DEBUG: Found comma in array")
                        start_idx += 1
                        start_idx = skip_spaces(tokens, start_idx)
                        print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                    elif is_token(tokens, start_idx, '}'):
                        print(f"DEBUG: Found closing brace")
                        start_idx += 1
                        break
                    else:
                        print(f"DEBUG: Expected ',' or '}}' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                        return False, None

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After array parsing, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check for semicolon
            if not is_token(tokens, start_idx, ';'):
                print(f"DEBUG: Expected ';' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            print(f"DEBUG: Found semicolon, array declaration complete")

            return True, start_idx + 1

        @staticmethod
        def validate_clust_seqval(tokens, start_idx):
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After initial skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check for identifier
            if not is_token(tokens, start_idx, 'Identifier'):
                print(f"DEBUG: Expected Identifier at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            print(f"DEBUG: Found Identifier: {tokens[start_idx]}")
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check for opening bracket
            if not is_token(tokens, start_idx, '['):
                print(f"DEBUG: Expected '[' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            print(f"DEBUG: Found opening bracket")
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check for dimension size
            if not is_token(tokens, start_idx, 'numlit'):
                print(f"DEBUG: Expected numlit at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None

            literal = tokens[start_idx]
            number_sign = check_number_sign(literal)
            print(f"DEBUG: Found numlit: {literal}, number_sign: {number_sign}")
            
            if number_sign not in {'doseliteral'}:
                print(f"DEBUG: Invalid number sign: {number_sign}, expected 'doseliteral'")
                return False, None
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check for closing bracket
            if not is_token(tokens, start_idx, ']'):
                print(f"DEBUG: Expected ']' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            print(f"DEBUG: Found closing bracket")
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check for second dimension (optional)
            if is_token(tokens, start_idx, '['):
                print(f"DEBUG: Found second dimension opening bracket")
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)
                print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

                if not is_token(tokens, start_idx, 'numlit') or check_number_sign(tokens[start_idx]) != "doseliteral":
                    print(f"DEBUG: Expected numlit with doseliteral at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                    return False, None
                print(f"DEBUG: Found second dimension size: {tokens[start_idx]}")
                start_idx += 1

                start_idx = skip_spaces(tokens, start_idx)
                print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                
                if not is_token(tokens, start_idx, ']'):
                    print(f"DEBUG: Expected ']' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                    return False, None
                print(f"DEBUG: Found second dimension closing bracket")
                start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check for equals sign
            if not is_token(tokens, start_idx, '='):
                print(f"DEBUG: Expected '=' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            print(f"DEBUG: Found equals sign")
            
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check for opening brace
            if not is_token(tokens, start_idx, '{'):
                print(f"DEBUG: Expected '{{' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            print(f"DEBUG: Found opening brace")
            start_idx += 1

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check what type of array we're dealing with
            if is_token(tokens, start_idx, '{'):
                print(f"DEBUG: Detected 2D array (nested braces)")
                # Handle 2D array case (nested braces)
                while True:
                    if is_token(tokens, start_idx, '{'):
                        print(f"DEBUG: Found inner opening brace")
                        start_idx += 1
                        start_idx = skip_spaces(tokens, start_idx)
                        print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

                        while True:
                            if not is_token(tokens, start_idx, 'string literal'):
                                print(f"DEBUG: Expected numlit at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                                return False, None

                            start_idx += 1

                            start_idx = skip_spaces(tokens, start_idx)
                            print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

                            if is_token(tokens, start_idx, ','):
                                print(f"DEBUG: Found comma in inner array")
                                start_idx += 1
                                start_idx = skip_spaces(tokens, start_idx)
                                print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                            elif is_token(tokens, start_idx, '}'):
                                print(f"DEBUG: Found inner closing brace")
                                start_idx += 1
                                break
                            else:
                                print(f"DEBUG: Expected ',' or '}}' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                                return False, None

                        start_idx = skip_spaces(tokens, start_idx)
                        print(f"DEBUG: After inner array, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

                        if is_token(tokens, start_idx, ','):
                            print(f"DEBUG: Found comma after inner array")
                            start_idx += 1
                            start_idx = skip_spaces(tokens, start_idx)
                            print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                        elif is_token(tokens, start_idx, '}'):
                            print(f"DEBUG: Found outer closing brace")
                            start_idx += 1
                            break
                        else:
                            print(f"DEBUG: Expected ',' or '}}' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                            return False, None
                    else:
                        print(f"DEBUG: Expected '{{' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                        return False, None
            else:
                print(f"DEBUG: Detected 1D array (direct values)")
                # Handle 1D array case (direct values)
                while True:
                    if not is_token(tokens, start_idx, 'string literal'):
                        print(f"DEBUG: Expected string literal at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                        return False, None

                    start_idx += 1

                    start_idx = skip_spaces(tokens, start_idx)
                    print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

                    if is_token(tokens, start_idx, ','):
                        print(f"DEBUG: Found comma in array")
                        start_idx += 1
                        start_idx = skip_spaces(tokens, start_idx)
                        print(f"DEBUG: After skip_spaces, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                    elif is_token(tokens, start_idx, '}'):
                        print(f"DEBUG: Found closing brace")
                        start_idx += 1
                        break
                    else:
                        print(f"DEBUG: Expected ',' or '}}' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                        return False, None

            start_idx = skip_spaces(tokens, start_idx)
            print(f"DEBUG: After array parsing, index: {start_idx}, token: {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")

            # Check for semicolon
            if not is_token(tokens, start_idx, ';'):
                print(f"DEBUG: Expected ';' at index {start_idx}, found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None
            print(f"DEBUG: Found semicolon, array declaration complete")

            return True, start_idx + 1

    class arithmetic:
        @staticmethod
        def arithmetic_expression(tokens, start_idx):
            print(f"[DEBUG] Entering arithmetic_expression at index {start_idx}")
            
            start_idx = skip_spaces(tokens, start_idx)

            # Handle parenthesized expressions
            if start_idx < len(tokens) and tokens[start_idx][1] == '(':
                print(f"[DEBUG] Found '(' at index {start_idx}, parsing sub-expression")
                
                start_idx += 1  # Move past '('
                start_idx = skip_spaces(tokens, start_idx)
                
                # Recursively parse the expression inside parentheses
                is_valid, new_idx = arithmetic.arithmetic_expression(tokens, start_idx)
                if not is_valid:
                    print(f"[DEBUG] Error: Invalid expression inside parentheses at index {start_idx}")
                    return False, start_idx
                
                start_idx = new_idx
                start_idx = skip_spaces(tokens, start_idx)
                
                if start_idx >= len(tokens) or tokens[start_idx][1] != ')':
                    print(f"[DEBUG] Error: Expected ')' but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'} at index {start_idx}")
                    return False, start_idx
                
                print(f"[DEBUG] Found matching ')' at index {start_idx}")
                start_idx += 1  # Move past ')'
                
                # After a parenthesized expression, check for operators
                start_idx = skip_spaces(tokens, start_idx)
                if start_idx < len(tokens) and is_token(tokens, start_idx, math_operator):
                    print(f"[DEBUG] Found operator '{tokens[start_idx][0]}' after parenthesized expression")
                    operator = tokens[start_idx][0]
                    start_idx += 1  # Move past operator
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    # Parse the right-hand side of the operator
                    is_valid, new_idx = arithmetic.arithmetic_expression(tokens, start_idx)
                    if not is_valid:
                        print(f"[DEBUG] Error: Invalid expression after operator '{operator}'")
                        return False, start_idx
                    
                    return True, new_idx
                
                return True, start_idx
            
            # Handle simple values (identifiers or literals)
            if is_token(tokens, start_idx, 'numlit') or is_token(tokens, start_idx, 'Identifier'):
                print(f"[DEBUG] Found value: {tokens[start_idx][0]}")
                start_idx += 1  # Move past the value
                start_idx = skip_spaces(tokens, start_idx)
                
                # Check for operators after the value
                if start_idx < len(tokens) and is_token(tokens, start_idx, math_operator):
                    print(f"[DEBUG] Found operator '{tokens[start_idx][0]}' after value")
                    operator = tokens[start_idx][0]
                    start_idx += 1  # Move past operator
                    start_idx = skip_spaces(tokens, start_idx)
                    
                    # Parse the right-hand side of the operator
                    is_valid, new_idx = arithmetic.arithmetic_expression(tokens, start_idx)
                    if not is_valid:
                        print(f"[DEBUG] Error: Invalid expression after operator '{operator}'")
                        return False, start_idx
                    
                    return True, new_idx
                
                return True, start_idx
            
            print(f"[DEBUG] Error: Expected value or '(' but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}")
            return False, start_idx

        @staticmethod
        def arithmetic_sequence(tokens, start_idx):
            output_text.insert(tk.END, "<arithmetic_sequence>➜")
            print("In arithmetic sequence")
            start_idx = skip_spaces(tokens, start_idx)

            is_valid, new_idx = arithmetic.arithmetic_value(tokens, start_idx)
            if not is_valid:
                output_text.insert(tk.END, f"Syntax Error: Expected arithmetic_value at line {get_line_number(tokens, start_idx)} but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                return False, None

            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            
            # Check if we have an operator
            if start_idx >= len(tokens) or not any(tokens[start_idx][1] in op for op in math_operator):
                # No operator, sequence ends here
                return True, start_idx
            
            # We have an operator
            output_text.insert(tk.END, "<math_operator>")
            start_idx += 1
            
            # Skip spaces
            start_idx = skip_spaces(tokens, start_idx)
            
            # Next value
            is_valid, new_idx = arithmetic.arithmetic_value(tokens, start_idx)
            if not is_valid:
                output_text.insert(tk.END, f"Syntax Error: Expected arithmetic_value at line {get_line_number(tokens, start_idx)} but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'}\n")
                return False, None

            start_idx += 1
            
            # Process any additional operators and operands via the tail
            return arithmetic.arithmetic_sequence_tail(tokens, start_idx)
        
        @staticmethod
        def arithmetic_sequence_tail(tokens, start_idx):
            output_text.insert(tk.END, "<arithmetic_sequence_tail>")
            
            # Skip spaces
            start_idx = skip_spaces(tokens, start_idx)
            
            # Check if we're at the end or have no more operators (empty tail)
            if start_idx >= len(tokens) or not any(tokens[start_idx][1] == op for op in math_operator):
                output_text.insert(tk.END, "➜λ\n")
                return True, start_idx
            
            # We found another operator, so this is a non-empty tail
            output_text.insert(tk.END, "➜<math_operator> ")
            operator = tokens[start_idx][0]  # Save for error messages
            start_idx += 1
            
            # Skip spaces
            start_idx = skip_spaces(tokens, start_idx)
            
            # Check if we're at the end of input
            if start_idx >= len(tokens):
                print(f"Error in tail: Unexpected end of input after operator '{operator}' in tail at index {start_idx}")
                return False, start_idx
            
            # We need to process a new arithmetic value here (not a full sequence)
            is_valid, new_idx = arithmetic.arithmetic_value(tokens, start_idx)
            if not is_valid:
                print(f"Error in tail: Invalid arithmetic sequence at index {start_idx}")
                return False, None

            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            
            
            # Recursively handle more operations by calling arithmetic_sequence_tail again
            return arithmetic.arithmetic_sequence_tail(tokens, start_idx)

        @staticmethod
        def arithmetic_value(tokens, start_idx):
            output_text.insert(tk.END, "<arithmetic_value>➜")
            start_idx = skip_spaces(tokens, start_idx)

            # Debugging the current token
            if start_idx < len(tokens):
                print(f"[DEBUG] Checking token at index {start_idx}: {tokens[start_idx]}")

            # Case 1: <math_lit> ➜ numlit or Identifier
            if is_token(tokens, start_idx, 'numlit') or is_token(tokens, start_idx, 'Identifier'):
                output_text.insert(tk.END, "<math_lit>")
                start_idx += 1  # Move past the literal or identifier
                return True, start_idx

            # Case 2: <arithmetic_value> ➜ (<arithmetic_sequence>)
            if is_token(tokens, start_idx, '('):
                print(f"[DEBUG] Found '(': Entering sub-expression at index {start_idx}")
                output_text.insert(tk.END, "(<arithmetic_sequence>)")
                start_idx += 1  # Move past '('

                # Process the arithmetic sequence inside parentheses
                is_valid, start_idx = arithmetic.arithmetic_sequence(tokens, start_idx)
                if not is_valid:
                    print(f"[DEBUG] Error in sub-expression at index {start_idx}")
                    return False, start_idx

                # Expect closing ')'
                start_idx = skip_spaces(tokens, start_idx)
                if not is_token(tokens, start_idx, ')'):
                    print(f"[DEBUG] Error: Expected ')' but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'} at index {start_idx}")
                    return False, start_idx
                print(f"[DEBUG] Found matching ')' at index {start_idx}")

                output_text.insert(tk.END, ")")
                start_idx += 1  # Move past ')'

                return True, start_idx  # **DO NOT PROCEED TO SEQUENCE TAIL HERE!**

            # If no valid arithmetic value is found
            print(f"[DEBUG] Error: Expected number, identifier, or '(' but found {tokens[start_idx][0] if start_idx < len(tokens) else 'EOF'} at index {start_idx}")
            return False, start_idx

    class parameters:
        @staticmethod
        def parse_params(tokens, start_idx):
            print("Parsing parameters...")

            param_types = {"dose", "quant", "seq", "allele"}
            params = []

            start_idx = skip_spaces(tokens, start_idx)

            # Lambda case: No parameters
            if start_idx >= len(tokens) or not is_token(tokens, start_idx, param_types):
                print(f"No parameters found at index {start_idx}.")
                return True, [], start_idx

            while start_idx < len(tokens):
                # First token must be a valid parameter type
                if not is_token(tokens, start_idx, param_types):
                    print(f"Error: Expected parameter type at index {start_idx}, found {tokens[start_idx]}")
                    return False, None, start_idx

                param_type = tokens[start_idx][0]  # Extract value
                start_idx += 1
                start_idx = skip_spaces(tokens, start_idx)

                # Next token must be an identifier (or lambda case)
                param_id = None
                if start_idx < len(tokens) and is_token(tokens, start_idx, "Identifier"):
                    param_id = tokens[start_idx][0]  # Extract identifier value
                    start_idx += 1
                    start_idx = skip_spaces(tokens, start_idx)

                params.append((param_type, param_id))
                print(f"Added parameter: ({param_type}, {param_id})")

                # Check for ',' indicating more parameters
                if start_idx < len(tokens) and is_token(tokens, start_idx, ','):
                    #<params_tail>
                    start_idx += 1  # Move past comma
                    start_idx = skip_spaces(tokens, start_idx)
                else:
                    break  # No more parameters

            print(f"Completed parsing parameters: {params}")
            return True, params, start_idx
       
    class express:
        @staticmethod
        def express_value(tokens, start_idx):
            """Parses an express_value sequence based on the given CFG.
            <express_value> → <literals> <express_value_tail>
            <express_value> → <seq_concat> <express_value_tail>
            <express_value> → <seq_type_cast> <express_value_tail>
            Modified to handle concatenation between string literals and seq function calls.
            """
            print("<express_value>")
            
            literals = {'string literal', 'numlit', 'Identifier', 'dom', 'rec'}
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
                    # Continue to other parsing options
            
            # Check if we should parse a seq_concat
            # We need to look ahead to see if there's a '+' after a literal
            elif start_idx < len(tokens) and is_token(tokens, start_idx, 'string literal'):
                lookahead_idx = skip_spaces(tokens, start_idx + 1)
                if lookahead_idx < len(tokens) and tokens[lookahead_idx][0] == "+":
                    print("Found 'string literal' followed by '+', parsing as seq_concat")
                    is_valid, concat_value, next_idx = express.seq_concat(tokens, start_idx)
                    if not is_valid:
                        print("Failed to parse seq_concat")
                        return False, start_idx
                        
                    # Successfully parsed a concatenation expression
                    values.append(concat_value)
                    start_idx = next_idx
                else:
                    # Just a regular literal
                    values.append(tokens[start_idx][1])  # Store the literal value
                    print(f"Added '{tokens[start_idx][1]}' to values: {values}")
                    start_idx += 1  # Move past the literal
            elif start_idx < len(tokens) and is_token(tokens, start_idx, literals):
                # Regular literal case
                values.append(tokens[start_idx][1])  # Store the literal value
                print(f"Added '{tokens[start_idx][1]}' to values: {values}")
                start_idx += 1  # Move past the literal
            else:
                print(f"Error: Expected a literal or seq type cast at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, start_idx  # Return failure
            
            # Now handle the express_value_tail (comma-separated values)
            start_idx = skip_spaces(tokens, start_idx)
            
            # Parse express_value_tail (handling comma-separated values)
            while start_idx < len(tokens) and is_token(tokens, start_idx, ','):
                print("Found a comma, proceeding with parsing.")
                
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
                
                # Check if we have a seq_concat after the comma
                elif start_idx < len(tokens) and is_token(tokens, start_idx, 'string literal'):
                    lookahead_idx = skip_spaces(tokens, start_idx + 1)
                    if lookahead_idx < len(tokens) and tokens[lookahead_idx][0] == "+":
                        print("Found 'string literal' followed by '+' after comma, parsing as seq_concat")
                        is_valid, concat_value, next_idx = express.seq_concat(tokens, start_idx)
                        if not is_valid:
                            print("Failed to parse seq_concat after comma")
                            return False, start_idx
                            
                        # Successfully parsed a concatenation expression
                        values.append(concat_value)
                        start_idx = next_idx
                        continue
                
                # Regular literal after comma
                if start_idx >= len(tokens) or not is_token(tokens, start_idx, literals):
                    print(f"Error: Expected a literal or seq type cast after ',' at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                    return False, start_idx  # Return failure
                
                values.append(tokens[start_idx][1])  # Store the next literal value
                print(f"Added '{tokens[start_idx][1]}' to values: {values}")
                
                start_idx += 1  # Move past the literal
                start_idx = skip_spaces(tokens, start_idx)  # Skip any spaces after the literal
            
            print("Parsing successful:", values)
            return True, start_idx  # Return success with next index only

        @staticmethod
        def seq_concat(tokens, start_idx):
            """Parses <seq_concat> based on CFG.
            <seq_concat> → <seq_concat_value> + <seq_concat_value> <seq_concat_tail>
            Currently simplified to handle string literals directly.
            """
            print("<seq_concat>")
            start_idx = skip_spaces(tokens, start_idx)
            
            # Parse the first string literal
            if not is_token(tokens, start_idx, 'string literal'):
                print(f"Error: Expected string literal at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None, start_idx
            
            # Get the first string value
            first_value = tokens[start_idx][1]
            print(f"First string literal: {first_value}")
            
            # Move past the first string literal
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            
            # Check for '+' operator
            if start_idx >= len(tokens) or tokens[start_idx][0] != "+":
                print(f"Error: Expected '+' at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None, start_idx
            
            # Move past the '+' operator
            start_idx += 1
            start_idx = skip_spaces(tokens, start_idx)
            
            # Parse the second string literal
            if not is_token(tokens, start_idx, 'string literal'):
                print(f"Error: Expected string literal at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None, start_idx
            
            # Get the second string value
            second_value = tokens[start_idx][1]
            print(f"Second string literal: {second_value}")
            
            # Concatenate the values
            result = first_value + second_value
            print(f"Concatenated result: {result}")
            
            # Move past the second string literal
            start_idx += 1
            
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
            """Parses <seq_concat_tail> recursively for + concatenation.
            <seq_concat_tail> → + <seq_concat_value> <seq_concat_tail>
            <seq_concat_tail> → λ
            Modified to handle string literals and seq function calls.
            """
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
                    return False, None, start_idx
                next_value = cast_value
                print(f"Next value is a seq function call: {next_value}")
                start_idx = next_idx
            else:
                print(f"Error: Expected string literal or seq function call at index {start_idx}, but found {tokens[start_idx] if start_idx < len(tokens) else 'EOF'}")
                return False, None, start_idx
            
            # Concatenate with current value
            updated_value = current_value + next_value
            print(f"Updated concatenation: {updated_value}")
            
            # Recursively call seq_concat_tail for further concatenation
            return express.seq_concat_tail(tokens, start_idx, updated_value)

        @staticmethod
        def seq_type_cast(tokens, start_idx):
            """Parses <seq_type_cast> based on CFG."""
            output_text.insert(tk.END, "<seq_type_cast>\n")
            
            # Check for 'seq' keyword followed by an Identifier
            if (start_idx + 1 < len(tokens) and
                    tokens[start_idx][1] == "seq" and
                    tokens[start_idx + 1][1] == "Identifier"):
                
                output_text.insert(tk.END, f"Found seq type cast at index {start_idx}: {tokens[start_idx]} {tokens[start_idx + 1]}\n")
                return True, f"seq({tokens[start_idx + 1][0]})", start_idx + 2  # Move past 'seq' and Identifier
            
            # Check for 'seq' keyword followed by '(', Identifier, and ')'
            if (start_idx + 3 < len(tokens) and
                    tokens[start_idx][1] == "seq" and
                    tokens[start_idx + 1][1] == "(" and
                    tokens[start_idx + 2][1] == "Identifier" and
                    tokens[start_idx + 3][1] == ")"):
                
                output_text.insert(tk.END, f"Found seq function call at index {start_idx}: {tokens[start_idx]} {tokens[start_idx + 1]} {tokens[start_idx + 2]} {tokens[start_idx + 3]}\n")
                return True, f"seq({tokens[start_idx + 2][0]})", start_idx + 4  # Move past 'seq', '(', Identifier, and ')'
            
            output_text.insert(tk.END, f"No valid seq type cast at index {start_idx}, returning λ\n")
            return True, None, start_idx  # Return empty (λ)

    def process_tokens(tokens):
        lines = []
        current_statement = []
        current_line = []
        current_line_number = 1
        brace_count = 0  # Track nested braces
        i = 0
        
        while i < len(tokens):
            token = tokens[i]
            if token is None or len(token) < 2:  # Prevents "None" token errors
                i += 1
                continue  # Skip invalid tokens

            # If we encounter a newline
            if token[1] == "newline":
                if current_line:  # Only add if there are tokens
                    current_statement.extend(current_line)
                    current_line = []

                current_line_number += 1

                if current_statement and any(t[1] == ';' for t in current_statement) and brace_count == 0:
                    lines.append(current_statement)
                    current_statement = []
            else:
                if token[1] == '{':
                    brace_count += 1
                elif token[1] == '}':
                    brace_count -= 1

                current_line.append(token)

                # Check if we have a closing brace followed by specific keywords
                if token[1] == '}' and brace_count == 0:
                    # Look ahead to see if 'else' or similar keywords follow
                    next_index = i + 1
                    while next_index < len(tokens) and tokens[next_index][1] in ["space", "newline"]:
                        next_index += 1
                    
                    # If we're at the end or the next token isn't a special keyword
                    if next_index >= len(tokens) or tokens[next_index][1] not in ["else", "while", "do", "elif"]:
                        current_statement.extend(current_line)
                        lines.append(current_statement)
                        current_statement = []
                        current_line = []

            i += 1

        if current_line:
            current_statement.extend(current_line)

        if current_statement:
            lines.append(current_statement)

        return lines

    arithmetic_value = {'numlit', 'Identifier'}
    conditional_value = {'numlit', 'Identifier', 'string literal'}
    conditional_op = {'<', '>', '<=', '=>', '==', '!=', '&&', '||', '!'}
    math_operator = {'+', '-', '*', "/"}
    literals = {'string literal', 'numlit', 'Identifier', 'dom', 'rec'}
    assignment_op = {'+=', '*=', '-=', '/=', '%=', '='}
    unary_op = {'++', '--'}

    math_pattern = [
        [arithmetic_value]    ]

    complex_math_pattern = [
        ['(', arithmetic_value, math_operator, arithmetic_value]
    ]

    conditional_pattern = [
        [conditional_value, conditional_op, conditional_value]   
    ]

    program_pattern = [
        ['act' ],
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

    destroy_pattern = [
        ['destroy']
    ]

    token_lines = process_tokens(tokens)
    valid_syntax = True

    print("\nTokens Received:")
    for idx, (token_id, token_value) in enumerate(tokens, start=1):
        print(f"{idx}. Token: {token_value} (ID: {token_id})")

    for line_num, line_tokens in enumerate(token_lines, start=1):
        # Remove space tokens (assuming space tokens are represented as ('whitespace', ' '))
        line_tokens = [token for token in line_tokens if token[1] != 'newline']

        def get_next_token(tokens, idx):
            """Returns the next non-space token and its index."""
            idx = skip_spaces(tokens, idx)
            if idx < len(tokens):
                return tokens[idx], idx
            return None, idx

        if not line_tokens:
            continue

        # Extract the first token value
        first_token = line_tokens[0][1] if line_tokens else None
        valid_line = False
        number_sign = None
        start_idx = 0 
        print(f"first token: {first_token}")
        
        if first_token == "act":
            for pattern in program_pattern:
                is_valid, next_idx, _ = validate_syntax_pattern(line_tokens, pattern)
                if is_valid:
                    is_valid_program, sign = program.main_function(line_tokens, next_idx)
                    if is_valid_program:
                        valid_line = True
                    break

        elif first_token in arithmetic_value or first_token == '(':
            next_token, lookahead_lexeme = get_next_token(line_tokens, start_idx + 1)  # Swap the values
            print(f"[DEBUG] Lookahead Token: '{next_token[1]}' (Lexeme: '{lookahead_lexeme}') at index {start_idx + 1}")

            if next_token[1] in math_operator:
                for pattern in chain(math_pattern, complex_math_pattern):  
                    is_valid, next_idx, _ = validate_syntax_pattern(line_tokens, pattern)
                    print("[DEBUG] Pasok pattern (arithmetic)")  # Debugging output
                    if is_valid:
                        print("[DEBUG] Pasok valid (arithmetic)")
                        is_valid_arith, sign = arithmetic.arithmetic_expression(line_tokens, next_idx)
                        if is_valid_arith:
                            valid_line = True
                        break  

            elif next_token[1] in conditional_op:
                print("condition yan bosss")
                for pattern in conditional_pattern:  
                    is_valid, next_idx, _ = validate_syntax_pattern(line_tokens, pattern)
                    print("[DEBUG] Pasok pattern (condition)")  # Debugging output
                    if is_valid:
                        print("[DEBUG] Pasok valid (condition)")
                        is_valid_condition, sign = conditional.condition_value_tail(line_tokens, next_idx)
                        if is_valid_condition:
                            valid_line = True
                        break  
         
        elif first_token == "destroy":
            for pattern in destroy_pattern:
                is_valid, next_idx, _ = validate_syntax_pattern(line_tokens, pattern)
                if is_valid:
                    is_valid_destroy, _ = statements.destroy_statement(line_tokens, next_idx)
                    if is_valid_destroy:
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
                            return

                    elif data_type == 'dose':
                        if is_valid:
                            is_valid_doseval, sign = variables.validate_doseval(line_tokens, next_idx)
                            if is_valid_doseval:
                                valid_line = True
                                number_sign = sign
                            return

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
