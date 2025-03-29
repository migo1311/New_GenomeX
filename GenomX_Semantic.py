
import re
import GenomeX_Lexer as gxl
import GenomeX_Syntax as gxs
import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
import sys
from itertools import chain

class SemanticAnalyzer:
    def __init__(self, tokens, symbol_table=None):
        self.tokens = tokens
        self.current_token = None
        self.symbol_table = symbol_table if symbol_table is not None else {}
        self.token_index = 0
        self.errors = []
        self.functions = {}  # Track function definitions
        self.current_line = 1  # Track line numbers for better error reporting
        self.in_loop = False  # Track if we're inside a loop for break/continue validation
        self.next_token()

    def next_token(self):
        # Skip spaces and newlines
        while (self.token_index < len(self.tokens) and 
            (self.tokens[self.token_index][1] == "space" or 
                self.tokens[self.token_index][1] == "newline"
                )):
            self.token_index += 1  # Skip spaces and newlines
        
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
            self.token_index += 1
        else:
            self.current_token = None
        print(f"Moved to next token: {self.current_token}")
    
    def parse(self):
        while self.current_token is not None:
            if self.current_token[1] == 'act':
                self.act_gene_function()
            elif self.current_token[1] == '_G':
                self.declaration()
            elif self.current_token[1] not in ['act', '_G']:
                # If the token is not 'act' or '_G', and not already an error
                self.act_gene_function()  # Attempt to parse as act by default
            else:
                self.errors.append(f"Semantic Error: Unexpected token: {self.current_token[1]}")
                self.next_token()  # Skip invalid token to continue analysis


    def act_gene_function(self):
        print(f"Current token: {self.current_token}")  # Debug print
        self.next_token()  # Move past 'act'
        print(f"Current token: {self.current_token}")  # Debug print
        
        # Skip Spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()  # Move past space
    
        # Check for '{'
        # if self.current_token is None or self.current_token[0] != '{':
        #     self.errors.append(f"Semantic Error: Expected '{{' after 'gene()', but found {self.current_token}")
        #     return
        # self.next_token()  # Move past '{'
        # print(f"Current token: {self.current_token}")  # Debug print
        
        # Skip Spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()  # Move past space
    
        # Parse the body statements
        self.parse_body_statements()  # Parse the body of the act gene function
        
        # Skip Spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()  # Move past space
    
        # Check for '}'
        # if self.current_token is None or self.current_token[0] != '}':
        #     self.errors.append(f"Semantic Error: Expected '}}' at end of 'act gene' function, but found {self.current_token}")
        #     return
        self.next_token()  # Move past '}'
        print(f"Current token: {self.current_token}")  # Debug print
        return

    def parse_body_statements(self):
        was_in_loop = self.in_loop  # Save previous loop state
        
        while self.current_token is not None and self.current_token[0] != '}':
            # Skip newlines and spaces
            while self.current_token is not None and self.current_token[1] in ['newline', 'space']:
                self.next_token()
                
            if self.current_token is None or self.current_token[0] == '}':
                break
                
            if self.current_token[0] in ['_L', '_G'] or self.current_token[1] in ['dose', 'quant', 'seq', 'allele']:
                self.declaration()
            elif self.current_token[1] == 'if':
                self.if_statement()
            elif self.current_token[1] == 'for':
                self.in_loop = True  # Mark that we're in a loop
                self.for_loop_statement()
                self.in_loop = was_in_loop  # Restore previous loop state
            elif self.current_token[1] == 'while':
                self.in_loop = True  # Mark that we're in a loop
                self.while_statement()
                self.in_loop = was_in_loop  # Restore previous loop state
            elif self.current_token[1] == 'do':
                self.in_loop = True  # Mark that we're in a loop
                self.do_while_statement()
                self.in_loop = was_in_loop  # Restore previous loop state
            elif self.current_token[1] == 'express':
                self.next_token()
            elif self.current_token[1] == 'Identifier':
                self.check_variable_usage()
            elif self.current_token[0] == 'destroy':
                self.break_statement()
            elif self.current_token[0] == 'contig':
                self.continue_statement()
            elif self.current_token[1] == 'clust':
                self.array_declaration()
            elif self.current_token[1] == 'act':
                self.function_declaration()
            elif self.current_token[1] == 'comment':
                self.next_token()
            elif self.current_token[1] == 'func':
                self.next_token()
            elif self.current_token[1] == None:
                self.next_token()
            else:
                # self.errors.append(f"Semantic Error: Unexpected token '{self.current_token[0]}' in body")
                self.next_token()  # Skip invalid token
    
    def break_statement(self):
        """Parse break statement"""
        if not self.in_loop:
            self.errors.append("Semantic Error: 'break' statement can only be used inside a loop")
        
        self.next_token()  # Move past 'break'
        
        # Check for semicolon
        if self.current_token is None or self.current_token[0] != ';':
            self.errors.append(f"Semantic Error: Expected ';' after 'break', found {self.current_token}")
            return
            
        self.next_token()  # Move past ';'
    
    def continue_statement(self):
        """Parse continue statement"""
        if not self.in_loop:
            self.errors.append("Semantic Error: 'continue' statement can only be used inside a loop")
        
        self.next_token()  # Move past 'continue'
        
        # Check for semicolon
        if self.current_token is None or self.current_token[0] != ';':
            self.errors.append(f"Semantic Error: Expected ';' after 'continue', found {self.current_token}")
            return
            
        self.next_token()  # Move past ';'
    
    def array_declaration(self):
        """Parse array declaration"""
        self.next_token()  # Move past 'array'
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
        
        # Get element type
        if self.current_token is None or self.current_token[1] not in ['dose', 'quant', 'seq', 'allele']:
            self.errors.append(f"Semantic Error: Expected valid type after 'array', found {self.current_token}")
            return
            
        element_type = self.current_token[1]
        self.next_token()  # Move past element type
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
            
        # Get array name
        if self.current_token is None or self.current_token[1] != 'Identifier':
            self.errors.append(f"Semantic Error: Expected identifier for array name, found {self.current_token}")
            return
            
        array_name = self.current_token[0]
        
        # Check for redeclaration
        if array_name in self.symbol_table:
            self.errors.append(f"Semantic Error: Variable '{array_name}' already declared")
            
        self.next_token()  # Move past identifier
        
        # Check for array size declaration [size]
        declared_size = None
        if self.current_token is not None and self.current_token[0] == '[':
            self.next_token()  # Move past '['
            
            # Get size value
            if self.current_token is None or (self.current_token[1] != 'numlit' and self.current_token[1] != 'identifier') or (self.current_token[1] == 'numlit' and '.' in self.current_token[0]):
                self.errors.append(f"Semantic Error: Expected integer value or identifier for array size, found {self.current_token}")
                return
                
            try:
                declared_size = int(self.current_token[0])
                if declared_size <= 0:
                    self.errors.append(f"Semantic Error: Array size must be positive, found {declared_size}")
            except:
                self.errors.append(f"Semantic Error: Invalid array size {self.current_token[0]}")
                return
                
            self.next_token()  # Move past size value
            
            # Check for closing bracket
            if self.current_token is None or self.current_token[0] != ']':
                self.errors.append(f"Semantic Error: Expected ']' after array size, found {self.current_token}")
                return
                
            self.next_token()  # Move past ']'
        
        # Add to symbol table
        self.symbol_table[array_name] = {
            'type': f'array_{element_type}',
            'value': [],
            'element_type': element_type,
            'size': declared_size  # Will be None if no size was declared
        }
        
        # Check for assignment
        if self.current_token is not None and self.current_token[0] == '=':
            self.next_token()  # Move past '='
            
            # Check for array initializer
            if self.current_token is None or self.current_token[0] != '{':
                self.errors.append(f"Semantic Error: Expected '{{' for array initialization, found {self.current_token}")
                return
                
            self.next_token()  # Move past '['
            
            # Parse array elements
            elements = []
            while self.current_token is not None and self.current_token[0] != '}':
                # Skip spaces and commas
                while self.current_token is not None and (self.current_token[1] == 'space' or self.current_token[0] == ','):
                    self.next_token()
                    
                if self.current_token is None or self.current_token[0] == ']':
                    break
                    
                # Check element type
                if element_type == 'dose' and (self.current_token[1] != 'numlit' or '.' in self.current_token[0]):
                    self.errors.append(f"Semantic Error: Expected integer value for dose array element, found {self.current_token}")
                elif element_type == 'quant' and self.current_token[1] != 'numlit':
                    self.errors.append(f"Semantic Error: Expected numeric value for quant array element, found {self.current_token}")
                elif element_type == 'seq' and self.current_token[1] != 'string literal':
                    self.errors.append(f"Semantic Error: Expected string value for seq array element, found {self.current_token}")
                elif element_type == 'allele' and self.current_token[0] not in ['dom', 'rec']:
                    self.errors.append(f"Semantic Error: Expected 'dom' or 'rec' for allele array element, found {self.current_token}")
                
                # Store element
                if element_type == 'dose':
                    try:
                        elements.append(int(self.current_token[0]))
                    except:
                        pass
                elif element_type == 'quant':
                    try:
                        elements.append(float(self.current_token[0]))
                    except:
                        pass
                elif element_type == 'seq':
                    elements.append(self.current_token[0].strip('"\''))
                elif element_type == 'allele':
                    elements.append(self.current_token[0] == 'dom')
                
                self.next_token()  # Move past element
                
                # Look for comma or closing bracket
                if self.current_token is None:
                    self.errors.append("Semantic Error: Unexpected end of tokens in array initialization")
                    return
                    
                if self.current_token[0] != ',' and self.current_token[0] != '}':
                    self.errors.append(f"Semantic Error: Expected ',' or '}}' in array initialization, found {self.current_token}")
            
            # Check for size mismatch between declaration and initialization
            if declared_size is not None and len(elements) != declared_size:
                self.errors.append(f"Semantic Error: Array '{array_name}' declared with size {declared_size} but initialized with {len(elements)} elements")
            
            # Update symbol table with elements
            self.symbol_table[array_name]['value'] = elements
            
            if self.current_token is None or self.current_token[0] != '}':
                self.errors.append(f"Semantic Error: Expected '}}' at end of array initialization, found {self.current_token}")
                return
                
            self.next_token()  # Move past ']'
        elif declared_size is not None:
            # If size was declared but no initialization, create array with default values
            default_value = None
            if element_type == 'dose':
                default_value = 0
            elif element_type == 'quant':
                default_value = 0.0
            elif element_type == 'seq':
                default_value = ""
            elif element_type == 'allele':
                default_value = False
                
            # Initialize array with default values
            self.symbol_table[array_name]['value'] = [default_value] * declared_size
        
        # Check for semicolon
        if self.current_token is None or self.current_token[0] != ';':
            self.errors.append(f"Semantic Error: Expected ';' after array declaration, found {self.current_token}")
            return
            
        self.next_token()  # Move past ';'
    
    def function_declaration(self):
        """Parse function declaration"""
        self.next_token()  # Move past 'act'
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
            
        # Get function name
        if self.current_token is None or self.current_token[1] != 'Identifier':
            self.errors.append(f"Semantic Error: Expected identifier for function name, found {self.current_token}")
            return
            
        function_name = self.current_token[0]
        
        # Check for redeclaration
        if function_name in self.functions:
            self.errors.append(f"Semantic Error: Function '{function_name}' already declared")
            
        self.next_token()  # Move past function name
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
        
        # Check for opening parenthesis
        if self.current_token is None or self.current_token[0] != '(':
            self.errors.append(f"Semantic Error: Expected '(' after function name, found {self.current_token}")
            return
            
        self.next_token()  # Move past '('
        
        # Parse parameters
        parameters = []
        while self.current_token is not None and self.current_token[0] != ')':
            # Skip spaces and commas
            while self.current_token is not None and (self.current_token[1] == 'space' or self.current_token[0] == ','):
                self.next_token()
                
            if self.current_token is None or self.current_token[0] == ')':
                break
                
            # Get parameter type
            if self.current_token[1] not in ['dose', 'quant', 'seq', 'allele']:
                self.errors.append(f"Semantic Error: Expected valid type for function parameter, found {self.current_token}")
                # Skip to next comma or closing parenthesis
                while self.current_token is not None and self.current_token[0] != ',' and self.current_token[0] != ')':
                    self.next_token()
                continue
                
            param_type = self.current_token[1]
            self.next_token()  # Move past type
            
            # Skip spaces
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
            
            # Get parameter name
            if self.current_token is None or self.current_token[1] != 'Identifier':
                self.errors.append(f"Semantic Error: Expected identifier for function parameter, found {self.current_token}")
                # Skip to next comma or closing parenthesis
                while self.current_token is not None and self.current_token[0] != ',' and self.current_token[0] != ')':
                    self.next_token()
                continue
                
            param_name = self.current_token[0]
            
            # Add parameter to list
            parameters.append({
                'name': param_name,
                'type': param_type
            })
            
            self.next_token()  # Move past parameter name
            
            # Look for comma or closing parenthesis
            if self.current_token is None:
                self.errors.append("Semantic Error: Unexpected end of tokens in function parameters")
                return
                
            if self.current_token[0] != ',' and self.current_token[0] != ')':
                self.errors.append(f"Semantic Error: Expected ',' or ')' in function parameters, found {self.current_token}")
                # Skip to next comma or closing parenthesis
                while self.current_token is not None and self.current_token[0] != ',' and self.current_token[0] != ')':
                    self.next_token()
        
        # Check for closing parenthesis
        if self.current_token is None or self.current_token[0] != ')':
            self.errors.append(f"Semantic Error: Expected ')' after function parameters, found {self.current_token}")
            return
            
        self.next_token()  # Move past ')'
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
        
        # Check for opening brace
        if self.current_token is None or self.current_token[0] != '{':
            self.errors.append(f"Semantic Error: Expected '{{' after function header, found {self.current_token}")
            return
            
        # Save function info
        self.functions[function_name] = {
            'return_type': return_type,
            'parameters': parameters
        }
        
        # Create new scope for function body
        outer_scope = self.symbol_table.copy()
        
        # Add parameters to symbol table
        for param in parameters:
            self.symbol_table[param['name']] = {
                'type': param['type'],
                'value': get_default_value_for_type(param['type'])
            }
        
        self.next_token()  # Move past '{'
        
        # Parse function body
        self.parse_body_statements()
        
        # Check for closing brace
        if self.current_token is None or self.current_token[0] != '}':
            self.errors.append(f"Semantic Error: Expected '}}' at end of function block, found {self.current_token}")
            return
            
        self.next_token()  # Move past '}'
        
        # Restore outer scope
        self.symbol_table = outer_scope
            
    def check_variable_usage(self):
        """Check if the identifier has been declared before use"""
        var_name = self.current_token[0]
        if var_name not in self.symbol_table:
            self.errors.append(f"Semantic Error: Variable '{var_name}' used before declaration")
        
        self.next_token()  # Move past identifier
        
        # Look for assignment operator
        if self.current_token is not None and self.current_token[0] == '=':
            self.next_token()  # Move past '='
            # Parse right side of assignment
            self.expr()
        
        # Check for semicolon
        while self.current_token is not None and self.current_token[1] != ';':
            self.next_token()
            
        if self.current_token is not None and self.current_token[0] == ';':
            self.next_token()  # Move past semicolon
        
    def declaration(self):
        print("DEBUG: Entering declaration method")
        
        # Check for variable scope
        var_scope = 'local'  # Default scope
        
        # If current token is _L or _G, set scope accordingly
        if self.current_token is not None and (self.current_token[0] == '_L' or self.current_token[0] == '_G'):
            var_scope = 'local' if self.current_token[0] == '_L' else 'global'
            print(f"DEBUG: Detected scope: {var_scope}")
            self.next_token()  # Move past scope token
            
            # Skip spaces after scope token
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
        
        # Check for array declaration (clust keyword)
        is_array = False
        if self.current_token is not None and self.current_token[1] == 'clust':
            is_array = True
            print("DEBUG: Detected array declaration (clust keyword)")
            self.next_token()  # Move past 'clust'
            
            # Skip spaces after clust keyword
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
                    
        # Now get the data type
        if self.current_token is None or self.current_token[1] not in ['dose', 'quant', 'seq', 'allele']:
            self.errors.append(f"Semantic Error: Expected data type, found {self.current_token}")
            print(f"DEBUG: Error - Invalid data type: {self.current_token}")
            return
                
        var_type = self.current_token[1]
        print(f"DEBUG: Detected type: {var_type}")
        self.next_token()  # Move past type

        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
        
        # Process variables (potentially multiple in a single line)
        while True:
            # Get variable name
            if self.current_token is None or self.current_token[1] != 'Identifier':
                self.errors.append(f"Semantic Error: Expected identifier after type declaration, found {self.current_token}")
                print(f"DEBUG: Error - Invalid identifier: {self.current_token}")
                return

            var_name = self.current_token[0]
            print(f"DEBUG: Detected variable name: {var_name}")
            
            # Check for redeclaration
            if var_name in self.symbol_table:
                self.errors.append(f"Semantic Error: Variable '{var_name}' already declared")
                print(f"DEBUG: Error - Variable redeclaration: {var_name}")
                # Continue to next variable instead of returning
                self.next_token()  # Move past identifier
                
                # Skip to comma or semicolon
                while (self.current_token is not None and 
                    self.current_token[0] != ',' and 
                    self.current_token[0] != ';'):
                    self.next_token()
                    
                # If we found a comma, continue to next variable
                if self.current_token is not None and self.current_token[0] == ',':
                    self.next_token()  # Move past comma
                    # Skip spaces after comma
                    while self.current_token is not None and self.current_token[1] == 'space':
                        self.next_token()
                    continue
                # If we found a semicolon, end declaration
                elif self.current_token is not None and self.current_token[0] == ';':
                    self.next_token()  # Move past semicolon
                    return
                else:
                    return  # End of tokens
            
            self.next_token()  # Move past identifier

            # Set default value based on type
            if var_type == 'dose':
                default_value = 0
            elif var_type == 'quant':
                default_value = 0.0
            elif var_type == 'seq':
                default_value = ""
            elif var_type == 'allele':
                default_value = False
            else:
                default_value = None
            
            print(f"DEBUG: Default value for type {var_type}: {default_value}")
            
            # Check for array size declaration [size][size]...
            declared_sizes = []
            if is_array:
                while self.current_token is not None and self.current_token[0] == '[':
                    print(f"DEBUG: Processing dimension {len(declared_sizes)+1} size declaration")
                    self.next_token()  # Move past '['
                    
                    # Get size value
                    if self.current_token is None or self.current_token[1] != 'numlit' or '.' in self.current_token[0]:
                        self.errors.append(f"Semantic Error: Expected integer value for array size, found {self.current_token}")
                        print(f"DEBUG: Error - Invalid array size: {self.current_token}")
                        return
                        
                    try:
                        size = int(self.current_token[0])
                        print(f"DEBUG: Array dimension {len(declared_sizes)+1} size: {size}")
                        if size <= 0:
                            self.errors.append(f"Semantic Error: Array size must be positive, found {size}")
                            print(f"DEBUG: Error - Non-positive array size: {size}")
                        declared_sizes.append(size)
                    except:
                        self.errors.append(f"Semantic Error: Invalid array size {self.current_token[0]}")
                        print(f"DEBUG: Error - Cannot convert array size to integer: {self.current_token[0]}")
                        return
                        
                    self.next_token()  # Move past size value
                    
                    # Check for closing bracket
                    if self.current_token is None or self.current_token[0] != ']':
                        self.errors.append(f"Semantic Error: Expected ']' after array size, found {self.current_token}")
                        print(f"DEBUG: Error - Missing closing bracket after array size: {self.current_token}")
                        return
                        
                    self.next_token()  # Move past ']'

                # Determine array dimensions
                dimensions = len(declared_sizes)
                print(f"DEBUG: Array has {dimensions} dimensions with sizes: {declared_sizes}")
            
            # Add to symbol table with multi-dimensional support
            if is_array:
                print(f"DEBUG: Adding array '{var_name}' to symbol table with element type {var_type} and sizes {declared_sizes}")
                self.symbol_table[var_name] = {
                    'scope': var_scope,
                    'type': f'array_{var_type}',
                    'value': [],
                    'element_type': var_type,
                    'dimensions': len(declared_sizes),
                    'sizes': declared_sizes
                }
            else:
                print(f"DEBUG: Adding variable '{var_name}' to symbol table with type {var_type}")
                self.symbol_table[var_name] = {
                    'scope': var_scope,
                    'type': var_type,
                    'value': default_value
                }
            
            # Check for assignment with multi-dimensional array support and type checking
            if self.current_token is not None and self.current_token[0] == '=':
                print("DEBUG: Detected assignment operator")
                self.next_token()  # Move past '='
                
                if is_array:
                    # Handle array initialization with multi-dimensional support
                    print("DEBUG: Processing array initialization")
                    
                    # Define a recursive function to parse nested arrays
                    def parse_array_level(level = 1, expected_size=None):
                        print(f"DEBUG: Parsing array level {level} (expected size: {expected_size})")
                        elements = []
                        
                        # Check for opening brace
                        if self.current_token is None or self.current_token[0] != '{':
                            self.errors.append(f"Semantic Error: Expected '{{' for array initialization at level {level}, found {self.current_token}")
                            print(f"DEBUG: Error - Missing opening brace for array level {level}: {self.current_token}")
                            return []
                            
                        self.next_token()  # Move past '{'
                        
                        # Parse elements at this level
                        while self.current_token is not None and self.current_token[0] != '}':
                            # Skip spaces and commas
                            while self.current_token is not None and (self.current_token[1] == 'space' or self.current_token[0] == ','):
                                self.next_token()
                                
                            if self.current_token is None or self.current_token[0] == '}':
                                break
                                
                            # If we're not at the deepest level, parse a nested array
                            if level < len(declared_sizes) - 1:
                                nested_elements = parse_array_level(level + 1, declared_sizes[level + 1] if level + 1 < len(declared_sizes) else None)
                                elements.append(nested_elements)
                                print(f"DEBUG: Added nested array with {len(nested_elements)} elements at level {level}")
                            else:
                                # We're at the deepest level, parse individual elements
                                print(f"DEBUG: Processing array element at level {level}: {self.current_token}")
                                
                                # Check element type (similar to before)
                                if var_type == 'dose' and (self.current_token[1] != 'numlit' or '.' in self.current_token[0]):
                                    self.errors.append(f"Semantic Error: Expected integer value for dose array element, found {self.current_token}")
                                    print(f"DEBUG: Error - Invalid dose array element: {self.current_token}")
                                elif var_type == 'quant' and self.current_token[1] != 'numlit':
                                    self.errors.append(f"Semantic Error: Expected numeric value for quant array element, found {self.current_token}")
                                    print(f"DEBUG: Error - Invalid quant array element: {self.current_token}")
                                elif var_type == 'seq' and self.current_token[1] != 'string literal':
                                    self.errors.append(f"Semantic Error: Expected string value for seq array element, found {self.current_token}")
                                    print(f"DEBUG: Error - Invalid seq array element: {self.current_token}")
                                elif var_type == 'allele' and self.current_token[0] not in ['dom', 'rec']:
                                    self.errors.append(f"Semantic Error: Expected 'dom' or 'rec' for allele array element, found {self.current_token}")
                                    print(f"DEBUG: Error - Invalid allele array element: {self.current_token}")
                                
                                # Store element (raw value as requested)
                                value = self.current_token[0]
                                elements.append(value)
                                print(f"DEBUG: Added {var_type} element (raw): {value}")
                                
                                self.next_token()  # Move past element
                            
                            # Look for comma or closing brace
                            if self.current_token is None:
                                self.errors.append(f"Semantic Error: Unexpected end of tokens in array initialization at level {level}")
                                print(f"DEBUG: Error - Unexpected end of tokens in array level {level}")
                                return elements
                                
                            if self.current_token[0] != ',' and self.current_token[0] != '}':
                                self.errors.append(f"Semantic Error: Expected ',' or '}}' in array initialization at level {level}, found {self.current_token}")
                                print(f"DEBUG: Error - Expected comma or closing brace at level {level}: {self.current_token}")
                        
                        # Check for size mismatch at this level
                        if expected_size is not None and len(elements) != expected_size:
                            self.errors.append(f"Semantic Error: Array at level {level} expected to have {expected_size} elements but has {len(elements)}")
                            print(f"DEBUG: Error - Size mismatch at level {level}: expected {expected_size}, got {len(elements)}")
                        
                        # Check for closing brace
                        if self.current_token is None or self.current_token[0] != '}':
                            self.errors.append(f"Semantic Error: Expected '}}' at end of array level {level}, found {self.current_token}")
                            print(f"DEBUG: Error - Missing closing brace at end of array level {level}: {self.current_token}")
                            return elements
                            
                        print(f"DEBUG: Found closing brace for array level {level}")
                        self.next_token()  # Move past '}'
                        
                        return elements

                    # Start parsing from the outermost level
                    all_elements = parse_array_level(0, declared_sizes[0] if declared_sizes else None)
                    
                    # Update symbol table with elements
                    self.symbol_table[var_name]['value'] = all_elements
                    print(f"DEBUG: Updated symbol table for array '{var_name}' with multi-dimensional array")
                    print(f"DEBUG: Symbol table entry after update: {self.symbol_table[var_name]}")
                    
                else:
                    # Handle regular variable assignment with type checking
                    print("DEBUG: Processing regular variable assignment")
                    
                    # Check if the right-hand side is an identifier (variable)
                    if self.current_token is not None and self.current_token[1] == 'Identifier':
                        rhs_var_name = self.current_token[0]
                        print(f"DEBUG: Assignment from variable: {rhs_var_name}")
                        
                        # Check if the variable exists in the symbol table
                        if rhs_var_name not in self.symbol_table:
                            self.errors.append(f"Semantic Error: Variable '{rhs_var_name}' used before declaration")
                            print(f"DEBUG: Error - Variable used before declaration: {rhs_var_name}")
                        else:
                            # Get the type of the right-hand side variable
                            rhs_var_info = self.symbol_table[rhs_var_name]
                            rhs_type = rhs_var_info['type']
                            print(f"DEBUG: RHS variable type: {rhs_type}")
                            
                            # Type compatibility check
                            if var_type == 'dose':
                                # dose can only be assigned from dose
                                if rhs_type != 'dose':
                                    self.errors.append(f"Semantic Error: Cannot assign {rhs_type} to dose variable '{var_name}'")
                                    print(f"DEBUG: Error - Type mismatch: Cannot assign {rhs_type} to dose")
                            elif var_type == 'quant':
                                # quant can be assigned from dose or quant
                                if rhs_type not in ['dose', 'quant']:
                                    self.errors.append(f"Semantic Error: Cannot assign {rhs_type} to quant variable '{var_name}'")
                                    print(f"DEBUG: Error - Type mismatch: Cannot assign {rhs_type} to quant")
                            elif var_type == 'seq':
                                # seq can only be assigned from seq
                                if rhs_type != 'seq':
                                    self.errors.append(f"Semantic Error: Cannot assign {rhs_type} to seq variable '{var_name}'")
                                    print(f"DEBUG: Error - Type mismatch: Cannot assign {rhs_type} to seq")
                            elif var_type == 'allele':
                                # allele can only be assigned from allele
                                if rhs_type != 'allele':
                                    self.errors.append(f"Semantic Error: Cannot assign {rhs_type} to allele variable '{var_name}'")
                                    print(f"DEBUG: Error - Type mismatch: Cannot assign {rhs_type} to allele")
                            
                            # If array type, check compatibility
                            if rhs_type.startswith('array_'):
                                self.errors.append(f"Semantic Error: Cannot assign array to non-array variable '{var_name}'")
                                print(f"DEBUG: Error - Type mismatch: Cannot assign array to non-array variable")
                            
                            # Update the symbol table with the value from the RHS variable
                            self.symbol_table[var_name]['value'] = rhs_var_info['value']
                            print(f"DEBUG: Assigned value from variable '{rhs_var_name}' to '{var_name}'")
                        
                        self.next_token()  # Move past identifier
                    else:
                        # For seq type, expect string literal
                        if var_type == 'seq' and (self.current_token is None or self.current_token[1] != 'string literal'):
                            self.errors.append(f"Semantic Error: Expected string literal for seq variable '{var_name}'")
                            print(f"DEBUG: Error - Invalid value for seq variable: {self.current_token}")
                        
                            
                        # For quant type, expect float
                        elif var_type == 'quant' and (self.current_token is None or self.current_token[1] != 'numlit' or self.current_token[1] != '('):
                            self.errors.append(f"Semantic Error: Expected numeric value for quant variable '{var_name}'")
                            print(f"DEBUG: Error - Invalid value for quant variable: {self.current_token}")
                            
                        # For allele type, expect dom or rec
                        elif var_type == 'allele' and (self.current_token is None or self.current_token[0] not in ['dom', 'rec']):
                            self.errors.append(f"Semantic Error: Expected 'dom' or 'rec' for allele variable '{var_name}'")
                            print(f"DEBUG: Error - Invalid value for allele variable: {self.current_token}")
                            
                        # Store assigned value
                        if self.current_token is not None:
                            print(f"DEBUG: Assigning value to variable '{var_name}': {self.current_token}")
                            # Update the symbol table with the actual value
                            if var_type == 'dose':
                                try:
                                    value = int(self.current_token[0])
                                    self.symbol_table[var_name]['value'] = value
                                    print(f"DEBUG: Assigned dose value: {value}")
                                except:
                                    self.errors.append(f"Semantic Error: Cannot convert {self.current_token[0]} to integer for dose variable '{var_name}'")
                                    print(f"DEBUG: Error - Failed to convert to integer: {self.current_token[0]}")
                                    
                            elif var_type == 'quant':
                                try:
                                    value = float(self.current_token[0])
                                    self.symbol_table[var_name]['value'] = value
                                    print(f"DEBUG: Assigned quant value: {value}")
                                except:
                                    self.errors.append(f"Semantic Error: Cannot convert {self.current_token[0]} to float for quant variable '{var_name}'")
                                    print(f"DEBUG: Error - Failed to convert to float: {self.current_token[0]}")
                                    
                            elif var_type == 'seq':
                                # Remove quotation marks
                                string_val = self.current_token[0].strip('"\'')
                                self.symbol_table[var_name]['value'] = string_val
                                print(f"DEBUG: Assigned seq value: {string_val}")
                                
                            elif var_type == 'allele':
                                boolean_val = (self.current_token[0] == 'dom')
                                self.symbol_table[var_name]['value'] = boolean_val
                                print(f"DEBUG: Assigned allele value: {boolean_val} ({self.current_token[0]})")
                    
                    self.next_token()  # Move past value
            elif is_array and declared_sizes:
                # Default initialization for multi-dimensional arrays
                def create_default_array(level):
                    if level >= len(declared_sizes) - 1:
                        # At the deepest level, create an array of default values
                        return [default_value] * declared_sizes[level]
                    else:
                        # At higher levels, create nested arrays
                        return [create_default_array(level + 1) for _ in range(declared_sizes[level])]
                
                # Initialize with nested default values
                default_array = create_default_array(0)
                self.symbol_table[var_name]['value'] = default_array
                print(f"DEBUG: Initialized multi-dimensional array '{var_name}' with default values")
            
            # Check for comma (multiple variables) or semicolon (end of declaration)
            # Skip spaces
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
                
            # Check for comma or semicolon
            if self.current_token is None:
                print("DEBUG: Unexpected end of tokens in declaration")
                return
                
            if self.current_token[0] == ',':
                print("DEBUG: Found comma, processing next variable")
                self.next_token()  # Move past comma
                
                # Skip spaces after comma
                while self.current_token is not None and self.current_token[1] == 'space':
                    self.next_token()
                    
                # Continue to process next variable
                continue
                
            elif self.current_token[0] == ';':
                print("DEBUG: Found semicolon at end of declaration")
                self.next_token()  # Move past semicolon
                return
                
            else:
                print(f"DEBUG: Warning - Expected comma or semicolon, found: {self.current_token}")
                # Continue parsing until semicolon
                while self.current_token is not None and self.current_token[0] != ';':
                    self.next_token()
                    
                if self.current_token is not None and self.current_token[0] == ';':
                    print("DEBUG: Found semicolon at end of declaration")
                    self.next_token()  # Move past semicolon
                else:
                    print(f"DEBUG: Warning - Missing semicolon at end of declaration: {self.current_token}")
                
                return
                
        print(f"DEBUG: Completed declaration statement")
        
    def if_statement(self):
        """Parse if statement, checking condition and body"""
        self.next_token()  # Move past 'if'
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
            
        # Check for opening parenthesis
        if self.current_token is None or self.current_token[0] != '(':
            self.errors.append(f"Semantic Error: Expected '(' after 'if', found {self.current_token}")
            return
            
        self.next_token()  # Move past '('
        
        # Parse condition
        self.parse_condition()
        
        # Check for closing parenthesis
        if self.current_token is None or self.current_token[0] != ')':
            self.errors.append(f"Semantic Error: Expected ')' after condition, found {self.current_token}")
            return
            
        self.next_token()  # Move past ')'
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
        
        # Check for opening brace
        if self.current_token is None or self.current_token[0] != '{':
            self.errors.append(f"Semantic Error: Expected '{{' after if condition, found {self.current_token}")
            return
            
        self.next_token()  # Move past '{'
        
        # Parse if body
        self.parse_body_statements()
        
        # Check for closing brace
        if self.current_token is None or self.current_token[0] != '}':
            self.errors.append(f"Semantic Error: Expected '}}' at end of if block, found {self.current_token}")
            return
            
        self.next_token()  # Move past '}'
        
        # Check for elif or else
        if self.current_token is not None and self.current_token[1] == 'elif':
            self.elif_statement()
        elif self.current_token is not None and self.current_token[1] == 'else':
            self.else_statement()

    def elif_statement(self):
        """Parse elif statement, similar to if statement"""
        self.next_token()  # Move past 'elif'
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
            
        # Check for opening parenthesis
        if self.current_token is None or self.current_token[0] != '(':
            self.errors.append(f"Semantic Error: Expected '(' after 'elif', found {self.current_token}")
            return
            
        self.next_token()  # Move past '('
        
        # Parse condition
        self.parse_condition()
        
        # Check for closing parenthesis
        if self.current_token is None or self.current_token[0] != ')':
            self.errors.append(f"Semantic Error: Expected ')' after condition, found {self.current_token}")
            return
            
        self.next_token()  # Move past ')'
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
        
        # Check for opening brace
        if self.current_token is None or self.current_token[0] != '{':
            self.errors.append(f"Semantic Error: Expected '{{' after elif condition, found {self.current_token}")
            return
            
        self.next_token()  # Move past '{'
        
        # Parse elif body
        self.parse_body_statements()
        
        # Check for closing brace
        if self.current_token is None or self.current_token[0] != '}':
            self.errors.append(f"Semantic Error: Expected '}}' at end of elif block, found {self.current_token}")
            return
            
        self.next_token()  # Move past '}'
        
        # Check for another elif or else
        if self.current_token is not None and self.current_token[1] == 'elif':
            self.elif_statement()
        elif self.current_token is not None and self.current_token[1] == 'else':
            self.else_statement()

    def else_statement(self):
        """Parse else statement"""
        self.next_token()  # Move past 'else'
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
        
        # Check for opening brace
        if self.current_token is None or self.current_token[0] != '{':
            self.errors.append(f"Semantic Error: Expected '{{' after else, found {self.current_token}")
            return
            
        self.next_token()  # Move past '{'
        
        # Parse else body
        self.parse_body_statements()
        
        # Check for closing brace
        if self.current_token is None or self.current_token[0] != '}':
            self.errors.append(f"Semantic Error: Expected '}}' at end of else block, found {self.current_token}")
            return
            
        self.next_token()  # Move past '}'

    def parse_condition(self):
        """Parse a condition, checking operands and operator compatibility"""
        # Left operand
        left_operand = None
        left_type = None
        
        if self.current_token is not None:
            if self.current_token[1] == 'Identifier':
                var_name = self.current_token[0]
                if var_name in self.symbol_table:
                    left_operand = self.symbol_table[var_name]['value']
                    left_type = self.symbol_table[var_name]['type']
                else:
                    self.errors.append(f"Semantic Error: Variable '{var_name}' used in condition before declaration")
            elif self.current_token[1] == 'numlit':
                if '.' in self.current_token[0]:
                    left_operand = float(self.current_token[0])
                    left_type = 'quant'
                else:
                    left_operand = int(self.current_token[0])
                    left_type = 'dose'
            elif self.current_token[1] == 'string literal':
                left_operand = self.current_token[0].strip('"\'')
                left_type = 'seq'
            elif self.current_token[0] in ['dom', 'rec']:
                left_operand = (self.current_token[0] == 'dom')
                left_type = 'allele'
        
        self.next_token()  # Move past left operand
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
        
        # Operator
        operator = None
        if self.current_token is not None:
            operator = self.current_token[0]
            if operator not in ['<', '>', '<=', '>=', '==', '!=']:
                self.errors.append(f"Semantic Error: Invalid comparison operator '{operator}' in condition")
                
        self.next_token()  # Move past operator
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
        
        # Right operand
        right_operand = None
        right_type = None
        
        if self.current_token is not None:
            if self.current_token[1] == 'Identifier':
                var_name = self.current_token[0]
                if var_name in self.symbol_table:
                    right_operand = self.symbol_table[var_name]['value']
                    right_type = self.symbol_table[var_name]['type']
                else:
                    self.errors.append(f"Semantic Error: Variable '{var_name}' used in condition before declaration")
            elif self.current_token[1] == 'numlit':
                if '.' in self.current_token[0]:
                    right_operand = float(self.current_token[0])
                    right_type = 'quant'
                else:
                    right_operand = int(self.current_token[0])
                    right_type = 'dose'
            elif self.current_token[1] == 'string literal':
                right_operand = self.current_token[0].strip('"\'')
                right_type = 'seq'
            elif self.current_token[0] in ['dom', 'rec']:
                right_operand = (self.current_token[0] == 'dom')
                right_type = 'allele'
                
        self.next_token()  # Move past right operand
        
        # Type checking
        if left_type is not None and right_type is not None and left_type != right_type:
            self.errors.append(f"Semantic Error: Type mismatch in condition: {left_type} {operator} {right_type}")
            
        # Operator checking for specific types
        if operator in ['<', '>', '<=', '>='] and left_type in ['seq', 'allele']:
            self.errors.append(f"Semantic Error: Operator '{operator}' cannot be used with {left_type} type")

    def for_loop_statement(self):
        """Parse for loop statement and check semantic validity"""
        self.next_token()  # Move past 'for'
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
        
        # Check for opening parenthesis
        if self.current_token is None or self.current_token[0] != '(':
            self.errors.append(f"Semantic Error: Expected '(' after 'for', found {self.current_token}")
            return
            
        self.next_token()  # Move past '('
        
        # Save current symbol table state to isolate loop variables
        outer_scope = self.symbol_table.copy()
        
        # Initialization part
        if self.current_token is not None and self.current_token[1] == 'dose':
            self.declaration()  # This will handle the first part of the for loop
        else:
            self.errors.append(f"Semantic Error: Expected 'dose' declaration as for loop initialization, found {self.current_token}")
            # Skip until semicolon
            while self.current_token is not None and self.current_token[0] != ';':
                self.next_token()
            self.next_token()  # Move past ';'
            
        # Condition part       
        self.next_token()  # Move past ';'
        
        # Update part - should be an increment/decrement expression
        if self.current_token is not None and self.current_token[1] == 'Identifier':
            var_name = self.current_token[0]
            if var_name not in self.symbol_table:
                self.errors.append(f"Semantic Error: Variable '{var_name}' used in for loop update before declaration")
            else:
                var_type = self.symbol_table[var_name]['type']
                if var_type != 'dose':
                    self.errors.append(f"Semantic Error: For loop update variable must be dose type, found {var_type}")
                                
        else:
            self.errors.append(f"Semantic Error: Expected identifier in for loop update, found {self.current_token}")
            
        # Skip until closing parenthesis
        while self.current_token is not None and self.current_token[0] != ')':
            self.next_token()
            
        if self.current_token is None or self.current_token[0] != ')':
            self.errors.append(f"Semantic Error: Expected ')' after for loop update, found {self.current_token}")
            return
            
        self.next_token()  # Move past ')'
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
        
        # Check for opening brace
        if self.current_token is None or self.current_token[0] != '{':
            self.errors.append(f"Semantic Error: Expected '{{' after for loop header, found {self.current_token}")
            return
            
        self.next_token()  # Move past '{'
        
        # Parse for loop body
        self.parse_body_statements()
        
        # Check for closing brace
        if self.current_token is None or self.current_token[0] != '}':
            self.errors.append(f"Semantic Error: Expected '}}' at end of for loop block, found {self.current_token}")
            return
            
        self.next_token()  # Move past '}'
        
        # Restore outer scope (remove loop-specific variables)
        self.symbol_table = outer_scope

    def while_statement(self):
        """Parse while loop statement and check semantic validity"""
        self.next_token()  # Move past 'while'
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
        
        # Check for opening parenthesis
        if self.current_token is None or self.current_token[0] != '(':
            self.errors.append(f"Semantic Error: Expected '(' after 'while', found {self.current_token}")
            return
            
        self.next_token()  # Move past '('
        
        # Parse condition
        self.parse_condition()
        
        # Check for closing parenthesis
        if self.current_token is None or self.current_token[0] != ')':
            self.errors.append(f"Semantic Error: Expected ')' after while condition, found {self.current_token}")
            return
            
        self.next_token()  # Move past ')'
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
        
        # Check for opening brace
        if self.current_token is None or self.current_token[0] != '{':
            self.errors.append(f"Semantic Error: Expected '{{' after while condition, found {self.current_token}")
            return
            
        self.next_token()  # Move past '{'
        
        # Parse while loop body
        self.parse_body_statements()
        
        # Check for closing brace
        if self.current_token is None or self.current_token[0] != '}':
            self.errors.append(f"Semantic Error: Expected '}}' at end of while loop block, found {self.current_token}")
            return
            
        self.next_token()  # Move past '}'

    def do_while_statement(self):
        """Parse do-while statement and check semantic validity"""
        self.next_token()  # Move past 'do'
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
        
        # Check for opening brace
        if self.current_token is None or self.current_token[0] != '{':
            self.errors.append(f"Semantic Error: Expected '{{' after 'do', found {self.current_token}")
            return
            
        self.next_token()  # Move past '{'
        
        # Parse do-while body
        self.parse_body_statements()
        
        # Check for closing brace
        if self.current_token is None or self.current_token[0] != '}':
            self.errors.append(f"Semantic Error: Expected '}}' after do block, found {self.current_token}")
            return
            
        self.next_token()  # Move past '}'
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
        
        # Check for 'while'
        if self.current_token is None or self.current_token[1] != 'while':
            self.errors.append(f"Semantic Error: Expected 'while' after do block, found {self.current_token}")
            return
            
        self.next_token()  # Move past 'while'
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
        
        # Check for opening parenthesis
        if self.current_token is None or self.current_token[0] != '(':
            self.errors.append(f"Semantic Error: Expected '(' after 'while', found {self.current_token}")
            return
            
        self.next_token()  # Move past '('
        
        # Parse condition
        self.parse_condition()
        
        # Check for closing parenthesis
        if self.current_token is None or self.current_token[0] != ')':
            self.errors.append(f"Semantic Error: Expected ')' after do-while condition, found {self.current_token}")
            return
            
        self.next_token()  # Move past ')'
        
        # Check for semicolon
        if self.current_token is None or self.current_token[0] != ';':
            self.errors.append(f"Semantic Error: Expected ';' after do-while statement, found {self.current_token}")
            return
            
        self.next_token()  # Move past ';'

    def express_statement(self):
        """Parse express statement (print statement)"""
        self.next_token()  # Move past 'express'
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
        
        # Check for opening parenthesis
        if self.current_token is None or self.current_token[0] != '(':
            self.errors.append(f"Semantic Error: Expected '(' after 'express', found {self.current_token}")
            return
            
        self.next_token()  # Move past '('
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
        
        # Check for variable identifier or literal
        if self.current_token is None:
            self.errors.append("Semantic Error: Unexpected end of tokens in express statement")
            return
        
        # Store the value to print
        value_to_print = None
        if self.current_token[1] == 'Identifier':
            var_name = self.current_token[0]
            if var_name not in self.symbol_table:
                self.errors.append(f"Semantic Error: Variable '{var_name}' used in express statement before declaration")
            else:
                # Get the value from the symbol table for printing
                value_to_print = self.symbol_table[var_name]['value']
                # Add to symbol table special 'express_output' key to store what should be printed
                self.symbol_table['express_output'] = {'type': 'output', 'value': value_to_print}
        elif self.current_token[1] in ['string literal', 'numlit']:
            # For literals, just store the literal value
            value_to_print = self.current_token[0]
            self.symbol_table['express_output'] = {'type': 'output', 'value': value_to_print}
        elif self.current_token[0] in ['dom', 'rec']:
            # For boolean literals
            value_to_print = self.current_token[0]
            self.symbol_table['express_output'] = {'type': 'output', 'value': value_to_print}
        else:
            self.errors.append(f"Semantic Error: Expected identifier or literal in express statement, found {self.current_token}")
                
        self.next_token()  # Move past identifier/literal
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
        
        # Check for closing parenthesis
        if self.current_token is None or self.current_token[0] != ')':
            self.errors.append(f"Semantic Error: Expected ')' in express statement, found {self.current_token}")
            return
            
        self.next_token()  # Move past ')'
        
        # Check for semicolon
        if self.current_token is None or self.current_token[0] != ';':
            self.errors.append(f"Semantic Error: Expected ';' after express statement, found {self.current_token}")
            return
            
        self.next_token()  # Move past ';'
    
    def assignment_stmt(self):
        """Parse an assignment statement"""
        print(f"DEBUG: Entering assignment_stmt() method. Current token: {self.current_token}")
        
        if self.current_token is None:
            print("DEBUG: Unexpected end of tokens in assignment statement")
            self.errors.append("Semantic Error: Unexpected end of tokens in assignment statement")
            return
        
        # Get the variable being assigned to
        if self.current_token[1] != 'Identifier':
            print(f"DEBUG: Expected identifier at start of assignment, found: {self.current_token}")
            self.errors.append(f"Semantic Error: Expected identifier at start of assignment, found: {self.current_token}")
            return
        
        var_name = self.current_token[0]
        print(f"DEBUG: Assignment to variable: {var_name}")
        
        # Check if variable is declared
        if var_name not in self.symbol_table:
            print(f"DEBUG: Variable '{var_name}' used before declaration")
            self.errors.append(f"Semantic Error: Variable '{var_name}' used in assignment before declaration")
            return
        
        # Get the type of the variable being assigned to
        left_type = self.symbol_table[var_name]['type']
        print(f"DEBUG: Variable '{var_name}' has type '{left_type}'")
        
        self.next_token()  # Move past identifier
        
        # Check for equals sign
        if self.current_token is None or self.current_token[0] != '=':
            print(f"DEBUG: Expected '=' in assignment, found: {self.current_token}")
            self.errors.append(f"Semantic Error: Expected '=' in assignment, found: {self.current_token}")
            return
        
        self.next_token()  # Move past equals sign
        
        # Parse the right-hand side expression
        print("DEBUG: Parsing right-hand side expression")
        right_expr, right_type = self.expr()
        
        # Check if the assignment is type-compatible
        if not self.is_valid_assignment(left_type, right_type):
            error_msg = f"Semantic Error: Cannot assign expression of type '{right_type}' to variable '{var_name}' of type '{left_type}'"
            self.errors.append(error_msg)
            print(f"DEBUG: {error_msg}")
            
            # Add more detailed explanation for specific cases
            if left_type == 'seq' and right_type in ['dose', 'quant']:
                detail_msg = f"Type Error: Cannot assign numeric value to sequence variable '{var_name}'"
                self.errors.append(detail_msg)
                print(f"DEBUG: {detail_msg}")
        else:
            print(f"DEBUG: Valid assignment of '{right_type}' expression to '{var_name}' ({left_type})")
        
        # Check for semicolon
        if self.current_token is None or self.current_token[0] != ';':
            print(f"DEBUG: Expected ';' at end of assignment, found: {self.current_token}")
            self.errors.append(f"Semantic Error: Expected ';' at end of assignment, found: {self.current_token}")
            return
        
        self.next_token()  # Move past semicolon
        print("DEBUG: Exiting assignment_stmt() method")

    def is_valid_assignment(self, left_type, right_type):
        """Check if an assignment is valid based on the types"""
        # Rule: Types must match exactly for assignment
        # seq can only be assigned seq
        # dose can only be assigned dose
        # quant can only be assigned quant
        # bool can only be assigned bool
        return left_type == right_type

    def expr(self):
        """Parse an expression, which could be a variable, literal, or operation"""
        # Debug: Start of expression parsing
        print(f"DEBUG: Entering expr() method. Current token: {self.current_token}")
        
        if self.current_token is None:
            print("DEBUG: Unexpected end of tokens in expression")
            self.errors.append("Semantic Error: Unexpected end of tokens in expression")
            return None, None  # Return None for operand and type
            
        expr_type = None  # Track the type of this expression
        
        # Variable
        if self.current_token[1] == 'Identifier':
            var_name = self.current_token[0]
            print(f"DEBUG: Identifier found: {var_name}")
            
            if var_name not in self.symbol_table:
                print(f"DEBUG: Variable '{var_name}' used before declaration")
                self.errors.append(f"Semantic Error: Variable '{var_name}' used in expression before declaration")
                expr_type = None  # Unknown type for undeclared variable
            else:
                # Get the type from symbol table
                expr_type = self.symbol_table[var_name]['type']
                print(f"DEBUG: Variable '{var_name}' has type '{expr_type}'")
            
            self.next_token()  # Move past identifier
            
            # Check for operation
            if self.current_token is not None and self.current_token[0] in ['+', '-', '*', '/', '%']:
                operator = self.current_token[0]
                print(f"DEBUG: Operator found after identifier: {operator}")
                self.next_token()  # Move past operator
                
                # Store the left operand name and type for error reporting
                left_operand = var_name
                left_type = expr_type
                
                # Parse right side of operation
                print("DEBUG: Parsing right side of operation")
                right_operand, right_type = self.expr()
                
                # Validate operation based on types
                if left_type and right_type:
                    if not self.is_valid_operation(left_type, right_type, operator):
                        error_msg = f"Semantic Error: Invalid operation '{operator}' between '{left_operand}' ({left_type}) and '{right_operand}' ({right_type})"
                        self.errors.append(error_msg)
                        print(f"DEBUG: {error_msg}")
                        
                        # Add more detailed explanation for specific cases
                        if left_type == 'seq' and right_type in ['dose', 'quant']:
                            detail_msg = f"Type Error: Cannot perform arithmetic between sequence and numeric types"
                            self.errors.append(detail_msg)
                            print(f"DEBUG: {detail_msg}")
                        
                        # Return the left operand and type as fallback
                        return left_operand, left_type
                    else:
                        print(f"DEBUG: Valid operation '{operator}' between '{left_operand}' ({left_type}) and '{right_operand}' ({right_type})")
                        # Determine result type of the operation
                        result_type = self.result_type(left_type, right_type, operator)
                        print(f"DEBUG: Result type of operation: {result_type}")
                        return f"({left_operand} {operator} {right_operand})", result_type
            else:
                print("DEBUG: No operation after identifier")
            
            return var_name, expr_type
        
        # Number literal
        elif self.current_token[1] == 'numlit':
            literal = self.current_token[0]
            print(f"DEBUG: Number literal found: {literal}")
            
            # Determine the type of the number literal
            number_sign = self.check_number_type(literal)
            if number_sign == 'doseliteral':
                expr_type = 'dose'
            elif number_sign == 'quantval':
                expr_type = 'quant'
            else:
                expr_type = 'dose'  # Default to dose for other number types
                
            print(f"DEBUG: Number literal has type '{expr_type}'")
            
            self.next_token()  # Move past number
            
            # Check for operation
            if self.current_token is not None and self.current_token[0] in ['+', '-', '*', '/', '%']:
                operator = self.current_token[0]
                print(f"DEBUG: Operator found after number literal: {operator}")
                self.next_token()  # Move past operator
                
                # Store the left operand and type for error reporting
                left_operand = literal
                left_type = expr_type
                
                # Parse right side of operation
                print("DEBUG: Parsing right side of operation")
                right_operand, right_type = self.expr()
                
                # Validate operation based on types
                if left_type and right_type:
                    if not self.is_valid_operation(left_type, right_type, operator):
                        error_msg = f"Semantic Error: Invalid operation '{operator}' between '{left_operand}' ({left_type}) and '{right_operand}' ({right_type})"
                        self.errors.append(error_msg)
                        print(f"DEBUG: {error_msg}")
                        # Return the left operand and type as fallback
                        return left_operand, left_type
                    else:
                        print(f"DEBUG: Valid operation '{operator}' between '{left_operand}' ({left_type}) and '{right_operand}' ({right_type})")
                        # Determine result type of the operation
                        result_type = self.result_type(left_type, right_type, operator)
                        print(f"DEBUG: Result type of operation: {result_type}")
                        return f"({left_operand} {operator} {right_operand})", result_type
            else:
                print("DEBUG: No operation after number literal")
            
            return literal, expr_type
        
        # String literal
        elif self.current_token[1] == 'string literal':
            literal = self.current_token[0]
            print(f"DEBUG: String literal found: {literal}")
            expr_type = 'seq'  # String literals are of type 'seq'
            self.next_token()  # Move past string
            
            # Check for concatenation
            if self.current_token is not None and self.current_token[0] == '+':
                print("DEBUG: String concatenation detected")
                self.next_token()  # Move past '+'
                
                # Store the left operand and type for error reporting
                left_operand = literal
                left_type = expr_type
                
                # Parse right side of concatenation
                print("DEBUG: Parsing right side of concatenation")
                right_operand, right_type = self.expr()
                
                # Validate concatenation
                if left_type and right_type:
                    if not self.is_valid_operation(left_type, right_type, '+'):
                        error_msg = f"Semantic Error: Cannot concatenate '{left_operand}' ({left_type}) with '{right_operand}' ({right_type})"
                        self.errors.append(error_msg)
                        print(f"DEBUG: {error_msg}")
                        # Return the left operand and type as fallback
                        return left_operand, left_type
                    else:
                        print(f"DEBUG: Valid concatenation between '{left_operand}' ({left_type}) and '{right_operand}' ({right_type})")
                        # Result of concatenation is still a seq
                        return f"({left_operand} + {right_operand})", 'seq'
            else:
                print("DEBUG: No concatenation after string literal")
            
            return literal, expr_type
        
        # Boolean literal (dom/rec)
        elif self.current_token[0] in ['dom', 'rec']:
            literal = self.current_token[0]
            print(f"DEBUG: Boolean literal found: {literal}")
            expr_type = 'bool'  # Boolean literals are of type 'bool'
            self.next_token()  # Move past boolean
            
            # Check for logical operation
            if self.current_token is not None and self.current_token[0] in ['&&', '||']:
                operator = self.current_token[0]
                print(f"DEBUG: Logical operator found: {operator}")
                self.next_token()  # Move past operator
                
                # Store the left operand and type for error reporting
                left_operand = literal
                left_type = expr_type
                
                # Parse right side of operation
                print("DEBUG: Parsing right side of logical operation")
                right_operand, right_type = self.expr()
                
                # Validate logical operation
                if left_type and right_type:
                    if not self.is_valid_operation(left_type, right_type, operator):
                        error_msg = f"Semantic Error: Cannot perform logical operation '{operator}' between '{left_operand}' ({left_type}) and '{right_operand}' ({right_type})"
                        self.errors.append(error_msg)
                        print(f"DEBUG: {error_msg}")
                        # Return the left operand and type as fallback
                        return left_operand, left_type
                    else:
                        print(f"DEBUG: Valid logical operation between '{left_operand}' ({left_type}) and '{right_operand}' ({right_type})")
                        # Result of logical operation is still a bool
                        return f"({left_operand} {operator} {right_operand})", 'bool'
            else:
                print("DEBUG: No logical operation after boolean literal")
            
            return literal, expr_type
        
        elif self.current_token[1] == 'stimuli':
            literal = self.current_token[0]
            print(f"DEBUG: Stimuli token found: {literal}")
            expr_type = 'stimuli'  # Stimuli tokens have their own type
            self.next_token()  # Move past stimuli token
            
            return literal, expr_type

        else:
            literal = str(self.current_token)
            print(f"DEBUG: Unexpected token in expression: {literal}")
            self.errors.append(f"Semantic Error: Unexpected token in expression: {literal}")
            self.next_token()  # Skip invalid token
            expr_type = None  # Unknown type for unexpected token
            
            return literal, expr_type

    def is_valid_operation(self, left_type, right_type, operator):
        """Check if an operation is valid based on the types of operands"""
        # Arithmetic operations (+, -, *, /, %)
        if operator in ['+', '-', '*', '/', '%']:
            # Rule: seq can only operate with seq
            if left_type == 'seq':
                return right_type == 'seq'  # seq can only operate with seq
            
            # Rule: dose can only operate with dose or quant
            if left_type == 'dose':
                return right_type in ['dose', 'quant']
                
            # Rule: quant can only operate with dose or quant
            if left_type == 'quant':
                return right_type in ['dose', 'quant']
                
            # Special case for division by zero would be handled elsewhere
            
            return False  # Default case for unknown types
            
        # Logical operations (&&, ||)
        elif operator in ['&&', '||']:
            # Both operands must be boolean
            return left_type == 'bool' and right_type == 'bool'
            
        # Unknown operator
        return False

    def result_type(self, left_type, right_type, operator):
        """Determine the result type of an operation"""
        # For arithmetic operations
        if operator in ['+', '-', '*', '/', '%']:
            # If either operand is quant, result is quant
            if left_type == 'quant' or right_type == 'quant':
                return 'quant'
            # If both are seq, result is seq
            if left_type == 'seq' and right_type == 'seq':
                return 'seq'
            # If both are dose, result is dose
            if left_type == 'dose' and right_type == 'dose':
                return 'dose'
            
        # For logical operations
        elif operator in ['&&', '||']:
            # Result of logical operation is boolean
            if left_type == 'bool' and right_type == 'bool':
                return 'bool'
            
        # Default case - return left type if no specific rule applies
        return left_type

    def check_number_type(self, literal):
        """Determine the type of a number literal"""
        # This is a placeholder - you'll need to implement the actual logic
        # based on how your number literals are formatted
        if 'q' in literal or 'Q' in literal:
            return 'quantval'
        elif 'd' in literal or 'D' in literal:
            return 'doseliteral'
        else:
            return 'doseliteral'  # Default
    
    def check_type_compatibility(self, left_type, right_type, operator):
        """Check if the types are compatible with the given operator"""
        if left_type == right_type:
            # Same types are generally compatible
            if left_type in ['dose', 'quant']:
                # Numeric types can use all arithmetic operators
                return True
            elif left_type == 'seq' and operator == '+':
                # Sequences can only be concatenated
                return True
            elif left_type == 'allele' and operator in ['&&', '||']:
                # Boolean types can use logical operators
                return True
            else:
                # Other cases are not compatible
                return False
        elif (left_type == 'dose' and right_type == 'quant') or (left_type == 'quant' and right_type == 'dose'):
            # Mixing integers and floats is allowed
            return True
        else:
            # Different types are not compatible
            return False

    def type_check_assignment(self, var_name, value_token):
        """Check if a value can be assigned to a variable of a specific type"""
        if var_name not in self.symbol_table:
            self.errors.append(f"Semantic Error: Variable '{var_name}' used before declaration")
            return
            
        var_type = self.symbol_table[var_name]['type']
        
        if value_token is None:
            return
            
        # Check literal value types
        if value_token[1] == 'numlit':
            if '.' in value_token[0]:
                value_type = 'quant'
            else:
                value_type = 'dose'
                
            if var_type == 'dose' and value_type == 'quant':
                self.errors.append(f"Semantic Error: Cannot assign float value to dose variable '{var_name}'")
            elif var_type not in ['dose', 'quant']:
                self.errors.append(f"Semantic Error: Cannot assign numeric value to {var_type} variable '{var_name}'")
                
        elif value_token[1] == 'string literal':
            if var_type != 'seq':
                self.errors.append(f"Semantic Error: Cannot assign string value to {var_type} variable '{var_name}'")
                
        elif value_token[0] in ['dom', 'rec']:
            if var_type != 'allele':
                self.errors.append(f"Semantic Error: Cannot assign boolean value to {var_type} variable '{var_name}'")
        
        # Check variable assignments
        elif value_token[1] == 'Identifier':
            value_name = value_token[0]
            if value_name in self.symbol_table:
                value_type = self.symbol_table[value_name]['type']
                
                if var_type == 'dose' and value_type == 'quant':
                    self.errors.append(f"Semantic Error: Cannot assign quant variable to dose variable '{var_name}'")
                elif var_type != value_type and not (var_type == 'quant' and value_type == 'dose'):
                    self.errors.append(f"Semantic Error: Cannot assign {value_type} variable to {var_type} variable '{var_name}'")
            else:
                self.errors.append(f"Semantic Error: Variable '{value_name}' used before declaration")

