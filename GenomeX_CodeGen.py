import tkinter as tk
import GenomeX_Lexer as gxl
import GenomeX_Syntax as gxs
import GenomX_Semantic as gxsem
import io
import sys
import re

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
                i = self.process_global_declaration(i)
                
            # Handle functions
            elif token_type == 'act':
                i = self.process_function(i)
                
            else:
                i += 1
                
        return "\n".join(self.python_code)
        
    def process_global_declaration(self, index):
        """Process a global variable declaration that continues until a semicolon"""
        # Skip _G token
        index += 1
        
        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] == "space":
            index += 1
        
        # Get variable type
        if index < len(self.tokens) and self.tokens[index][1] in ["dose", "quant", "seq", "allele"]:
            var_type = self.tokens[index][1]
            index += 1
            
            # Skip spaces
            while index < len(self.tokens) and self.tokens[index][1] == "space":
                index += 1
            
            # Get variable name
            if index < len(self.tokens) and self.tokens[index][1] == "Identifier":
                var_name = self.tokens[index][0]
                index += 1
                
                # Skip spaces
                while index < len(self.tokens) and self.tokens[index][1] == "space":
                    index += 1
                
                # Check for assignment
                if index < len(self.tokens) and self.tokens[index][0] == "=":
                    index += 1
                    
                    # Skip spaces
                    while index < len(self.tokens) and self.tokens[index][1] == "space":
                        index += 1
                    
                    # Build expression until semicolon
                    expression = ""
                    while index < len(self.tokens) and self.tokens[index][0] != ";":
                        if self.tokens[index][1] != "space":
                            expression += self.tokens[index][0]
                        index += 1
                    
                    self.add_line(f"{var_name} = {expression}")
                else:
                    # No assignment, use default value
                    default_value = self.get_default_value(var_type)
                    self.add_line(f"{var_name} = {default_value}")
        
        # Skip the semicolon if present
        if index < len(self.tokens) and self.tokens[index][0] == ";":
            index += 1
        
        return index

    def process_function(self, index):
        """Process a function declaration"""
        # Skip 'act' token
        index += 1
        
        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] == "space":
            index += 1
            
        is_main = False
        function_name = None
        
        # Check for gene (main function)
        if index < len(self.tokens) and self.tokens[index][1] == "gene":
            is_main = True
            function_name = "main"
            index += 1
        # Check for regular function
        elif index < len(self.tokens) and self.tokens[index][1] == "Identifier":
            function_name = self.tokens[index][0]
            index += 1
            
        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] == "space":
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
                    while index < len(self.tokens) and self.tokens[index][1] == "space":
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
            while index < len(self.tokens) and self.tokens[index][1] == "space":
                index += 1
                
            # Check for opening brace
            if index < len(self.tokens) and self.tokens[index][0] == "{":
                index += 1

                while index < len(self.tokens):
                    # Process function body
                    index = self.process_function_body(index)

                    # Skip closing brace
                    if index < len(self.tokens) and self.tokens[index][0] == "}":
                        index += 1
                    else:
                        # If no closing brace, stop processing
                        break
            
            self.indentation -= 1
            self.current_scope = "global"
            
            # Add main function call at the end if this was the main function
            if is_main:
                # Reset indentation completely for the main section
                current_indent = self.indentation
                self.indentation = 0
                
                # Add a blank line to separate from previous code
                self.add_line("")
                
                # Add the main check with proper syntax
                self.add_line("if __name__ == \"__main__\":")
                
                # Set specific indentation for the main() call
                self.indentation = 1
                self.add_line("main()")
                
                # Reset indentation to what it was before
                self.indentation = current_indent
                
        return index
    
    def process_function_body(self, index, stop_at=None):
        """Process the body of a function"""
        while index < len(self.tokens):
            if stop_at is not None and index >= stop_at:
                print(f"[DEBUG] Stopping body processing at index {index} (limit: {stop_at})")
                break
            token, token_type = self.tokens[index]
            
            # Exit when we reach the closing brace
            if token == None:
                break
                
            # Skip spaces and newlines
            if token_type in ["space", "newline", "tab"]:
                index += 1
                continue
                
            # Handle local variable declarations
            if token_type == "_L":
                print(f"[DEBUG] Found _L at index {index}: {self.tokens[index]}")
                index = self.process_local_declaration(index)
                
            # Handle express statement (print)
            elif token_type == "express":
                print(f"[DEBUG] Found express at index {index}: {self.tokens[index]}")
                index = self.process_express_statement(index)
                
            # Handle if statement
            elif token_type == "if":
                print(f"[DEBUG] Found if at index {index}: {self.tokens[index]}")
                index = self.process_if_statement(index)
                
            elif token_type == "elif":
                print(f"[DEBUG] Found elif at index {index}: {self.tokens[index]}")
                # self.indentation -= 1
                index = self.process_elif_statement(index)

            elif token_type == "else":
                print(f"[DEBUG] Found else at index {index}: {self.tokens[index]}")
                # self.indentation -= 1
                index = self.process_else_statement(index)

            # Handle while loop
            elif token_type == "while":
                print(f"[DEBUG] Found while at index {index}: {self.tokens[index]}")
                index = self.process_while_loop(index)
                
            # Handle for loop
            elif token_type == "for":
                print(f"[DEBUG] Found for at index {index}: {self.tokens[index]}")
                index = self.process_for_loop(index)
                
            # Handle prod statement (return)
            elif token_type == "prod":
                print(f"[DEBUG] Found prod at index {index}: {self.tokens[index]}")
                index = self.process_prod_statement(index)
            
            # Handle function call
            elif token_type == "func":
                print(f"[DEBUG] Found func at index {index}: {self.tokens[index]}")
                index = self.process_function_call(index)
                
            # Handle assignment
            elif token_type == "Identifier":
                print(f"[DEBUG] Found Identifier at index {index}: {self.tokens[index]}")
                index = self.process_assignment(index)
                
            elif token_type == "comment":
                pass
            else:
                index += 1
                
        return index
    
    def process_local_declaration(self, index):
        """Process a local variable declaration"""
        # Skip _L token
        index += 1

        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] == "space":
            index += 1

        # Get variable type
        if index < len(self.tokens) and self.tokens[index][1] in ["dose", "quant", "seq", "allele"]:
            var_type = self.tokens[index][1]
            index += 1

            while index < len(self.tokens):
                # Skip spaces
                while index < len(self.tokens) and self.tokens[index][1] == "space":
                    index += 1

                # Check for variable name
                if index < len(self.tokens) and self.tokens[index][1] == "Identifier":
                    var_name = self.tokens[index][0]
                    self.variable_types[var_name] = var_type  # Track variable type
                    index += 1

                    # Skip spaces
                    while index < len(self.tokens) and self.tokens[index][1] == "space":
                        index += 1

                    # Check for assignment
                    if index < len(self.tokens) and self.tokens[index][0] == "=":
                        index += 1
                        # Skip spaces
                        while index < len(self.tokens) and self.tokens[index][1] == "space":
                            index += 1

                        # Get the value
                        value, index = self.extract_value(index)
                        self.add_line(f"{var_name} = {value}")
                    else:
                        # Default initialization based on type
                        default_value = self.get_default_value(var_type)
                        self.add_line(f"{var_name} = {default_value}")
                
                # Skip spaces
                while index < len(self.tokens) and self.tokens[index][1] == "space":
                    index += 1

                # If semicolon, end of declaration
                if index < len(self.tokens) and self.tokens[index][0] == ";":
                    index += 1
                    break

                # If comma, move to next variable
                elif index < len(self.tokens) and self.tokens[index][0] == ",":
                    index += 1
                    continue
                else:
                    # Unexpected token
                    break

        return index
        
    def process_express_statement(self, index):
        index += 1  # Skip 'express'

        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] == "space":
            index += 1

        # Check for opening parenthesis
        if index < len(self.tokens) and self.tokens[index][0] == "(":
            index += 1

            # Build the expression as a string
            expression_parts = []
            paren_count = 1  # we've already seen one (
            while index < len(self.tokens) and paren_count > 0:
                token, token_type = self.tokens[index]

                if token == "(":
                    paren_count += 1
                elif token == ")":
                    paren_count -= 1
                    if paren_count == 0:
                        break

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

                    processed_words.append(f"{func_name}({var})")
                    i += 4  # Skip all four tokens
                else:
                    processed_words.append(words[i])
                    i += 1

            processed_expression = " ".join(processed_words)
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
        while index < len(self.tokens) and self.tokens[index][1] == "space":
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
        while index < len(self.tokens) and self.tokens[index][1] == "space":
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
        while index < len(self.tokens) and self.tokens[index][1] == "space":
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
        while index < len(self.tokens) and self.tokens[index][1] == "space":
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
        while index < len(self.tokens) and self.tokens[index][1] == "space":
            print(f"[DEBUG] Skipping space at index {index}")
            index += 1

        # Generate Python if statement
        self.add_line(f"else :")
        print(f"[DEBUG] Added line: elif :")

        self.indentation += 1
        print(f"[DEBUG] Increased indentation to {self.indentation}")

        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] == "space":
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
        print(f"DEBUG: Entering process_while_loop at index {index}, token: {self.tokens[index]}")

        # Skip 'while'
        index += 1

        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] == "space":
            index += 1

        # Extract condition
        condition, index = self.extract_condition(index)
        print(f"DEBUG: Extracted condition: '{condition}', new index: {index}")

        # Clean up the condition - remove extra spaces and ensure proper formatting
        condition = condition.strip()
        
        # Generate the while loop with proper condition formatting
        self.add_line(f"while {condition}:")
        self.indentation += 1

        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] == "space":
            index += 1

        # Expect opening brace
        if index < len(self.tokens) and self.tokens[index][0] == "{":
            index += 1  # Skip '{'
            
            # Skip newlines after the opening brace
            while index < len(self.tokens) and self.tokens[index][1] == "newline":
                index += 1

            # Process the loop body
            while index < len(self.tokens):
                token, token_type = self.tokens[index]

                # Skip spaces without affecting newlines
                while index < len(self.tokens) and self.tokens[index][1] == "space":
                    index += 1
                    if index >= len(self.tokens):
                        break
                    token, token_type = self.tokens[index]

                # End of while loop body
                if token == "}":
                    index += 1
                    break

                # Process statement
                if token_type == "while":
                    index = self.process_while_loop(index)
                elif token_type == "if":
                    index = self.process_if_statement(index)
                elif token_type == "Identifier":
                    index = self.process_assignment(index)
                elif token_type == "for":
                    index = self.process_for_loop(index)
                elif token_type == "express":
                    index = self.process_express_statement(index)
                else:
                    print(f"DEBUG: Extracting regular statement at index {index}")
                    statement, index = self.extract_statement(index)
                    if statement:  # Only add non-empty statements
                        self.add_line(statement)
                    
                # Skip newlines after statements
                while index < len(self.tokens) and self.tokens[index][1] == "newline":
                    index += 1
        else:
            print(f"DEBUG: Expected '{{' but found {self.tokens[index] if index < len(self.tokens) else 'EOF'}")

        self.indentation -= 1
        print(f"DEBUG: Exiting process_while_loop at index {index}")
        return index
    
    def process_for_loop(self, index):
        """Process a for loop and translate it into Python syntax"""
        print(f"DEBUG: Starting process_for_loop at index {index}, token: {self.tokens[index] if index < len(self.tokens) else 'END'}")
        print(f"DEBUG: Full loop tokens: {self.tokens[index:index+15]}")  # Print more tokens to see the structure
        
        index += 1  # Skip 'for'
        print(f"DEBUG: After skipping 'for', index: {index}, token: {self.tokens[index] if index < len(self.tokens) else 'END'}")

        while index < len(self.tokens) and self.tokens[index][1] == "space":
            index += 1
        
        print(f"DEBUG: After skipping spaces, index: {index}, token: {self.tokens[index] if index < len(self.tokens) else 'END'}")

        if index < len(self.tokens) and self.tokens[index][0] == "(":
            index += 1
            print(f"DEBUG: After opening parenthesis, index: {index}, token: {self.tokens[index] if index < len(self.tokens) else 'END'}")

            while index < len(self.tokens) and self.tokens[index][1] == "space":
                index += 1

            # Initialization - Handle both standard case and "type var = value" case
            init_var = None
            init_value = None

            # Check if we have a declaration like "int i = 1" or "dose I = 1"
            if index + 4 < len(self.tokens) and self.tokens[index][1] in ["Identifier", "dose"] and self.tokens[index+1][1] == "space" and self.tokens[index+2][1] == "Identifier":
                # This looks like a type declaration (e.g., "dose I = 1")
                type_name = self.tokens[index][0]
                index += 1  # Skip type name
                
                while index < len(self.tokens) and self.tokens[index][1] == "space":
                    index += 1
                    
                if index < len(self.tokens) and self.tokens[index][1] == "Identifier":
                    init_var = self.tokens[index][0]
                    print(f"DEBUG: Found init_var with type: {type_name} {init_var}")
                    index += 1

                    while index < len(self.tokens) and self.tokens[index][1] == "space":
                        index += 1

                    if index < len(self.tokens) and self.tokens[index][0] == "=":
                        index += 1

                        while index < len(self.tokens) and self.tokens[index][1] == "space":
                            index += 1

                        # Get the numeric value
                        if index < len(self.tokens) and self.tokens[index][1] in ["Number", "Identifier"]:
                            init_value = self.tokens[index][0]
                            print(f"DEBUG: Found init_value: {init_value}")
                            index += 1
                        else:
                            init_value, index = self.extract_value(index)
                            print(f"DEBUG: Found extracted init_value: {init_value}")
            
            # Standard case (var = value) if we haven't found a variable yet
            elif index < len(self.tokens) and self.tokens[index][1] == "Identifier":
                init_var = self.tokens[index][0]
                print(f"DEBUG: Found init_var: {init_var}")
                index += 1

                while index < len(self.tokens) and self.tokens[index][1] == "space":
                    index += 1

                if index < len(self.tokens) and self.tokens[index][0] == "=":
                    index += 1

                    while index < len(self.tokens) and self.tokens[index][1] == "space":
                        index += 1

                    init_value, index = self.extract_value(index)
                    print(f"DEBUG: Found init_value: {init_value}")

            # Skip semicolon
            while index < len(self.tokens) and self.tokens[index][0] != ";":
                index += 1
            
            if index < len(self.tokens):
                print(f"DEBUG: Found semicolon at index: {index}")
                index += 1
            else:
                print(f"DEBUG: Reached end without finding semicolon")

            while index < len(self.tokens) and self.tokens[index][1] == "space":
                index += 1

            # Condition
            print(f"DEBUG: Before extracting condition, index: {index}, token: {self.tokens[index] if index < len(self.tokens) else 'END'}")
            condition, index = self.extract_for_condition(index)
            print(f"DEBUG: Extracted condition: '{condition}', new index: {index}")
            
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
                print(f"DEBUG: Parsed condition - var: {condition_var}, op: {condition_op}, value: {condition_value}")
            else:
                print(f"DEBUG: Failed to parse condition: '{condition}'")

            # Skip semicolon
            print(f"DEBUG: Looking for second semicolon, current token: {self.tokens[index] if index < len(self.tokens) else 'END'}")
            while index < len(self.tokens) and self.tokens[index][0] != ";":
                index += 1
                print(f"DEBUG: Searching for semicolon, index: {index}, token: {self.tokens[index] if index < len(self.tokens) else 'END'}")
            
            if index < len(self.tokens):
                print(f"DEBUG: Found second semicolon at index: {index}")
                index += 1
            else:
                print(f"DEBUG: Reached end without finding second semicolon")

            while index < len(self.tokens) and self.tokens[index][1] == "space":
                index += 1

            # Increment
            increment_var = None
            increment_op = None
            increment_value = "1"

            print(f"DEBUG: Before increment part, index: {index}, token: {self.tokens[index] if index < len(self.tokens) else 'END'}")
            
            # Check for increment variable
            if index < len(self.tokens) and self.tokens[index][1] == "Identifier":
                increment_var = self.tokens[index][0]
                print(f"DEBUG: Found increment_var: {increment_var}")
                index += 1

                while index < len(self.tokens) and self.tokens[index][1] == "space":
                    index += 1

                # Check for increment operator (++, --, +=, -=)
                print(f"DEBUG: Looking for increment operator, token: {self.tokens[index] if index < len(self.tokens) else 'END'}")
                
                # Handle ++ and -- operators, even if they're split from the variable
                if index < len(self.tokens):
                    if self.tokens[index][0] in ["++", "--"]:
                        increment_op = "+=" if self.tokens[index][0] == "++" else "-="
                        print(f"DEBUG: Found increment_op from ++/--: {increment_op}")
                        index += 1
                    elif self.tokens[index][0] in ["+=", "-="]:
                        increment_op = self.tokens[index][0]
                        print(f"DEBUG: Found increment_op: {increment_op}")
                        index += 1

                        while index < len(self.tokens) and self.tokens[index][1] == "space":
                            index += 1

                        increment_value, index = self.extract_value(index)
                        print(f"DEBUG: Found increment_value: {increment_value}")
                    # Check for space followed by ++ or -- (for cases like "I ++")
                    elif self.tokens[index][1] == "space":
                        temp_index = index
                        while temp_index < len(self.tokens) and self.tokens[temp_index][1] == "space":
                            temp_index += 1
                        
                        if temp_index < len(self.tokens) and self.tokens[temp_index][0] in ["++", "--"]:
                            increment_op = "+=" if self.tokens[temp_index][0] == "++" else "-="
                            print(f"DEBUG: Found increment_op (with space) from ++/--: {increment_op}")
                            index = temp_index + 1

            print(f"DEBUG: Looking for closing parenthesis, current token: {self.tokens[index] if index < len(self.tokens) else 'END'}")
            while index < len(self.tokens) and self.tokens[index][0] != ")":
                index += 1
                print(f"DEBUG: Searching for closing parenthesis, index: {index}, token: {self.tokens[index] if index < len(self.tokens) else 'END'}")
            
            if index < len(self.tokens):
                print(f"DEBUG: Found closing parenthesis at index: {index}")
                index += 1
            else:
                print(f"DEBUG: Reached end without finding closing parenthesis")

            # Attempt to translate to Python range-based for loop
            python_range_generated = False
            
            print(f"DEBUG: Translation check - init_var: {init_var}, init_value: {init_value}, condition_var: {condition_var}, " +
                f"condition_op: {condition_op}, condition_value: {condition_value}, " +
                f"increment_var: {increment_var}, increment_op: {increment_op}")
            
            # Special case for "for (dose I = 1; I <= Num; I++)" to "for I in range(1, Num + 1):"
            if init_value and condition_var and condition_op == "<=" and condition_value and increment_var and increment_op == "+=":
                if init_var == increment_var == condition_var:  # Standard case
                    print(f"DEBUG: Standard case - variables match")
                    end_value = condition_value
                    step = increment_value
                    self.add_line(f"for {init_var} in range({init_value}, {end_value} + 1, {step}):")
                    python_range_generated = True
                elif increment_var == condition_var:  # Special case with type declaration
                    print(f"DEBUG: Special case - increment/condition vars match but init_var is different")
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
                
                print(f"DEBUG: Range translation - end_value: {end_value}, step: {step}, condition_op: {condition_op}")
                
                if condition_op == "<":
                    # for i = start; i < end; i++ -> range(start, end)
                    self.add_line(f"for {init_var} in range({init_value}, {end_value}, {step}):")
                    print(f"DEBUG: Generated range with < operator")
                    python_range_generated = True
                elif condition_op == "<=":
                    # for i = start; i <= end; i++ -> range(start, end + 1)
                    self.add_line(f"for {init_var} in range({init_value}, {end_value} + 1, {step}):")
                    print(f"DEBUG: Generated range with <= operator")
                    python_range_generated = True
                elif condition_op == ">":
                    # for i = start; i > end; i-- -> range(start, end, -step)
                    if increment_op == "-=":
                        self.add_line(f"for {init_var} in range({init_value}, {end_value}, {step}):")
                        print(f"DEBUG: Generated range with > operator")
                        python_range_generated = True
                elif condition_op == ">=":
                    # for i = start; i >= end; i-- -> range(start, end - 1, -step)
                    if increment_op == "-=":
                        self.add_line(f"for {init_var} in range({init_value}, {end_value} - 1, {step}):")
                        print(f"DEBUG: Generated range with >= operator")
                        python_range_generated = True

            if not python_range_generated:
                print(f"DEBUG: Falling back to while loop")
                if init_var and init_value:
                    self.add_line(f"{init_var} = {init_value}")
                self.add_line(f"for {condition}:")

            self.indentation += 1

            while index < len(self.tokens) and self.tokens[index][1] == "space":
                index += 1

            print(f"DEBUG: Looking for opening brace, token: {self.tokens[index] if index < len(self.tokens) else 'END'}")
            if index < len(self.tokens) and self.tokens[index][0] == "{":
                print(f"DEBUG: Found opening brace")
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
            print(f"DEBUG: Finished process_for_loop, returning index: {index}")

        return index
    def process_prod_statement(self, index):
        """Process a prod (return) statement"""
        # Skip prod token
        index += 1
        
        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] == "space":
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
        print(f"[DEBUG] Variable name identified: '{var_name}'")
        index += 1

        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] == "space":
            print(f"[DEBUG] Skipping space at index {index}")
            index += 1

        # Check for assignment operator
        if index < len(self.tokens) and self.tokens[index][0] in ["=", "-=", "+=", "/=", "*="]:
            assignment_op = self.tokens[index][0]
            print(f"[DEBUG] Assignment operator found: '{assignment_op}' at index {index}")
            index += 1

            # Skip spaces
            while index < len(self.tokens) and self.tokens[index][1] == "space":
                print(f"[DEBUG] Skipping space at index {index} after assignment operator")
                index += 1

            # Check if the next token is a 'stimuli'
            if index < len(self.tokens) and self.tokens[index][1] == "stimuli":
                print(f"[DEBUG] Found 'stimuli' input at index {index}: {self.tokens[index]}")
                index = self.process_input(var_name, index)
            else:
                # Extract expression until semicolon
                value = ""
                print(f"[DEBUG] Beginning to parse expression for assignment to '{var_name}'")

                while index < len(self.tokens) and self.tokens[index][0] != ";":
                    token = self.tokens[index][0]
                    token_type = self.tokens[index][1]

                    if token_type != "space":
                        if token in ["+", "-", "/", "*", "%"]:  # Added modulo operator
                            value += " " + token + " "
                            print(f"[DEBUG] Appended operator to expression: '{token}'")
                        else:
                            value += token
                            print(f"[DEBUG] Appended token to expression: '{token}'")
                    
                    index += 1

                # Skip the semicolon
                if index < len(self.tokens) and self.tokens[index][0] == ";":
                    print(f"[DEBUG] Found semicolon at index {index}, ending assignment")
                    index += 1

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
        while index < len(self.tokens) and self.tokens[index][1] == "space":
            index += 1

        prompt = ""

        # Check if there's a parenthesis and string inside
        if index < len(self.tokens) and self.tokens[index][0] == "(":
            index += 1  # skip '('

            # Skip spaces
            while index < len(self.tokens) and self.tokens[index][1] == "space":
                index += 1

            if index < len(self.tokens) and self.tokens[index][1] == "string literal":
                prompt = self.tokens[index][0]
                index += 1

            # Skip spaces
            while index < len(self.tokens) and self.tokens[index][1] == "space":
                index += 1

            if index < len(self.tokens) and self.tokens[index][0] == ")":
                index += 1  # skip ')'

        # Check variable type to wrap with int() if needed
        if self.variable_types.get(var_name) == "dose":
            self.add_line(f'{var_name} = int(input({prompt}))')
        else:
            self.add_line(f'{var_name} = input({prompt})')

        return index

    def extract_value(self, index):
        """Extract a value expression"""
        if index >= len(self.tokens):
            return "None", index
            
        token, token_type = self.tokens[index]
        
        # Handle different value types
        if token_type == "numlit" :
            # Integer
            value = token
            index += 1

        # elif token_type == "quantval" or token_type == "nequantliteral":
        #     # Float
        #     value = token
        #     index += 1
        elif token_type == "string literal":
            # String
            value = token
            index += 1
        elif token_type == "Identifier":
            # Variable
            value = token
            index += 1
        elif token == "(":
            # Parenthesized expression
            index += 1
            value, index = self.extract_expression(index)
            
            # Skip closing parenthesis
            if index < len(self.tokens) and self.tokens[index][0] == ")":
                index += 1
        else:
            # Default
            value = "None"
            index += 1
            
        return value, index
    
    def extract_expression(self, index):
        """Extract a complete expression"""
        if index >= len(self.tokens):
            return "None", index
            
        left_value, index = self.extract_value(index)
        
        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] == "space":
            index += 1
            
        # Check for operators
        if index < len(self.tokens) and self.tokens[index][0] in ["+", "-", "*", "/", "%"]:
            operator = self.tokens[index][0]
            index += 1
            
            # Skip spaces
            while index < len(self.tokens) and self.tokens[index][1] == "space":
                index += 1
                
            right_value, index = self.extract_expression(index)
            
            return f"{left_value} {operator} {right_value}", index
        
        return left_value, index
    
    def extract_statement(self, index):
        """Extracts a regular statement ending with a semicolon"""
        print(f"DEBUG: Entering extract_statement at index {index}")
        statement_tokens = []
        
        # Skip spaces at the beginning
        while index < len(self.tokens) and self.tokens[index][1] == "space":
            index += 1

        # Extract tokens until we find a semicolon
        while index < len(self.tokens):
            token, token_type = self.tokens[index]
            
            # Stop at semicolon
            if token == ";":
                index += 1  # skip the semicolon
                break
                
            # Add non-space tokens to the statement
            if token_type != "space":
                statement_tokens.append(token)
                
            index += 1

        # Join tokens but use proper Python syntax
        statement = " ".join(statement_tokens).strip()
        
        # Handle division - convert / to // for integer division when appropriate
        # This is a simplistic approach, would need more context analysis for accuracy
        if re.search(r'(\b|[^/])/(\b|[^/])', statement) and not re.search(r'"/|/"', statement):
            statement = re.sub(r'(\b|[^/])/(\b|[^/])', r'\1//\2', statement)
        
        # Fix any incorrect colons that might have been introduced
        statement = statement.replace(":", "")
        
        print(f"DEBUG: Exiting extract_statement with statement: '{statement}', next index: {index}")
        return statement, index
    def extract_condition(self, index):
        """Extract a condition expression from tokens starting at the given index"""
        print(f"DEBUG: Starting extract_condition at index {index}, token: {self.tokens[index] if index < len(self.tokens) else 'END'}")
        
        start_index = index
        condition_parts = []
        paren_level = 0
        
        # Skip spaces at the beginning
        while index < len(self.tokens) and self.tokens[index][1] == "space":
            index += 1
            
        # Check for opening parenthesis
        if index < len(self.tokens) and self.tokens[index][0] == "(":
            condition_parts.append(self.tokens[index][0])
            index += 1
            paren_level += 1
            
            # Skip spaces after opening parenthesis
            while index < len(self.tokens) and self.tokens[index][1] == "space":
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
                # Add token to condition if it's not a space
                if token_type != "space":
                    condition_parts.append(token)
            
            index += 1
        
        # Join all parts of the condition
        condition = " ".join(condition_parts)
        
        # Replace '&&' with 'and'
        condition = condition.replace("&&", "and")
        
        # Remove surrounding parentheses if present
        condition = condition.strip()
        if condition.startswith("(") and condition.endswith(")"):
            condition = condition[1:-1].strip()
        
        print(f"DEBUG: Extracted condition: '{condition}', from tokens: {self.tokens[start_index:index]}")
        
        return condition, index

    def extract_for_condition(self, index):
        """Extract a condition for if/while statements"""
        if index >= len(self.tokens):
            return "False", index
            
        left_value, index = self.extract_value(index)
        
        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] == "space":
            index += 1
            
        # Check for comparison operators
        if index < len(self.tokens) and self.tokens[index][0] in ["==", "!=", "<", ">", "<=", ">="]:
            operator = self.tokens[index][0]
            index += 1
            
            # Skip spaces
            while index < len(self.tokens) and self.tokens[index][1] == "space":
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
        """Process a function call statement"""
        # Skip func token
        index += 1

        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] == "space":
            index += 1

        # Get function name
        function_name = None
        if index < len(self.tokens) and self.tokens[index][1] == "Identifier":
            function_name = self.tokens[index][0]
            index += 1

            # Skip spaces
            while index < len(self.tokens) and self.tokens[index][1] == "space":
                index += 1

            # Check for opening parenthesis
            if index < len(self.tokens) and self.tokens[index][0] == "(":
                index += 1

                # Process arguments
                args = []
                while index < len(self.tokens) and self.tokens[index][0] != ")":
                    # Skip spaces and commas
                    while index < len(self.tokens) and (self.tokens[index][1] == "space" or self.tokens[index][0] == ","):
                        index += 1

                    if index < len(self.tokens) and self.tokens[index][0] == ")":
                        break

                    # Get argument value
                    arg_value, index = self.extract_value(index)
                    args.append(arg_value)

                # Skip closing parenthesis
                if index < len(self.tokens) and self.tokens[index][0] == ")":
                    index += 1

                # Wrap the function call inside a print statement
                self.add_line(f"print({function_name}({', '.join(args)}))")

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
    print(f"parseCodeGen called with {len(tokens)} tokens")
    
    try:
        # Generate Python code
        print("[DEBUG] About to generate Python code from tokens...")
        python_code = generate_python_code(tokens)
        print(f"[DEBUG] Python code generated successfully, length: {len(python_code)}")
        print(f"[DEBUG] First 50 chars of generated code: {python_code[:50]}...")
        
        # Display the generated code in the codegen panel
        print("[DEBUG] About to display code in codegen panel...")
        #TRANSLATOR MISMO
        # display_codegen_output(python_code, codegen_panel)
        print("[DEBUG] Code displayed in output panel")

        # === Capture and execute code output ===
        # Redirect stdout temporarily to capture print statements
        print("[DEBUG] Setting up stdout redirection for execution capture...")
        original_stdout = sys.stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output

        try:
            print("[DEBUG] Starting execution of generated Python code...")
            # exec(python_code, {})
            output = captured_output.getvalue()
            print(f"[DEBUG] Captured output length: {len(output)} characters")
        except Exception as exec_error:
            print(f"[DEBUG] ERROR during code execution: {exec_error}")
            import traceback
            traceback.print_exc()
            output = f"Execution Error: {str(exec_error)}"
        finally:
            # Restore original stdout
            print("[DEBUG] Restoring original stdout...")
            sys.stdout = original_stdout

        # Print captured output to terminal
        print("----- Executed Code Output -----")
        # print(output)
        print("----- End of Output -----")
        
        # Add the output to the codegen panel as well
        print("[DEBUG] Adding execution output to codegen panel...")
        # codegen_panel.insert(tk.END, "\n\n----- EXECUTION OUTPUT -----\n")
        # codegen_panel.insert(tk.END, output)
        # codegen_panel.insert(tk.END, "\n----- END OF OUTPUT -----")
        print("[DEBUG] Execution output added to panel")

        return True, python_code

    except Exception as e:
        sys.stdout = original_stdout  # Ensure stdout is restored if an exception occurs
        print(f"[DEBUG] CRITICAL ERROR in parseCodeGen: {e}")
        import traceback
        traceback.print_exc()
        
        # Display the error in the codegen panel
        print("[DEBUG] Adding error message to codegen panel...")
        codegen_panel.insert(tk.END, "\n\n----- EXECUTION ERROR -----\n")
        codegen_panel.insert(tk.END, str(e))
        codegen_panel.insert(tk.END, "\n----- END OF ERROR -----")
        
        return False, str(e)
