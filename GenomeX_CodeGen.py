import tkinter as tk
import GenomeX_Lexer as gxl
import GenomeX_Syntax as gxs
import GenomX_Semantic as gxsem
import io
import sys
import re
import builtins

# Remove recursion limit

class GenomeXCodeGenerator:

    print("Initializing GenomeXCodeGenerator...")
    def __init__(self, tokens, symbol_table=None):
        self.tokens = tokens
        self.symbol_table = symbol_table if symbol_table else {}
        self.functions = {}
        self.indentation = 0
        self.variable_types = {}
        self.python_code = []
        self.current_scope = "global"
        
    def add_line(self, line):
        """Add a line of Python code with proper indentation"""
        indent = "    " * self.indentation
        self.python_code.append(f"{indent}{line}")
        
    def generate_code(self):
        print("Generating Python code from codegen...")
        """Main method to generate Python code from tokens"""
        self.add_line("# Generated Python code from GenomeX")
        self.add_line("")
        
        i = 0
        while i < len(self.tokens):
            token, token_type = self.tokens[i]
            
            # Skip spaces and newlines
            if token_type in ["space", "newline", "tab"]:
                i += 1
                continue
                
            # Handle global declarations
            if token_type == '_G':
                i = self.process_local_declaration(i)
                
            # Handle functions
            elif token_type == 'act':
                i = self.process_function(i)
                
            else:
                i += 1
                
        return "\n".join(self.python_code)

    def process_function(self, index):
        """Process a function declaration"""
        # Skip 'act' token
        index += 1
        
        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
            index += 1
            
        is_main = False
        function_name = None
        
        # Check for gene (main function)
        if index < len(self.tokens) and self.tokens[index][1] == "gene":
            is_main = True
            function_name = "main"
            index += 1
        # Check for void keyword
        elif index < len(self.tokens) and self.tokens[index][1] == "void":
            index += 1  # Skip void keyword
            
            # Skip spaces
            while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                index += 1
                
            # Get function name after void
            if index < len(self.tokens) and self.tokens[index][1] == "Identifier":
                function_name = self.tokens[index][0]
                index += 1
        # Check for regular function
        elif index < len(self.tokens) and self.tokens[index][1] == "Identifier":
            function_name = self.tokens[index][0]
            index += 1
            
        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
            index += 1
            
        # Check for opening parenthesis
        if index < len(self.tokens) and self.tokens[index][0] == "(":
            index += 1
            
            # Process parameters
            params = []
            while index < len(self.tokens) and self.tokens[index][0] != ")":
                # Skip spaces and commas
                while index < len(self.tokens) and (self.tokens[index][1] == "space" or self.tokens[index][0] == ","):
                    index += 1
                
                if index < len(self.tokens) and self.tokens[index][0] == ")":
                    break
                
                # Get parameter type (ignore for Python)
                if index < len(self.tokens) and self.tokens[index][1] in ["dose", "quant", "seq", "allele"]:
                    index += 1
                    
                    # Skip spaces
                    while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                        index += 1
                    
                    # Get parameter name
                    if index < len(self.tokens) and self.tokens[index][1] == "Identifier":
                        param_name = self.tokens[index][0]
                        params.append(param_name)
                        index += 1
            
            # Skip closing parenthesis
            if index < len(self.tokens) and self.tokens[index][0] == ")":
                index += 1
            
            # Generate function definition
            if is_main:
                self.add_line("def main():")
            else:
                self.add_line(f"def {function_name}({', '.join(params)}):")
                
            self.indentation += 1
            self.current_scope = function_name
            
            # Skip spaces
            while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                index += 1
                
            # Check for opening brace
            if index < len(self.tokens) and self.tokens[index][0] == "{":
                index += 1
                
                # Process function body
                index = self.process_function_body(index)
                
                # Skip closing brace
                if index < len(self.tokens) and self.tokens[index][0] == "}":
                    index += 1
            
            self.indentation -= 1
            self.current_scope = "global"
            
            # Add main function call at the end if this was the main function
            if is_main:
                self.add_line("")
                self.add_line("if __name__ == \"__main__\":")
                self.indentation += 1
                self.add_line("main()")
                self.indentation -= 1
                
        return index
    
    def process_function_body(self, index, stop_at=None):
        """Process the body of a function"""
        while index < len(self.tokens):
            token, token_type = self.tokens[index]
            
            # Exit when we reach the closing brace
            if token == "}":
                break
                
            # Skip spaces, newlines and tabs
            if token_type in ["space", "newline", "tab"]:
                index += 1
                continue
                
            # Handle local variable declarations
            if token_type == "_L":
                index = self.process_local_declaration(index)
                
            # Handle express statement (print)
            elif token_type == "express":
                index = self.process_express_statement(index)
                
            # Handle if statement
            elif token_type == "if":
                index = self.process_if_statement(index)

            elif token_type == "elif":
                print(f"[DEBUG] Found elif at index {index}: {self.tokens[index]}")
                index = self.process_elif_statement(index)

            elif token_type == "else":
                print(f"[DEBUG] Found else at index {index}: {self.tokens[index]}")
                index = self.process_else_statement(index)

            # Handle while loop
            elif token_type == "while":
                index = self.process_while_loop(index)
                
            # Handle for loop
            elif token_type == "for":
                index = self.process_for_loop(index)
                
            # Handle prod statement (return)
            elif token_type == "prod":
                index = self.process_prod_statement(index)
            
            # Handle function call
            elif token_type == "func":
                index = self.process_function_call(index)
                
            # Handle assignment
            elif token_type == "Identifier":
                index = self.process_assignment(index)

            elif token_type == "destroy":
                # Directly translate "destroy" to "break"
                self.add_line("break")
                index += 1
                
                # Skip spaces
                while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                    index += 1
                    
                # Check for semicolon
                if index < len(self.tokens) and self.tokens[index][0] == ";":
                    index += 1
                else:
                    self.add_error("Expected ';' after destroy statement")

            elif token_type == "contig":
                # Directly translate "contig" to "continue"
                self.add_line("continue")
                index += 1
                
                # Skip spaces
                while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                    index += 1
                    
                # Check for semicolon
                if index < len(self.tokens) and self.tokens[index][0] == ";":
                    index += 1
                else:
                    self.add_error("Expected ';' after contig statement")
                

            else:
                index += 1
                
        return index

    def process_local_declaration(self, index):
        """Process a local variable declaration (including 1D and 2D arrays)"""
        print(f"Starting local declaration at token index {index}")
        # Skip _L token
        index += 1

        # Skip spaces and newline tokens
        while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
            index += 1

        # Skip 'perms' token if present
        if index < len(self.tokens) and self.tokens[index][1] == "perms":
            print("Ignoring 'perms' keyword in local declaration")
            index += 1
            while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                index += 1

        # Check for optional 'clust' (array)
        is_array = False
        if index < len(self.tokens) and self.tokens[index][1] == "clust":
            print("Detected 'clust' keyword (array)")
            is_array = True
            index += 1
            while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                index += 1

        # Get variable type
        if index < len(self.tokens) and self.tokens[index][1] in ["dose", "quant", "seq", "allele"]:
            var_type = self.tokens[index][1]
            print(f"Detected variable type: {var_type}")
            index += 1

            while index < len(self.tokens):
                while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                    index += 1

                # Variable name
                if index < len(self.tokens) and self.tokens[index][1] == "Identifier":
                    var_name = self.tokens[index][0]
                    # Handle True/False identifier renaming TTrue/FFalse
                    if var_name in ["True", "False"]:
                        var_name = f"T{var_name}" if var_name == "True" else f"F{var_name}"
                    print(f"Detected variable name: {var_name}")
                    self.variable_types[var_name] = var_type
                    index += 1

                    current_is_array = is_array
                    is_2d_array = False
                    array_sizes = []

                    # Check for [size] (array declaration)
                    array_dimensions = 0
                    while current_is_array and index < len(self.tokens):
                        while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                            index += 1
                        if index < len(self.tokens) and self.tokens[index][0] == "[":
                            array_dimensions += 1
                            index += 1
                            while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                                index += 1
                            # Get size (numlit, identifier, dom, rec)
                            size_value = None
                            if index < len(self.tokens) and self.tokens[index][1] in ("numlit", "Identifier"):
                                if self.tokens[index][1] == "numlit":
                                    # Normalize the number (remove leading/trailing zeros)
                                    size_value = self._normalize_number(self.tokens[index][0])
                                else:
                                    size_value = self.tokens[index][0]
                                print(f"Detected array size token: {size_value}")
                                index += 1
                            # elif index < len(self.tokens) and self.tokens[index][0] in ("dom", "rec"):
                            #     size_value = "True" if self.tokens[index][0] == "dom" else "False"
                            #     print(f"Detected array size token (boolean): {size_value}")
                            #     index += 1
                            
                            if size_value is not None:
                                array_sizes.append(size_value)
                            
                            while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                                index += 1
                            if index < len(self.tokens) and self.tokens[index][0] == "]":
                                index += 1
                            else:
                                break
                        else:
                            break

                    if array_dimensions == 2:
                        is_2d_array = True
                        print("Detected 2D array")
                    elif array_dimensions == 1:
                        print("Detected 1D array")

                    while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                        index += 1

                    # Assignment
                    if index < len(self.tokens) and self.tokens[index][0] == "=":
                        print(f"Detected assignment '=' for {var_name}")
                        index += 1
                        while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                            index += 1

                        elements = []
                        if current_is_array:
                            if is_2d_array:
                                print(f"Processing 2D array initializer for {var_name}")
                                while index < len(self.tokens) and self.tokens[index][0] != "}":
                                    row = []
                                    if index < len(self.tokens) and self.tokens[index][0] == "{":
                                        index += 1
                                        print("Detected opening brace '{' for row")
                                        while index < len(self.tokens) and self.tokens[index][0] != "}":
                                            if self.tokens[index][1] == "numlit":
                                                # Normalize the number (remove leading/trailing zeros)
                                                normalized_value = self._normalize_number(self.tokens[index][0])
                                                row.append(normalized_value)
                                                print(f"Added normalized numeric literal to row: {normalized_value} (from {self.tokens[index][0]})")
                                            elif self.tokens[index][0] == "dom":
                                                row.append("True")
                                                print("Added boolean True to array")
                                            elif self.tokens[index][0] == "rec":
                                                row.append("False")
                                                print("Added boolean False to array")
                                            elif self.tokens[index][1] == "string literal":
                                                row.append(self.tokens[index][0])
                                                print(f"Added string literal to row: {self.tokens[index][0]}")
                                            elif self.tokens[index][1] == "Identifier":
                                                # Handle True/False identifier renaming
                                                identifier = self.tokens[index][0]
                                                if identifier in ["True", "False"]:
                                                    identifier = f"T{identifier}" if identifier == "True" else f"F{identifier}"
                                                row.append(identifier)
                                                print(f"Added identifier to row: {identifier}")
                                            index += 1
                                            if index < len(self.tokens) and self.tokens[index][0] == ",":
                                                index += 1
                                            while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                                                if self.tokens[index][0] == "\n":
                                                    print("Ignoring newline token '\\n'")
                                                index += 1
                                        if index < len(self.tokens) and self.tokens[index][0] == "}":
                                            print("Detected closing brace '}' for row")
                                            index += 1
                                        elements.append(f"[{', '.join(row)}]")
                                        print(f"Completed row: {row}")

                                        if index < len(self.tokens) and self.tokens[index][0] == ",":
                                            index += 1
                                        while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                                            if self.tokens[index][0] == "\n":
                                                print("Ignoring newline token '\\n'")
                                            index += 1
                                if index < len(self.tokens) and self.tokens[index][0] == "}":
                                    print("Detected closing brace '}' for 2D array")
                                    index += 1

                                self.add_line(f"{var_name} = [{', '.join(elements)}]")
                                print(f"Generated 2D array assignment: {var_name} = [{', '.join(elements)}]")
                            else:
                                print(f"Processing 1D array initializer for {var_name}")
                                if index < len(self.tokens) and self.tokens[index][0] == "{":
                                    index += 1
                                    while index < len(self.tokens) and self.tokens[index][0] != "}":
                                        if self.tokens[index][1] == "numlit":
                                            # Normalize the number (remove leading/trailing zeros)
                                            normalized_value = self._normalize_number(self.tokens[index][0])
                                            elements.append(normalized_value)
                                            print(f"Added normalized numeric literal to array: {normalized_value} (from {self.tokens[index][0]})")
                                        elif self.tokens[index][0] == "dom":
                                            elements.append("True")
                                            print("Added boolean True to array")
                                        elif self.tokens[index][0] == "rec":
                                            elements.append("False")
                                            print("Added boolean False to array")
                                        elif self.tokens[index][1] == "string literal":
                                            elements.append(self.tokens[index][0])
                                            print(f"Added string literal to array: {self.tokens[index][0]}")
                                        elif self.tokens[index][1] == "Identifier":
                                            # Handle True/False identifier renaming
                                            identifier = self.tokens[index][0]
                                            if identifier in ["True", "False"]:
                                                identifier = f"T{identifier}" if identifier == "True" else f"F{identifier}"
                                            elements.append(identifier)
                                            print(f"Added identifier to array: {identifier}")
                                        index += 1
                                        if index < len(self.tokens) and self.tokens[index][0] == ",":
                                            index += 1
                                        while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                                            if self.tokens[index][0] == "\n":
                                                print("Ignoring newline token '\\n'")
                                            index += 1
                                    if index < len(self.tokens) and self.tokens[index][0] == "}":
                                        print("Detected closing brace '}' for 1D array")
                                        index += 1
                                    self.add_line(f"{var_name} = [{', '.join(elements)}]")
                                    print(f"Generated 1D array assignment: {var_name} = [{', '.join(elements)}]")
                        else:
                            value, index = self.extract_value(index)
                            self.add_line(f"{var_name} = {value}")
                            print(f"Assigned scalar value to {var_name}: {value}")
                    else:
                        # Default initialization
                        default_value = self.get_default_value(var_type)
                        if current_is_array:
                            if array_sizes:  # If array size is specified
                                if is_2d_array and len(array_sizes) >= 2:
                                    # Initialize 2D array with default values
                                    # Ensure array sizes are properly converted to integers
                                    rows = int(array_sizes[0])
                                    cols = int(array_sizes[1])
                                    
                                    # Create default value based on type
                                    if var_type == "dose":
                                        default_element = "0"
                                    elif var_type == "quant":
                                        default_element = "0.0"
                                    elif var_type == "seq":
                                        default_element = '""'
                                    elif var_type == "allele":
                                        default_element = "False"
                                    else:
                                        default_element = "None"
                                    
                                    # Create the 2D array initialization
                                    rows_list = []
                                    for _ in range(rows):
                                        cols_list = [default_element] * cols
                                        rows_list.append(f"[{', '.join(cols_list)}]")
                                    
                                    self.add_line(f"{var_name} = [{', '.join(rows_list)}]")
                                    print(f"Initialized 2D array {var_name} with size [{rows}][{cols}] and default value {default_element}")
                                else:
                                    # Initialize 1D array with default values
                                    # Ensure array size is properly converted to integer
                                    size = int(array_sizes[0])
                                    
                                    # Create default value based on type
                                    if var_type == "dose":
                                        default_element = "0"
                                    elif var_type == "quant":
                                        default_element = "0.0"
                                    elif var_type == "seq":
                                        default_element = '""'
                                    elif var_type == "allele":
                                        default_element = "False"
                                    else:
                                        default_element = "None"
                                    
                                    # Create the 1D array initialization
                                    elements = [default_element] * size
                                    self.add_line(f"{var_name} = [{', '.join(elements)}]")
                                    print(f"Initialized 1D array {var_name} with size {size} and default value {default_element}")
                            else:
                                # No size specified, initialize as empty array
                                self.add_line(f"{var_name} = []")
                                print(f"Default initialized empty array {var_name}")
                        else:
                            self.add_line(f"{var_name} = {default_value}")
                            print(f"Default initialized scalar {var_name} = {default_value}")

                    while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                        index += 1

                    if index < len(self.tokens) and self.tokens[index][0] == ";":
                        print("Detected semicolon ';' end of statement")
                        index += 1
                        # Always break after semicolon, even for single scalar declarations
                        break
                    elif index < len(self.tokens) and self.tokens[index][0] == ",":
                        print("Detected comma ',' more variables declared")
                        index += 1
                        continue
                    else:
                        # If neither semicolon nor comma, break to avoid infinite loop
                        break

            return index
   
    def process_express_statement(self, index):
        index += 1  # Skip 'express'

        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
            index += 1

        # Check for opening parenthesis
        if index < len(self.tokens) and self.tokens[index][0] == "(":
            index += 1

            # Build the expression as a string
            expression_parts = []
            paren_count = 1  # we've already seen one (
            dose_variables = []  # Track dose variables found in the expression
            allele_variables = []  # Track allele variables found in the expression
            
            while index < len(self.tokens) and paren_count > 0:
                token, token_type = self.tokens[index]

                if token == "(":
                    paren_count += 1
                elif token == ")":
                    paren_count -= 1
                    if paren_count == 0:
                        break
                
                # Track if this token is a dose variable identifier
                if token_type == "Identifier" and token in self.variable_types:
                    if self.variable_types[token] == "dose":
                        dose_variables.append(token)
                    elif self.variable_types[token] == "allele":
                        allele_variables.append(token)
                
                # Handle numeric literals with special handling for caret notation
                if token_type == "numlit":
                    if token.startswith("^"):
                        # Convert ^number to -number
                        token = f"-{self._normalize_number(token[1:])}"
                    else:
                        # Normalize the number (remove leading/trailing zeros)
                        token = self._normalize_number(token)
                # Handle dom/rec translation
                elif token == "dom":
                    token = "True"
                elif token == "rec":
                    token = "False"
                # Handle True/False identifier renaming
                elif token_type == "Identifier" and token in ["True", "False"]:
                    token = f"T{token}" if token == "True" else f"F{token}"
                # Handle logical operators
                elif token == "&&":
                    token = "and"
                elif token == "||":
                    token = "or"
                elif token == "!":
                    token = "not"
                
                expression_parts.append(token)
                index += 1

            # Skip the closing ')'
            if index < len(self.tokens) and self.tokens[index][0] == ")":
                index += 1

            # Process the expression with function extracting
            expression = " ".join(expression_parts)
            
            # Process expressions like "seq ( Sum )" to extract just "Sum" or transform "seq" to "str"
            words = expression.split()
            processed_words = []
            i = 0
            while i < len(words):
                # Check for pattern: function_name ( variable )
                if (i + 3 < len(words) and 
                    words[i+1] == "(" and 
                    words[i+3] == ")"):
                    func_name = words[i]
                    var = words[i+2]

                    # Replace "seq" with "str"
                    if func_name == "seq":
                        func_name = "str"
                        
                        # If the variable is a 'dose' type (integer), ensure it's converted to int first to remove decimal points
                        if var in self.variable_types and self.variable_types.get(var) == "dose":
                            processed_words.append(f"str(int({var}))")
                            i += 4  # Skip all four tokens
                            continue

                    processed_words.append(f"{func_name}({var})")
                    i += 4  # Skip all four tokens
                else:
                    processed_words.append(words[i])
                    i += 1

            processed_expression = " ".join(processed_words)
            
            # Replace all seq(dose_var) patterns with str(int(dose_var))
            for dose_var in dose_variables:
                processed_expression = re.sub(
                    fr'seq\s*\(\s*{dose_var}\s*\)', 
                    fr'str(int({dose_var}))', 
                    processed_expression
                )
            
            # Handle array indexing for dose variables with string conversion
            # First check if we're dealing with a dose variable
            for var_name, var_type in self.variable_types.items():
                if var_type == "dose" and var_name in processed_expression:
                    # Replace "seq ( Table [ I ] [ J ] )" with "str(int(Table[I][J]))" for dose variables
                    processed_expression = re.sub(
                        fr'seq\s*\(\s*{var_name}\s*\[\s*([A-Za-z0-9_]+)\s*\]\s*\[\s*([A-Za-z0-9_]+)\s*\]\s*\)', 
                        fr'str(int({var_name}[\1][\2]))', 
                        processed_expression
                    )
                    
                    # Replace "seq ( Table [ I ] )" with "str(int(Table[I]))" for 1D arrays of dose variables
                    processed_expression = re.sub(
                        fr'seq\s*\(\s*{var_name}\s*\[\s*([A-Za-z0-9_]+)\s*\]\s*\)', 
                        fr'str(int({var_name}[\1]))', 
                        processed_expression
                    )
            
            # Handle general case array indexing and string concatenation (for non-dose variables)
            # Replace "seq ( Table [ I ] [ J ] )" with "str(Table[I][J])"
            processed_expression = re.sub(r'seq\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\[\s*([A-Za-z0-9_]+)\s*\]\s*\[\s*([A-Za-z0-9_]+)\s*\]\s*\)', r'str(\1[\2][\3])', processed_expression)
            
            # Replace "seq ( Table [ I ] )" with "str(Table[I])" for 1D arrays
            processed_expression = re.sub(r'seq\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\[\s*([A-Za-z0-9_]+)\s*\]\s*\)', r'str(\1[\2])', processed_expression)
            
            # Handle string concatenation with array access
            # Replace "Table [ I ] [ J ] + \" \"" with "Table[I][J] + \" \""
            processed_expression = re.sub(r'([A-Za-z_][A-Za-z0-9_]*)\s*\[\s*([A-Za-z0-9_]+)\s*\]\s*\[\s*([A-Za-z0-9_]+)\s*\]\s*\+\s*\"\s*\"', r'\1[\2][\3] + " "', processed_expression)
            
            # Replace "Table [ I ] + \" \"" with "Table[I] + \" \"" for 1D arrays
            processed_expression = re.sub(r'([A-Za-z_][A-Za-z0-9_]*)\s*\[\s*([A-Za-z0-9_]+)\s*\]\s*\+\s*\"\s*\"', r'\1[\2] + " "', processed_expression)
            
            # Wrap allele variables with bool()
            for allele_var in allele_variables:
                # Handle simple variable case
                processed_expression = re.sub(
                    fr'\b{allele_var}\b(?!\s*\()',  # Match variable name not followed by (
                    f'bool({allele_var})',
                    processed_expression
                )
                
                # Handle array access cases
                processed_expression = re.sub(
                    fr'{allele_var}\s*\[\s*([A-Za-z0-9_]+)\s*\]',
                    f'bool({allele_var}[\\1])',
                    processed_expression
                )
                
                processed_expression = re.sub(
                    fr'{allele_var}\s*\[\s*([A-Za-z0-9_]+)\s*\]\s*\[\s*([A-Za-z0-9_]+)\s*\]',
                    f'bool({allele_var}[\\1][\\2])',
                    processed_expression
                )
            
            self.add_line(f"print({processed_expression})")

        return index

    
    def process_if_statement(self, index):
        """Process an if statement"""
        print(f"[DEBUG] Entering process_if_statement at index {index} with token: {self.tokens[index] if index < len(self.tokens) else 'END'}")

        # Store the current statement beginning index
        if_start_index = index

        # Skip 'if' token
        index += 1
        print(f"[DEBUG] Skipped 'if', now at index {index}")

        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
            print(f"[DEBUG] Skipping space at index {index}")
            index += 1

        # Extract condition
        condition, index = self.extract_condition(index)
        print(f"[DEBUG] Extracted condition: '{condition}'")

        # Generate Python if statement
        self.add_line(f"if {condition}:")
        print(f"[DEBUG] Added line: if {condition}:")

        self.indentation += 1
        print(f"[DEBUG] Increased indentation to {self.indentation}")

        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
            print(f"[DEBUG] Skipping space at index {index} before brace")
            index += 1

        # Check for opening brace
        if self.tokens[index][0] == "{":
            index += 1
            body_start_index = index
            brace_depth = 1

            while index < len(self.tokens) and brace_depth > 0:
                if self.tokens[index][0] == "{":
                    brace_depth += 1
                elif self.tokens[index][0] == "}":
                    brace_depth -= 1
                index += 1

            body_end_index = index - 1  # Don't include closing }

            print("[DEBUG] ====== PROCESSING ONLY TOKENS INSIDE IF BRACES ======")
            for i in range(body_start_index, body_end_index):
                print(f"[DEBUG] Token {i}: {self.tokens[i]}")
            print("[DEBUG] ====== END OF IF BODY SCOPE (IGNORE OUTSIDE) ======")

            self.indentation += 1
            self.process_function_body(body_start_index, stop_at=body_end_index)
            self.indentation -= 1

        else:
            print("[DEBUG] Warning: Opening brace for if body not found!")

        self.indentation -= 1
        print(f"[DEBUG] Decreased indentation to {self.indentation}")
        print("[DEBUG] Exiting process_if_statement")
        return index


    def process_elif_statement(self, index):
        """Process an if statement"""
        print(f"[DEBUG] Entering process_if_statement at index {index} with token: {self.tokens[index] if index < len(self.tokens) else 'END'}")

        # Store the current statement beginning index
        if_start_index = index

        # Skip 'if' token
        index += 1
        print(f"[DEBUG] Skipped 'if', now at index {index}")

        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
            print(f"[DEBUG] Skipping space at index {index}")
            index += 1

        # Extract condition
        condition, index = self.extract_condition(index)
        print(f"[DEBUG] Extracted condition: '{condition}'")

        # Generate Python if statement
        self.add_line(f"elif {condition}:")
        print(f"[DEBUG] Added line: elif {condition}:")

        self.indentation += 1
        print(f"[DEBUG] Increased indentation to {self.indentation}")

        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
            print(f"[DEBUG] Skipping space at index {index} before brace")
            index += 1

        # Check for opening brace
        if self.tokens[index][0] == "{":
            index += 1
            body_start_index = index
            brace_depth = 1

            while index < len(self.tokens) and brace_depth > 0:
                if self.tokens[index][0] == "{":
                    brace_depth += 1
                elif self.tokens[index][0] == "}":
                    brace_depth -= 1
                index += 1

            body_end_index = index - 1  # Don't include closing }

            print("[DEBUG] ====== PROCESSING ONLY TOKENS INSIDE IF BRACES ======")
            for i in range(body_start_index, body_end_index):
                print(f"[DEBUG] Token {i}: {self.tokens[i]}")
            print("[DEBUG] ====== END OF IF BODY SCOPE (IGNORE OUTSIDE) ======")

            self.indentation += 1
            self.process_function_body(body_start_index, stop_at=body_end_index)
            self.indentation -= 1

        else:
            print("[DEBUG] Warning: Opening brace for if body not found!")

        self.indentation -= 1
        print(f"[DEBUG] Decreased indentation to {self.indentation}")
        print("[DEBUG] Exiting process_if_statement")
        return index


    def process_else_statement(self, index):
        """Process an if statement"""
        print(f"[DEBUG] Entering process_if_statement at index {index} with token: {self.tokens[index] if index < len(self.tokens) else 'END'}")

        # Store the current statement beginning index
        if_start_index = index

        # Skip 'if' token
        index += 1
        print(f"[DEBUG] Skipped 'if', now at index {index}")

        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
            print(f"[DEBUG] Skipping space at index {index}")
            index += 1

        # Generate Python if statement
        self.add_line(f"else :")
        print(f"[DEBUG] Added line: elif :")

        self.indentation += 1
        print(f"[DEBUG] Increased indentation to {self.indentation}")

        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
            print(f"[DEBUG] Skipping space at index {index} before brace")
            index += 1

        # Check for opening brace
        if self.tokens[index][0] == "{":
            index += 1
            body_start_index = index
            brace_depth = 1

            while index < len(self.tokens) and brace_depth > 0:
                if self.tokens[index][0] == "{":
                    brace_depth += 1
                elif self.tokens[index][0] == "}":
                    brace_depth -= 1
                index += 1

            body_end_index = index - 1  # Don't include closing }

            print("[DEBUG] ====== PROCESSING ONLY TOKENS INSIDE IF BRACES ======")
            for i in range(body_start_index, body_end_index):
                print(f"[DEBUG] Token {i}: {self.tokens[i]}")
            print("[DEBUG] ====== END OF IF BODY SCOPE (IGNORE OUTSIDE) ======")

            self.indentation += 1
            self.process_function_body(body_start_index, stop_at=body_end_index)
            self.indentation -= 1

        else:
            print("[DEBUG] Warning: Opening brace for if body not found!")

        self.indentation -= 1
        print(f"[DEBUG] Decreased indentation to {self.indentation}")
        print("[DEBUG] Exiting process_if_statement")
        return index
    
    def process_while_loop(self, index):
        """Process a while loop"""
        #print(f"DEBUG: Entering process_while_loop at index {index}, token: {self.tokens[index]}")

        # Skip 'while'
        index += 1

        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
            index += 1

        # Extract condition
        condition, index = self.extract_condition(index)
        #print(f"DEBUG: Extracted condition: '{condition}', new index: {index}")

        # Clean up the condition - remove extra spaces and ensure proper formatting
        condition = condition.strip()
        
        # Generate the while loop with proper condition formatting
        self.add_line(f"while {condition}:")
        self.indentation += 1

        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
            index += 1

        # Expect opening brace
        if index < len(self.tokens) and self.tokens[index][0] == "{":
            #print(f"DEBUG: Found opening brace")
            index += 1  # Skip '{'
            
            # Store the body start index
            body_start_index = index
            brace_depth = 1
            
            # Find the matching closing brace by tracking brace depth
            while index < len(self.tokens) and brace_depth > 0:
                if self.tokens[index][0] == "{":
                    brace_depth += 1
                elif self.tokens[index][0] == "}":
                    brace_depth -= 1
                index += 1
            
            body_end_index = index - 1  # Don't include closing }
            
            print("[DEBUG] ====== PROCESSING ONLY TOKENS INSIDE WHILE LOOP BRACES ======")
            for i in range(body_start_index, body_end_index):
                print(f"[DEBUG] Token {i}: {self.tokens[i]}")
            print("[DEBUG] ====== END OF WHILE LOOP BODY SCOPE (IGNORE OUTSIDE) ======")
            
            # Process the body with specific start and end indices
            self.process_function_body(body_start_index, stop_at=body_end_index)

        self.indentation -= 1
        #print(f"DEBUG: Exiting process_while_loop at index {index}")
        return index
    
    def process_for_loop(self, index):
        """Process a for loop and translate it into Python syntax"""
        #print(f"DEBUG: Starting process_for_loop at index {index}, token: {self.tokens[index] if index < len(self.tokens) else 'END'}")
        #print(f"DEBUG: Full loop tokens: {self.tokens[index:index+15]}")  # Print more tokens to see the structure
        
        index += 1  # Skip 'for'
        #print(f"DEBUG: After skipping 'for', index: {index}, token: {self.tokens[index] if index < len(self.tokens) else 'END'}")

        while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
            index += 1
        
        #print(f"DEBUG: After skipping spaces, index: {index}, token: {self.tokens[index] if index < len(self.tokens) else 'END'}")

        if index < len(self.tokens) and self.tokens[index][0] == "(":
            index += 1
            #print(f"DEBUG: After opening parenthesis, index: {index}, token: {self.tokens[index] if index < len(self.tokens) else 'END'}")

            while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                index += 1

            # Initialization - Handle both standard case and "type var = value" case
            init_var = None
            init_value = None

            # Check if we have a declaration like "int i = 1" or "dose I = 1"
            if index + 4 < len(self.tokens) and self.tokens[index][1] in ["Identifier", "dose"] and self.tokens[index+1][1] == "space" and self.tokens[index+2][1] == "Identifier":
                # This looks like a type declaration (e.g., "dose I = 1")
                type_name = self.tokens[index][0]
                index += 1  # Skip type name
                
                while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                    index += 1
                    
                if index < len(self.tokens) and self.tokens[index][1] == "Identifier":
                    init_var = self.tokens[index][0]
                    #print(f"DEBUG: Found init_var with type: {type_name} {init_var}")
                    index += 1

                    while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                        index += 1

                    if index < len(self.tokens) and self.tokens[index][0] == "=":
                        index += 1

                        while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:

                            index += 1

                        # Get the numeric value
                        if index < len(self.tokens) and self.tokens[index][1] in ["Number", "Identifier"]:
                            init_value = self.tokens[index][0]
                            #print(f"DEBUG: Found init_value: {init_value}")
                            index += 1
                        else:
                            init_value, index = self.extract_value(index)
                            #print(f"DEBUG: Found extracted init_value: {init_value}")
            
            # Standard case (var = value) if we haven't found a variable yet
            elif index < len(self.tokens) and self.tokens[index][1] == "Identifier":
                init_var = self.tokens[index][0]
                #print(f"DEBUG: Found init_var: {init_var}")
                index += 1

                while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:

                    index += 1

                if index < len(self.tokens) and self.tokens[index][0] == "=":
                    index += 1

                    while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                        index += 1

                    init_value, index = self.extract_value(index)
                    #print(f"DEBUG: Found init_value: {init_value}")

            # Skip semicolon
            while index < len(self.tokens) and self.tokens[index][0] != ";":
                index += 1
            
            if index < len(self.tokens):
                #print(f"DEBUG: Found semicolon at index: {index}")
                index += 1


            while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                index += 1

            # Condition
            #print(f"DEBUG: Before extracting condition, index: {index}, token: {self.tokens[index] if index < len(self.tokens) else 'END'}")
            condition, index = self.extract_for_condition(index)
            #print(f"DEBUG: Extracted condition: '{condition}', new index: {index}")
            
            # Extract condition components for range-based conversion
            condition_var = None
            condition_op = None
            condition_value = None
            
            # Parse condition into components (var, operator, value)
            condition_match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*(<=|<|>=|>|==)\s*([a-zA-Z0-9_]+)', condition)
            if condition_match:
                condition_var = condition_match.group(1)
                condition_op = condition_match.group(2)
                condition_value = condition_match.group(3)
                #print(f"DEBUG: Parsed condition - var: {condition_var}, op: {condition_op}, value: {condition_value}")


            # Skip semicolon
            #print(f"DEBUG: Looking for second semicolon, current token: {self.tokens[index] if index < len(self.tokens) else 'END'}")
            while index < len(self.tokens) and self.tokens[index][0] != ";":
                index += 1
                #print(f"DEBUG: Searching for semicolon, index: {index}, token: {self.tokens[index] if index < len(self.tokens) else 'END'}")
            
            if index < len(self.tokens):
                #print(f"DEBUG: Found second semicolon at index: {index}")
                index += 1


            while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                index += 1

            # Increment
            increment_var = None
            increment_op = None
            increment_value = "1"

            #print(f"DEBUG: Before increment part, index: {index}, token: {self.tokens[index] if index < len(self.tokens) else 'END'}")
            
            # Check for increment variable
            if index < len(self.tokens) and self.tokens[index][1] == "Identifier":
                increment_var = self.tokens[index][0]
                #print(f"DEBUG: Found increment_var: {increment_var}")
                index += 1

                while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                    index += 1

                # Check for increment operator (++, --, +=, -=)
                #print(f"DEBUG: Looking for increment operator, token: {self.tokens[index] if index < len(self.tokens) else 'END'}")
                
                # Handle ++ and -- operators, even if they're split from the variable
                if index < len(self.tokens):
                    if self.tokens[index][0] in ["++", "--"]:
                        increment_op = "+=" if self.tokens[index][0] == "++" else "-="
                        #print(f"DEBUG: Found increment_op from ++/--: {increment_op}")
                        index += 1
                    elif self.tokens[index][0] in ["+=", "-="]:
                        increment_op = self.tokens[index][0]
                        #print(f"DEBUG: Found increment_op: {increment_op}")
                        index += 1

                        while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                            index += 1

                        increment_value, index = self.extract_value(index)
                        #print(f"DEBUG: Found increment_value: {increment_value}")
                    # Check for space followed by ++ or -- (for cases like "I ++")
                    elif self.tokens[index][1] == "space":
                        temp_index = index
                        while temp_index < len(self.tokens) and self.tokens[temp_index][1] == "space":
                            temp_index += 1
                        
                        if temp_index < len(self.tokens) and self.tokens[temp_index][0] in ["++", "--"]:
                            increment_op = "+=" if self.tokens[temp_index][0] == "++" else "-="
                            #print(f"DEBUG: Found increment_op (with space) from ++/--: {increment_op}")
                            index = temp_index + 1

            #print(f"DEBUG: Looking for closing parenthesis, current token: {self.tokens[index] if index < len(self.tokens) else 'END'}")
            while index < len(self.tokens) and self.tokens[index][0] != ")":
                index += 1
                #print(f"DEBUG: Searching for closing parenthesis, index: {index}, token: {self.tokens[index] if index < len(self.tokens) else 'END'}")
            
            if index < len(self.tokens):
                #print(f"DEBUG: Found closing parenthesis at index: {index}")
                index += 1


            # Attempt to translate to Python range-based for loop
            python_range_generated = False
            
            #print(f"DEBUG: Translation check - init_var: {init_var}, init_value: {init_value}, condition_var: {condition_var}, " +
            #f"condition_op: {condition_op}, condition_value: {condition_value}, " +
            #f"increment_var: {increment_var}, increment_op: {increment_op}")
            
            # Special case for "for (dose I = 1; I <= Num; I++)" to "for I in range(1, Num + 1):"
            if init_value and condition_var and condition_op == "<=" and condition_value and increment_var and increment_op == "+=":
                if init_var == increment_var == condition_var:  # Standard case
                    #print(f"DEBUG: Standard case - variables match")
                    end_value = condition_value
                    step = increment_value
                    self.add_line(f"for {init_var} in range({init_value}, {end_value} + 1, {step}):")
                    python_range_generated = True
                elif increment_var == condition_var:  # Special case with type declaration
                    #print(f"DEBUG: Special case - increment/condition vars match but init_var is different")
                    # This is the "dose I = 1" special case
                    end_value = condition_value
                    step = increment_value
                    self.add_line(f"for {increment_var} in range({init_value}, {end_value} + 1, {step}):")
                    python_range_generated = True
            
            # Standard case if the special case didn't apply
            if not python_range_generated and (init_var and init_value and condition_var and condition_op and condition_value and 
                increment_var and increment_op and init_var == condition_var == increment_var):
                
                # Handle different comparison operators for the range end value
                end_value = condition_value
                step = increment_value if increment_op == "+=" else f"-{increment_value}"
                
                #print(f"DEBUG: Range translation - end_value: {end_value}, step: {step}, condition_op: {condition_op}")
                
                if condition_op == "<":
                    # for i = start; i < end; i++ -> range(start, end)
                    self.add_line(f"for {init_var} in range({init_value}, {end_value}, {step}):")
                    #print(f"DEBUG: Generated range with < operator")
                    python_range_generated = True
                elif condition_op == "<=":
                    # for i = start; i <= end; i++ -> range(start, end + 1)
                    self.add_line(f"for {init_var} in range({init_value}, {end_value} + 1, {step}):")
                    #print(f"DEBUG: Generated range with <= operator")
                    python_range_generated = True
                elif condition_op == ">":
                    # for i = start; i > end; i-- -> range(start, end, -step)
                    if increment_op == "-=":
                        self.add_line(f"for {init_var} in range({init_value}, {end_value}, {step}):")
                        #print(f"DEBUG: Generated range with > operator")
                        python_range_generated = True
                elif condition_op == ">=":
                    # for i = start; i >= end; i-- -> range(start, end - 1, -step)
                    if increment_op == "-=":
                        self.add_line(f"for {init_var} in range({init_value}, {end_value} - 1, {step}):")
                        #print(f"DEBUG: Generated range with >= operator")
                        python_range_generated = True

            if not python_range_generated:
                #print(f"DEBUG: Falling back to while loop")
                if init_var and init_value:
                    self.add_line(f"{init_var} = {init_value}")
                self.add_line(f"for {condition}:")

            self.indentation += 1

            while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                index += 1

            #print(f"DEBUG: Looking for opening brace, token: {self.tokens[index] if index < len(self.tokens) else 'END'}")
            if index < len(self.tokens) and self.tokens[index][0] == "{":
                #print(f"DEBUG: Found opening brace")
                index += 1
                
                # Store the body start index
                body_start_index = index
                brace_depth = 1
                
                # Find the matching closing brace by tracking brace depth
                while index < len(self.tokens) and brace_depth > 0:
                    if self.tokens[index][0] == "{":
                        brace_depth += 1
                    elif self.tokens[index][0] == "}":
                        brace_depth -= 1
                    index += 1
                
                body_end_index = index - 1  # Don't include closing }
                
                print("[DEBUG] ====== PROCESSING ONLY TOKENS INSIDE FOR LOOP BRACES ======")
                for i in range(body_start_index, body_end_index):
                    print(f"[DEBUG] Token {i}: {self.tokens[i]}")
                print("[DEBUG] ====== END OF FOR LOOP BODY SCOPE (IGNORE OUTSIDE) ======")
                
                # Process the body with specific start and end indices
                self.process_function_body(body_start_index, stop_at=body_end_index)
                
                # Add increment statement for non-range loops after processing the body
                if not python_range_generated and increment_var and increment_op:
                    self.add_line(f"{increment_var} {increment_op} {increment_value}")

            self.indentation -= 1
            #print(f"DEBUG: Finished process_for_loop, returning index: {index}")

        return index
    def process_prod_statement(self, index):
        """Process a prod (return) statement"""
        # Skip prod token
        index += 1
        
        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
            index += 1
        
        # Extract expression until semicolon
        expression = ""
        start_index = index
        
        while index < len(self.tokens) and self.tokens[index][0] != ";":
            if self.tokens[index][1] != "space":  # Skip spaces in the expression
                expression += self.tokens[index][0]
            index += 1
        
        # Skip the semicolon
        if index < len(self.tokens) and self.tokens[index][0] == ";":
            index += 1
        
        # Generate Python return statement
        self.add_line(f"return {expression}")
        
        return index
    
    def process_assignment(self, index):
        """Process a variable assignment"""
        print("[DEBUG] ====== PROCESS ASSIGNMENT ======")

        print(f"[DEBUG] Entering process_assignment at index {index} with token: {self.tokens[index] if index < len(self.tokens) else 'END'}")

        var_name = self.tokens[index][0]
        # Handle True/False identifier renaming
        if var_name in ["True", "False"]:
            var_name = f"T{var_name}" if var_name == "True" else f"F{var_name}"
        print(f"[DEBUG] Variable name identified: '{var_name}'")
        index += 1

        # Check for array indexing for the variable being assigned to
        array_indices = []
        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
            print(f"[DEBUG] Skipping space at index {index}")
            index += 1

        # Check for [ which indicates array indexing
        while index < len(self.tokens) and self.tokens[index][0] == "[":
            print(f"[DEBUG] Found array index start for variable '{var_name}' at index {index}")
            index += 1  # Move past '['
            
            # Skip spaces
            while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                print(f"[DEBUG] Skipping space in array index at {index}")
                index += 1
                
            # Read the index value
            array_index = ""
            while index < len(self.tokens) and self.tokens[index][0] != "]":
                if self.tokens[index][1] not in ["space", "newline"]:
                    array_index += self.tokens[index][0]
                    print(f"[DEBUG] Appending to array index: {self.tokens[index][0]}")
                index += 1
                
            if index < len(self.tokens) and self.tokens[index][0] == "]":
                print(f"[DEBUG] Found array index end, index value: '{array_index}'")
                array_indices.append(array_index)
                index += 1
            else:
                print(f"[ERROR] Missing closing bracket for array index")
                break

        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
            print(f"[DEBUG] Skipping space at index {index}")
            index += 1

        # Check for assignment operator
        if index < len(self.tokens) and self.tokens[index][0] in ["=", "-=", "+=", "/=", "*="]:
            assignment_op = self.tokens[index][0]
            print(f"[DEBUG] Assignment operator found: '{assignment_op}' at index {index}")
            index += 1

            # Skip spaces
            while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                print(f"[DEBUG] Skipping space at index {index} after assignment operator")
                index += 1

            # Check if the next token is a 'stimuli'
            if index < len(self.tokens) and self.tokens[index][1] == "stimuli":
                print(f"[DEBUG] Found 'stimuli' input at index {index}: {self.tokens[index]}")
                
                # Move past 'stimuli'
                index += 1
                
                # Skip spaces
                while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                    index += 1
                    
                # Extract the prompt string
                prompt = ""
                if index < len(self.tokens) and self.tokens[index][0] == "(":
                    index += 1  # Skip '('
                    
                    # Skip spaces
                    while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                        index += 1
                    
                    # Get the string literal
                    if index < len(self.tokens) and self.tokens[index][1] == "string literal":
                        prompt = self.tokens[index][0]
                        print(f"[DEBUG] Found prompt: {prompt}")
                        index += 1
                    
                    # Skip spaces
                    while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                        index += 1
                    
                    # Skip closing parenthesis
                    if index < len(self.tokens) and self.tokens[index][0] == ")":
                        index += 1
                
                # Check variable type to wrap with appropriate conversion if needed
                var_type = self.variable_types.get(var_name)
                print(f"[DEBUG] Variable type of {var_name}: {var_type}")
                
                # Generate the appropriate input statement based on variable type
                if var_type == "dose":  # Integer numeric type
                    # For dose type, use int(input())
                    if array_indices:
                        array_access = f"{var_name}[{']['.join(array_indices)}]"
                        self.add_line(f"{array_access} {assignment_op} int(input({prompt}))")
                        print(f"[DEBUG] Added line: {array_access} {assignment_op} int(input({prompt}))")
                    else:
                        self.add_line(f"{var_name} {assignment_op} int(input({prompt}))")
                        print(f"[DEBUG] Added line: {var_name} {assignment_op} int(input({prompt}))")
                elif var_type == "quant":  # Float numeric type
                    # For quant type, use Decimal for precise decimal handling
                    if array_indices:
                        array_access = f"{var_name}[{']['.join(array_indices)}]"
                        self.add_line(f"from decimal import Decimal")
                        self.add_line(f"{array_access} {assignment_op} Decimal(input({prompt}))")
                        print(f"[DEBUG] Added line: {array_access} {assignment_op} Decimal(input({prompt}))")
                    else:
                        self.add_line(f"from decimal import Decimal")
                        self.add_line(f"{var_name} {assignment_op} Decimal(input({prompt}))")
                        print(f"[DEBUG] Added line: {var_name} {assignment_op} Decimal(input({prompt}))")
                else:  # seq, allele, etc.
                    # For string and other types, use input() without conversion
                    if array_indices:
                        array_access = f"{var_name}[{']['.join(array_indices)}]"
                        self.add_line(f"{array_access} {assignment_op} input({prompt})")
                        print(f"[DEBUG] Added line: {array_access} {assignment_op} input({prompt})")
                    else:
                        self.add_line(f"{var_name} {assignment_op} input({prompt})")
                        print(f"[DEBUG] Added line: {var_name} {assignment_op} input({prompt})")
                
                # Skip the semicolon if present
                if index < len(self.tokens) and self.tokens[index][0] == ";":
                    print(f"[DEBUG] Found semicolon at index {index}, ending assignment")
                    index += 1
            else:
                # Extract expression until semicolon
                value = ""
                print(f"[DEBUG] Beginning to parse expression for assignment to '{var_name}'")
                
                in_array_access = False
                current_identifier = ""

                while index < len(self.tokens) and self.tokens[index][0] != ";":
                    token = self.tokens[index][0]
                    token_type = self.tokens[index][1]

                    if token_type not in ["space", "newline"]:
                        if token == "dom":
                            value += "True"
                            print(f"[DEBUG] Replaced 'dom' with 'True'")
                        elif token == "rec":
                            value += "False"
                            print(f"[DEBUG] Replaced 'rec' with 'False'")
                        elif token in ["+", "-", "/", "*", "%"]:
                            if token == "/" and self.variable_types.get(var_name) == "dose":
                                # Use integer division for dose variables
                                value += " // "
                                print(f"[DEBUG] Converted '/' to integer division '//' for dose variable")
                            else:
                                value += " " + token + " "
                            print(f"[DEBUG] Appended operator to expression: '{token}'")
                        elif token == "[":
                            # Start of array indexing in expression
                            in_array_access = True
                            value += token
                            print(f"[DEBUG] Started array access: '{token}'")
                        elif token == "]":
                            # End of array indexing in expression
                            in_array_access = False
                            value += token
                            print(f"[DEBUG] Ended array access: '{token}'")
                        elif token_type == "numlit" and token.startswith("^"):
                            # Handle negative numbers using caret (^)
                            # Convert ^number to -number
                            negative_value = f"-{self._normalize_number(token[1:])}"
                            value += negative_value
                            print(f"[DEBUG] Converted caret number '{token}' to '{negative_value}'")
                        elif token_type == "numlit":
                            # Normalize number (remove leading zeros)
                            normalized_value = self._normalize_number(token)
                            value += normalized_value
                            print(f"[DEBUG] Normalized number '{token}' to '{normalized_value}'")
                        elif token == "seq":
                            # Handle seq(Num) pattern by translating to str(Num)
                            value += "str"  # Replace seq with str
                            print(f"[DEBUG] Replaced 'seq' with 'str'")
                        elif token_type == "Identifier":
                            # Handle True/False identifier renaming
                            if token in ["True", "False"]:
                                token = f"T{token}" if token == "True" else f"F{token}"
                            value += token
                            print(f"[DEBUG] Appended identifier to expression: '{token}'")
                        elif token == "||":
                            value += " or "
                            print(f"[DEBUG] Replaced '||' with 'or'")
                        elif token == "&&":
                            value += " and "
                            print(f"[DEBUG] Replaced '&&' with 'and'")
                        elif token == "!":
                            value += "not "
                            print(f"[DEBUG] Replaced '!' with 'not'")
                        else:
                            value += token
                            print(f"[DEBUG] Appended token to expression: '{token}'")

                    index += 1

                # Skip the semicolon
                if index < len(self.tokens) and self.tokens[index][0] == ";":
                    print(f"[DEBUG] Found semicolon at index {index}, ending assignment")
                    index += 1

                # Form the final assignment statement
                if array_indices:
                    array_access = f"{var_name}[{']['.join(array_indices)}]"
                    self.add_line(f"{array_access} {assignment_op} {value}")
                    print(f"[DEBUG] Added line: {array_access} {assignment_op} {value}")
                else:
                    self.add_line(f"{var_name} {assignment_op} {value}")
                    print(f"[DEBUG] Added line: {var_name} {assignment_op} {value}")
        else:
            print(f"[DEBUG] No valid assignment operator found at index {index}")

        print(f"[DEBUG] Exiting process_assignment at index {index}")
        print("[DEBUG] ====== END OF PROCESS ASSIGNMENT ======")

        return index

    def process_input(self, var_name, index):
        """Generate input() assignment for the given variable with optional prompt"""
        index += 1  # skip 'stimuli'

        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
            index += 1

        prompt = ""

        # Check if there's a parenthesis and string inside
        if index < len(self.tokens) and self.tokens[index][0] == "(":
            index += 1  # skip '('

            # Skip spaces
            while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                index += 1

            if index < len(self.tokens) and self.tokens[index][1] == "string literal":
                prompt = self.tokens[index][0]
                index += 1

            # Skip spaces
            while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                index += 1

            if index < len(self.tokens) and self.tokens[index][0] == ")":
                index += 1  # skip ')'

        # Check variable type to wrap with int() if needed
        if self.variable_types.get(var_name) == "dose":
            self.add_line(f'{var_name} = int(input({prompt}))')
        elif self.variable_types.get(var_name) == "seq":
            self.add_line(f'{var_name} = input({prompt})')
        else:
            self.add_line(f'{var_name} = input({prompt})')

        return index

    def extract_value(self, index):
        """Extract a value expression"""
        if index >= len(self.tokens):
            return "None", index
            
        token, token_type = self.tokens[index]

        if token_type == "numlit":
            # Handle negative numbers using caret (^)
            if token.startswith("^"):
                # Convert ^number to -number 
                value = f"-{self._normalize_number(token[1:])}"
            else:
                # Normalize the number (remove leading/trailing zeros)
                value = self._normalize_number(token)
            index += 1

        elif token_type == "string literal":
            # String
            value = token
            index += 1
        elif token_type == "Identifier":
            # Variable
            value = token
            index += 1
        elif token == "dom":
            value = "True"
            index += 1
        elif token == "rec":
            value = "False"
            index += 1
        elif token == "(":
            index += 1
            value, index = self.extract_expression(index)
            if index < len(self.tokens) and self.tokens[index][0] == ")":
                index += 1
        else:
            value = "None"
            index += 1

        return value, index
        
    def _normalize_number(self, num_str):
        """
        Normalize a number string:
        - Remove leading zeros from whole numbers (0003 -> 3)
        - Keep decimal numbers as they are
        """
        # Check if it's a decimal number
        if '.' in num_str:
            # Keep decimal numbers as they are
            return num_str
        else:
            # For whole numbers, remove leading zeros and convert to integer
            try:
                return str(int(num_str))
            except ValueError:
                # If conversion fails, return original string
                return num_str

    def extract_expression(self, index):
        """Extract a complete expression"""
        if index >= len(self.tokens):
            return "None", index
            
        left_value, index = self.extract_value(index)
        
        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
            index += 1
            
        # Check for operators
        if index < len(self.tokens) and self.tokens[index][0] in ["+", "-", "*", "/", "%"]:
            operator = self.tokens[index][0]
            index += 1
            
            # Skip spaces
            while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                index += 1
                
            right_value, index = self.extract_expression(index)
            
            # Special handling for string concatenation with dose variables
            if operator == "+" and (
                ('"' in left_value or "str(" in left_value) or 
                ('"' in right_value or "str(" in right_value)):
                
                # Check if left_value is a dose variable and not already wrapped in str() or int()
                if (left_value in self.variable_types and 
                    self.variable_types.get(left_value) == "dose" and 
                    not left_value.startswith("str(") and 
                    not left_value.startswith("int(")):
                    left_value = f"str(int({left_value}))"
                
                # Check if right_value is a dose variable and not already wrapped in str() or int()
                if (right_value in self.variable_types and 
                    self.variable_types.get(right_value) == "dose" and 
                    not right_value.startswith("str(") and 
                    not right_value.startswith("int(")):
                    right_value = f"str(int({right_value}))"
            
            # Special handling for division with dose variables - use integer division
            if operator == "/" and (
                (left_value in self.variable_types and self.variable_types.get(left_value) == "dose") or
                (right_value in self.variable_types and self.variable_types.get(right_value) == "dose")):
                operator = "//"  # Replace with integer division
            
            return f"{left_value} {operator} {right_value}", index
        
        return left_value, index
    
    def extract_statement(self, index):
        """Extracts a regular statement ending with a semicolon"""
        #print(f"DEBUG: Entering extract_statement at index {index}")
        statement_tokens = []
        
        # Skip spaces at the beginning
        while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
            index += 1

        # Extract tokens until we find a semicolon
        while index < len(self.tokens):
            token, token_type = self.tokens[index]
            
            # Stop at semicolon
            if token == ";":
                index += 1  # skip the semicolon
                break
                
            # Add non-space tokens to the statement
            if token_type != "space" and token_type != "newline":
                statement_tokens.append(token)
                
            index += 1

        # Join tokens but use proper Python syntax
        statement = " ".join(statement_tokens).strip()
        
        # Handle division - always convert / to // for integer division when dose variables are involved
        if "/" in statement and not '"//' in statement and not '//"' in statement:
            # Extract variable names from the statement
            var_names = re.findall(r'\b[A-Za-z_][A-Za-z0-9_]*\b', statement)
            
            # Check if any variables involved in division are dose type (integers)
            has_dose = False
            for var_name in var_names:
                if var_name in self.variable_types and self.variable_types[var_name] == "dose":
                    has_dose = True
                    break
            
            # If any variables are dose type, use integer division
            if has_dose:
                # Use regex to find division operations not inside strings
                def replace_division(match):
                    if match.group(0) in ['"/', '/"']:
                        return match.group(0)  # Don't replace if in string
                    return match.group(1) + "//" + match.group(2)
                
                statement = re.sub(r'([^"/])\/([^"/])', replace_division, statement)
        
        # Fix any incorrect colons that might have been introduced
        statement = statement.replace(":", "")
        
        # For dose type variables, ensure any floating point results are converted to int
        assignment_match = re.match(r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)', statement)
        if assignment_match:
            var_name = assignment_match.group(1)
            expression = assignment_match.group(2)
            
            # If assigning to a dose variable and expression contains division, wrap in int()
            if var_name in self.variable_types and self.variable_types[var_name] == "dose" and ('/' in expression and not '//' in expression):
                statement = f"{var_name} = int({expression})"
        
        #print(f"DEBUG: Exiting extract_statement with statement: '{statement}', next index: {index}")
        return statement, index
    def extract_condition(self, index):
        """Extract a condition expression from tokens starting at the given index"""
        #print(f"DEBUG: Starting extract_condition at index {index}, token: {self.tokens[index] if index < len(self.tokens) else 'END'}")
        
        start_index = index
        condition_parts = []
        paren_level = 0

        # Skip spaces and newlines at the beginning
        while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
            index += 1

        # Check for opening parenthesis
        if index < len(self.tokens) and self.tokens[index][0] == "(":
            condition_parts.append(self.tokens[index][0])
            index += 1
            paren_level += 1

            # Skip spaces and newlines after opening parenthesis
            while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                index += 1

        # Extract the condition
        while index < len(self.tokens):
            token, token_type = self.tokens[index]

            # Handle nested parentheses
            if token == "(":
                paren_level += 1
                condition_parts.append(token)
            elif token == ")":
                paren_level -= 1
                condition_parts.append(token)
                if paren_level <= 0:  # We've reached a closing parenthesis that ends the condition
                    index += 1  # Skip the closing parenthesis
                    break
            else:
                # Replace dom/rec with Python booleans
                if token == "dom":
                    condition_parts.append("True")
                elif token == "rec":
                    condition_parts.append("False")
                # Handle caret notation (^number) for negative numbers
                elif token_type == "numlit" and token.startswith("^"):
                    # Convert ^number to -number
                    negative_value = "-" + token[1:]
                    condition_parts.append(negative_value)
                elif token_type == "numlit":
                    # Normalize numeric literals
                    normalized_value = self._normalize_number(token)
                    condition_parts.append(normalized_value)
                elif token_type not in ["space", "newline"]:
                    condition_parts.append(token)

            index += 1

        # Join all parts of the condition
        condition = " ".join(condition_parts)

        # Replace logical operators
        condition = condition.replace("&&", "and").replace("||", "or")

        # Remove surrounding parentheses if present
        condition = condition.strip()
        if condition.startswith("(") and condition.endswith(")"):
            condition = condition[1:-1].strip()

        #print(f"DEBUG: Extracted condition: '{condition}', from tokens: {self.tokens[start_index:index]}")

        return condition, index


    def extract_for_condition(self, index):
        """Extract a condition for if/while statements"""
        if index >= len(self.tokens):
            return "False", index
            
        left_value, index = self.extract_value(index)
        
        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
            index += 1
            
        # Check for comparison operators
        if index < len(self.tokens) and self.tokens[index][0] in ["==", "!=", "<", ">", "<=", ">="]:
            operator = self.tokens[index][0]
            index += 1
            
            # Skip spaces
            while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                index += 1
                
            right_value, index = self.extract_value(index)
            
            return f"{left_value} {operator} {right_value}", index
        
        return left_value, index
    
    def get_default_value(self, var_type):
        """Get the default value for a given type"""
        if var_type == "dose":
            return "0"
        elif var_type == "quant":
            return "0.0"
        elif var_type == "seq":
            return '""'
        elif var_type == "allele":
            return "False"
        else:
            return "None"
    
    def process_function_call(self, index):
        """Process a function call or assignment statement"""
        # Skip func token
        index += 1

        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
            index += 1

        # Get function name
        function_name = None
        if index < len(self.tokens) and self.tokens[index][1] == "Identifier":
            function_name = self.tokens[index][0]
            index += 1

            # Skip spaces
            while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                index += 1

            has_params = False
            args = []
            
            # Check for opening parenthesis for function parameters
            if index < len(self.tokens) and self.tokens[index][0] == "(":
                has_params = True
                index += 1

                # Process arguments
                args = []
                
                # Skip initial spaces
                while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                    index += 1
                    
                # Handle empty argument list
                if index < len(self.tokens) and self.tokens[index][0] == ")":
                    index += 1
                else:
                    # Process first argument
                    if index < len(self.tokens):
                        arg_value, index = self.extract_value(index)
                        args.append(arg_value)
                    
                    # Process additional arguments
                    while index < len(self.tokens) and self.tokens[index][0] != ")":
                        # Skip spaces
                        while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                            index += 1
                        
                        # Check for comma
                        if index < len(self.tokens) and self.tokens[index][0] == ",":
                            index += 1  # Skip comma
                            
                            # Skip spaces after comma
                            while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                                index += 1
                            
                            # Extract the next argument
                            if index < len(self.tokens) and self.tokens[index][0] != ")":
                                arg_value, index = self.extract_value(index)
                                args.append(arg_value)
                        else:
                            # If no comma is found, we should be at the end
                            break

                # Skip closing parenthesis
                if index < len(self.tokens) and self.tokens[index][0] == ")":
                    index += 1
                    
                # Skip spaces after closing parenthesis
                while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                    index += 1

            # Check if this is an assignment (func GCD(A, B) = G or func name = other)
            if index < len(self.tokens) and self.tokens[index][0] == "=":
                index += 1  # Skip over equals sign
                
                # Skip spaces after equals
                while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                    index += 1
                    
                # Get assignment target
                if index < len(self.tokens) and self.tokens[index][1] == "Identifier":
                    assign_target = self.tokens[index][0]
                    index += 1
                    
                    if has_params:
                        # This is a function with parameters that's being assigned (func GCD(A, B) = G)
                        self.add_line(f"{assign_target} = {function_name}({', '.join(args)})")

                    else:
                        # This is a simple assignment (func name = other)
                        self.add_line(f"{function_name} = {assign_target}")
                else:
                    # Handle error - expected identifier after =
                    print(f"Error: Expected identifier after '=' at index {index}")
                    
            elif has_params:
                # This is a normal function call with parameters
                self.add_line(f"{function_name}({', '.join(args)})")
            else:
                # This is just a function reference with no call
                self.add_line(f"{function_name}")
                
            # Skip spaces after everything
            while index < len(self.tokens) and self.tokens[index][1] in ["space", "newline"]:
                index += 1
                
            # Skip semicolon if present
            if index < len(self.tokens) and self.tokens[index][0] == ";":
                index += 1

        return index
