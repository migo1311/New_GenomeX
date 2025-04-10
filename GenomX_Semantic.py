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
        self.current_assignment_type = None  # Track the type of the current assignment
        self.next_token()
        self.pending_inputs = []  # Add this line to store pending inputs
        self.express_outputs = []  # Add this line to store express outputs

    def next_token(self):
        while self.token_index < len(self.tokens) and self.tokens[self.token_index][1] == "space":
            self.token_index += 1  # Skip spaces
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
            self.token_index += 1
        else:
            self.current_token = None
        print(f"Moved to next token: {self.current_token}") 

    def parse(self):
        while self.current_token is not None:
            if self.current_token[1] == '_G':
                self.declaration()
            elif self.current_token[1] == 'act':
                self.act_gene_function()
            elif self.current_token[1] == 'newline':
                self.next_token()  # Skip newlines
            elif self.current_token[1] == 'space':
                self.next_token()
            else:
                self.errors.append(f"Semantic Error: Unexpected token: {self.current_token[1]}")
                self.next_token()  # Skip invalid token to continue analysis

    
    def act_gene_function(self):
        
        print(f"Current token: {self.current_token}")  # Debug print
        self.next_token()  # Move past 'act'
        
        # Skip Spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()  # Move past space

        # Check for 'gene', 'void', or function identifier
        function_type = None
        function_name = None
        
        if self.current_token is None:
            self.errors.append("Semantic Error: Unexpected end of tokens after 'act'")
            return
            
        if self.current_token[1] == 'gene':
            function_type = 'gene'
            function_name = 'gene'
            self.next_token()  # Move past 'gene'
        elif self.current_token[1] == 'void':
            function_type = 'void'
            self.next_token()  # Move past 'void'
            
            # Skip spaces
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
                
            # Expect identifier
            if self.current_token is None or self.current_token[1] != 'Identifier':
                self.errors.append(f"Semantic Error: Expected identifier after 'void', but found {self.current_token}")
                return
                
            function_name = self.current_token[0]
            self.next_token()  # Move past identifier
        elif self.current_token[1] == 'Identifier':
            function_type = 'regular'
            function_name = self.current_token[0]
            self.next_token()  # Move past identifier
        else:
            self.errors.append(f"Semantic Error: Expected 'gene', 'void', or identifier after 'act', but found {self.current_token}")
            return
        
        print(f"Function type: {function_type}, Function name: {function_name}")
        
        # Skip Spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()  # Move past space

        # Check for '('
        if self.current_token is None or self.current_token[0] != '(':
            self.errors.append(f"Semantic Error: Expected '(' after function name, but found {self.current_token}")
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
            
            # If we have more parameters, we should see a comma
            if self.current_token is not None and self.current_token[0] == ',':
                self.next_token()  # Move past comma
            elif self.current_token is not None and self.current_token[0] != ')':
                self.errors.append(f"Semantic Error: Expected ',' or ')' after parameter, found {self.current_token}")
        
        # Check for ')'
        if self.current_token is None or self.current_token[0] != ')':
            self.errors.append(f"Semantic Error: Expected ')' after '(', but found {self.current_token}")
            return
        self.next_token()  # Move past ')'
        
        # Skip Spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()  # Move past space

        # Check for '{'
        if self.current_token is None or self.current_token[0] != '{':
            self.errors.append(f"Semantic Error: Expected '{{' after function declaration, but found {self.current_token}")
            return
        self.next_token()  # Move past '{'
        
        # Add function to function table if it's not gene
        if function_name != 'gene':
            return_type = 'void' if function_type == 'void' else param_type
            self.functions[function_name] = {
                'return_type': return_type,
                'parameters': parameters  # Now using the parameters list we collected
            }
        
        # Parse the body statements
        self.parse_body_statements()  # Parse the function body
        
        # Check for '}'
        if self.current_token is None or self.current_token[0] != '}':
            self.errors.append(f"Semantic Error: Expected '}}' at end of function body, but found {self.current_token}")
            return
        self.next_token()  # Move past '}'
        print(f"Finished parsing function: {function_name}")
    def prod_statement(self): 

        """Parse prod statement (return statement) and check type compatibility"""
        self.next_token()  # Move past 'prod'
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
        
        # Check if we're in a function
        if not self.functions:
            self.errors.append("Semantic Error: 'prod' statement can only be used inside a function")
            
        # Get the current function's return type
        # For simplicity, we'll assume we're in the most recently defined function
        current_function = None
        return_type = None
        if self.functions:
            current_function = list(self.functions.keys())[-1]
            return_type = self.functions[current_function]['return_type']
            
        # Handle void functions (no return value)
        if return_type == 'void':
            # Void functions should not return a value
            if self.current_token is not None and self.current_token[0] != ';':
                self.errors.append("Semantic Error: Void function cannot return a value")
                
                # Skip until semicolon
                while self.current_token is not None and self.current_token[0] != ';':
                    self.next_token()
        else:
            # Non-void functions must return a value of the correct type
            value_type = self.parse_expression()
            
            # Check if returned value type matches function return type
            if value_type is not None and return_type is not None and value_type != return_type:
                # Allow dose to be returned from a quant function
                if not (return_type == 'quant' and value_type == 'dose'):
                    self.errors.append(f"Semantic Error: Function returns {return_type} but got {value_type}")
        
        # Check for semicolon
        if self.current_token is None or self.current_token[0] != ';':
            self.errors.append(f"Semantic Error: Expected ';' after prod statement, found {self.current_token}")
            return
            
        self.next_token()  # Move past ';'
    def function_call(self):
        """Parse function call statement starting with 'func'"""
        self.next_token()  # Move past 'func'
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
        
        # Get function name
        if self.current_token is None or self.current_token[1] != 'Identifier':
            self.errors.append(f"Semantic Error: Expected function identifier after 'func', found {self.current_token}")
            return
            
        function_name = self.current_token[0]
        
        # Check if function exists
        if function_name not in self.functions:
            self.errors.append(f"Semantic Error: Function '{function_name}' called but not defined")
        
        self.next_token()  # Move past function name
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
            
        # Check for semicolon
        if self.current_token is None or self.current_token[0] != ';':
            self.errors.append(f"Semantic Error: Expected ';' after function call, found {self.current_token}")
            return
            
        self.next_token()  # Move past ';'
    def stimuli_statement(self):
        """Parse stimuli statement (input statement) and validate types"""
        self.next_token()  # Move past 'stimuli'
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
        
        # Check for opening parenthesis
        if self.current_token is None or self.current_token[0] != '(':
            self.errors.append(f"Semantic Error: Expected '(' after 'stimuli', found {self.current_token}")
            # Try to skip ahead to recover
            while self.current_token is not None and self.current_token[0] != ';':
                self.next_token()
            if self.current_token is not None:
                self.next_token()  # Move past semicolon
            return
            
        self.next_token()  # Move past '('
        
        # Check for prompt message (string literal)
        prompt = None
        if self.current_token is not None and self.current_token[1] == 'string literal':
            prompt = self.current_token[0].strip('"\'')
            self.next_token()  # Move past string literal
        else:
            self.errors.append(f"Semantic Error: Expected string literal for input prompt, found {self.current_token}")
        
        # Skip ahead to closing parenthesis
        while self.current_token is not None and self.current_token[0] != ')':
            self.next_token()
        
        if self.current_token is None or self.current_token[0] != ')':
            self.errors.append(f"Semantic Error: Expected ')' after input prompt, found {self.current_token}")
            # Try to skip ahead to recover
            while self.current_token is not None and self.current_token[0] != ';':
                self.next_token()
            if self.current_token is not None:
                self.next_token()  # Move past semicolon
            return
            
        self.next_token()  # Move past ')'
        
        # Check for semicolon
        if self.current_token is None or self.current_token[0] != ';':
            self.errors.append(f"Semantic Error: Expected ';' after stimuli statement, found {self.current_token}")
            # Try to skip ahead to recover
            while self.current_token is not None and self.current_token[0] != ';':
                self.next_token()
        
        if self.current_token is not None and self.current_token[0] == ';':
            self.next_token()  # Move past ';'

    def parse_body_statements(self):
        was_in_loop = self.in_loop  # Save previous loop state
        
        while self.current_token is not None and self.current_token[0] != '}':
            # Skip newlines and spaces
            while self.current_token is not None and self.current_token[1] in ['newline', 'space']:
                self.next_token()
                
            if self.current_token is None or self.current_token[0] == '}':
                break
                
            try:
                # Handle variable declarations
                if self.current_token[0] in ['_L'] or self.current_token[1] in ['dose', 'quant', 'seq', 'allele']:
                    self.declaration()
                # Handle if statements
                elif self.current_token[1] == 'if':
                    self.if_statement()
                # Handle prod (return) statements
                elif self.current_token[1] == 'prod':
                    self.prod_statement()
                # Handle function calls
                elif self.current_token[1] == 'func':
                    self.function_call()
                # Handle loops
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
                # Handle print statements
                elif self.current_token[1] == 'express':
                    self.express_statement()
                # Handle input statements
                elif self.current_token[1] == 'stimuli':
                    self.stimuli_statement()
                # Handle variable assignments
                elif self.current_token[1] == 'Identifier':
                    self.check_variable_usage()
                # Handle break and continue statements
                elif self.current_token[1] == 'destroy':
                    self.break_statement()
                elif self.current_token[0] == 'contig':
                    self.continue_statement()
                # Handle array declarations
                elif self.current_token[1] == 'array':
                    self.array_declaration()
                # Handle function declarations
                elif self.current_token[1] == 'function':
                    self.function_declaration()
                elif self.current_token[1] == 'comment':    
                    self.next_token()
                # Handle conversion functions
                elif self.current_token[1] == 'seq':
                    # Simple approach: skip tokens until semicolon
                    while self.current_token is not None and self.current_token[0] != ';':
                        self.next_token()
                    if self.current_token is not None:
                        self.next_token()  # Move past semicolon
                elif self.current_token[1] == 'elif' or self.current_token[1] == 'else':
                    # These are handled by if_statement, if they appear here it's a syntax error
                    self.errors.append(f"Semantic Error: Unexpected {self.current_token[1]} without matching if statement")
                    # Skip until we find an open brace, then skip the entire block
                    while self.current_token is not None and self.current_token[0] != '{':
                        self.next_token()
                    if self.current_token is not None:
                        self.next_token()  # Move past '{'
                        self.skip_to_end_of_block()
                elif self.current_token[0] == ';':
                    # Allow empty statements with just a semicolon
                    self.next_token()  # Skip semicolon
                else:
                    # For any unrecognized token, report error and skip to next semicolon or closing brace
                    self.errors.append(f"Semantic Error: Unexpected token '{self.current_token[0]}' in body")
                    # Skip until next semicolon or closing brace
                    while (self.current_token is not None and 
                           self.current_token[0] != ';' and 
                           self.current_token[0] != '}'):
                        self.next_token()
                    # If we found a semicolon, move past it
                    if self.current_token is not None and self.current_token[0] == ';':
                        self.next_token()
            except Exception as e:
                # In case of any exception, try to recover by skipping to next semicolon or closing brace
                self.errors.append(f"Semantic Error: Exception in parsing: {str(e)}")
                while (self.current_token is not None and 
                       self.current_token[0] != ';' and 
                       self.current_token[0] != '}'):
                    self.next_token()
                # If we found a semicolon, move past it
                if self.current_token is not None and self.current_token[0] == ';':
                    self.next_token()
    
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
        
        # Add to symbol table
        self.symbol_table[array_name] = {
            'type': f'array_{element_type}',
            'value': [],
            'element_type': element_type
        }
        
        # Check for assignment
        if self.current_token is not None and self.current_token[0] == '=':
            self.next_token()  # Move past '='
            
            # Check for array initializer
            if self.current_token is None or self.current_token[0] != '[':
                self.errors.append(f"Semantic Error: Expected '[' for array initialization, found {self.current_token}")
                return
                
            self.next_token()  # Move past '['
            
            # Parse array elements
            elements = []
            while self.current_token is not None and self.current_token[0] != ']':
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
                    
                if self.current_token[0] != ',' and self.current_token[0] != ']':
                    self.errors.append(f"Semantic Error: Expected ',' or ']' in array initialization, found {self.current_token}")
            
            # Update symbol table with elements
            self.symbol_table[array_name]['value'] = elements
            
            if self.current_token is None or self.current_token[0] != ']':
                self.errors.append(f"Semantic Error: Expected ']' at end of array initialization, found {self.current_token}")
                return
                
            self.next_token()  # Move past ']'
        
        # Check for semicolon
        if self.current_token is None or self.current_token[0] != ';':
            self.errors.append(f"Semantic Error: Expected ';' after array declaration, found {self.current_token}")
            return
            
        self.next_token()  # Move past ';'

    
    def function_declaration(self):
        """Parse function declaration"""
        self.next_token()  # Move past 'function'
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
        
        # Get return type
        if self.current_token is None or self.current_token[1] not in ['dose', 'quant', 'seq', 'allele', 'void']:
            self.errors.append(f"Semantic Error: Expected valid return type for function, found {self.current_token}")
            return
            
        return_type = self.current_token[1]
        self.next_token()  # Move past return type
        
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
            return
        
        # Get the variable type from the symbol table
        var_type = self.symbol_table[var_name]['type']
        
        self.next_token()  # Move past identifier
        
        # Look for assignment operator
        if self.current_token is not None and self.current_token[0] == '=':
            self.next_token()  # Move past '='
            
            # Set the current assignment type for type checking
            self.current_assignment_type = var_type
            
            # Collect tokens for the expression until semicolon
            expression_tokens = []
            
            while self.current_token is not None and self.current_token[0] != ';':
                expression_tokens.append(self.current_token)
                self.next_token()
            
            # Special handling for stimuli function
            if len(expression_tokens) >= 1 and expression_tokens[0][1] == 'stimuli':
                # Check for stimuli function with proper structure
                prompt = None
                
                # Find the prompt string
                for i in range(len(expression_tokens)):
                    if expression_tokens[i][1] == 'string literal':
                        prompt = expression_tokens[i][0].strip('"\'')
                        break
                
                if prompt is None:
                    self.errors.append(f"Semantic Error: Missing prompt in stimuli function")
                
                # Store the default value based on variable type
                if var_type == 'dose':
                    self.symbol_table[var_name]['value'] = 0  # Default integer value
                elif var_type == 'quant':
                    self.symbol_table[var_name]['value'] = 0.0  # Default float value
                elif var_type == 'seq':
                    self.symbol_table[var_name]['value'] = ""  # Default string value
                else:
                    self.errors.append(f"Semantic Error: Cannot use stimuli with {var_type} type")
                
                # Store the prompt for runtime processing
                if not hasattr(self, 'pending_inputs'):
                    self.pending_inputs = []
                self.pending_inputs.append((var_name, var_type, prompt))
                
                return  # Skip further processing for stimuli
            
            # Evaluate the expression
            if len(expression_tokens) == 1:
                token = expression_tokens[0]
                
                # Check if the assigned value is an identifier
                if token[1] == 'Identifier':
                    var_to_assign = token[0]
                    if var_to_assign in self.symbol_table:
                        # Get value from the identifier's stored value
                        assigned_value = self.symbol_table[var_to_assign]['value']
                        assigned_type = self.symbol_table[var_to_assign]['type']
                        
                        # Check type compatibility
                        if var_type == assigned_type or (var_type == 'quant' and assigned_type == 'dose'):
                            self.symbol_table[var_name]['value'] = assigned_value
                        else:
                            self.errors.append(f"Semantic Error: Cannot assign {assigned_type} variable to {var_type} variable '{var_name}'")
                    else:
                        self.errors.append(f"Semantic Error: Variable '{var_to_assign}' used before declaration")
                
                # Handle literals
                elif token[1] == 'numlit':
                    if var_type == 'dose':
                        try:
                            self.symbol_table[var_name]['value'] = int(token[0])
                        except:
                            self.errors.append(f"Semantic Error: Cannot convert {token[0]} to integer for dose variable '{var_name}'")
                    elif var_type == 'quant':
                        try:
                            self.symbol_table[var_name]['value'] = float(token[0])
                        except:
                            self.errors.append(f"Semantic Error: Cannot convert {token[0]} to float for quant variable '{var_name}'")
                    else:
                        self.errors.append(f"Semantic Error: Cannot assign numeric value to {var_type} variable '{var_name}'")
                
                elif token[1] == 'string literal':
                    if var_type == 'seq':
                        # Remove quotation marks
                        string_val = token[0].strip('"\'')
                        self.symbol_table[var_name]['value'] = string_val
                    else:
                        self.errors.append(f"Semantic Error: Cannot assign string value to {var_type} variable '{var_name}'")
                
                elif token[0] in ['dom', 'rec']:
                    if var_type == 'allele':
                        boolean_val = (token[0] == 'dom')
                        self.symbol_table[var_name]['value'] = boolean_val
                    else:
                        self.errors.append(f"Semantic Error: Cannot assign boolean value to {var_type} variable '{var_name}'")
            
            # Handle complex expressions (with operators)
            elif len(expression_tokens) > 1:
                # Only handle arithmetic expressions for numeric types
                if var_type in ['dose', 'quant']:
                    expr_str = ""
                    valid_expression = True
                    
                    # Track if division is used, which forces quant result type
                    contains_division = False
                    
                    for token in expression_tokens:
                        if token[1] == 'Identifier':
                            if token[0] in self.symbol_table:
                                if self.symbol_table[token[0]]['type'] in ['dose', 'quant']:
                                    expr_str += str(self.symbol_table[token[0]]['value'])
                                else:
                                    self.errors.append(f"Semantic Error: Cannot use non-numeric variable '{token[0]}' in arithmetic expression")
                                    valid_expression = False
                                    break
                            else:
                                self.errors.append(f"Semantic Error: Variable '{token[0]}' used before declaration")
                                valid_expression = False
                                break
                        elif token[1] == 'numlit':
                            expr_str += token[0]
                        elif token[0] in ['+', '-', '*', '/', '%', '(', ')']:
                            # Track division for type conversion
                            if token[0] == '/':
                                contains_division = True
                            expr_str += token[0]
                        elif token[1] == 'space':
                            continue  # Skip spaces
                        else:
                            self.errors.append(f"Semantic Error: Invalid token '{token[0]}' in arithmetic expression")
                            valid_expression = False
                            break
                    
                    if valid_expression and expr_str:
                        try:
                            # Force float result for division operations or if target is quant
                            if var_type == 'quant' or contains_division:
                                result = float(eval(expr_str))
                            else:  # dose type with no division
                                result = int(eval(expr_str))
                            
                            self.symbol_table[var_name]['value'] = result
                        except Exception as e:
                            self.errors.append(f"Semantic Error: Failed to evaluate expression: {str(e)}")
                            
                        # Check for division by zero
                        if contains_division and '/' in expr_str:
                            try:
                                # This is just a simple check - a more robust solution would parse the expression
                                parts = expr_str.split('/')
                                if len(parts) > 1 and float(eval(parts[1].strip())) == 0:
                                    self.errors.append(f"Semantic Error: Division by zero detected in expression for '{var_name}'")
                            except:
                                # If we can't evaluate the right side, we ignore this check
                                pass
                
                # Handle string concatenation for seq type
                elif var_type == 'seq':
                    result = ""
                    valid_expression = True
                    
                    for i, token in enumerate(expression_tokens):
                        if token[0] == '+':
                            continue
                        
                        if token[1] == 'Identifier':
                            if token[0] in self.symbol_table:
                                if self.symbol_table[token[0]]['type'] == 'seq':
                                    result += str(self.symbol_table[token[0]]['value'])
                                else:
                                    self.errors.append(f"Semantic Error: Cannot concatenate non-string variable '{token[0]}'")
                                    valid_expression = False
                                    break
                            else:
                                self.errors.append(f"Semantic Error: Variable '{token[0]}' used before declaration")
                                valid_expression = False
                                break
                        elif token[1] == 'string literal':
                            result += token[0].strip('"\'')
                        elif token[1] == 'space':
                            continue  # Skip spaces
                        else:
                            self.errors.append(f"Semantic Error: Invalid token '{token[0]}' in string concatenation")
                            valid_expression = False
                            break
                    
                    if valid_expression:
                        self.symbol_table[var_name]['value'] = result
                else:
                    self.errors.append(f"Semantic Error: Complex expressions not supported for {var_type} type")
        
        # Check for semicolon if not already consumed
        if self.current_token is not None and self.current_token[0] == ';':
            self.next_token()  # Move past semicolon
    
    def declaration(self):
        # Check for variable scope
        var_scope = 'local'  # Default scope
        
        # If current token is _L or _G, set scope accordingly
        if self.current_token is not None and (self.current_token[0] == '_L' or self.current_token[0] == '_G'):
            var_scope = 'local' if self.current_token[0] == '_L' else 'global'
            self.next_token()  # Move past scope token
            
            # Skip spaces after scope token
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
                
        # Now get the data type
        if self.current_token is None or self.current_token[1] not in ['dose', 'quant', 'seq', 'allele']:
            self.errors.append(f"Semantic Error: Expected data type, found {self.current_token}")
            return
            
        var_type = self.current_token[1]
        self.next_token()  # Move past type

        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
            
        # Process multiple variable declarations separated by commas
        while True:
            # Get variable name
            if self.current_token is None or self.current_token[1] != 'Identifier':
                self.errors.append(f"Semantic Error: Expected identifier after type declaration, found {self.current_token}")
                return

            var_name = self.current_token[0]
            
            # Check for redeclaration
            if var_name in self.symbol_table:
                self.errors.append(f"Semantic Error: Variable '{var_name}' already declared")
                
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

            # Add to symbol table
            self.symbol_table[var_name] = {
                'scope': var_scope,
                'type': var_type,
                'value': default_value
            }
            
            # Check for assignment
            if self.current_token is not None and self.current_token[0] == '=':
                self.next_token()  # Move past '='
                
                # Set the current assignment type for type checking
                self.current_assignment_type = var_type
                
                # Collect tokens for the expression until semicolon or comma
                expression_tokens = []
                start_pos = self.token_index - 1  # Start after '='
                
                while self.current_token is not None and self.current_token[0] != ';' and self.current_token[0] != ',':
                    expression_tokens.append(self.current_token)
                    self.next_token()
                
                # Evaluate the expression for the current variable
                if len(expression_tokens) == 1:
                    token = expression_tokens[0]
                    
                    # Check if the assigned value is an identifier
                    if token[1] == 'Identifier':
                        var_to_assign = token[0]
                        if var_to_assign in self.symbol_table:
                            # Get value from the identifier's stored value
                            assigned_value = self.symbol_table[var_to_assign]['value']
                            assigned_type = self.symbol_table[var_to_assign]['type']
                            
                            # Check type compatibility
                            if var_type == assigned_type or (var_type == 'quant' and assigned_type == 'dose'):
                                self.symbol_table[var_name]['value'] = assigned_value
                            else:
                                self.errors.append(f"Semantic Error: Cannot assign {assigned_type} variable to {var_type} variable '{var_name}'")
                        else:
                            self.errors.append(f"Semantic Error: Variable '{var_to_assign}' used before declaration")
                    
                    # Handle literals
                    elif token[1] == 'numlit':
                        if var_type == 'dose':
                            try:
                                self.symbol_table[var_name]['value'] = int(token[0])
                            except:
                                self.errors.append(f"Semantic Error: Cannot convert {token[0]} to integer for dose variable '{var_name}'")
                        elif var_type == 'quant':
                            try:
                                self.symbol_table[var_name]['value'] = float(token[0])
                            except:
                                self.errors.append(f"Semantic Error: Cannot convert {token[0]} to float for quant variable '{var_name}'")
                        else:
                            self.errors.append(f"Semantic Error: Cannot assign numeric value to {var_type} variable '{var_name}'")
                    
                    elif token[1] == 'string literal':
                        if var_type == 'seq':
                            # Remove quotation marks
                            string_val = token[0].strip('"\'')
                            self.symbol_table[var_name]['value'] = string_val
                        else:
                            self.errors.append(f"Semantic Error: Cannot assign string value to {var_type} variable '{var_name}'")
                    
                    elif token[0] in ['dom', 'rec']:
                        if var_type == 'allele':
                            boolean_val = (token[0] == 'dom')
                            self.symbol_table[var_name]['value'] = boolean_val
                        else:
                            self.errors.append(f"Semantic Error: Cannot assign boolean value to {var_type} variable '{var_name}'")
                
                # Handle complex expressions
                elif len(expression_tokens) > 1:
                    # Only handle arithmetic expressions for numeric types
                    if var_type in ['dose', 'quant']:
                        expr_str = ""
                        valid_expression = True
                        
                        # Track if division is used, which forces quant result type
                        contains_division = False
                        
                        for token in expression_tokens:
                            if token[1] == 'Identifier':
                                if token[0] in self.symbol_table:
                                    if self.symbol_table[token[0]]['type'] in ['dose', 'quant']:
                                        expr_str += str(self.symbol_table[token[0]]['value'])
                                    else:
                                        self.errors.append(f"Semantic Error: Cannot use non-numeric variable '{token[0]}' in arithmetic expression")
                                        valid_expression = False
                                        break
                                else:
                                    self.errors.append(f"Semantic Error: Variable '{token[0]}' used before declaration")
                                    valid_expression = False
                                    break
                            elif token[1] == 'numlit':
                                expr_str += token[0]
                            elif token[0] in ['+', '-', '*', '/', '%', '(', ')']:
                                # Track division for type conversion
                                if token[0] == '/':
                                    contains_division = True
                                expr_str += token[0]
                            elif token[1] == 'space':
                                continue  # Skip spaces
                            else:
                                self.errors.append(f"Semantic Error: Invalid token '{token[0]}' in arithmetic expression")
                                valid_expression = False
                                break
                        
                        if valid_expression and expr_str:
                            try:
                                # Force float result for division operations or if target is quant
                                if var_type == 'quant' or contains_division:
                                    result = float(eval(expr_str))
                                else:  # dose type with no division
                                    result = int(eval(expr_str))
                                
                                self.symbol_table[var_name]['value'] = result
                            except Exception as e:
                                self.errors.append(f"Semantic Error: Failed to evaluate expression: {str(e)}")
                                
                            # Check for division by zero
                            if contains_division and '/' in expr_str:
                                try:
                                    # This is just a simple check - a more robust solution would parse the expression
                                    parts = expr_str.split('/')
                                    if len(parts) > 1 and float(eval(parts[1].strip())) == 0:
                                        self.errors.append(f"Semantic Error: Division by zero detected in expression for '{var_name}'")
                                except:
                                    # If we can't evaluate the right side, we ignore this check
                                    pass
                    
                    # Handle string concatenation for seq type
                    elif var_type == 'seq':
                        result = ""
                        valid_expression = True
                        
                        for i, token in enumerate(expression_tokens):
                            if token[0] == '+':
                                continue
                            
                            if token[1] == 'Identifier':
                                if token[0] in self.symbol_table:
                                    if self.symbol_table[token[0]]['type'] == 'seq':
                                        result += str(self.symbol_table[token[0]]['value'])
                                    else:
                                        self.errors.append(f"Semantic Error: Cannot concatenate non-string variable '{token[0]}'")
                                        valid_expression = False
                                        break
                                else:
                                    self.errors.append(f"Semantic Error: Variable '{token[0]}' used before declaration")
                                    valid_expression = False
                                    break
                            elif token[1] == 'string literal':
                                result += token[0].strip('"\'')
                            elif token[1] == 'space':
                                continue  # Skip spaces
                            else:
                                self.errors.append(f"Semantic Error: Invalid token '{token[0]}' in string concatenation")
                                valid_expression = False
                                break
                        
                        if valid_expression:
                            self.symbol_table[var_name]['value'] = result
                    else:
                        self.errors.append(f"Semantic Error: Complex expressions not supported for {var_type} type")
                
            # Check if we have another variable declaration (comma) or end of declaration (semicolon)
            if self.current_token is None:
                self.errors.append("Semantic Error: Unexpected end of tokens in declaration")
                return
            
            if self.current_token[0] == ';':
                self.next_token()  # Move past semicolon
                return  # End of declaration
            
            if self.current_token[0] == ',':
                self.next_token()  # Move past comma
                
                # Skip spaces after comma
                while self.current_token is not None and self.current_token[1] == 'space':
                    self.next_token()
                
                # Continue to the next variable declaration
                continue
            
            # If neither semicolon nor comma, there's a syntax error
            self.errors.append(f"Semantic Error: Expected ',' or ';' after variable declaration, found {self.current_token}")
            return

    def if_statement(self):
        """Parse if statement, checking condition and body"""
        self.next_token()  # Move past 'if'
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
            
        # Check for opening parenthesis
        if self.current_token is None or self.current_token[0] != '(':
            self.errors.append(f"Semantic Error: Expected '(' after 'if', found {self.current_token}")
            # Try to recover by skipping to the { if possible
            while self.current_token is not None and self.current_token[0] != '{':
                self.next_token()
            if self.current_token is None:
                return
        else:
            self.next_token()  # Move past '('
            
            # Skip the entire condition - we'll just count parentheses to find the matching ')'
            parenthesis_count = 1
            while self.current_token is not None and parenthesis_count > 0:
                if self.current_token[0] == '(':
                    parenthesis_count += 1
                elif self.current_token[0] == ')':
                    parenthesis_count -= 1
                self.next_token()
                
            # Skip spaces after the closing parenthesis
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
        
        # Check for opening brace
        if self.current_token is None or self.current_token[0] != '{':
            self.errors.append(f"Semantic Error: Expected '{{' after if condition, found {self.current_token}")
            return
            
        self.next_token()  # Move past '{'
        
        # Skip the entire if block body
        self.skip_to_end_of_block()
        
        # Now we're at the token after the closing brace
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
            # Try to recover by skipping to the { if possible
            while self.current_token is not None and self.current_token[0] != '{':
                self.next_token()
            if self.current_token is None:
                return
        else:
            self.next_token()  # Move past '('
            
            # Skip the entire condition - we'll just count parentheses to find the matching ')'
            parenthesis_count = 1
            while self.current_token is not None and parenthesis_count > 0:
                if self.current_token[0] == '(':
                    parenthesis_count += 1
                elif self.current_token[0] == ')':
                    parenthesis_count -= 1
                self.next_token()
                
            # Skip spaces after the closing parenthesis
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
        
        # Check for opening brace
        if self.current_token is None or self.current_token[0] != '{':
            self.errors.append(f"Semantic Error: Expected '{{' after elif condition, found {self.current_token}")
            return
            
        self.next_token()  # Move past '{'
        
        # Skip the entire elif block body
        self.skip_to_end_of_block()
        
        # Now we're at the token after the closing brace
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
        
        # Skip the entire else block body
        self.skip_to_end_of_block()

    def parse_condition(self):
        """Parse a condition, checking operands and operator compatibility"""
        # Handle logical conditions with parentheses
        if self.current_token is not None and self.current_token[0] == '(':
            self.next_token()  # Move past opening parenthesis
            
            # Skip spaces
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
                
            # Parse the inner condition
            self.parse_condition()
            
            # Skip spaces
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
            
            # Check for logical operators && and ||
            if self.current_token is not None and self.current_token[0] in ['&&', '||']:
                logical_op = self.current_token[0]
                self.next_token()  # Move past logical operator
                
                # Skip spaces
                while self.current_token is not None and self.current_token[1] == 'space':
                    self.next_token()
                
                # Parse the right side of the logical condition
                self.parse_condition()
            
            # Check for closing parenthesis
            if self.current_token is None or self.current_token[0] != ')':
                self.errors.append(f"Semantic Error: Expected ')' after condition, found {self.current_token}")
                return
                
            self.next_token()  # Move past closing parenthesis
            return
        
        # Left operand - could be a literal or variable
        left_operand = None
        left_type = None
        
        if self.current_token is not None:
            if self.current_token[1] == 'numlit':
                # Handle numeric literal on left side (like "0 == Year % 4")
                if '.' in self.current_token[0]:
                    left_operand = float(self.current_token[0])
                    left_type = 'quant'
                else:
                    left_operand = int(self.current_token[0])
                    left_type = 'dose'
                self.next_token()  # Move past number
            elif self.current_token[1] == 'Identifier':
                var_name = self.current_token[0]
                if var_name in self.symbol_table:
                    left_operand = self.symbol_table[var_name]['value']
                    left_type = self.symbol_table[var_name]['type']
                else:
                    self.errors.append(f"Semantic Error: Variable '{var_name}' used in condition before declaration")
                self.next_token()  # Move past identifier
            elif self.current_token[1] == 'string literal':
                left_operand = self.current_token[0].strip('"\'')
                left_type = 'seq'
                self.next_token()  # Move past string
            elif self.current_token[0] in ['dom', 'rec']:
                left_operand = (self.current_token[0] == 'dom')
                left_type = 'allele'
                self.next_token()  # Move past boolean
            else:
                # If not any of these, try to parse as an expression
                left_type = self.parse_expression()
        
        # Skip spaces after left operand
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
        
        # Operator
        operator = None
        if self.current_token is not None:
            operator = self.current_token[0]
            if operator not in ['<', '>', '<=', '>=', '==', '!=']:
                self.errors.append(f"Semantic Error: Invalid comparison operator '{operator}' in condition")
            else:
                self.next_token()  # Move past operator
                
                # Skip spaces after operator
                while self.current_token is not None and self.current_token[1] == 'space':
                    self.next_token()
                
                # Parse right side expression (can be complex with multiple operations)
                right_type = self.parse_expression()
                
                # Type checking between left and right operands
                if left_type is not None and right_type is not None:
                    if left_type != right_type:
                        # Allow numeric type comparisons (dose and quant)
                        if not (left_type in ['dose', 'quant'] and right_type in ['dose', 'quant']):
                            self.errors.append(f"Semantic Error: Type mismatch in condition: {left_type} {operator} {right_type}")
                    
                    # Operator checking for specific types
                    if operator in ['<', '>', '<=', '>=']:
                        if left_type in ['seq', 'allele'] or right_type in ['seq', 'allele']:
                            self.errors.append(f"Semantic Error: Operator '{operator}' cannot be used with {left_type} or {right_type} type")
        
        # Check for logical operators && and ||
        if self.current_token is not None and self.current_token[0] in ['&&', '||']:
            logical_op = self.current_token[0]
            self.next_token()  # Move past logical operator
            
            # Skip spaces
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
            
            # Parse right side of the logical expression
            self.parse_condition()

    def parse_expression(self):
        """Parse a potentially complex expression and return its type"""
        expr_type = self.parse_term()
        
        # Continue parsing terms if there are + or - operators
        while self.current_token is not None and self.current_token[0] in ['+', '-']:
            operator = self.current_token[0]
            self.next_token()  # Move past operator
            
            # Skip spaces
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
            
            # Get the next term
            term_type = self.parse_term()
            
            # Check type compatibility
            if expr_type in ['dose', 'quant'] and term_type in ['dose', 'quant']:
                # If any term is quant, the result is quant
                if expr_type == 'quant' or term_type == 'quant':
                    expr_type = 'quant'
            elif expr_type == 'seq' and term_type == 'seq' and operator == '+':
                # String concatenation is allowed
                expr_type = 'seq'
            else:
                self.errors.append(f"Semantic Error: Operator '{operator}' cannot be used with types {expr_type} and {term_type}")
        
        return expr_type
    
    def parse_term(self):
        """Parse a term (factor followed by * or / or % operators)"""
        factor_type = self.parse_factor()
        
        # Continue parsing factors if there are *, / or % operators
        while self.current_token is not None and self.current_token[0] in ['*', '/', '%']:
            operator = self.current_token[0]
            self.next_token()  # Move past operator
            
            # Skip spaces
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
            
            # Get the next factor
            next_factor_type = self.parse_factor()
            
            # Check type compatibility - only numeric types can use these operators
            if factor_type in ['dose', 'quant'] and next_factor_type in ['dose', 'quant']:
                # If any factor is quant, the result is quant
                if factor_type == 'quant' or next_factor_type == 'quant':
                    factor_type = 'quant'
                
                # Special case for division - always results in quant type
                if operator == '/':
                    factor_type = 'quant'
                    
                # For dose type, ensure no division by zero issues
                if operator in ['/', '%'] and next_factor_type == 'dose':
                    # Check if we know the value at compile time
                    # This is a common semantic check for division operations
                    if (self.current_token is not None and 
                        self.current_token[1] == 'Identifier' and 
                        self.current_token[0] in self.symbol_table and 
                        self.symbol_table[self.current_token[0]]['value'] == 0):
                        self.errors.append(f"Semantic Error: Division by zero detected with operator '{operator}'")
            else:
                self.errors.append(f"Semantic Error: Operator '{operator}' can only be used with numeric types, not {factor_type} and {next_factor_type}")
        
        return factor_type
    
    def parse_factor(self):
        """Parse a factor (variable, literal, or parenthesized expression)"""
        if self.current_token is None:
            self.errors.append("Semantic Error: Unexpected end of tokens in expression")
            return None
            
        factor_type = None
        
        # Handle identifier
        if self.current_token[1] == 'Identifier':
            var_name = self.current_token[0]
            if var_name in self.symbol_table:
                factor_type = self.symbol_table[var_name]['type']
            else:
                self.errors.append(f"Semantic Error: Variable '{var_name}' used before declaration")
                factor_type = 'unknown'  # Use a placeholder type
            self.next_token()  # Move past identifier
            
        # Handle numeric literal
        elif self.current_token[1] == 'numlit':
            if '.' in self.current_token[0]:
                factor_type = 'quant'
            else:
                factor_type = 'dose'
            self.next_token()  # Move past number
            
        # Handle string literal
        elif self.current_token[1] == 'string literal':
            factor_type = 'seq'
            self.next_token()  # Move past string
            
        # Handle boolean literal
        elif self.current_token[0] in ['dom', 'rec']:
            factor_type = 'allele'
            self.next_token()  # Move past boolean
            
        # Handle seq() conversion function
        elif self.current_token[1] == 'seq':
            self.next_token()  # Move past 'seq'
            
            # Skip spaces
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
            
            # Check for opening parenthesis
            if self.current_token is None or self.current_token[0] != '(':
                self.errors.append(f"Semantic Error: Expected '(' after 'seq', found {self.current_token}")
                return 'unknown'
                
                
            self.next_token()  # Move past '('
            
            # Skip spaces
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
            
            # Parse the expression to convert
            inner_type = self.parse_expression()
            
            # We return seq type regardless of the inner type - it's a conversion function
            factor_type = 'seq'
            
            # Skip spaces
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
            
            # Check for closing parenthesis
            if self.current_token is None or self.current_token[0] != ')':
                self.errors.append(f"Semantic Error: Expected ')' after seq argument, found {self.current_token}")
                return factor_type
                
            self.next_token()  # Move past ')'
            
        # Handle stimuli function (user input)
        elif self.current_token[1] == 'stimuli':
            self.next_token()  # Move past 'stimuli'
            
            # Skip spaces
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
            
            # Check for opening parenthesis
            if self.current_token is None or self.current_token[0] != '(':
                self.errors.append(f"Semantic Error: Expected '(' after 'stimuli', found {self.current_token}")
                return 'unknown'
                
            self.next_token()  # Move past '('
            
            # Skip spaces
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
            
            # Check for prompt message (string literal)
            if self.current_token is None or self.current_token[1] != 'string literal':
                self.errors.append(f"Semantic Error: Expected string literal for input prompt, found {self.current_token}")
                # Skip to closing parenthesis to continue parsing
                while self.current_token is not None and self.current_token[0] != ')':
                    self.next_token()
            else:
                # Process the prompt message
                self.next_token()  # Move past string literal
            
            # Skip spaces
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
            
            # Check for closing parenthesis
            if self.current_token is None or self.current_token[0] != ')':
                self.errors.append(f"Semantic Error: Expected ')' after input prompt, found {self.current_token}")
                return 'unknown'
                
            self.next_token()  # Move past ')'
            
            # At parse time, we assume stimuli returns a string by default
            factor_type = 'seq'
            
            # If this is part of an assignment, we need to check the target variable type
            if hasattr(self, 'current_assignment_type'):
                target_type = self.current_assignment_type
                if target_type == 'dose':
                    # Allow conversion from string to dose (integer)
                    factor_type = 'dose'
                elif target_type == 'quant':
                    # Allow conversion from string to quant (float)
                    factor_type = 'quant'
                elif target_type == 'seq':
                    # Keep as string
                    factor_type = 'seq'
                else:
                    self.errors.append(f"Semantic Error: Cannot assign stimuli input to {target_type} variable")
        
        # Handle parenthesized expression
        elif self.current_token[0] == '(':
            self.next_token()  # Move past '('
            factor_type = self.parse_expression()  # Recursively parse the inner expression
            
            # Check for closing parenthesis
            if self.current_token is None or self.current_token[0] != ')':
                self.errors.append(f"Semantic Error: Expected ')' after expression, found {self.current_token}")
            else:
                self.next_token()  # Move past ')'
                
        else:
            self.errors.append(f"Semantic Error: Unexpected token in expression: {self.current_token}")
            self.next_token()  # Skip invalid token
            factor_type = 'unknown'  # Use a placeholder type
            
        return factor_type

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
        self.parse_condition()
        
        # Check for semicolon
        if self.current_token is None or self.current_token[0] != ';':
            self.errors.append(f"Semantic Error: Expected ';' after for loop condition, found {self.current_token}")
            return
            
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
                    
            self.next_token()  # Move past identifier

            # Check for ++ or -- operators which may be tokenized either as '++', '--' or as separate + or - tokens
            if self.current_token is None:
                self.errors.append("Semantic Error: Unexpected end of tokens in for loop update")
            elif self.current_token[0] in ['++', '--']:
                # Handle pre-tokenized increment/decrement operators
                self.next_token()  # Move past the operator
            elif self.current_token[0] in ['+', '-']:
                # Store the first + or - character
                first_char = self.current_token[0]
                self.next_token()  # Move to next token
                
                # Skip spaces
                while self.current_token is not None and self.current_token[1] == 'space':
                    self.next_token()  # Move past space
                
                # Check if next token is the same (++ or --)
                if self.current_token is None or self.current_token[0] != first_char:
                    self.errors.append(f"Semantic Error: Expected '{first_char}{first_char}' in for loop update, found incomplete operator")
                else:
                    self.next_token()  # Move past the second + or - character
            else:
                self.errors.append(f"Semantic Error: Expected increment/decrement operator in for loop update, found {self.current_token}")
                self.next_token()  # Skip the current token
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
        """Parse express statement (print statement) that can handle multiple values"""
        self.next_token()  # Move past 'express'
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
        
        # Check for opening parenthesis
        if self.current_token is None or self.current_token[0] != '(':
            self.errors.append(f"Semantic Error: Expected '(' after 'express', found {self.current_token}")
            # Try to recover by skipping to semicolon if possible
            while self.current_token is not None and self.current_token[0] != ';':
                self.next_token()
            if self.current_token is not None:
                self.next_token()  # Move past semicolon
            return
            
        self.next_token()  # Move past '('
        
        # Process and collect all expressions to be printed
        express_values = []
        
        # Process the first expression
        if self.current_token is not None and self.current_token[0] != ')':
            # Parse the expression
            if self.current_token[1] == 'Identifier':
                var_name = self.current_token[0]
                if var_name in self.symbol_table:
                    var_value = self.symbol_table[var_name].get('value', 'undefined')
                    express_values.append(f"{var_name}: {var_value}")
                else:
                    self.errors.append(f"Semantic Error: Variable '{var_name}' used before declaration")
                    express_values.append(f"{var_name}: undefined")
                self.next_token()  # Move past identifier
            elif self.current_token[1] in ['numlit', 'string literal', 'dom', 'rec']:
                express_values.append(str(self.current_token[0]))
                self.next_token()  # Move past literal
            else:
                # For other tokens, just add them as is
                express_values.append(str(self.current_token[0]))
                self.next_token()  # Move past token
                
            # Handle comma-separated values
            while self.current_token is not None and self.current_token[0] == ',':
                self.next_token()  # Move past comma
                
                # Skip spaces
                while self.current_token is not None and self.current_token[1] == 'space':
                    self.next_token()
                    
                if self.current_token is not None and self.current_token[0] != ')':
                    if self.current_token[1] == 'Identifier':
                        var_name = self.current_token[0]
                        if var_name in self.symbol_table:
                            var_value = self.symbol_table[var_name].get('value', 'undefined')
                            express_values.append(f"{var_name}: {var_value}")
                        else:
                            self.errors.append(f"Semantic Error: Variable '{var_name}' used before declaration")
                            express_values.append(f"{var_name}: undefined")
                        self.next_token()  # Move past identifier
                    elif self.current_token[1] in ['numlit', 'string literal', 'dom', 'rec']:
                        express_values.append(str(self.current_token[0]))
                        self.next_token()  # Move past literal
                    else:
                        # For other tokens, just add them as is
                        express_values.append(str(self.current_token[0]))
                        self.next_token()  # Move past token
        
        # Check for closing parenthesis
        if self.current_token is None or self.current_token[0] != ')':
            self.errors.append(f"Semantic Error: Expected ')' in express statement, found {self.current_token}")
            # Try to recover by skipping to semicolon if possible
            while self.current_token is not None and self.current_token[0] != ';':
                self.next_token()
            if self.current_token is not None:
                self.next_token()  # Move past semicolon
            return
        
        self.next_token()  # Move past ')'
        
        # Check for semicolon
        if self.current_token is None or self.current_token[0] != ';':
            self.errors.append(f"Semantic Error: Expected ';' after express statement, found {self.current_token}")
            # Try to recover by skipping to semicolon if possible
            while self.current_token is not None and self.current_token[0] != ';':
                self.next_token()
            if self.current_token is not None:
                self.next_token()  # Move past semicolon
            return
            
        self.next_token()  # Move past ';'
        
        # Store the express statement for output in the semantic panel
        if hasattr(self, 'express_outputs'):
            self.express_outputs.append(express_values)
        else:
            self.express_outputs = [express_values]

    def expr(self):
        """Parse an expression, which could be a variable, literal, or a chain of operations"""
        if self.current_token is None:
            self.errors.append("Semantic Error: Unexpected end of tokens in expression")
            return
            
        # First parse the first operand
        self.parse_operand()
        
        # Then handle any following operations in a loop
        while self.current_token is not None and self.current_token[0] in ['+', '-', '*', '/', '%', '&&', '||']:
            operator = self.current_token[0]
            self.next_token()  # Move past operator
            
            # Skip spaces after operator
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
                
            # Parse the next operand
            self.parse_operand()
            
    def parse_operand(self):
        """Parse a single operand (variable, literal, or parenthesized expression)"""
        # Skip spaces before operand
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
            
        if self.current_token is None:
            self.errors.append("Semantic Error: Expected operand but found end of tokens")
            return
            
        # Variable
        if self.current_token[1] == 'Identifier':
            var_name = self.current_token[0]
            if var_name not in self.symbol_table:
                self.errors.append(f"Semantic Error: Variable '{var_name}' used in expression before declaration")
            
            self.next_token()  # Move past identifier
                
        # Number literal
        elif self.current_token[1] == 'numlit':
            self.next_token()  # Move past number
                
        # String literal
        elif self.current_token[1] == 'string literal':
            self.next_token()  # Move past string
                
        # Boolean literal (dom/rec)
        elif self.current_token[0] in ['dom', 'rec']:
            self.next_token()  # Move past boolean
            
        # Handle stimuli function
        elif self.current_token[1] == 'stimuli':
            self.next_token()  # Move past 'stimuli'
            
            # Skip spaces
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
            
            # Check for opening parenthesis
            if self.current_token is None or self.current_token[0] != '(':
                self.errors.append(f"Semantic Error: Expected '(' after 'stimuli', found {self.current_token}")
                return
                
            self.next_token()  # Move past '('
            
            # Skip spaces
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
            
            # Check for prompt message (string literal)
            if self.current_token is None or self.current_token[1] != 'string literal':
                self.errors.append(f"Semantic Error: Expected string literal for input prompt, found {self.current_token}")
                return
                
            prompt = self.current_token[0].strip('"\'')  # Store the prompt message
            self.next_token()  # Move past string literal
            
            # Skip spaces
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
            
            # Check for closing parenthesis
            if self.current_token is None or self.current_token[0] != ')':
                self.errors.append(f"Semantic Error: Expected ')' after input prompt, found {self.current_token}")
                return
                
            self.next_token()  # Move past ')'
            
            # Store the prompt for runtime input
            if not hasattr(self, 'pending_inputs'):
                self.pending_inputs = []
            self.pending_inputs.append(prompt)
            
        # Parenthesized expression
        elif self.current_token[0] == '(':
            self.next_token()  # Move past '('
            self.expr()  # Parse inner expression
            
            # Check for closing parenthesis
            if self.current_token is None or self.current_token[0] != ')':
                self.errors.append(f"Semantic Error: Expected ')' but found {self.current_token}")
            else:
                self.next_token()  # Move past ')'
                
        else:
            self.errors.append(f"Semantic Error: Unexpected token in expression: {self.current_token}")
            self.next_token()  # Skip invalid token
        
        # Skip spaces after operand
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()

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

    def skip_to_end_of_block(self):
        """
        Helper method to skip tokens until the end of the current block.
        This is used for error recovery.
        """
        # Look for matching closing braces
        brace_count = 1  # Start with 1 assuming we're inside a block
        
        while self.current_token is not None and brace_count > 0:
            if self.current_token[0] == '{':
                brace_count += 1
            elif self.current_token[0] == '}':
                brace_count -= 1
                
            self.next_token()
            
        # Now we should be at the token after the closing brace
        # or at the end of tokens


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
    elif type_name.startswith('array_'):
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
        # If there are pending inputs, handle them directly
        if analyzer.pending_inputs:
            for prompt in analyzer.pending_inputs:
                # Store the prompt in the semantic panel
                semantic_panel.insert(tk.END, f"{prompt}\n")
                # For now, we'll use a default value of 0 for dose variables
                for var_name, var_info in analyzer.symbol_table.items():
                    if var_info.get('type') == 'dose' and var_info.get('value') == 'undefined':
                        analyzer.symbol_table[var_name]['value'] = 0
                        break
                
                # After getting input, re-run the analysis to update the output
                analyzer.parse()
                display_results(analyzer, semantic_panel)
        else:
            display_results(analyzer, semantic_panel)
        
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
        
        return False