def generate_symtab(parsed_tokens):
    """Create a symbol table from parsed tokens"""
    analyzer = SemanticAnalyzer(parsed_tokens)
    analyzer.parse()
    return analyzer.symbol_table, analyzer.errors

def run_semantic_analysis(file_contents):
    """Run the complete semantic analysis on the given file contents"""
    # Get tokens from lexer
    tokens = gxl.tokenize(file_contents)
    
    # Run the semantic analyzer
    symbol_table, errors = generate_symtab(tokens)
    
    return symbol_table, errors

# Additional helper functions for integration with other components

def validate_program(tokens):
    """
    Validate a complete program by checking for semantic errors
    Returns a tuple of (is_valid, errors)
    """
    symbol_table, errors = generate_symtab(tokens)
    return len(errors) == 0, errors

def analyze_code_snippet(code_snippet):
    """
    Analyze a code snippet without running a full program
    Useful for IDE-like feedback during typing
    """
    tokens = gxl.tokenize(code_snippet)
    analyzer = SemanticAnalyzer(tokens)
    analyzer.parse()
    return analyzer.errors

def get_variable_info(symbol_table, var_name):
    """
    Get detailed information about a variable from the symbol table
    Useful for tooltips and context-aware help
    """
    if var_name in symbol_table:
        return symbol_table[var_name]
    return None

