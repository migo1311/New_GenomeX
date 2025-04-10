import tkinter as tk
import GenomeX_Lexer as gxl
import GenomeX_Syntax as gxs
import GenomX_Semantic as gxsem

class GenomeXCodeGenerator:
    def __init__(self, tokens, symbol_table=None):
        self.tokens = tokens
        self.symbol_table = symbol_table if symbol_table else {}
        self.functions = {}
        self.indentation = 0
        self.python_code = []
        self.current_scope = "global"
        
    def add_line(self, line):
        """Add a line of Python code with proper indentation"""
        indent = "    " * self.indentation
        self.python_code.append(f"{indent}{line}")
        
    def generate_code(self):
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
        """Process a global variable declaration"""
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
                
                # Check for assignment
                while index < len(self.tokens) and self.tokens[index][1] == "space":
                    index += 1
                
                # If assignment
                if index < len(self.tokens) and self.tokens[index][0] == "=":
                    index += 1
                    # Skip spaces
                    while index < len(self.tokens) and self.tokens[index][1] == "space":
                        index += 1
                    
                    # Get the value
                    value, index = self.extract_value(index)
                    
                    # Generate Python assignment
                    self.add_line(f"{var_name} = {value}")
                else:
                    # Default initialization based on type
                    default_value = self.get_default_value(var_type)
                    self.add_line(f"{var_name} = {default_value}")
        
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
    
    def process_function_body(self, index):
        """Process the body of a function"""
        while index < len(self.tokens):
            token, token_type = self.tokens[index]
            
            # Exit when we reach the closing brace
            if token == "}":
                break
                
            # Skip spaces and newlines
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
            
            # Skip spaces
            while index < len(self.tokens) and self.tokens[index][1] == "space":
                index += 1
                
            # Get variable name
            if index < len(self.tokens) and self.tokens[index][1] == "Identifier":
                var_name = self.tokens[index][0]
                index += 1
                
                # Check for assignment
                while index < len(self.tokens) and self.tokens[index][1] == "space":
                    index += 1
                
                # If assignment
                if index < len(self.tokens) and self.tokens[index][0] == "=":
                    index += 1
                    # Skip spaces
                    while index < len(self.tokens) and self.tokens[index][1] == "space":
                        index += 1
                    
                    # Get the value
                    value, index = self.extract_value(index)
                    
                    # Generate Python assignment
                    self.add_line(f"{var_name} = {value}")
                else:
                    # Default initialization based on type
                    default_value = self.get_default_value(var_type)
                    self.add_line(f"{var_name} = {default_value}")
        
        return index
    
    def process_express_statement(self, index):
        """Process an express (print) statement"""
        # Skip express token
        index += 1
        
        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] == "space":
            index += 1
            
        # Check for opening parenthesis
        if index < len(self.tokens) and self.tokens[index][0] == "(":
            index += 1
            
            # Process values to print
            values = []
            while index < len(self.tokens) and self.tokens[index][0] != ")":
                # Skip spaces and commas
                while index < len(self.tokens) and (self.tokens[index][1] == "space" or self.tokens[index][0] == ","):
                    index += 1
                
                if index < len(self.tokens) and self.tokens[index][0] == ")":
                    break
                
                # Get the value to print
                value, index = self.extract_value(index)
                values.append(value)
            
            # Skip closing parenthesis
            if index < len(self.tokens) and self.tokens[index][0] == ")":
                index += 1
            
            # Generate Python print statement
            if len(values) == 1:
                self.add_line(f"print({values[0]})")
            else:
                self.add_line(f"print({', '.join(values)})")
        else:
            # No parenthesis, simple value
            value, index = self.extract_value(index)
            self.add_line(f"print({value})")
        
        return index
    
    def process_if_statement(self, index):
        """Process an if statement"""
        # Skip if token
        index += 1
        
        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] == "space":
            index += 1
            
        # Extract condition
        condition, index = self.extract_condition(index)
        
        # Generate Python if statement
        self.add_line(f"if {condition}:")
        
        self.indentation += 1
        
        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] == "space":
            index += 1
            
        # Check for opening brace
        if index < len(self.tokens) and self.tokens[index][0] == "{":
            index += 1
            
            # Process if body
            index = self.process_function_body(index)
            
            # Skip closing brace
            if index < len(self.tokens) and self.tokens[index][0] == "}":
                index += 1
        
        self.indentation -= 1
        
        # Check for elif or else
        while index < len(self.tokens) and self.tokens[index][1] == "space":
            index += 1
            
        if index < len(self.tokens) and self.tokens[index][1] == "elif":
            index = self.process_elif_statement(index)
        elif index < len(self.tokens) and self.tokens[index][1] == "else":
            index = self.process_else_statement(index)
            
        return index
    
    def process_elif_statement(self, index):
        """Process an elif statement"""
        # Skip elif token
        index += 1
        
        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] == "space":
            index += 1
            
        # Extract condition
        condition, index = self.extract_condition(index)
        
        # Generate Python elif statement
        self.add_line(f"elif {condition}:")
        
        self.indentation += 1
        
        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] == "space":
            index += 1
            
        # Check for opening brace
        if index < len(self.tokens) and self.tokens[index][0] == "{":
            index += 1
            
            # Process elif body
            index = self.process_function_body(index)
            
            # Skip closing brace
            if index < len(self.tokens) and self.tokens[index][0] == "}":
                index += 1
        
        self.indentation -= 1
        
        # Check for more elif or else
        while index < len(self.tokens) and self.tokens[index][1] == "space":
            index += 1
            
        if index < len(self.tokens) and self.tokens[index][1] == "elif":
            index = self.process_elif_statement(index)
        elif index < len(self.tokens) and self.tokens[index][1] == "else":
            index = self.process_else_statement(index)
            
        return index
    
    def process_else_statement(self, index):
        """Process an else statement"""
        # Skip else token
        index += 1
        
        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] == "space":
            index += 1
            
        # Generate Python else statement
        self.add_line("else:")
        
        self.indentation += 1
        
        # Check for opening brace
        if index < len(self.tokens) and self.tokens[index][0] == "{":
            index += 1
            
            # Process else body
            index = self.process_function_body(index)
            
            # Skip closing brace
            if index < len(self.tokens) and self.tokens[index][0] == "}":
                index += 1
        
        self.indentation -= 1
            
        return index
    
    def process_while_loop(self, index):
        """Process a while loop"""
        # Skip while token
        index += 1
        
        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] == "space":
            index += 1
            
        # Extract condition
        condition, index = self.extract_condition(index)
        
        # Generate Python while loop
        self.add_line(f"while {condition}:")
        
        self.indentation += 1
        
        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] == "space":
            index += 1
            
        # Check for opening brace
        if index < len(self.tokens) and self.tokens[index][0] == "{":
            index += 1
            
            # Process while body
            index = self.process_function_body(index)
            
            # Skip closing brace
            if index < len(self.tokens) and self.tokens[index][0] == "}":
                index += 1
        
        self.indentation -= 1
            
        return index
    
    def process_for_loop(self, index):
        """Process a for loop"""
        # Skip for token
        index += 1
        
        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] == "space":
            index += 1
            
        # Check for opening parenthesis
        if index < len(self.tokens) and self.tokens[index][0] == "(":
            index += 1
            
            # Skip spaces
            while index < len(self.tokens) and self.tokens[index][1] == "space":
                index += 1
                
            # Extract initialization
            init_var = None
            init_value = None
            
            # Look for initialization (variable = value)
            if index < len(self.tokens) and self.tokens[index][1] == "Identifier":
                init_var = self.tokens[index][0]
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
                    
                    # Get initial value
                    init_value, index = self.extract_value(index)
            
            # Skip semicolon
            while index < len(self.tokens) and self.tokens[index][0] != ";":
                index += 1
            index += 1
            
            # Skip spaces
            while index < len(self.tokens) and self.tokens[index][1] == "space":
                index += 1
            
            # Extract condition
            condition, index = self.extract_condition(index)
            
            # Skip semicolon
            while index < len(self.tokens) and self.tokens[index][0] != ";":
                index += 1
            index += 1
            
            # Skip spaces
            while index < len(self.tokens) and self.tokens[index][1] == "space":
                index += 1
            
            # Extract increment
            increment_var = None
            increment_op = None
            
            if index < len(self.tokens) and self.tokens[index][1] == "Identifier":
                increment_var = self.tokens[index][0]
                index += 1
                
                # Skip spaces
                while index < len(self.tokens) and self.tokens[index][1] == "space":
                    index += 1
                
                # Check for increment/decrement
                if index < len(self.tokens) and self.tokens[index][0] in ["+=", "-="]:
                    increment_op = self.tokens[index][0]
                    index += 1
                    
                    # Skip spaces
                    while index < len(self.tokens) and self.tokens[index][1] == "space":
                        index += 1
                    
                    # Get increment value
                    increment_value, index = self.extract_value(index)
            
            # Skip closing parenthesis
            while index < len(self.tokens) and self.tokens[index][0] != ")":
                index += 1
            index += 1
            
            # Generate Python for loop components
            if init_var and init_value:
                self.add_line(f"{init_var} = {init_value}")
            
            self.add_line(f"while {condition}:")
            self.indentation += 1
            
            # Skip spaces
            while index < len(self.tokens) and self.tokens[index][1] == "space":
                index += 1
            
            # Check for opening brace
            if index < len(self.tokens) and self.tokens[index][0] == "{":
                index += 1
                
                # Process for loop body
                index = self.process_function_body(index)
                
                # Add increment at the end of the loop body
                if increment_var and increment_op:
                    if increment_op == "+=":
                        self.add_line(f"{increment_var} += {increment_value}")
                    elif increment_op == "-=":
                        self.add_line(f"{increment_var} -= {increment_value}")
                
                # Skip closing brace
                if index < len(self.tokens) and self.tokens[index][0] == "}":
                    index += 1
            
            self.indentation -= 1
            
        return index
    
    def process_prod_statement(self, index):
        """Process a prod (return) statement"""
        # Skip prod token
        index += 1
        
        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] == "space":
            index += 1
            
        # Extract return value
        value, index = self.extract_value(index)
        
        # Generate Python return statement
        self.add_line(f"return {value}")
        
        return index
    
    def process_assignment(self, index):
        """Process a variable assignment"""
        var_name = self.tokens[index][0]
        index += 1
        
        # Skip spaces
        while index < len(self.tokens) and self.tokens[index][1] == "space":
            index += 1
        
        # Check for assignment operator
        if index < len(self.tokens) and self.tokens[index][0] == "=":
            index += 1
            
            # Skip spaces
            while index < len(self.tokens) and self.tokens[index][1] == "space":
                index += 1
            
            # Extract value
            value, index = self.extract_value(index)
            
            # Generate Python assignment
            self.add_line(f"{var_name} = {value}")
        
        return index
    
    def extract_value(self, index):
        """Extract a value expression"""
        if index >= len(self.tokens):
            return "None", index
            
        token, token_type = self.tokens[index]
        
        # Handle different value types
        if token_type == "doseliteral" or token_type == "neliteral":
            # Integer
            value = token
            index += 1
        elif token_type == "quantval" or token_type == "nequantliteral":
            # Float
            value = token
            index += 1
        elif token_type == "stringlit":
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
    
    def extract_condition(self, index):
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
                
                # Generate Python function call
                self.add_line(f"{function_name}({', '.join(args)})")
        
        return index

def generate_python_code(tokens, symbol_table=None):
    """Generate Python code from GenomeX tokens"""
    code_generator = GenomeXCodeGenerator(tokens, symbol_table)
    return code_generator.generate_code()

def display_codegen_output(python_code, output_panel):
    """Display the generated Python code in the output panel"""
    output_panel.delete(1.0, tk.END)
    output_panel.insert(tk.END, python_code)
    return python_code

def parseCodeGen(tokens, codegen_panel):
    """Parse tokens and generate Python code if semantic analysis passes"""
    # Perform semantic analysis first
    semantic_success = gxsem.parseSemantic(tokens, None)
    
    if semantic_success:
        # Generate Python code
        python_code = generate_python_code(tokens)
        
        # Display the generated code
        display_codegen_output(python_code, codegen_panel)
        
        # Return success and the Python code
        return True, python_code
    else:
        # If semantic analysis failed, display an error message
        codegen_panel.delete(1.0, tk.END)
        codegen_panel.insert(tk.END, "Cannot generate code: Semantic analysis failed. Please fix the errors first.")
        
        # Return failure
        return False, None
