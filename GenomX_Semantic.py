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
        self.global_symbol_table = symbol_table if symbol_table is not None else {}
        self.function_scopes = {}  # Store function-specific symbol tables
        self.current_function = None  # Track the current function being processed
        self.symbol_table = self.global_symbol_table  # Initially use global scope
        self.token_index = 0
        self.errors = []
        self.functions = {}  # Track function definitions
        self.current_line = 1  # Track line numbers for better error reporting
        self.in_loop = False  # Track if we're inside a loop for break/continue validation
        self.current_assignment_type = None  # Track the type of the current assignment
        self.next_token()
        self.pending_inputs = []  # Add this line to store pending inputs
        self.express_outputs = []  # Add this line to store express outputs
        self._condition_nesting_level = 0  # Track nesting level for condition parsing

    def next_token(self):
        while self.token_index < len(self.tokens) and self.tokens[self.token_index][1] in ["space", "tab", "newline"]:
            self.token_index += 1  # Skip spaces, tabs, and newlines
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
            elif self.current_token[1] == 'perms' or self.current_token[0] == 'perms':
                self.perms_declaration()
            elif self.current_token[1] == 'space':
                self.next_token()
            else:
                # self.errors.append(f"Semantic Error: Unexpected token: {self.current_token[1]}")
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
        
        # Check if function name already exists in symbol table (as a variable)
        if function_name in self.global_symbol_table:
            self.errors.append(f"Semantic Error: Function name '{function_name}' already used as a variable")
            return
        
        # Check if function name exists in any function scope
        for scope_name, scope in self.function_scopes.items():
            if function_name in scope:
                self.errors.append(f"Semantic Error: Function name '{function_name}' already used as a variable in function '{scope_name}'")
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
            # For regular functions, determine the return type
            if function_type == 'void':
                return_type = 'void'
                return_types = []
            else:
                # For functions with parameters, each parameter type can be a return type
                if parameters:
                    # Use the type of the first parameter as primary return type (for compatibility)
                    return_type = parameters[0]['type']
                    # Create a list of all parameter types as potential return types
                    return_types = [param['type'] for param in parameters]
                else:
                    # For functions with no parameters, use 'regular' as the return type
                    return_type = 'regular'
                    return_types = [return_type]
                    
            # Support for multiple return values
            self.functions[function_name] = {
                'return_type': return_type,                # Primary return type (first parameter) for backward compatibility
                'parameters': parameters,                  # Parameters list
                'multiple_returns': len(parameters) > 1,   # Set to true if function has multiple parameters
                'return_types': return_types               # Array of potential return types (matches parameters)
            }
        
        # Enter function scope
        self.enter_function_scope(function_name)
        
        # Add parameters to function scope
        for param in parameters:
            self.symbol_table[param['name']] = {
                'scope': 'parameter',
                'type': param['type'],
                'value': get_default_value_for_type(param['type'])
            }
                                         
        # Parse the body statements
        self.parse_body_statements()  # Parse the function body
        
        # Exit function scope
        self.exit_function_scope()
        
        # Check for '}'
        if self.current_token is None or self.current_token[0] != '}':
            self.errors.append(f"Semantic Error: Expected '}}' at end of function body, found {self.current_token}")
            return
        self.next_token()  # Move past '}'
        print(f"Finished parsing function: {function_name}")

    # Parameter Passing
    def check_parameter_passing(self, function_name, args):
        """Check if arguments match function parameters"""
        if function_name not in self.functions:
            self.errors.append(f"Semantic Error: Function '{function_name}' not defined")
            return False

        func_info = self.functions[function_name]
        expected_params = func_info['parameters']

        # Check number of arguments matches parameters
        if len(args) != len(expected_params):
            # Only report an error if the function has parameters but was called with a different number
            # Allow calling a no-parameter function with no arguments
            if not (len(expected_params) == 0 and len(args) == 0):
                self.errors.append(f"Semantic Error: Function '{function_name}' expects {len(expected_params)} arguments but got {len(args)}")
                return False

        # If there are no parameters, nothing to check further
        if len(expected_params) == 0:
            return True

        # Get expected return types for the function
        expected_return_types = func_info.get('return_types', [])
        is_multi_return = func_info.get('multiple_returns', False) or len(expected_return_types) > 1
        
        # If we have multiple returns but no return_types yet, initialize them from parameters
        if not expected_return_types and len(expected_params) > 1:
            expected_return_types = [param['type'] for param in expected_params]
            func_info['return_types'] = expected_return_types

        # Check each argument matches parameter type
        for i, (arg, param) in enumerate(zip(args, expected_params)):
            arg_name = arg['name']
            param_type = param['type']
            param_name = param['name']
            arg_type = arg['type']
            arg_value = arg.get('value', None)

            # Get the expected return type for this parameter index
            expected_return_type = expected_return_types[i] if i < len(expected_return_types) else param_type

            # Check type compatibility - with the correct expected type for this position
            if arg_type != param_type:
                # Special cases for type compatibility
                if param_type == 'quant' and arg_type == 'dose':
                    # Allow dose to be passed to quant parameter (implicit conversion)
                    pass
                elif param_type == 'seq' and arg_type == 'chr':
                    # Allow character to be passed to string parameter (implicit conversion)
                    pass
                elif param_type == 'allele' and arg_type in ['dose', 'quant']:
                    # Allow numeric types to be converted to boolean (non-zero = dom, zero = rec)
                    pass
                else:
                    self.errors.append(f"Semantic Error: Function '{function_name}' parameter {i+1} ('{param_name}') expects {param_type} but got {arg_type}")
                    return False
            
            # Store the argument value in a temporary variable for this function call
            # This helps with tracking parameter values during semantic analysis
            temp_param_var = f"_{function_name}_{param_name}"
            self.symbol_table[temp_param_var] = {
                'type': param_type,
                'value': arg_value,
                'is_parameter': True,
                'original_var': arg_name
            }

        return True
    def perms_declaration(self):
        """Parse perms declaration (constants that must be initialized)"""
        self.next_token()  # Move past 'perms'
        
        # Get the scope from the stored current_scope if it exists, otherwise use 'constant'
        scope = getattr(self, 'current_scope', 'constant')
        
        # Reset current_scope for future use
        if hasattr(self, 'current_scope'):
            delattr(self, 'current_scope')
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
            
        # Get the data type
        if self.current_token is None or self.current_token[1] not in ['dose', 'quant', 'seq', 'allele']:
            self.errors.append(f"Semantic Error: Expected data type after 'perms', found {self.current_token}")
            return
            
        var_type = self.current_token[1]
        self.next_token()  # Move past type

        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
        
        # Process multiple perms declarations separated by commas
        while True:
            # Get constant name
            if self.current_token is None or self.current_token[1] != 'Identifier':
                self.errors.append(f"Semantic Error: Expected identifier after type in perms declaration, found {self.current_token}")
                return

            const_name = self.current_token[0]
            
            # Check for redeclaration
            if const_name in self.symbol_table:
                self.errors.append(f"Semantic Error: Constant '{const_name}' already declared")
                
            # Check if constant name already exists as a function name
            if const_name in self.functions:
                self.errors.append(f"Semantic Error: Constant name '{const_name}' already used as a function")
                
            self.next_token()  # Move past identifier

            # Skip spaces
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
                
            # Check for assignment (required for perms)
            if self.current_token is None or self.current_token[0] != '=':
                self.errors.append(f"Semantic Error: Perms declaration for '{const_name}' requires initialization with '='")
                return
                
            self.next_token()  # Move past '='
            
            # Skip spaces
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
                
            # Set the current assignment type for type checking
            self.current_assignment_type = var_type
            
            # Collect tokens for the expression until semicolon or comma
            expression_tokens = []
            
            while self.current_token is not None and self.current_token[0] != ';' and self.current_token[0] != ',':
                expression_tokens.append(self.current_token)
                self.next_token()
            
            # Check if there's an initialization value
            if not expression_tokens:
                self.errors.append(f"Semantic Error: Perms declaration for '{const_name}' requires a value")
                return
                
            # Evaluate the expression for the constant
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
                            value = assigned_value
                        else:
                            self.errors.append(f"Semantic Error: Cannot assign {assigned_type} value to {var_type} perms '{const_name}'")
                            value = None
                    else:
                        self.errors.append(f"Semantic Error: Variable '{var_to_assign}' used before declaration")
                        value = None
                
                # Handle literals
                elif token[1] == 'numlit':
                    if var_type == 'dose':
                        try:
                            value = int(token[0])
                        except:
                            self.errors.append(f"Semantic Error: Cannot convert {token[0]} to integer for dose perms '{const_name}'")
                            value = 0
                    elif var_type == 'quant':
                        try:
                            value = float(token[0])
                        except:
                            self.errors.append(f"Semantic Error: Cannot convert {token[0]} to float for quant perms '{const_name}'")
                            value = 0.0
                    else:
                        self.errors.append(f"Semantic Error: Cannot assign numeric value to {var_type} perms '{const_name}'")
                        value = None
                
                elif token[1] == 'string literal':
                    if var_type == 'seq':
                        # Remove quotation marks
                        value = token[0].strip('"\'')
                    else:
                        self.errors.append(f"Semantic Error: Cannot assign string value to {var_type} perms '{const_name}'")
                        value = None
                
                elif token[0] in ['dom', 'rec']:
                    if var_type == 'allele':
                        value = (token[0] == 'dom')
                    else:
                        self.errors.append(f"Semantic Error: Cannot assign boolean value to {var_type} perms '{const_name}'")
                        value = None
                else:
                    self.errors.append(f"Semantic Error: Invalid value for perms '{const_name}'")
                    value = None
            
            # Handle complex expressions
            elif len(expression_tokens) > 1:
                # Only handle arithmetic expressions for numeric types
                if var_type in ['dose', 'quant']:
                    expr_str = ""
                    valid_expression = True
                    
                    # Track if division is used, which forces quant result type
                    contains_division = False
                    
                    # Check for string literals or seq variables in numeric expressions
                    has_string_operand = False
                    for token in expression_tokens:
                        if token[1] == 'string literal':
                            has_string_operand = True
                            self.errors.append(f"Semantic Error: Cannot use string '{token[0]}' in arithmetic expression for {var_type} variable '{var_name}'")
                            valid_expression = False
                            break
                        elif token[1] == 'Identifier':
                            if token[0] in self.symbol_table:
                                if self.symbol_table[token[0]]['type'] == 'seq':
                                    has_string_operand = True
                                    self.errors.append(f"Semantic Error: Cannot use string variable '{token[0]}' in arithmetic expression for {var_type} variable '{var_name}'")
                                    valid_expression = False
                                    break
                            elif token[0] in self.global_symbol_table:
                                if self.global_symbol_table[token[0]]['type'] == 'seq':
                                    has_string_operand = True
                                    self.errors.append(f"Semantic Error: Cannot use string variable '{token[0]}' in arithmetic expression for {var_type} variable '{var_name}'")
                                    valid_expression = False
                                    break
                    
                    # If there are string operands, don't proceed with evaluating the expression
                    if has_string_operand:
                        self.symbol_table[var_name]['value'] = 0 if var_type == 'dose' else 0.0
                        continue
                    
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
                            pass
                        # Check for division by zero
                        if contains_division and '/' in expr_str:
                            try:
                                # This is just a simple check - a more robust solution would parse the expression
                                eval(expr_str.replace('/', '//'))
                            except ZeroDivisionError:
                                self.errors.append(f"Semantic Error: Division by zero in expression for variable '{var_name}'")
                            except:
                                pass
                
                # Handle string concatenation for seq type
                elif var_type == 'seq':
                    result = ""
                    valid_expression = True
                    
                    for i, token in enumerate(expression_tokens):
                        if token[0] == '+':
                            continue
                        elif token[1] == 'string literal':
                            result += token[0].strip('"\'')
                        elif token[1] == 'Identifier' and token[0] in self.symbol_table:
                            if self.symbol_table[token[0]]['type'] == 'seq':
                                result += str(self.symbol_table[token[0]]['value'])
                        elif token[1] == 'space':
                            continue
                        else:
                            self.errors.append(f"Semantic Error: Invalid token '{token[0]}' in perms string expression")
                            valid_expression = False
                            break
                    
                    if valid_expression:
                        value = result
                    else:
                        value = ""
                else:
                    self.errors.append(f"Semantic Error: Complex expressions not supported for {var_type} perms")
                    value = None
            else:
                self.errors.append(f"Semantic Error: Empty expression for perms '{const_name}'")
                value = None
                
            # Add to symbol table
            self.symbol_table[const_name] = {
                'scope': scope,       # Use the scope we determined earlier
                'type': var_type,
                'value': value,
                'is_perms': True      # Mark as a perms constant
            }
            
            # Check if we need to continue for multiple perms declarations
            if self.current_token is None or self.current_token[0] != ',':
                break
                
            self.next_token()  # Move past comma
            
            # Skip spaces
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
        
        # Check for semicolon
        if self.current_token is None or self.current_token[0] != ';':
            self.errors.append(f"Semantic Error: Expected ';' after perms declaration, found {self.current_token}")
        else:
            self.next_token()  # Move past semicolon
    def prod_statement(self):
        """Parse prod statement (return statement) and check type compatibility"""
        self.next_token()  # Move past 'prod'
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
        
        # Check if we're in a function
        if not self.functions:
            self.errors.append("Semantic Error: 'prod' statement can only be used inside a function")
            return
            
        # Get the current function's return type
        current_function = None
        return_type = None
        if self.functions:
            current_function = list(self.functions.keys())[-1]
            function_info = self.functions[current_function]
            return_type = function_info['return_type']
            
            # Get expected return types and track which ones have been returned
            is_multi_return = function_info.get('multiple_returns', False)
            expected_return_types = function_info.get('return_types', [])
            
            # Initialize returned values tracking if not present
            if 'returned_indexes' not in function_info:
                function_info['returned_indexes'] = set()
            
        # Handle void functions (no return value)
        if return_type == 'void':
            # Void functions should not return a value
            if self.current_token is not None and self.current_token[0] != ';':
                self.errors.append("Semantic Error: Void function cannot return a value")
                
                # Skip until semicolon
                while self.current_token is not None and self.current_token[0] != ';':
                    self.next_token()
            return
            
        # Parse the expression being returned
        value_type = self.parse_expression()
        
        # For functions with multiple expected return values
        if is_multi_return and expected_return_types:
            # Get the value being returned in this prod statement
            if self.current_token is not None and self.current_token[1] == 'Identifier':
                returned_var = self.current_token[0]
                
                # Find which parameter this corresponds to
                parameter_index = -1
                for i, param in enumerate(function_info['parameters']):
                    if param['name'] == returned_var:
                        parameter_index = i
                        break
                
                # If we found a matching parameter, mark it as returned
                if parameter_index >= 0:
                    function_info['returned_indexes'].add(parameter_index)
                    
                    # Check that the return type matches the parameter type
                    expected_type = expected_return_types[parameter_index]
                    if value_type != expected_type:
                        # Allow certain implicit conversions
                        if not ((expected_type == 'quant' and value_type == 'dose') or
                               (expected_type == 'seq' and value_type == 'chr') or
                               (expected_type == 'allele' and value_type in ['dose', 'quant'])):
                            self.errors.append(f"Semantic Error: Function's return value for parameter '{returned_var}' should be {expected_type} but got {value_type}")
                else:
                    # Handle the case where the returned value doesn't match a parameter name
                    # Find the first unused expected return type
                    for i, expected_type in enumerate(expected_return_types):
                        if i not in function_info['returned_indexes']:
                            function_info['returned_indexes'].add(i)
                            
                            # Check type compatibility
                            if value_type != expected_type:
                                # Allow certain implicit conversions
                                if not ((expected_type == 'quant' and value_type == 'dose') or
                                       (expected_type == 'seq' and value_type == 'chr') or
                                       (expected_type == 'allele' and value_type in ['dose', 'quant'])):
                                    self.errors.append(f"Semantic Error: Function's return value at position {i+1} should be {expected_type} but got {value_type}")
                            break
            else:
                # For literal values or complex expressions, find the first unused expected return type
                for i, expected_type in enumerate(expected_return_types):
                    if i not in function_info['returned_indexes']:
                        function_info['returned_indexes'].add(i)
                        
                        # Check type compatibility
                        if value_type != expected_type:
                            # Allow certain implicit conversions
                            if not ((expected_type == 'quant' and value_type == 'dose') or
                                   (expected_type == 'seq' and value_type == 'chr') or
                                   (expected_type == 'allele' and value_type in ['dose', 'quant'])):
                                self.errors.append(f"Semantic Error: Function's return value at position {i+1} should be {expected_type} but got {value_type}")
                        break
        else:
            # Single return value - check against the function's primary return type
            if value_type != return_type:
                # Allow dose to be returned from a quant function
                if not (return_type == 'quant' and value_type == 'dose'):
                    self.errors.append(f"Semantic Error: Function returns {return_type} but got {value_type}")
        
        # Check for semicolon
        if self.current_token is None or self.current_token[0] != ';': 
            self.errors.append(f"Semantic Error: Expected ';' after prod statement, found {self.current_token}")
            return
            # GIT PUSH
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
            # Skip to end of statement for error recovery
            while self.current_token is not None and self.current_token[0] != ';':
                self.next_token()
            if self.current_token is not None:
                self.next_token()  # Move past ';'
            return
        
        function_name = self.current_token[0]  # Store the function name
        
        self.next_token()  # Move past function name
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
        
        # Parse arguments - in your GenomeX language, arguments can be with or without parentheses
        args = []
        
        # First check if there are parentheses (optional syntax)
        has_parentheses = False
        if self.current_token is not None and self.current_token[0] == '(':
            has_parentheses = True
            self.next_token()  # Move past '('
            
            # Check for empty parameter list (directly followed by a closing parenthesis)
            if self.current_token is not None and self.current_token[0] == ')':
                # Handle the case of func Multiply(); - empty parameter list
                self.next_token()  # Move past ')'
                # Validate against the function definition
                self.check_parameter_passing(function_name, args)
                
                # Check for semicolon
                if self.current_token is None or self.current_token[0] != ';':
                    self.errors.append(f"Semantic Error: Expected ';' after function call, found {self.current_token}")
                    return
                    
                self.next_token()  # Move past ';'
                return
        
        # For cases like: func Multiply(Number);
        if has_parentheses:
            # Parse arguments inside parentheses
            while self.current_token is not None and self.current_token[0] != ')':
                # Skip spaces
                while self.current_token is not None and self.current_token[1] == 'space':
                    self.next_token()
                
                # Check if we've reached the end of arguments
                if self.current_token is not None and self.current_token[0] == ')':
                    break
                
                # Get argument - can be variable name or literal value
                if self.current_token[1] == 'Identifier':
                    # Variable as argument
                    arg_name = self.current_token[0]
                    
                    # Check if variable exists in symbol table
                    if arg_name in self.symbol_table:
                        arg_type = self.symbol_table[arg_name]['type']
                        arg_value = self.symbol_table[arg_name].get('value')
                    elif arg_name in self.global_symbol_table:
                        arg_type = self.global_symbol_table[arg_name]['type']
                        arg_value = self.global_symbol_table[arg_name].get('value')
                    else:
                        self.errors.append(f"Semantic Error: Variable '{arg_name}' used as argument before declaration")
                        # Skip to end of statement for error recovery
                        while self.current_token is not None and self.current_token[0] != ';':
                            self.next_token()
                        if self.current_token is not None:
                            self.next_token()  # Move past ';'
                        return
                    
                    # Add argument to the list
                    args.append({
                        'name': arg_name,
                        'type': arg_type,
                        'value': arg_value
                    })
                    
                elif self.current_token[1] == 'numlit':
                    # Numeric literal as argument
                    value = self.current_token[0]
                    
                    # Determine if it's an integer or float
                    if '.' in value:
                        arg_type = 'quant'
                        try:
                            arg_value = float(value)
                        except:
                            arg_value = 0.0
                    else:
                        arg_type = 'dose'
                        try:
                            arg_value = int(value)
                        except:
                            arg_value = 0
                    
                    # Add argument to the list
                    args.append({
                        'name': value,  # Use the literal value as name
                        'type': arg_type,
                        'value': arg_value
                    })
                    
                elif self.current_token[1] == 'string literal':
                    # String literal as argument
                    value = self.current_token[0].strip('"\'')
                    
                    # Add argument to the list
                    args.append({
                        'name': value,  # Use the literal value as name
                        'type': 'seq',
                        'value': value
                    })
                    
                elif self.current_token[0] in ['dom', 'rec']:
                    # Boolean literal as argument
                    value = self.current_token[0]
                    arg_value = (value == 'dom')
                    
                    # Add argument to the list
                    args.append({
                        'name': value,  # Use the literal value as name
                        'type': 'allele',
                        'value': arg_value
                    })
                    
                else:
                    self.errors.append(f"Semantic Error: Expected valid argument, found {self.current_token}")
                    # Skip to end of statement for error recovery
                    while self.current_token is not None and self.current_token[0] != ';':
                        self.next_token()
                    if self.current_token is not None:
                        self.next_token()  # Move past ';'
                    return
                
                self.next_token()  # Move past argument
                
                # Skip spaces
                while self.current_token is not None and self.current_token[1] == 'space':
                    self.next_token()
                
                # Check for comma or closing parenthesis
                if self.current_token is None:
                    self.errors.append("Semantic Error: Unexpected end of tokens in function arguments")
                    return
                
                if self.current_token[0] == ',':
                    self.next_token()  # Move past comma
                    continue
                elif self.current_token[0] != ')':
                    self.errors.append(f"Semantic Error: Expected ',' or ')' in function arguments, found {self.current_token}")
                    # Skip to end of statement for error recovery
                    while self.current_token is not None and self.current_token[0] != ';':
                        self.next_token()
                    if self.current_token is not None:
                        self.next_token()  # Move past ';'
                    return
            
            # Move past ')'
            if self.current_token is not None and self.current_token[0] == ')':
                self.next_token()
        # For cases like: func Multiply Number;
        else:
            # Check if there are any arguments after the function name (before semicolon)
            while self.current_token is not None and self.current_token[0] != ';':
                # Skip spaces
                while self.current_token is not None and self.current_token[1] == 'space':
                    self.next_token()
                
                # Check if we've reached the end
                if self.current_token is not None and self.current_token[0] == ';':
                    break
                    
                # Get argument - can be variable name or literal value
                if self.current_token[1] == 'Identifier':
                    # Variable as argument
                    arg_name = self.current_token[0]
                    
                    # Check if variable exists in symbol table
                    if arg_name in self.symbol_table:
                        arg_type = self.symbol_table[arg_name]['type']
                        arg_value = self.symbol_table[arg_name].get('value')
                    elif arg_name in self.global_symbol_table:
                        arg_type = self.global_symbol_table[arg_name]['type']
                        arg_value = self.global_symbol_table[arg_name].get('value')
                    else:
                        self.errors.append(f"Semantic Error: Variable '{arg_name}' used as argument before declaration")
                        # Skip to end of statement for error recovery
                        while self.current_token is not None and self.current_token[0] != ';':
                            self.next_token()
                        if self.current_token is not None:
                            self.next_token()  # Move past ';'
                        return
                    
                    # Add argument to the list
                    args.append({
                        'name': arg_name,
                        'type': arg_type,
                        'value': arg_value
                    })
                    
                elif self.current_token[1] == 'numlit':
                    # Numeric literal as argument
                    value = self.current_token[0]
                    
                    # Determine if it's an integer or float
                    if '.' in value:
                        arg_type = 'quant'
                        try:
                            arg_value = float(value)
                        except:
                            arg_value = 0.0
                    else:
                        arg_type = 'dose'
                        try:
                            arg_value = int(value)
                        except:
                            arg_value = 0
                    
                    # Add argument to the list
                    args.append({
                        'name': value,  # Use the literal value as name
                        'type': arg_type,
                        'value': arg_value
                    })
                    
                elif self.current_token[1] == 'string literal':
                    # String literal as argument
                    value = self.current_token[0].strip('"\'')
                    
                    # Add argument to the list
                    args.append({
                        'name': value,  # Use the literal value as name
                        'type': 'seq',
                        'value': value
                    })
                    
                elif self.current_token[0] in ['dom', 'rec']:
                    # Boolean literal as argument
                    value = self.current_token[0]
                    arg_value = (value == 'dom')
                    
                    # Add argument to the list
                    args.append({
                        'name': value,  # Use the literal value as name
                        'type': 'allele',
                        'value': arg_value
                    })
                else:
                    self.errors.append(f"Semantic Error: Expected valid argument, found {self.current_token}")
                    # Skip to end of statement for error recovery
                    while self.current_token is not None and self.current_token[0] != ';':
                        self.next_token()
                    if self.current_token is not None:
                        self.next_token()  # Move past ';'
                    return
                
                self.next_token()  # Move past argument
                
                # Skip spaces
                while self.current_token is not None and self.current_token[1] == 'space':
                    self.next_token()
                
                # Support for comma-separated arguments without parentheses
                if self.current_token is not None and self.current_token[0] == ',':
                    self.next_token()  # Move past comma
        
        # Validate parameter types and number
        self.check_parameter_passing(function_name, args)
        
        # Check for semicolon
        if self.current_token is None or self.current_token[0] != ';':
            # self.errors.append(f"Semantic Error: Expected ';' after function call, found {self.current_token}")

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
            
    def clust_declaration(self):
        
        """Parse clust declaration"""
        self.next_token()  # Move past 'clust'
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
            
        # Get element type
        if self.current_token is None or self.current_token[1] not in ['dose', 'quant', 'seq', 'allele']:
            self.errors.append(f"Semantic Error: Expected valid type after 'clust', found {self.current_token}")
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
        
        # Check for array size
        if self.current_token is None or self.current_token[0] != '[':
            self.errors.append(f"Semantic Error: Expected '[' for array size, found {self.current_token}")
            return
            
        self.next_token()  # Move past '['
        
        # Get array first dimension size
        if self.current_token is None or self.current_token[1] != 'numlit':
            self.errors.append(f"Semantic Error: Expected numeric value for array size, found {self.current_token}")
            return
            
        try:
            array_size1 = int(self.current_token[0])
            if array_size1 <= 0:
                self.errors.append(f"Semantic Error: Array size must be positive, found {array_size1}")
                return
        except ValueError:
            self.errors.append(f"Semantic Error: Invalid array size value, found {self.current_token}")
            return
            
        self.next_token()  # Move past size
        
        if self.current_token is None or self.current_token[0] != ']':
            self.errors.append(f"Semantic Error: Expected ']' after array size, found {self.current_token}")
            return
            
        self.next_token()  # Move past ']'
        
        # Check for second dimension (2D array)
        is_2d_array = False
        array_size2 = 0
        
        if self.current_token is not None and self.current_token[0] == '[':
            is_2d_array = True
            self.next_token()  # Move past '['
            
            # Get array second dimension size
            if self.current_token is None or self.current_token[1] != 'numlit':
                self.errors.append(f"Semantic Error: Expected numeric value for second array dimension, found {self.current_token}")
                return
                
            try:
                array_size2 = int(self.current_token[0])
                if array_size2 <= 0:
                    self.errors.append(f"Semantic Error: Array second dimension must be positive, found {array_size2}")
                    return
            except ValueError:
                self.errors.append(f"Semantic Error: Invalid array size value for second dimension, found {self.current_token}")
                return
                
            self.next_token()  # Move past size
            
            if self.current_token is None or self.current_token[0] != ']':
                self.errors.append(f"Semantic Error: Expected ']' after second array dimension, found {self.current_token}")
                return
                
            self.next_token()  # Move past ']'
        
        # Add to symbol table
        if is_2d_array:
            self.symbol_table[array_name] = {
                'type': f'2d_array_{element_type}',
                'value': [],
                'element_type': element_type,
                'size1': array_size1,
                'size2': array_size2,
                'is_2d': True
            }
        else:
            self.symbol_table[array_name] = {
                'type': f'array_{element_type}',
                'value': [],
                'element_type': element_type,
                'size': array_size1,
                'is_2d': False
            }
        
        # Check for assignment
        if self.current_token is not None and self.current_token[0] == '=':
            self.next_token()  # Move past '='
            
            # Check for array initializer
            if self.current_token is None or self.current_token[0] != '{':
                self.errors.append(f"Semantic Error: Expected '{{' for array initialization, found {self.current_token}")
                return
                
            self.next_token()  # Move past '{'
            
            if is_2d_array:
                # Parse 2D array elements
                all_elements = []
                row_count = 0
                
                while self.current_token is not None and self.current_token[0] != '}':
                    # Skip spaces and commas between rows
                    while self.current_token is not None and (self.current_token[1] == 'space' or self.current_token[0] == ','):
                        self.next_token()
                        
                    if self.current_token is None or self.current_token[0] == '}':
                        break
                        
                    # Expect '{' for row start
                    if self.current_token[0] != '{':
                        self.errors.append(f"Semantic Error: Expected '{{' for start of row in 2D array, found {self.current_token}")
                        return
                        
                    self.next_token()  # Move past '{'
                    
                    # Parse row elements
                    row_elements = []
                    while self.current_token is not None and self.current_token[0] != '}':
                        # Skip spaces and commas
                        while self.current_token is not None and (self.current_token[1] == 'space' or self.current_token[0] == ','):
                            self.next_token()
                            
                        if self.current_token is None or self.current_token[0] == '}':
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
                                # Handle ^ as negative sign for dose
                                if self.current_token[0].startswith('^'):
                                    row_elements.append(-int(self.current_token[0][1:]))
                                else:
                                    row_elements.append(int(self.current_token[0]))
                            except:
                                pass
                        elif element_type == 'quant':
                            try:
                                # Handle ^ as negative sign for quant
                                if self.current_token[0].startswith('^'):
                                    row_elements.append(-float(self.current_token[0][1:]))
                                else:
                                    row_elements.append(float(self.current_token[0]))
                            except:
                                pass
                        elif element_type == 'seq':
                            row_elements.append(self.current_token[0].strip('"\''))
                        elif element_type == 'allele':
                            row_elements.append(self.current_token[0] == 'dom')
                        
                        self.next_token()  # Move past element
                        
                        # Look for comma or closing brace
                        if self.current_token is None:
                            self.errors.append("Semantic Error: Unexpected end of tokens in 2D array row initialization")
                            return
                            
                        if self.current_token[0] != ',' and self.current_token[0] != '}':
                            self.errors.append(f"Semantic Error: Expected ',' or '}}' in array row initialization, found {self.current_token}")
                    
                    # Check if row size matches second dimension
                    if len(row_elements) != array_size2:
                        self.errors.append(f"Semantic Error: Number of elements in row {row_count+1} ({len(row_elements)}) does not match second dimension size ({array_size2})")
                    
                    all_elements.append(row_elements)
                    row_count += 1
                    
                    if self.current_token is None:
                        self.errors.append("Semantic Error: Unexpected end of tokens in 2D array initialization")
                        return
                        
                    if self.current_token[0] != '}':
                        self.errors.append(f"Semantic Error: Expected '}}' at end of array row, found {self.current_token}")
                        return
                        
                    self.next_token()  # Move past '}'
                
                # Check if number of rows matches first dimension
                if row_count != array_size1:
                    self.errors.append(f"Semantic Error: Number of rows ({row_count}) does not match first dimension size ({array_size1})")
                
                # Update symbol table with 2D array elements
                self.symbol_table[array_name]['value'] = all_elements
            else:
                # Parse 1D array elements (existing code)
                elements = []
                while self.current_token is not None and self.current_token[0] != '}':
                    # Skip spaces and commas
                    while self.current_token is not None and (self.current_token[1] == 'space' or self.current_token[0] == ','):
                        self.next_token()
                        
                    if self.current_token is None or self.current_token[0] == '}':
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
                            # Handle ^ as negative sign for dose
                            if self.current_token[0].startswith('^'):
                                elements.append(-int(self.current_token[0][1:]))
                            else:
                                elements.append(int(self.current_token[0]))
                        except:
                            pass
                    elif element_type == 'quant':
                        try:
                            # Handle ^ as negative sign for quant
                            if self.current_token[0].startswith('^'):
                                elements.append(-float(self.current_token[0][1:]))
                            else:
                                elements.append(float(self.current_token[0]))
                        except:
                            pass
                    elif element_type == 'seq':
                        elements.append(self.current_token[0].strip('"\''))
                    elif element_type == 'allele':
                        elements.append(self.current_token[0] == 'dom')
                    
                    self.next_token()  # Move past element
                    
                    # Look for comma or closing brace
                    if self.current_token is None:
                        self.errors.append("Semantic Error: Unexpected end of tokens in array initialization")
                        return
                        
                    if self.current_token[0] != ',' and self.current_token[0] != '}':
                        self.errors.append(f"Semantic Error: Expected ',' or '}}' in array initialization, found {self.current_token}")
                
                # Check if number of elements matches array size
                if len(elements) != array_size1:
                    self.errors.append(f"Semantic Error: Number of elements ({len(elements)}) does not match array size ({array_size1})")
                    return
                
                # Update symbol table with elements
                self.symbol_table[array_name]['value'] = elements
            
            if self.current_token is None or self.current_token[0] != '}':
                self.errors.append(f"Semantic Error: Expected '}}' at end of array initialization, found {self.current_token}")
                return
                
            self.next_token()  # Move past '}'
        
        # Check for semicolon
        if self.current_token is None or self.current_token[0] != ';':
            self.errors.append(f"Semantic Error: Expected ';' after array declaration, found {self.current_token}")
            return
            
        self.next_token()  # Move past ';'
    def parse_body_statements(self):
        was_in_loop = self.in_loop  # Save previous loop state
        
        while self.current_token is not None and self.current_token[0] != '}':
            # Skip spaces
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
                
            if self.current_token is None or self.current_token[0] == '}':
                break
                
            try:
                # Handle variable declarations
                if self.current_token[0] in ['_L'] or self.current_token[1] in ['dose', 'quant', 'seq', ' ']:
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
                elif self.current_token[1] == 'perms' or self.current_token[0] == 'perms':
                    self.perms_declaration()
                # Handle variable assignments
                elif self.current_token[1] == 'Identifier':
                    self.check_variable_usage()
                # Handle break and continue statements
                elif self.current_token[1] == 'destroy':
                    self.destroy_statement()
                elif self.current_token[0] == 'contig':
                    self.continue_statement()
                # Handle array declarations
                elif self.current_token[1] == 'clust':
                    self.clust_declaration()
                # Handle function declarations
                elif self.current_token[1] == 'function':
                    self.function_declaration()
                # Handle single-line comments (with #)
                elif self.current_token[1] == 'comment' or self.current_token[0] == '#':    
                    self.next_token()  # Skip single-line comment
                # Handle multi-line comments
                elif self.current_token[1] == 'multiline' or self.current_token[0] == '/*':
                    # Skip the multi-line comment token
                    self.next_token()
                    # Skip any tokens until we find '*/' if we're using '/*' token checks
                    if self.current_token is not None and self.current_token[0] == '*/':
                        self.next_token()  # Skip the closing */
                # Handle conversion functions
                elif self.current_token[1] == 'seq':
                    # Simple approach: skip tokens until semicolon
                    while self.current_token is not None and self.current_token[0] != ';':
                        self.next_token()
                    if self.current_token is not None:
                        self.next_token()  # Move past semicolon
                elif self.current_token[1] == 'elif' or self.current_token[1] == 'else':
                    # These are handled by if_statement, if they appear here it's a syntax error
                    # self.errors.append(f"Semantic Error: Unexpected {self.current_token[1]} without matching if statement")
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
                    # self.errors.append(f"Semantic Error: Unexpected token '{self.current_token[0]}' in body")
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
  
    def destroy_statement(self):
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
        
        # First check if the variable is in the current function scope
        if var_name in self.symbol_table:
            var_info = self.symbol_table[var_name]
            var_type = var_info['type']
        # Then check if it's in the global scope
        elif var_name in self.global_symbol_table:
            var_info = self.global_symbol_table[var_name]
            var_type = var_info['type']
        else:
            self.errors.append(f"Semantic Error: Variable '{var_name}' used before declaration")
            self.next_token()  # Move past identifier
            return
        
        self.next_token()  # Move past identifier
        
        # Check for array access
        is_array_element = False
        array_element_type = None
        
        if self.current_token is not None and self.current_token[0] == '[':
            # This is an array access
            is_array_element = True
            
            # Determine the element type of the array
            if var_type.startswith('array_'):
                array_element_type = var_type[6:]  # Extract element type (e.g., 'array_dose' -> 'dose')
            elif var_type.startswith('2d_array_'):
                array_element_type = var_type[9:]  # Extract element type for 2D arrays
            elif var_type == 'seq':
                # String variables can be indexed like arrays - individual characters are still strings
                array_element_type = 'seq'
                # Skip past the index expression
                self.next_token()  # Move past '['
                
                # Parse the index expression (skip until closing bracket)
                bracket_count = 1
                while self.current_token is not None and bracket_count > 0:
                    if self.current_token[0] == '[':
                        bracket_count += 1
                    elif self.current_token[0] == ']':
                        bracket_count -= 1
                    self.next_token()
                
                # Continue with other operations (like assignment)
                # Look for assignment operator
                # Skip any whitespace between array access and assignment operator
                while self.current_token is not None and self.current_token[1] in ["space", "tab"]:
                    self.next_token()
                    
                if self.current_token is not None and self.current_token[0] == '=':
                    self.next_token()  # Move past '='
                    
                    # Set the current assignment type for type checking
                    self.current_assignment_type = array_element_type
                    
                    # Collect tokens for the expression until semicolon
                    expression_tokens = []
                    
                    while self.current_token is not None and self.current_token[0] != ';':
                        expression_tokens.append(self.current_token)
                        self.next_token()
                    
                    # Process the expression (simplified for string character assignment)
                    # Actual processing would depend on your language semantics
                    
                    # Check for semicolon
                    if self.current_token is not None and self.current_token[0] == ';':
                        self.next_token()  # Move past semicolon
                    
                    return
            else:
                # self.errors.append(f"Semantic Error: Variable '{var_name}' is not an array")
                # Skip past this statement
                while self.current_token is not None and self.current_token[0] != ';':
                    self.next_token()
                if self.current_token is not None:
                    self.next_token()  # Move past semicolon
                return
                
            # Skip past the index expression
            self.next_token()  # Move past '['
            
            # Before skipping the index expression, check if it's a splicing operation with negative float
            # Look for splicing pattern: [: ^1.1] - splicing uses colons
            is_splicing = False
            if self.current_token is not None and self.current_token[0] == ':':
                is_splicing = True
                
            # Parse the index expression (skip until closing bracket)
            bracket_count = 1
            while self.current_token is not None and bracket_count > 0:
                # Check for negative float value in splicing operation
                if is_splicing and self.current_token is not None and self.current_token[1] == 'numlit':
                    # Check if it's a negative float (starts with ^ and has a decimal point)
                    value = self.current_token[0]
                    if value.startswith('^') and '.' in value:
                        self.errors.append("Semantic Error: negative quant values are not allowed in array splicing")
                
                if self.current_token[0] == '[':
                    bracket_count += 1
                elif self.current_token[0] == ']':
                    bracket_count -= 1
                self.next_token()
                
            # For 2D arrays, check for second dimension
            if var_type.startswith('2d_array_') and self.current_token is not None and self.current_token[0] == '[':
                self.next_token()  # Move past '['
                
                # Skip second dimension index
                bracket_count = 1
                while self.current_token is not None and bracket_count > 0:
                    if self.current_token[0] == '[':
                        bracket_count += 1
                    elif self.current_token[0] == ']':
                        bracket_count -= 1
                    self.next_token()
        
        # Skip any whitespace before assignment operator
        while self.current_token is not None and self.current_token[1] in ["space", "tab"]:
            self.next_token()
            
        # Look for assignment operator or compound assignment operators
        is_compound_assignment = False
        compound_operator = None
        
        if self.current_token is not None:
            if self.current_token[0] == '=':
                # Regular assignment
                pass
            elif self.current_token[0] in ['+=', '-=', '*=', '/=', '%=']:
                # Compound assignment
                is_compound_assignment = True
                compound_operator = self.current_token[0][0]  # Extract the operator part
            else:
                # Not an assignment operation
                # Skip any other statements like function calls or non-assignment operations
                while self.current_token is not None and self.current_token[0] != ';':
                    self.next_token()
                if self.current_token is not None:
                    self.next_token()  # Move past semicolon
                return
                
        # Look for assignment operator
        if self.current_token is not None and (self.current_token[0] == '=' or self.current_token[0] in ['+=', '-=', '*=', '/=', '%=']):
            # Check if the variable is a perms (constant)
            if var_info.get('is_perms', False):
                self.errors.append(f"Semantic Error: Cannot reassign value to perms (constant) '{var_name}'")
                # Skip to the end of the statement
                while self.current_token is not None and self.current_token[0] != ';':
                    self.next_token()
                if self.current_token is not None:
                    self.next_token()  # Move past semicolon
                return
            
            self.next_token()  # Move past assignment operator
            
            # Skip any whitespace after assignment operator
            while self.current_token is not None and self.current_token[1] in ["space", "tab"]:
                self.next_token()
                
            # Set the current assignment type for type checking
            if is_array_element:
                self.current_assignment_type = array_element_type
            else:
                self.current_assignment_type = var_type
            
            # Collect tokens for the expression until semicolon
            expression_tokens = []
            
            while self.current_token is not None and self.current_token[0] != ';':
                expression_tokens.append(self.current_token)
                self.next_token()
            
            # For compound assignments (+=, -=, etc.), check if types are compatible with the operation
            if is_compound_assignment:
                check_type = array_element_type if is_array_element else var_type
                
                # Check for division by zero in /= operation
                if compound_operator == '/' and len(expression_tokens) == 1:
                    # Check for direct division by zero
                    if expression_tokens[0][1] == 'numlit' and float(expression_tokens[0][0]) == 0:
                        target_name = f"{var_name}[index]" if is_array_element else var_name
                        self.errors.append(f"Semantic Error: Division by zero in assignment '{target_name} /= 0'")
                        if self.current_token is not None and self.current_token[0] == ';':
                            self.next_token()  # Move past semicolon
                        return
                
                # Type compatibility checks for compound assignments
                if check_type == 'seq':
                    # For strings, only += (concatenation) is allowed, not other arithmetic ops
                    if compound_operator != '+':
                        target_name = f"{var_name}[index]" if is_array_element else var_name
                        self.errors.append(f"Semantic Error: Invalid operation '{target_name} {compound_operator}=' for {check_type} type. Only '+=' is supported for strings.")
                        if self.current_token is not None and self.current_token[0] == ';':
                            self.next_token()  # Move past semicolon
                        return
                    
                    # For += on strings, check the RHS is also a string
                    has_non_string_operand = False
                    for token in expression_tokens:
                        if token[1] == 'numlit' or (token[1] == 'Identifier' and 
                            ((token[0] in self.symbol_table and self.symbol_table[token[0]]['type'] in ['dose', 'quant']) or
                             (token[0] in self.global_symbol_table and self.global_symbol_table[token[0]]['type'] in ['dose', 'quant']))):
                            has_non_string_operand = True
                            break
                    
                    if has_non_string_operand:
                        target_name = f"{var_name}[index]" if is_array_element else var_name
                        self.errors.append(f"Semantic Error: Cannot concatenate non-string value to {check_type} variable '{target_name}'")
                        if self.current_token is not None and self.current_token[0] == ';':
                            self.next_token()  # Move past semicolon
                        return
                
                elif check_type in ['dose', 'quant']:
                    # For numeric types, check for string operands
                    has_string_operand = False
                    for token in expression_tokens:
                        if token[1] == 'string literal' or (token[1] == 'Identifier' and 
                            ((token[0] in self.symbol_table and self.symbol_table[token[0]]['type'] == 'seq') or
                             (token[0] in self.global_symbol_table and self.global_symbol_table[token[0]]['type'] == 'seq'))):
                            has_string_operand = True
                            break
                    
                    if has_string_operand:
                        target_name = f"{var_name}[index]" if is_array_element else var_name
                        self.errors.append(f"Semantic Error: Cannot use string operands in arithmetic operation for {check_type} variable '{target_name}'")
                        if self.current_token is not None and self.current_token[0] == ';':
                            self.next_token()  # Move past semicolon
                        return
            
            # Special case: For TempChar = String[X], if both are string type, just accept it
            if is_array_element == False and var_type == 'seq' and len(expression_tokens) >= 2:
                # Check if it's a pattern like Var = Array[index]
                if (expression_tokens[0][1] == 'Identifier' and 
                    len(expression_tokens) > 1 and 
                    expression_tokens[1][0] == '['):
                    
                    # Get the array variable
                    array_var_name = expression_tokens[0][0]
                    
                    # Check if it exists in symbol table
                    array_var_info = None
                    if array_var_name in self.symbol_table:
                        array_var_info = self.symbol_table[array_var_name]
                    elif array_var_name in self.global_symbol_table:
                        array_var_info = self.global_symbol_table[array_var_name]
                    
                    if array_var_info:
                        array_var_type = array_var_info['type']
                        
                        # If it's a string array, allow the assignment without error
                        if array_var_type.startswith('array_seq') or array_var_type.startswith('2d_array_seq'):
                            # This is a valid assignment of string array element to string variable
                            if self.current_token is not None and self.current_token[0] == ';':
                                self.next_token()  # Move past semicolon
                            return
            
            # Special handling for stimuli function
            if len(expression_tokens) >= 1 and expression_tokens[0][1] == 'stimuli':
                # Check if the variable is a perms (constant)
                if var_info.get('is_perms', False):
                    self.errors.append(f"Semantic Error: Cannot assign input value to perms (constant) '{var_name}'")
                    # Skip to the end of the statement
                    if self.current_token is not None and self.current_token[0] == ';':
                        self.next_token()  # Move past semicolon
                    return
                
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
                if is_array_element:
                    # Don't update the array element value, just validate the assignment
                    if array_element_type == 'dose':
                        if 'value' in var_info:
                            # No direct update needed for array element
                            pass
                    elif array_element_type == 'quant':
                        if 'value' in var_info:
                            # No direct update needed for array element
                            pass
                    elif array_element_type == 'seq':
                        if 'value' in var_info:
                            # No direct update needed for array element
                            pass
                    else:
                        self.errors.append(f"Semantic Error: Cannot use stimuli with {array_element_type} type array element")
                else:
                    # Regular variable assignment
                    if var_type == 'dose':
                        var_info['value'] = 0  # Default integer value
                    elif var_type == 'quant':
                        var_info['value'] = 0.0  # Default float value
                    elif var_type == 'seq':
                        var_info['value'] = ""  # Default string value
                    else:
                        # self.errors.append(f"Semantic Error: Cannot use stimuli with {var_type} type")
                        pass
                
                # Store the prompt for runtime processing
                if not hasattr(self, 'pending_inputs'):
                    self.pending_inputs = []
                self.pending_inputs.append((var_name, var_type, prompt))
                
                return  # Skip further processing for stimuli
            
            # Handle special case for string array to string variable assignment (like in TempChar = String[X])
            if len(expression_tokens) > 0 and expression_tokens[0][1] == 'Identifier':
                # Direct assignment from another variable or array element
                assign_var_name = expression_tokens[0][0]
                is_assign_array = False
                
                # Check if there's an array access after the identifier
                if len(expression_tokens) > 1 and expression_tokens[1][0] == '[':
                    is_assign_array = True
                    
                # Get the RHS variable from the symbol table
                assign_var_info = None
                if assign_var_name in self.symbol_table:
                    assign_var_info = self.symbol_table[assign_var_name]
                elif assign_var_name in self.global_symbol_table:
                    assign_var_info = self.global_symbol_table[assign_var_name]
                
                if assign_var_info:
                    assign_var_type = assign_var_info['type']
                    
                    # If assigning from an array element to a variable
                    if is_assign_array:
                        # Extract element type
                        if assign_var_type.startswith('array_'):
                            assign_element_type = assign_var_type[6:]
                        elif assign_var_type.startswith('2d_array_'):
                            assign_element_type = assign_var_type[9:]
                        else:
                            # self.errors.append(f"Semantic Error: Variable '{assign_var_name}' is not an array")
                            if self.current_token is not None and self.current_token[0] == ';':
                                self.next_token()  # Move past semicolon
                            return
                        
                        # Check type compatibility for assignment
                        check_type = array_element_type if is_array_element else var_type
                        
                        # For string array element to string variable, this is valid
                        if check_type == 'seq' and assign_element_type == 'seq':
                            # Valid assignment, skip further checks
                            if self.current_token is not None and self.current_token[0] == ';':
                                self.next_token()  # Move past semicolon
                            return
                        
                        # Check other type compatibilities
                        if check_type == assign_element_type or (check_type == 'quant' and assign_element_type == 'dose'):
                            # Compatible types, accept the assignment
                            if not is_array_element:
                                # For regular variables, can update the value
                                var_info['value'] = assign_var_info.get('value', None)  # Might be None for array elements
                            # Skip further checks
                            if self.current_token is not None and self.current_token[0] == ';':
                                self.next_token()  # Move past semicolon
                            return
                        else:
                            # Incompatible types
                            target_name = f"{var_name}[index]" if is_array_element else var_name
                            self.errors.append(f"Semantic Error: Cannot assign {assign_element_type} array element to {check_type} {target_name}")
                            if self.current_token is not None and self.current_token[0] == ';':
                                self.next_token()  # Move past semicolon
                            return
            
            # Evaluate the expression
            if len(expression_tokens) == 1:
                token = expression_tokens[0]
                
                # Check if the assigned value is an identifier
                if token[1] == 'Identifier':
                    var_to_assign = token[0]
                    # Check both function scope and global scope
                    if var_to_assign in self.symbol_table:
                        assigned_value_info = self.symbol_table[var_to_assign]
                    elif var_to_assign in self.global_symbol_table:
                        assigned_value_info = self.global_symbol_table[var_to_assign]
                    else:
                        self.errors.append(f"Semantic Error: Variable '{var_to_assign}' used before declaration")
                        return

                    # Get value from the identifier's stored value
                    assigned_value = assigned_value_info['value']
                    assigned_type = assigned_value_info['type']
                    
                    # Check type compatibility - for regular or array element assignment
                    check_type = array_element_type if is_array_element else var_type
                    
                    if check_type == assigned_type or (check_type == 'quant' and assigned_type == 'dose'):
                        if not is_array_element:
                            var_info['value'] = assigned_value
                        # For array elements, we only validate the type but don't update the actual value
                        # as that would require tracking array indices at runtime
                    elif check_type == 'allele':
                        # Allow assigning any type to allele based on truthiness
                        if assigned_type == 'seq':
                            # For strings, empty is falsy (rec), non-empty is truthy (dom)
                            boolean_val = (assigned_value != "")
                            if not is_array_element:
                                var_info['value'] = boolean_val
                        elif assigned_type in ['dose', 'quant']:
                            # For numeric types, 0 is falsy (rec), non-zero is truthy (dom)
                            boolean_val = (assigned_value != 0)
                            if not is_array_element:
                                var_info['value'] = boolean_val
                        else:
                            # For other types, use the value directly if it's a boolean
                            if not is_array_element:
                                var_info['value'] = bool(assigned_value)
                    else:
                        target_name = f"{var_name}[index]" if is_array_element else var_name
                        self.errors.append(f"Semantic Error: Cannot assign {assigned_type} variable to {check_type} {target_name}")
                
                # Handle literals
                elif token[1] == 'numlit':
                    check_type = array_element_type if is_array_element else var_type
                    
                    if check_type == 'dose':
                        # For dose type, check if the value has a decimal point
                        if '.' in token[0]:
                            target_name = f"{var_name}[index]" if is_array_element else var_name
                            self.errors.append(f"Semantic Error: Cannot convert {token[0]} to integer for dose {target_name}")
                        else:
                            try:
                                # Handle ^ as negative sign for dose
                                if token[0].startswith('^'):
                                    numeric_value = -int(token[0][1:])
                                else:
                                    numeric_value = int(token[0])
                                
                                if not is_array_element:
                                    var_info['value'] = numeric_value
                            except:
                                target_name = f"{var_name}[index]" if is_array_element else var_name
                                self.errors.append(f"Semantic Error: Cannot convert {token[0]} to integer for dose {target_name}")
                    elif check_type == 'quant':
                        try:
                            # Handle ^ as negative sign for quant
                            if token[0].startswith('^'):
                                numeric_value = -float(token[0][1:])
                            else:
                                numeric_value = float(token[0])
                                
                            if not is_array_element:
                                var_info['value'] = numeric_value
                        except:
                            target_name = f"{var_name}[index]" if is_array_element else var_name
                            self.errors.append(f"Semantic Error: Cannot convert {token[0]} to float for quant {target_name}")
                    elif check_type == 'allele':
                        # Allow numeric values for allele type, non-zero is dom (true)
                        try:
                            # Handle ^ as negative sign for numeric values
                            if token[0].startswith('^'):
                                numeric_value = -float(token[0][1:])
                            else:
                                numeric_value = float(token[0])
                            
                            boolean_val = (numeric_value != 0)
                            if not is_array_element:
                                var_info['value'] = boolean_val
                        except:
                            target_name = f"{var_name}[index]" if is_array_element else var_name
                            self.errors.append(f"Semantic Error: Cannot convert {token[0]} to allele value for {target_name}")
                    else:
                        target_name = f"{var_name}[index]" if is_array_element else var_name
                        self.errors.append(f"Semantic Error: Cannot assign numeric value to {check_type} {target_name}")
                
                elif token[1] == 'string literal':
                    check_type = array_element_type if is_array_element else var_type
                    
                    if check_type == 'seq':
                        # Remove quotation marks
                        string_val = token[0].strip('"\'')
                        if not is_array_element:
                            var_info['value'] = string_val
                    elif check_type == 'allele':
                        # Allow string values for allele type, non-empty is dom (true)
                        string_val = token[0].strip('"\'')
                        boolean_val = (string_val != "")
                        if not is_array_element:
                            var_info['value'] = boolean_val
                    else:
                        target_name = f"{var_name}[index]" if is_array_element else var_name
                        self.errors.append(f"Semantic Error: Cannot assign string value to {check_type} {target_name}")
            
            # Handle complex expressions (with operators)
            elif len(expression_tokens) > 1:
                check_type = array_element_type if is_array_element else var_type
                
                # Special case for string array access - relaxed checking
                has_array_access = False
                for i in range(len(expression_tokens)-1):
                    if (expression_tokens[i][1] == 'Identifier' and 
                        i+1 < len(expression_tokens) and
                        expression_tokens[i+1][0] == '['):
                        has_array_access = True
                        break
                
                # For string assignments with array access, just validate without errors
                if check_type == 'seq' and has_array_access:
                    # Skip further validation for string operations with arrays
                    if self.current_token is not None and self.current_token[0] == ';':
                        self.next_token()  # Move past semicolon
                    return
                
                # Check for arithmetic operations in the expression (*, /, +, -, %)
                has_arithmetic_ops = False
                for token in expression_tokens:
                    if token[0] in ['*', '/', '+', '-', '%']:
                        has_arithmetic_ops = True
                        break
                
                # Check for string literals or seq variables in arithmetic expressions for dose/quant variables
                if check_type in ['dose', 'quant'] and has_arithmetic_ops:
                    has_string_operands = False
                    
                    # First, check for string literals
                    for token in expression_tokens:
                        if token[1] == 'string literal':
                            has_string_operands = True
                            break
                            
                    # Then check for seq variables
                    if not has_string_operands:
                        for token in expression_tokens:
                            if token[1] == 'Identifier':
                                token_var_name = token[0]
                                token_var_info = None
                                
                                if token_var_name in self.symbol_table:
                                    token_var_info = self.symbol_table[token_var_name]
                                elif token_var_name in self.global_symbol_table:
                                    token_var_info = self.global_symbol_table[token_var_name]
                                    
                                if token_var_info and token_var_info['type'] == 'seq':
                                    has_string_operands = True
                                    break
                    
                    # Display error if string operands were found in arithmetic operation
                    if has_string_operands:
                        target_name = f"{var_name}[index]" if is_array_element else var_name
                        self.errors.append(f"Semantic Error: Cannot use string operands in arithmetic expression for {check_type} variable '{target_name}'")
                        if self.current_token is not None and self.current_token[0] == ';':
                            self.next_token()  # Move past semicolon
                        return
                
                # Only handle arithmetic expressions for numeric types
                if check_type in ['dose', 'quant']:
                    expr_str = ""
                    valid_expression = True
                    
                    # Track if division is used, which forces quant result type
                    contains_division = False
                    
                    # Check for string literals or seq variables in arithmetic expressions
                    has_string_operands = False
                    for token in expression_tokens:
                        if token[1] == 'string literal':
                            has_string_operands = True
                            target_name = f"{var_name}[index]" if is_array_element else var_name
                            self.errors.append(f"Semantic Error: Cannot use string '{token[0]}' in arithmetic expression for {check_type} variable '{target_name}'")
                            valid_expression = False
                            break
                        elif token[1] == 'Identifier':
                            token_var_name = token[0]
                            token_var_info = None
                            
                            if token_var_name in self.symbol_table:
                                token_var_info = self.symbol_table[token_var_name]
                            elif token_var_name in self.global_symbol_table:
                                token_var_info = self.global_symbol_table[token_var_name]
                                
                            if token_var_info and token_var_info['type'] == 'seq':
                                has_string_operands = True
                                target_name = f"{var_name}[index]" if is_array_element else var_name
                                self.errors.append(f"Semantic Error: Cannot use string variable '{token_var_name}' in arithmetic expression for {check_type} variable '{target_name}'")
                                valid_expression = False
                                break
                    
                    # If there are string operands, don't proceed with evaluating the expression
                    if has_string_operands:
                        if self.current_token is not None and self.current_token[0] == ';':
                            self.next_token()  # Move past semicolon
                        return
                    
                    for token in expression_tokens:
                        if token[1] == 'Identifier':
                            # Check both current function scope and global scope
                            token_var_name = token[0]
                            if token_var_name in self.symbol_table:
                                token_var_info = self.symbol_table[token_var_name]
                            elif token_var_name in self.global_symbol_table:
                                token_var_info = self.global_symbol_table[token_var_name]
                            else:
                                self.errors.append(f"Semantic Error: Variable '{token_var_name}' used before declaration")
                                valid_expression = False
                                break
                                
                            if token_var_info['type'] in ['dose', 'quant']:
                                expr_str += str(token_var_info['value'])
                            # else:
                            #     self.errors.append(f"Semantic Error: Cannot use non-numeric variable '{token[0]}' in arithmetic expression")
                            #     valid_expression = False
                            #     break
                        elif token[1] == 'numlit':
                            # Handle ^ as negative sign in complex expressions
                            if token[0].startswith('^'):
                                expr_str += f"-{token[0][1:]}"
                            else:
                                expr_str += token[0]
                        elif token[0] in ['+', '-', '*', '/', '%', '(', ')']:
                            # Track division for type conversion
                            if token[0] == '/':
                                contains_division = True
                            expr_str += token[0]
                        elif token[1] in ["space", "tab"]:
                            continue  # Skip spaces and tabs
                        # else:
                        #     self.errors.append(f"Semantic Error: Invalid token '{token[0]}' in arithmetic expression")
                        #     valid_expression = False
                        #     break
                    
                    if valid_expression and expr_str:
                        try:
                            # Force float result for division operations or if target is quant
                            if check_type == 'quant' or contains_division:
                                result = float(eval(expr_str))
                            else:  # dose type with no division
                                result = int(eval(expr_str))
                            
                            if not is_array_element:
                                var_info['value'] = result
                            # For array elements, we only validate type compatibility
                        except ZeroDivisionError:
                            target_name = f"{var_name}[index]" if is_array_element else var_name
                            self.errors.append(f"Semantic Error: Division by zero in expression for '{target_name}'")
                            if self.current_token is not None and self.current_token[0] == ';':
                                self.next_token()  # Move past semicolon
                            return
                        except Exception as e:
                            # self.errors.append(f"Semantic Error: Failed to evaluate expression: {str(e)}")
                            pass
                            
                        # Check for division by zero
                        if contains_division and '/' in expr_str:
                            try:
                                # This is just a simple check - a more robust solution would parse the expression
                                parts = expr_str.split('/')
                                for part in parts[1:]:  # Check all divisors
                                    if float(eval(part.strip())) == 0:
                                        target_name = f"{var_name}[index]" if is_array_element else var_name
                                        self.errors.append(f"Semantic Error: Division by zero detected in expression for '{target_name}'")
                                        break
                            except:
                                # If we can't evaluate the right side, we ignore this check
                                pass
                
                # Handle string concatenation for seq type
                elif check_type == 'seq':
                    # Check if this is an arithmetic operation (not string concatenation)
                    if has_arithmetic_ops:
                        # Look specifically for multiplication, division, or modulo
                        for token in expression_tokens:
                            if token[0] in ['*', '/', '%']:
                                target_name = f"{var_name}[index]" if is_array_element else var_name
                                self.errors.append(f"Semantic Error: Cannot assign arithmetic expression result to {check_type} variable '{target_name}'")
                                break
                    
                    # For string concatenation, we're less strict now
                    # We'll accept the concatenation if it contains string values or string array elements
                    valid_expression = True
                    
                    # Just skip further validation for string expressions with array access
                    if self.current_token is not None and self.current_token[0] == ';':
                        self.next_token()  # Move past semicolon
                else:
                    target_name = f"{var_name}[index]" if is_array_element else var_name
                    self.errors.append(f"Semantic Error: Complex expressions not supported for {check_type} {target_name}")
        
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
            
            # Handle special case for array declaration with clust
            if self.current_token is not None and self.current_token[1] == 'clust':
                self.clust_declaration()
                return
                
            # Check for perms declaration with scope
            if self.current_token is not None and self.current_token[1] == 'perms' or self.current_token[0] == 'perms':
                # Store the scope for use in perms_declaration
                self.current_scope = var_scope
                self.perms_declaration()
                return
                
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
            
            # Check if variable name already exists as a function name
            if var_name in self.functions:
                self.errors.append(f"Semantic Error: Variable name '{var_name}' already used as a function")
                
            # Check for redeclaration in current scope only
            if var_name in self.symbol_table:
                self.errors.append(f"Semantic Error: Variable '{var_name}' already declared in current scope")
                
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

            # Add to current scope's symbol table
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
                            elif var_type == 'allele':
                                # Allow any type to be converted to allele based on truthiness
                                if assigned_type == 'seq':
                                    # For strings, empty string is falsy (rec), non-empty is truthy (dom)
                                    self.symbol_table[var_name]['value'] = (assigned_value != "")
                                elif assigned_type in ['dose', 'quant']:
                                    # For numeric types, 0 is falsy (rec), non-zero is truthy (dom)
                                    self.symbol_table[var_name]['value'] = (assigned_value != 0)
                                else:
                                    # For other types, use the value directly if it's a boolean
                                    self.symbol_table[var_name]['value'] = bool(assigned_value)
                            else:
                                self.errors.append(f"Semantic Error: Cannot assign {assigned_type} variable to {var_type} variable '{var_name}'")
                        else:
                            self.errors.append(f"Semantic Error: Variable '{var_to_assign}' used before declaration")
                    
                    # Handle literals
                    elif token[1] == 'numlit':
                        if var_type == 'dose':
                            try:
                                # Handle ^ as negative sign
                                if token[0].startswith('^'):
                                    converted_value = -int(token[0][1:])
                                else:
                                    converted_value = int(token[0])
                                self.symbol_table[var_name]['value'] = converted_value
                            except:
                                self.errors.append(f"Semantic Error: Cannot convert {token[0]} to integer for dose variable '{var_name}'")
                        elif var_type == 'quant':
                            try:
                                # Handle ^ as negative sign
                                if token[0].startswith('^'):
                                    converted_value = -float(token[0][1:])
                                else:
                                    converted_value = float(token[0])
                                self.symbol_table[var_name]['value'] = converted_value
                            except:
                                self.errors.append(f"Semantic Error: Cannot convert {token[0]} to float for quant variable '{var_name}'")
                        elif var_type == 'allele':
                            # Allow numeric values for allele type, non-zero is dom (true)
                            try:
                                # Handle ^ as negative sign
                                if token[0].startswith('^'):
                                    numeric_value = -float(token[0][1:])
                                else:
                                    numeric_value = float(token[0])
                                # Convert to boolean - any non-zero value is dom (true)
                                self.symbol_table[var_name]['value'] = (numeric_value != 0)
                            except:
                                self.errors.append(f"Semantic Error: Cannot convert {token[0]} to allele value for variable '{var_name}'")
                        else:
                            self.errors.append(f"Semantic Error: Cannot assign numeric value to {var_type} variable '{var_name}'")
                    
                    elif token[1] == 'string literal':
                        if var_type == 'seq':
                            # Remove quotation marks
                            string_val = token[0].strip('"\'')
                            self.symbol_table[var_name]['value'] = string_val
                        elif var_type == 'allele':
                            # Allow string values for allele type, non-empty string is dom (true)
                            string_val = token[0].strip('"\'')
                            self.symbol_table[var_name]['value'] = (string_val != "")
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
                        
                        # First, check for string literals in numeric expression
                        for token in expression_tokens:
                            if token[1] == 'string literal':
                                self.errors.append(f"Semantic Error: Cannot use string '{token[0]}' in arithmetic expression for {var_type} variable '{var_name}'")
                                valid_expression = False
                                break
                            elif token[1] == 'Identifier' and token[0] in self.symbol_table and self.symbol_table[token[0]]['type'] == 'seq':
                                self.errors.append(f"Semantic Error: Cannot use string variable '{token[0]}' in arithmetic expression for {var_type} variable '{var_name}'")
                                valid_expression = False
                                break
                        
                        # If we found string literals in numeric expression, skip the rest of processing
                        if not valid_expression:
                            continue
                        
                        for token in expression_tokens:
                            if token[1] == 'Identifier':
                                if token[0] in self.symbol_table:
                                    if self.symbol_table[token[0]]['type'] in ['dose', 'quant']:
                                        expr_str += str(self.symbol_table[token[0]]['value'])
                                    # else:
                                    #     self.errors.append(f"Semantic Error: Cannot use non-numeric variable '{token[0]}' in arithmetic expression")
                                    #     valid_expression = False
                                    #     break
                                else:
                                    self.errors.append(f"Semantic Error: Variable '{token[0]}' used before declaration")
                                    valid_expression = False
                                    break
                            elif token[1] == 'numlit':
                                # Handle ^ as negative sign in complex expressions
                                if token[0].startswith('^'):
                                    expr_str += f"-{token[0][1:]}"
                                else:
                                    expr_str += token[0]
                            elif token[0] in ['+', '-', '*', '/', '%', '(', ')']:
                                # Track division for type conversion
                                if token[0] == '/':
                                    contains_division = True
                                expr_str += token[0]
                            elif token[1] == 'space':
                                continue  # Skip spaces
                            # else:
                            #     self.errors.append(f"Semantic Error: Invalid token '{token[0]}' in arithmetic expression")
                            #     valid_expression = False
                            #     break
                        
                        if valid_expression and expr_str:
                            try:
                                # Force float result for division operations or if target is quant
                                if var_type == 'quant' or contains_division:
                                    result = float(eval(expr_str))
                                else:  # dose type with no division
                                    result = int(eval(expr_str))
                                
                                self.symbol_table[var_name]['value'] = result
                            except Exception as e:
                                # self.errors.append(f"Semantic Error: Failed to evaluate expression: {str(e)}")
                                pass
                            # Check for division by zero
                            if contains_division and '/' in expr_str:
                                try:
                                    # This is just a simple check - a more robust solution would parse the expression
                                    eval(expr_str.replace('/', '//'))
                                except ZeroDivisionError:
                                    self.errors.append(f"Semantic Error: Division by zero in expression for variable '{var_name}'")
                                except:
                                    pass
                    
                    # Handle string concatenation for seq type
                    elif var_type == 'seq':
                        result = ""
                        valid_expression = True
                        
                        for i, token in enumerate(expression_tokens):
                            if token[0] == '+':
                                continue
                            elif token[1] == 'string literal':
                                result += token[0].strip('"\'')
                            elif token[1] == 'Identifier' and token[0] in self.symbol_table:
                                if self.symbol_table[token[0]]['type'] == 'seq':
                                    result += str(self.symbol_table[token[0]]['value'])

                            elif token[1] == 'space':
                                continue  # Skip spaces
                            else:
                            # self.errors.append(f"Semantic Error: Invalid token '{token[0]}' in string concatenation")
                            # valid_expression = False
                            # break
                                pass
                        
                        if valid_expression:
                            self.symbol_table[var_name]['value'] = result
                    else:
                        self.errors.append(f"Semantic Error: Complex expressions not supported for {var_type} type")
            
            # Check if we need to continue for multiple declarations
            if self.current_token is None or self.current_token[0] != ',':
                break
                
            self.next_token()  # Move past comma
            
            # Skip spaces
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
        
        # Check for semicolon if not already consumed
        if self.current_token is not None and self.current_token[0] == ';':
            self.next_token()  # Move past semicolon

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
            
            # Instead of skipping, actually parse the condition to check variable usage
            self.parse_condition()
            
            # Check for closing parenthesis - parse_condition might not consume it
            if self.current_token is not None and self.current_token[0] == ')':
                self.next_token()  # Move past ')'
            
    # push error
    
            # Skip spaces after the closing parenthesis
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
        
        # Check for opening brace
        # if self.current_token is None or self.current_token[0] != '{':
        #     self.errors.append(f"Semantic Error: Expected '{{' after if condition, found {self.current_token}")
        #     return
            
        self.next_token()  # Move past '{'
        
        # Instead of skipping the block, parse the body statements to check variable declarations
        self.parse_body_statements()
        
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
            
            # Instead of skipping, actually parse the condition to check variable usage
            self.parse_condition()
            
            # Check for closing parenthesis - parse_condition might not consume it
            if self.current_token is not None and self.current_token[0] == ')':
                self.next_token()  # Move past ')'
            
            # Skip spaces after the closing parenthesis
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
        
        # Check for opening brace
        if self.current_token is None or self.current_token[0] != '{':
            self.errors.append(f"Semantic Error: Expected '{{' after elif condition, found {self.current_token}")
            return
            
        self.next_token()  # Move past '{'
        
        # Instead of skipping the block, parse the body statements to check variable declarations
        self.parse_body_statements()
        
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
        if self.current_token is None:
            return None
        
        # Track the nesting level to prevent infinite recursion
        nesting_level = getattr(self, '_condition_nesting_level', 0)
        self._condition_nesting_level = nesting_level + 1
        
        # Prevent excessive recursion
        if nesting_level > 100:  # Set a reasonable limit
            self.errors.append("Semantic Error: Maximum recursion depth exceeded in condition parsing")
            # Skip to the next semicolon or closing brace
            while self.current_token is not None and self.current_token[0] not in [';', '}']:
                self.next_token()
            self._condition_nesting_level = nesting_level  # Restore previous level
            return None
        
        # Parse the first operand
        left_type = self.parse_expression()
        
        # If there's no comparison operator, this is a boolean expression
        if self.current_token is None or self.current_token[0] not in ['==', '!=', '<', '>', '<=', '>=']:
            self._condition_nesting_level = nesting_level  # Restore previous level
            return 'allele'  # Return boolean type
        
        # Store the operator for type checking
        operator = self.current_token[0]
        self.next_token()  # Move past operator
        
        # Parse the second operand
        right_type = self.parse_expression()
        
        # Check type compatibility for comparison
        if left_type is not None and right_type is not None:
            self.check_type_compatibility(left_type, right_type, operator)
        
        self._condition_nesting_level = nesting_level  # Restore previous level
        return 'allele'  # Comparison always yields a boolean

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
                if operator == '+' and ((expr_type in ['dose', 'quant'] and term_type == 'seq') or 
                                       (expr_type == 'seq' and term_type in ['dose', 'quant'])):
                    # Specific error for string/number concatenation
                    self.errors.append(f"Semantic Error: Cannot concatenate {expr_type} and {term_type} directly. Use seq() function to convert numeric values to strings.")
                else:
                    # General error for other incompatible types
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
            # Check in current function scope first, then global scope
            if var_name in self.symbol_table:
                factor_type = self.symbol_table[var_name]['type']
            elif var_name in self.global_symbol_table:
                factor_type = self.global_symbol_table[var_name]['type']
            else:
                self.errors.append(f"Semantic Error: Variable '{var_name}' used before declaration")
                factor_type = 'unknown'  # Use a placeholder type
            
            # Save the current position to restore it later
            save_pos = self.token_index
            
            self.next_token()  # Move past identifier
            
            # Check if this is an array access
            if self.current_token is not None and self.current_token[0] == '[':
                # This is an array element access or string character access
                # Check if the variable is an array or a string
                if factor_type.startswith('array_'):
                    # Extract the element type
                    factor_type = factor_type[6:]  # Get element type (e.g., 'array_dose' -> 'dose')
                elif factor_type.startswith('2d_array_'):
                    # Extract the element type for 2D arrays
                    factor_type = factor_type[9:]  # Get element type
                elif factor_type == 'seq':
                    # String variables can be accessed by index (like arrays)
                    factor_type = 'seq'  # Individual characters are still strings
                else:
                    # For non-array, non-string variables, restore position and return original type
                    self.token_index = save_pos
                    self.next_token()  # Move past identifier
                    return factor_type
                
                # Skip the array index expression
                self.next_token()  # Move past '['
                
                # Before skipping the index expression, check if it's a splicing operation with negative float
                # Look for splicing pattern: [: ^1.1] - splicing uses colons
                is_splicing = False
                if self.current_token is not None and self.current_token[0] == ':':
                    is_splicing = True
                    
                bracket_count = 1
                while self.current_token is not None and bracket_count > 0:
                    # Check for negative float value in splicing operation
                    if is_splicing and self.current_token is not None and self.current_token[1] == 'numlit':
                        # Check if it's a negative float (starts with ^ and has a decimal point)
                        value = self.current_token[0]
                        if value.startswith('^') and '.' in value:
                            self.errors.append("Semantic Error: negative quant values are not allowed in array splicing")
                    
                    if self.current_token[0] == '[':
                        bracket_count += 1
                    elif self.current_token[0] == ']':
                        bracket_count -= 1
                    if bracket_count > 0:  # Only advance if we're still inside brackets
                        self.next_token()
                self.next_token()  # Move past closing ']'
                
                # Handle potential second dimension for 2D arrays
                if factor_type.startswith('2d_array_') and self.current_token is not None and self.current_token[0] == '[':
                    self.next_token()  # Move past '['
                    bracket_count = 1
                    while self.current_token is not None and bracket_count > 0:
                        if self.current_token[0] == '[':
                            bracket_count += 1
                        elif self.current_token[0] == ']':
                            bracket_count -= 1
                        if bracket_count > 0:
                            self.next_token()
                    self.next_token()  # Move past closing ']'
            else:
                # Not an array access, restore the saved position
                self.token_index = save_pos
                self.next_token()  # Move past identifier
            
        # Handle numeric literal
        elif self.current_token[1] == 'numlit':
            # Check if it has a decimal point to determine type
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
            # self.errors.append(f"Semantic Error: Expected ')' after while condition, found {self.current_token}")
            return
            
        self.next_token()  # Move past ')'
        
        # Skip spaces
        while self.current_token is not None and self.current_token[1] == 'space':
            self.next_token()
        
        # Check for opening brace
        if self.current_token is None or self.current_token[0] != '{':
            # self.errors.append(f"Semantic Error: Expected '{{' after while condition, found {self.current_token}")
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
            return
            
        self.next_token()  # Move past '('
        
        # Store all values to print
        values_to_print = []
        
        # Parse values until closing parenthesis
        while self.current_token is not None and self.current_token[0] != ')':
            # Skip spaces
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
            
            # Check for variable identifier or literal
            if self.current_token is None:
                self.errors.append("Semantic Error: Unexpected end of tokens in express statement")
                return
            
            # Check for array access with splicing using negative float
            if self.current_token[1] == 'Identifier':
                var_name = self.current_token[0]
                # Check if variable exists
                var_info = None
                if var_name in self.symbol_table:
                    var_info = self.symbol_table[var_name]
                elif var_name in self.global_symbol_table:
                    var_info = self.global_symbol_table[var_name]
                
                # Save current position
                save_pos = self.token_index
                
                self.next_token()  # Move past identifier
                
                # Check if this is an array access
                if self.current_token is not None and self.current_token[0] == '[':
                    self.next_token()  # Move past '['
                    
                    # Check for splicing pattern with colon
                    if self.current_token is not None and self.current_token[0] == ':':
                        is_splicing = True
                        self.next_token()  # Move past ':'
                        
                        # Look for negative float after colon
                        while self.current_token is not None and self.current_token[0] != ']':
                            if self.current_token is not None and self.current_token[1] == 'numlit':
                                # Check if it's a negative float (starts with ^ and has a decimal point)
                                value = self.current_token[0]
                                if value.startswith('^') and '.' in value:
                                    self.errors.append("Semantic Error: negative quant values are not allowed in array splicing")
                            self.next_token()
                    
                    # Skip the rest of the array index expression
                    bracket_count = 1
                    while self.current_token is not None and bracket_count > 0:
                        if self.current_token[0] == '[':
                            bracket_count += 1
                        elif self.current_token[0] == ']':
                            bracket_count -= 1
                        if bracket_count > 0:
                            self.next_token()
                    
                    # Move past closing bracket
                    if self.current_token is not None and self.current_token[0] == ']':
                        self.next_token()
                
                # Restore position to process the value normally
                self.token_index = save_pos
                self.current_token = self.tokens[self.token_index - 1] if self.token_index > 0 else None
            
            # Check for expressions with + operator (concatenation)
            # Save the current position to restore it after checking
            save_position = self.token_index
            
            # Check if this is an expression with concatenation
            first_operand_type = None
            if self.current_token[1] == 'Identifier':
                var_name = self.current_token[0]
                # Check both scopes
                if var_name in self.symbol_table:
                    first_operand_type = self.symbol_table[var_name]['type']
                elif var_name in self.global_symbol_table:
                    first_operand_type = self.global_symbol_table[var_name]['type']
            elif self.current_token[1] == 'numlit':
                first_operand_type = 'dose' if '.' not in self.current_token[0] else 'quant'
            elif self.current_token[1] == 'string literal':
                first_operand_type = 'seq'
                
            # Move past the first operand
            self.next_token()
            
            # Skip spaces
            while self.current_token is not None and self.current_token[1] == 'space':
                self.next_token()
                
            # Check if there's a + operator
            if self.current_token is not None and self.current_token[0] == '+':
                self.next_token()  # Move past +
                
                # Skip spaces
                while self.current_token is not None and self.current_token[1] == 'space':
                    self.next_token()
                    
                # Check second operand type
                second_operand_type = None
                if self.current_token[1] == 'Identifier':
                    var_name = self.current_token[0]
                    # Check both scopes
                    if var_name in self.symbol_table:
                        second_operand_type = self.symbol_table[var_name]['type']
                    elif var_name in self.global_symbol_table:
                        second_operand_type = self.global_symbol_table[var_name]['type']
                elif self.current_token[1] == 'numlit':
                    second_operand_type = 'dose' if '.' not in self.current_token[0] else 'quant'
                elif self.current_token[1] == 'string literal':
                    second_operand_type = 'seq'
                elif self.current_token[1] == 'seq':
                    # This is a seq() function call, which is allowed for conversion
                    second_operand_type = 'seq'
                
                # Check if types are compatible for concatenation
                if first_operand_type and second_operand_type:
                    if (first_operand_type in ['dose', 'quant'] and second_operand_type == 'seq') or \
                       (first_operand_type == 'seq' and second_operand_type in ['dose', 'quant']):
                        # Error: Cannot directly concatenate numbers and strings
                        self.errors.append(f"Semantic Error: Cannot concatenate {first_operand_type} and {second_operand_type} directly. Use seq() function to convert numeric values to strings.")
            
            # Restore position to process the value normally
            self.token_index = save_position
            self.current_token = self.tokens[self.token_index - 1] if self.token_index > 0 else None
            
            # Process the current value
            if self.current_token[1] == 'Identifier':
                var_name = self.current_token[0]
                self.next_token()  # Move past identifier
                
                # Check if this is a function name (followed by parentheses)
                if self.current_token is not None and self.current_token[0] == '(':
                    # Handle function call
                    if var_name not in self.functions:
                        # self.errors.append(f"Semantic Error: Function '{var_name}' used in express statement before declaration")
                        # values_to_print.append(f"undefined({var_name})")
                        pass
                    else:
                        # Parse function arguments
                        args = []
                        self.next_token()  # Move past '('
                        
                        # Parse arguments
                        while self.current_token is not None and self.current_token[0] != ')':
                            # Skip spaces
                            while self.current_token is not None and self.current_token[1] == 'space':
                                self.next_token()
                            
                            # Get argument (variable name)
                            if self.current_token is None or self.current_token[1] != 'Identifier':
                                self.errors.append(f"Semantic Error: Expected identifier as function argument, found {self.current_token}")
                                break
                            
                            arg_name = self.current_token[0]
                            
                            # Check if variable exists in current scope first, then global scope
                            if arg_name not in self.symbol_table and arg_name not in self.global_symbol_table:
                                self.errors.append(f"Semantic Error: Variable '{arg_name}' used as argument before declaration")
                                break
                            
                            # Get variable info from the appropriate scope
                            if arg_name in self.symbol_table:
                                arg_info = self.symbol_table[arg_name]
                            else:
                                arg_info = self.global_symbol_table[arg_name]
                            
                            # Add argument to the list
                            args.append({
                                'name': arg_name,
                                'type': arg_info['type'],
                                'value': arg_info.get('value', None)
                            })
                            
                            self.next_token()  # Move past argument
                            
                            # Skip spaces
                            while self.current_token is not None and self.current_token[1] == 'space':
                                self.next_token()
                            
                            # Check for comma or closing parenthesis
                            if self.current_token is None:
                                self.errors.append("Semantic Error: Unexpected end of tokens in function arguments")
                                break
                            
                            if self.current_token[0] == ',':
                                self.next_token()  # Move past comma
                                continue
                            elif self.current_token[0] != ')':
                                self.errors.append(f"Semantic Error: Expected ',' or ')' in function arguments, found {self.current_token}")
                                break
                        
                        # Validate parameter types and number
                        is_valid = self.check_parameter_passing(var_name, args)
                        
                        if is_valid:
                            # Check if the function returns multiple values
                            if self.functions[var_name].get('multiple_returns', False):
                                # Get all return types
                                return_types = self.functions[var_name].get('return_types', [])
                                # Create a placeholder for each return value
                                multiple_returns = []
                                for i, ret_type in enumerate(return_types):
                                    multiple_returns.append(f"{var_name}() result {i+1} [type: {ret_type}]")
                                # Add all return values to the express output
                                values_to_print.append(f"Multiple returns from {var_name}(): {', '.join(multiple_returns)}")
                            else:
                                # Single return value (old behavior)
                                func_return_type = self.functions[var_name].get('return_type', 'unknown')
                                values_to_print.append(f"{var_name}() result [type: {func_return_type}]")
                        else:
                            values_to_print.append(f"invalid call to {var_name}()")
                        
                        if self.current_token is not None and self.current_token[0] == ')':
                            self.next_token()  # Move past ')'
                else:
                    # Check for array access after identifier
                    if self.current_token is not None and self.current_token[0] == '[':
                        # This is an array access
                        var_type = None
                        if var_name in self.symbol_table:
                            var_type = self.symbol_table[var_name]['type']
                        elif var_name in self.global_symbol_table:
                            var_type = self.global_symbol_table[var_name]['type']
                            
                        # Process array access notation
                        if var_type and (var_type.startswith('array_') or var_type.startswith('clust_') or var_type.startswith('2d_array_')):
                            self.next_token()  # Move past '['
                            
                            # Check for splicing with colon
                            if self.current_token is not None and self.current_token[0] == ':':
                                self.next_token()  # Move past ':'
                                
                                # Check for negative float value in splicing
                                if self.current_token is not None and self.current_token[1] == 'numlit':
                                    value = self.current_token[0]
                                    if value.startswith('^') and '.' in value:
                                        self.errors.append("Semantic Error: negative quant values are not allowed in array splicing")
                            
                            # Skip to the end of the array access
                            bracket_count = 1
                            while self.current_token is not None and bracket_count > 0:
                                if self.current_token[0] == '[':
                                    bracket_count += 1
                                elif self.current_token[0] == ']':
                                    bracket_count -= 1
                                self.next_token()
                            
                            # Add to values_to_print
                            values_to_print.append(f"{var_name}[...] (array element)")
                        else:
                            # Add to values_to_print anyway
                            values_to_print.append(f"{var_name}[...]")
                            
                            # Skip to the end of the invalid array access
                            bracket_count = 1
                            while self.current_token is not None and bracket_count > 0:
                                if self.current_token[0] == '[':
                                    bracket_count += 1
                                elif self.current_token[0] == ']':
                                    bracket_count -= 1
                                self.next_token()
                    else:
                        # Handle function reference in express(Multiply) syntax
                        # This is a reference to a function without calling it (displaying function info)
                        if var_name in self.functions:
                            # Check if the function returns multiple values
                            if self.functions[var_name].get('multiple_returns', False):
                                # Get all return types
                                return_types = self.functions[var_name].get('return_types', [])
                                return_types_str = ', '.join(return_types)
                                param_count = len(self.functions[var_name].get('parameters', []))
                                values_to_print.append(f"Function {var_name} (returns multiple values: {return_types_str}, takes {param_count} parameters)")
                            else:
                                # Just print the function information (single return)
                                func_return_type = self.functions[var_name].get('return_type', 'unknown')
                                param_count = len(self.functions[var_name].get('parameters', []))
                                values_to_print.append(f"Function {var_name} (returns {func_return_type}, takes {param_count} parameters)")
                        # Regular variable - check in current scope first, then global
                        elif var_name not in self.symbol_table and var_name not in self.global_symbol_table:
                            self.errors.append(f"Semantic Error: Variable '{var_name}' used in express statement is not declared in current scope")
                            values_to_print.append(f"undefined({var_name})")
                        else:
                            # Get the value from the symbol table for printing
                            if var_name in self.symbol_table:
                                values_to_print.append(str(self.symbol_table[var_name]['value']))
                            else:
                                values_to_print.append(str(self.global_symbol_table[var_name]['value']))
            elif self.current_token[1] == 'string literal':
                # For string literals, strip quotes and handle escape sequences
                string_val = self.current_token[0].strip('"\'')
                # Handle \n escape sequence
                string_val = string_val.replace('\\n', '\n')
                values_to_print.append(string_val)
                self.next_token()  # Move past string literal
            elif self.current_token[1] == 'numlit':
                # For numeric literals
                values_to_print.append(self.current_token[0])
                self.next_token()  # Move past numlit
            elif self.current_token[0] in ['dom', 'rec']:
                # For boolean literals
                values_to_print.append(self.current_token[0])
                self.next_token()  # Move past boolean literal
            else:
                # For any other token - just take it as is
                values_to_print.append(str(self.current_token[0]))
                self.next_token()
            
            # Check for comma (multiple values)
            if self.current_token is not None and self.current_token[0] == ',':
                self.next_token()  # Move past comma
                continue
        
        # Check for closing parenthesis
        if self.current_token is None or self.current_token[0] != ')':
            self.errors.append(f"Semantic Error: Expected ')' in express statement, found {self.current_token}")
            return
            
        self.next_token()  # Move past ')'
        
        # Check for semicolon
        if self.current_token is None or self.current_token[0] != ';':
            
            # self.errors.append(f"Semantic Error: Expected ';' after express statement, found {self.current_token}")
            return
            
        self.next_token()  # Move past ';'
        
        # Store the express statement for output in the semantic panel
        self.express_outputs.append(values_to_print)

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
            var_info = None
            
            # Check both function and global scopes
            if var_name in self.symbol_table:
                var_info = self.symbol_table[var_name]
            elif var_name in self.global_symbol_table:
                var_info = self.global_symbol_table[var_name]
                
            if var_info is None:
                self.errors.append(f"Semantic Error: Variable '{var_name}' used in expression before declaration")
            
            # Save position to check for array access
            save_pos = self.token_index
            
            self.next_token()  # Move past identifier
            
            # Check for array access
            if self.current_token is not None and self.current_token[0] == '[':
                var_type = var_info['type'] if var_info else 'unknown'
                
                # Check if it's actually an array or a string
                if var_type.startswith('array_') or var_type.startswith('2d_array_') or var_type == 'seq':
                    # Skip the array index
                    self.next_token()  # Move past '['
                    bracket_count = 1
                    while self.current_token is not None and bracket_count > 0:
                        if self.current_token[0] == '[':
                            bracket_count += 1
                        elif self.current_token[0] == ']':
                            bracket_count -= 1
                        if bracket_count > 0:
                            self.next_token()
                    self.next_token()  # Move past the closing ']'
                else:
                    # Not an array access, restore position
                    self.token_index = save_pos
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
                # Strings can use concatenation
                return True
            elif left_type == 'allele' and operator in ['==', '!=']:
                # Boolean types can use equality operators
                return True
            elif operator in ['==', '!=']:
                # All types can use equality operators
                return True
            else:
                return False
        elif left_type in ['dose', 'quant'] and right_type in ['dose', 'quant']:
            # Different numeric types can be used together
            return True
        else:
            # Different non-numeric types are not compatible
            return False
        
    def type_check_assignment(self, var_name, value_token):
        """Check if value can be assigned to variable of given type"""
        if var_name not in self.symbol_table:
            self.errors.append(f"Semantic Error: Variable '{var_name}' not declared")
            return False
            
        # Check if the variable is a constant (perms)
        if self.symbol_table[var_name].get('is_const', False):
            self.errors.append(f"Semantic Error: Cannot reassign constant '{var_name}' (declared as perms)")
            return False
            
        var_type = self.symbol_table[var_name]['type']
        
        # Handle different token types
        if value_token[1] == 'numlit':
            if '.' in value_token[0]:  # Float value
                if var_type == 'quant':
                    return True
                elif var_type == 'dose':
                    self.errors.append(f"Semantic Error: Cannot assign float to dose variable '{var_name}'")
                    return False
                else:
                    self.errors.append(f"Semantic Error: Cannot assign number to {var_type} variable '{var_name}'")
                    return False
            else:  # Integer value
                if var_type in ['dose', 'quant']:
                    return True
                else:
                    self.errors.append(f"Semantic Error: Cannot assign number to {var_type} variable '{var_name}'")
                    return False
        elif value_token[1] == 'string literal':
            if var_type == 'seq':
                return True
            else:
                self.errors.append(f"Semantic Error: Cannot assign string to {var_type} variable '{var_name}'")
                return False
        elif value_token[0] in ['dom', 'rec']:
            if var_type == 'allele':
                return True
            else:
                self.errors.append(f"Semantic Error: Cannot assign boolean to {var_type} variable '{var_name}'")
                return False
        elif value_token[1] == 'Identifier':
            if value_token[0] not in self.symbol_table:
                self.errors.append(f"Semantic Error: Variable '{value_token[0]}' not declared")
                return False
                
            value_type = self.symbol_table[value_token[0]]['type']
            
            if var_type == value_type:
                return True
            elif var_type == 'quant' and value_type == 'dose':
                # Allow implicit conversion from dose to quant
                return True
            else:
                self.errors.append(f"Semantic Error: Cannot assign {value_type} value to {var_type} variable '{var_name}'")
                return False
        else:
            self.errors.append(f"Semantic Error: Invalid value token: {value_token}")
            return False
            
    def skip_to_end_of_block(self):
        """Skip tokens until the end of the current block (matching closing brace)"""
        # We assume we're just inside the { of a block
        brace_count = 1  # Already inside one level
        
        while self.current_token is not None and brace_count > 0:
            if self.current_token[0] == '{':
                brace_count += 1
            elif self.current_token[0] == '}':
                brace_count -= 1
                
            self.next_token()
            
        # At this point, we're at the token after the closing brace

    def enter_function_scope(self, function_name):
        """Enter a function scope - create or switch to function's symbol table"""
        self.current_function = function_name
        
        # Create new function scope if it doesn't exist
        if function_name not in self.function_scopes:
            self.function_scopes[function_name] = {}
            
        # Switch to function's symbol table
        self.symbol_table = self.function_scopes[function_name]

    def exit_function_scope(self):
        """Exit function scope - return to global scope"""
        self.current_function = None
        self.symbol_table = self.global_symbol_table


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
    """Analyze a code snippet (separate from the main file analysis)"""
    # Tokenize the snippet
    tokens = gxl.tokenize_input(code_snippet)
    
    # Create a semantic analyzer with an empty symbol table
    analyzer = SemanticAnalyzer(tokens)
    
    # Parse the tokens
    analyzer.parse()
    
    # Return the analyzer for examination
    return analyzer

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
        # Configure tags for styling
        semantic_panel.tag_configure("heading", font=("Inter", 12, "bold"))
        semantic_panel.tag_configure("success", foreground="green")
        semantic_panel.tag_configure("item", foreground="blue")
        semantic_panel.tag_configure("error", foreground="red")
        
        # Display errors in a simplified format
        semantic_panel.insert(tk.END, "Semantic Analysis Errors:\n", "heading")
        
        for i, error in enumerate(errors, 1):
            semantic_panel.insert(tk.END, f"{i}. {error}\n", "error")
        
        return False