def check_type_compatibility_for_operation(left_type, right_type, operator):
    """
    Check if an operation between two types is valid
    This can be used by other components without instantiating the full analyzer
    """
    # Handle array types if needed
    if left_type.startswith('array_'):
        base_type = left_type[6:]  # Extract base type from array_<type>
        if operator in ['==', '!='] and right_type == left_type:
            return True
        elif operator == '+' and right_type == left_type:  # Array concatenation
            return True
        return False
    
    # Same types are generally compatible
    if left_type == right_type:
        if left_type in ['dose', 'quant']:
            # Numeric types can use all arithmetic operators
            return operator in ['+', '-', '*', '/', '%', '<', '>', '<=', '>=', '==', '!=']
        elif left_type == 'seq':
            # Sequences can only be concatenated or compared for equality
            return operator in ['+', '==', '!=']
        elif left_type == 'allele':
            # Boolean types can use logical operators or be compared
            return operator in ['&&', '||', '==', '!=']
        
    # Mixed numeric types
    elif (left_type == 'dose' and right_type == 'quant') or (left_type == 'quant' and right_type == 'dose'):
        return operator in ['+', '-', '*', '/', '%', '<', '>', '<=', '>=', '==', '!=']
    
    # Any other combination is invalid
    return False

def generate_error_report(errors):
    """
    Generate a formatted error report from a list of semantic errors
    """
    if not errors:
        return "No semantic errors found."
        
    report = "Semantic Analysis Errors:\n" + "="*25 + "\n"
    for i, error in enumerate(errors, 1):
        report += f"{i}. {error}\n"
    
    report += "\nTotal Errors: " + str(len(errors))
    return report