def display_results(analyzer, semantic_panel):
    """Helper function to display analysis results"""
    semantic_panel.delete("1.0", tk.END)
    
    # Check if there are any errors first
    if analyzer.errors:
        semantic_panel.insert(tk.END, "Semantic Analysis: Errors found.\n\n")
        for error in analyzer.errors:
            semantic_panel.insert(tk.END, f"{error}\n")
    else:
        semantic_panel.insert(tk.END, "Semantic Analysis: No errors found.\n\n")
    
    # Check if there are any express outputs to display
    if hasattr(analyzer, 'express_outputs') and analyzer.express_outputs:
        semantic_panel.insert(tk.END, "Express Output:\n")
        for i, express_values in enumerate(analyzer.express_outputs):
            if i > 0:
                semantic_panel.insert(tk.END, "\n")  # Add line between multiple express statements
            
            # Format the express values for display
            output_line = "  "
            for j, value in enumerate(express_values):
                if j > 0:
                    output_line += ", "
                output_line += str(value)
            
            semantic_panel.insert(tk.END, output_line)
        
        semantic_panel.insert(tk.END, "\n\n")
    
    # Display symbol table
    semantic_panel.insert(tk.END, "Variables:\n")
    for var_name, var_info in analyzer.symbol_table.items():
        # Skip the special express_output entry when displaying variables
        if var_name == 'express_output':
            continue
            
        var_type = var_info.get('type', 'unknown')
        var_value = var_info.get('value', 'undefined')
        
        # Format value display
        value_display = var_value
        if var_type == 'quant' and isinstance(var_value, float) and var_value == int(var_value):
            # Display whole numbers without decimal point
            value_display = int(var_value)
        
        semantic_panel.insert(tk.END, f"  {var_name} ({var_type}): {value_display}\n")
    
    # Display function table if any functions were defined
    if analyzer.functions:
        semantic_panel.insert(tk.END, "\nFunction Table:\n")
        
        for func_name, func_info in analyzer.functions.items():
            return_type = func_info.get('return_type', 'void')
            params = func_info.get('parameters', [])
            
            semantic_panel.insert(tk.END, f"  {func_name}: {return_type}\n")
            
            if params:
                param_str = "  Parameters: "
                for i, param in enumerate(params):
                    if i > 0:
                        param_str += ", "
                    param_str += f"{param['name']} ({param['type']})"
                semantic_panel.insert(tk.END, param_str + "\n")
            else:
                semantic_panel.insert(tk.END, f"  Parameters: None\n")