def generate_python_code(tokens, symbol_table=None):
    """Generate Python code from GenomeX tokens"""
    code_generator = GenomeXCodeGenerator(tokens, symbol_table)
    generated_code = code_generator.generate_code()
    
    # Fix common issues in the generated code
    generated_code = generated_code.replace("**name**", "__name__")
    
    return generated_code

def display_codegen_output(python_code, output_panel):
    """Display the generated Python code in the output panel"""
    output_panel.delete(1.0, tk.END)
    output_panel.insert(tk.END, python_code)
    return python_code

def parseCodeGen(tokens, codegen_panel):
    """Parse tokens, generate Python code, display it, and execute it with output shown in terminal"""
    # Clear any previous content
    codegen_panel.delete(1.0, tk.END)
    
    try:
        # Generate Python code
        python_code = generate_python_code(tokens)
        
        # Replace **name** with __name__ if needed
        fixed_code = python_code.replace("**name**", "__name__")
        
        # Display the generated Python code with syntax highlighting TRANSLATOR
        codegen_panel.insert(tk.END, "===== GENERATED PYTHON CODE =====\n\n", "info")
        codegen_panel.insert(tk.END, fixed_code, "code")
        codegen_panel.insert(tk.END, "\n\n===== EXECUTION OUTPUT =====\n\n", "info")
        
        # Configure tags for syntax highlighting
        codegen_panel.tag_configure("info", foreground="#2196f3", font=("Consolas", 12, "bold"))
        codegen_panel.tag_configure("code", font=("Consolas", 11))
        codegen_panel.tag_configure("error", foreground="#f44336", font=("Consolas", 12, "bold"))
        codegen_panel.tag_configure("success", foreground="#4caf50", font=("Consolas", 12, "bold"))
        codegen_panel.tag_configure("warning", foreground="#ff9800", font=("Consolas", 12))
        codegen_panel.tag_configure("cmd", foreground="#9c27b0", font=("Consolas", 12))
        codegen_panel.tag_configure("output", foreground="#212121", font=("Consolas", 12))
        
        # Get the root window from the text widget
        parent_window = codegen_panel.winfo_toplevel()
        
        # Create a custom stdout class for real-time output
        class TkTextRedirector(io.StringIO):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
                
            def write(self, string):
                # Write directly to the text widget in the main thread
                parent_window.after_idle(self._write, string)
                return len(string)
                
            def _write(self, string):
                # Convert negative numbers to caret notation (e.g., -123 to ^123)
                # Use regex to find negative numbers and replace them
                # Handle integers first
                string = re.sub(r'(^|\s|[^a-zA-Z0-9.])-(\d+)', r'\1^\2', string)
                # Handle decimals (-123.45 to ^123.45)
                string = re.sub(r'(^|\s|[^a-zA-Z0-9.])-(\d+\.\d+)', r'\1^\2', string)
                
                # Convert boolean values to GenomeX syntax
                # Replace "True" with "dom" and "False" with "rec"
                string = re.sub(r'(^|\s)True(\s|$|\.|\,|\;|\:)', r'\1dom\2', string)
                string = re.sub(r'(^|\s)False(\s|$|\.|\,|\;|\:)', r'\1rec\2', string)
                
                self.text_widget.insert(tk.END, string, "output")
                self.text_widget.see(tk.END)
                parent_window.update()  # Force update immediately
        
        # Redirect stdout to capture print output
        original_stdout = sys.stdout
        captured_output = TkTextRedirector(codegen_panel)
        sys.stdout = captured_output
        
        # Backup the original input function
        original_input = builtins.input
        
        # Create a simple input handler
        def panel_input(prompt=''):
            # Ensure all previous output is displayed
            parent_window.update()
            
            # Display the prompt
            codegen_panel.insert(tk.END, prompt, "info")
            codegen_panel.see(tk.END)
            parent_window.update()
            
            # Create a styled frame for input
            input_frame = tk.Frame(codegen_panel, bg="#f0f0ff", padx=8, pady=8, 
                                  highlightbackground="#7c4dff", highlightthickness=1)
            
            # Create entry field
            input_entry = tk.Entry(input_frame, width=40, font=("Consolas", 11),
                                  bg="white", fg="#212121", insertbackground="#5e35b1",
                                  relief="flat", bd=0)
            input_entry.pack(side=tk.LEFT, padx=(0, 8), ipady=6)
            
            # Use a list to store the result
            input_result = [None]
            
            def format_input(input_value):
                """
                Format the input according to the following rules:
                - If starts with ^, convert to negative
                - If string, leave as is
                - If number, validate and format appropriately:
                  * Integers: up to 13 digits, remove leading zeros (0000003 -> 3)
                  * Decimals: up to 13 digits in whole number part, exactly 6 decimal places
                """
                # Handle ^ prefix for negative numbers
                if input_value.startswith('^') and len(input_value) > 1:
                    input_value = '-' + input_value[1:]
                
                # Try to interpret as number only if it looks like a number
                if input_value.replace('-', '', 1).replace('.', '', 1).isdigit():
                    try:
                        # Split into whole and decimal parts if it's a decimal number
                        if '.' in input_value:
                            whole_part, decimal_part = input_value.split('.')
                            
                            # Check whole number part length
                            if len(whole_part.lstrip('-')) > 13:
                                raise ValueError("ERROR: Whole number part exceeds maximum limit of 13 digits")
                            
                            # Check decimal part length
                            if len(decimal_part) > 6:
                                raise ValueError("ERROR: Decimal part exceeds maximum limit of 6 digits")
                            
                            # Return the original input value if it passes validation
                            return input_value
                        else:
                            # Handle integer case - remove leading zeros
                            num = int(input_value)
                            if len(str(abs(num))) > 13:
                                raise ValueError("ERROR: Integer exceeds maximum limit of 13 digits")
                            return str(num)  # Converting to int and back to str removes leading zeros
                            
                    except ValueError as e:
                        # If it's our custom error, propagate it
                        if str(e).startswith("ERROR:"):
                            raise
                        # For other ValueError cases, return the original input
                        return input_value
                
                # If not a number or number conversion failed, return as is
                return input_value
            
            def on_submit():
                raw_input = input_entry.get()
                
                try:
                    formatted_input = format_input(raw_input)
                    input_result[0] = formatted_input
                    
                    input_entry.config(state="disabled", bg="#f5f5f5")
                    submit_button.config(state="disabled")
                    
                    # Signal that input is ready
                    input_frame.event_generate('<<InputReady>>')
                except ValueError as e:
                    error_msg = str(e)
                    error_label = tk.Label(input_frame, text=error_msg, fg="#f44336", 
                                         bg="#f0f0ff", font=("Consolas", 10))
                    error_label.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
                    
                    original_bg = input_entry.cget("bg")
                    input_entry.config(bg="#ffebee")
                    
                    def reset_error():
                        error_label.destroy()
                        input_entry.config(bg=original_bg)
                    
                    parent_window.after(3000, reset_error)
            
            def finish_input():
                input_frame.destroy()
                # Convert negative numbers to caret notation in the display
                display_value = input_result[0]
                if isinstance(display_value, str) and display_value.startswith('-'):
                    # Remove the minus sign and check if the rest is a valid number (integer or decimal)
                    num_part = display_value[1:]
                    if num_part.isdigit() or (num_part.count('.') == 1 and num_part.replace('.', '', 1).isdigit()):
                        display_value = '^' + num_part
                
                # Convert True/False to dom/rec
                if display_value == "True":
                    display_value = "dom"
                elif display_value == "False":
                    display_value = "rec"
                
                codegen_panel.insert(tk.END, f"{display_value}\n", "cmd")
                codegen_panel.see(tk.END)
                parent_window.update()
            
            # Create submit button
            submit_button = tk.Button(input_frame, text="Submit", font=("Segoe UI", 10, "bold"),
                                    bg="#5e35b1", fg="white", relief="flat",
                                    activebackground="#7c4dff", activeforeground="white",
                                    command=on_submit, padx=12, pady=4, bd=0,
                                    cursor="hand2", width=8)
            submit_button.pack(side=tk.LEFT)
            
            # Insert the frame into the text widget
            codegen_panel.insert(tk.END, "\n")
            codegen_panel.window_create(tk.END, window=input_frame)
            codegen_panel.insert(tk.END, "\n")
            codegen_panel.see(tk.END)
            
            # Focus the entry
            input_entry.focus_set()
            
            def on_entry_focus(event):
                input_frame.config(highlightbackground="#9c27b0")
            
            def on_entry_focus_out(event):
                input_frame.config(highlightbackground="#7c4dff")
            
            input_entry.bind("<FocusIn>", on_entry_focus)
            input_entry.bind("<FocusOut>", on_entry_focus_out)
            input_entry.bind("<Return>", lambda event: on_submit())
            
            # Bind the input ready event
            input_frame.bind('<<InputReady>>', lambda e: finish_input())
            
            # Wait for input using Tkinter's event loop
            input_frame.wait_window()
            
            return input_result[0]
        
        # Override the input function
        builtins.input = panel_input
        
        # Display a message that code is executing
        codegen_panel.insert(tk.END, "Executing code...\n\n", "info")
        codegen_panel.see(tk.END)
        parent_window.update()
        
        try:
            # Execute the code
            exec_globals = {'__name__': '__main__'}
            exec(fixed_code, exec_globals)
            codegen_panel.insert(tk.END, "\nCode executed successfully.\n", "success")
            execution_success = True
        except Exception as exec_error:
            import traceback
            error_msg = f"Execution Error: {str(exec_error)}"
            codegen_panel.insert(tk.END, f"\n{error_msg}\n", "error")
            codegen_panel.see(tk.END)
            traceback.print_exc()
            output = error_msg
            execution_success = False
        finally:
            # Make sure to restore stdout and input function
            sys.stdout = original_stdout
            builtins.input = original_input
        
        # Display end of execution message
        codegen_panel.see(tk.END)

        return True, python_code

    except Exception as e:
        # Ensure stdout is restored if an exception occurs
        if 'original_stdout' in locals():
            sys.stdout = original_stdout
        
        if 'original_input' in locals() and 'builtins' in locals():
            builtins.input = original_input
        
        # Display the error in the codegen panel
        codegen_panel.insert(tk.END, "----- EXECUTION ERROR -----\n", "error")
        codegen_panel.insert(tk.END, str(e), "error")
        codegen_panel.insert(tk.END, "\n----- END OF ERROR -----", "error")
        
        return False, str(e)