def analyze_expression_value(expr, symbol_table):
    """
    Attempt to determine the value of an expression at compile time
    For use in constant folding and optimization
    """
    if isinstance(expr, tuple) and len(expr) == 3:
        left, op, right = expr
        left_val = analyze_expression_value(left, symbol_table)
        right_val = analyze_expression_value(right, symbol_table)
        
        if left_val is not None and right_val is not None:
            if op == '+':
                return left_val + right_val
            elif op == '-':
                return left_val - right_val
            elif op == '*':
                return left_val * right_val
            elif op == '/':
                return left_val / right_val if right_val != 0 else None
            elif op == '%':
                return left_val % right_val if right_val != 0 else None
    
    elif isinstance(expr, str):
        # Variable reference
        if expr in symbol_table and 'value' in symbol_table[expr]:
            return symbol_table[expr]['value']
    
    elif isinstance(expr, (int, float, str, bool)):
        # Literal value
        return expr
        
    return None  # Could not determine value at compile time

# Support for common type utility functions

def get_default_value_for_type(type_name):
    """Return the default value for a given type"""
    if type_name == 'dose':
        return 0
    elif type_name == 'quant':
        return 0.0
    elif type_name == 'seq':
        return ""
    elif type_name == 'allele':
        return False
    elif type_name.startswith('clust'):
        return []
    return None  # Unknown type