def display_results(analyzer, semantic_panel):
    """Display the results of semantic analysis in a simple, clean format"""
    # Clear the panel first
    semantic_panel.delete('1.0', tk.END)
    
    # Configure tags for styling
    semantic_panel.tag_configure("heading", font=("Inter", 12, "bold"))
    semantic_panel.tag_configure("subheading", font=("Inter", 11, "bold"))
    semantic_panel.tag_configure("success", foreground="green")
    semantic_panel.tag_configure("item", foreground="blue")
    semantic_panel.tag_configure("error", foreground="red")
    
    # Display the global symbol table
    semantic_panel.insert(tk.END, "Global Symbol Table:\n", "heading")
    for var_name, var_info in analyzer.global_symbol_table.items():
        if not var_name.startswith('_'):  # Skip internal temporary variables
            type_str = var_info.get('type', 'unknown')
            value_str = str(var_info.get('value', 'undefined'))
            semantic_panel.insert(tk.END, f"• {var_name}: {type_str} = {value_str}\n", "item")
    
    # Display function-specific symbol tables
    if hasattr(analyzer, 'function_scopes') and analyzer.function_scopes:
        semantic_panel.insert(tk.END, "\nFunction Scopes:\n", "heading")
        for func_name, scope in analyzer.function_scopes.items():
            semantic_panel.insert(tk.END, f"\n{func_name}:\n", "subheading")
            if not scope:  # Empty function scope
                semantic_panel.insert(tk.END, "  (No local variables)\n", "item")
            else:
                for var_name, var_info in scope.items():
                    if not var_name.startswith('_'):  # Skip internal temporary variables
                        type_str = var_info.get('type', 'unknown')
                        value_str = str(var_info.get('value', 'undefined'))
                        semantic_panel.insert(tk.END, f"  • {var_name}: {type_str} = {value_str}\n", "item")
    
    # Display the function table
    semantic_panel.insert(tk.END, "\nFunctions:\n", "heading")
    for func_name, func_info in analyzer.functions.items():
        return_type = func_info.get('return_type', 'unknown')
        parameters = func_info.get('parameters', [])
        param_str = ", ".join([f"{p['name']}: {p['type']}" for p in parameters])
        semantic_panel.insert(tk.END, f"• {func_name} → {return_type} ({param_str})\n", "item")
    
    # Display express outputs
    if hasattr(analyzer, 'express_outputs') and analyzer.express_outputs:
        semantic_panel.insert(tk.END, "\nExpress Outputs:\n", "heading")
        for i, output_values in enumerate(analyzer.express_outputs):
            output_line = ", ".join(output_values)
            semantic_panel.insert(tk.END, f"• {output_line}\n", "item")
    
    # Display errors (if any)
    if analyzer.errors:
        semantic_panel.insert(tk.END, "\nErrors:\n", "heading")
        for error in analyzer.errors:
            semantic_panel.insert(tk.END, f"• {error}\n", "error")
            
    # Add success message if no errors
    if not analyzer.errors:
        semantic_panel.insert(tk.END, "\n✓ Semantic analysis completed successfully. No errors found.\n", "success")