def is_numeric_type(type_name):
    """Check if a type is numeric (dose or quant)"""
    return type_name in ['dose', 'quant']

def can_convert_between_types(from_type, to_type):
    """Check if a value can be converted from one type to another"""
    # Same type - always convertible
    if from_type == to_type:
        return True
    
    # Dose can be converted to quant, but not vice versa (would lose precision)
    if from_type == 'dose' and to_type == 'quant':
        return True
    
    # Special case: integer-like quant (e.g., 5.0) could be converted to dose
    # But this would need runtime checking, so we don't allow it at compile time
    
    # Arrays of the same element type can be converted
    if from_type.startswith('array_') and to_type.startswith('array_'):
        from_element_type = from_type[6:]
        to_element_type = to_type[6:]
        return can_convert_between_types(from_element_type, to_element_type)
    
    return False

def parseSemantic(tokens, semantic_panel):
    """
    Run semantic analysis on tokens and display results in the semantic panel
    Returns True if no semantic errors, False otherwise
    """
    # Clear previous output
    semantic_panel.delete("1.0", tk.END)
    
    # Create a semantic analyzer instance
    analyzer = SemanticAnalyzer(tokens)
    
    # Run the analysis
    analyzer.parse()
    
    # Get the errors
    errors = analyzer.errors
    
    if not errors:
        semantic_panel.insert(tk.END, "Semantic Analysis: No errors found.\n\n")
        
        # Check if there's any express statement output to display
        if 'express_output' in analyzer.symbol_table:
            express_value = analyzer.symbol_table['express_output']['value']
            semantic_panel.insert(tk.END, f"Express Output: {express_value}\n\n")
        
        
        # Display symbol table
        for var_name, var_info in analyzer.symbol_table.items():
            # Skip the special express_output entry when displaying variables
            if var_name == 'express_output':
                continue
                
            var_type = var_info.get('type', 'unknown')
            var_value = var_info.get('value', 'undefined')
            semantic_panel.insert(tk.END, f"Variable: {var_name}\n")
            semantic_panel.insert(tk.END, f"  Type: {var_type}\n")
            semantic_panel.insert(tk.END, f"  Value: {var_value}\n\n")
        
        # Display function table if any functions were defined
        if analyzer.functions:
            semantic_panel.insert(tk.END, "\nFunction Table:\n")
            
            for func_name, func_info in analyzer.functions.items():
                return_type = func_info.get('return_type', 'void')
                params = func_info.get('parameters', [])
                
                semantic_panel.insert(tk.END, f"Function: {func_name}\n")
                semantic_panel.insert(tk.END, f"  Return Type: {return_type}\n")
                
                if params:
                    semantic_panel.insert(tk.END, f"  Parameters:\n")
                    for param in params:
                        semantic_panel.insert(tk.END, f"    {param['name']} ({param['type']})\n")
                else:
                    semantic_panel.insert(tk.END, f"  Parameters: None\n")
                
                semantic_panel.insert(tk.END, "\n")
                
        return True
    else:
        # Display errors
        semantic_panel.insert(tk.END, "Semantic Analysis Errors:\n")
        
        for i, error in enumerate(errors, 1):
            semantic_panel.insert(tk.END, f"{i}. {error}\n")
            
            # Apply error tags for highlighting
            error_start = f"{i}.0"
            error_end = f"{i}.end"
            semantic_panel.tag_add("error", error_start, error_end)
        
        semantic_panel.insert(tk.END, f"\nTotal Errors: {len(errors)}\n")
        semantic_panel.tag_config("error", foreground="red")
        
        # Switch to the semantic tab to show errors
        # Note: This would be done in the GUI code
        
        return False
