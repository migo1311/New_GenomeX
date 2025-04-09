import re
import sys
from typing import List, Dict, Tuple, Any, Optional, Union

class CodeGenerator:
    """
    Code Generator for GenomeX language.
    Translates tokens and syntax tree to a high-level language (Python).
    """
    
    def __init__(self, tokens=None, output_lang="python"):
        """
        Initialize the code generator.
        
        Args:
            tokens: List of tokens from lexical analysis
            output_lang: Target language for code generation
        """
        self.tokens = tokens or []
        self.output_lang = output_lang.lower()
        self.output_code = []
        self.current_indent = 0
        self.symbol_table = {}
        self.function_table = {}
        self.in_function = False
        self.in_gene = False
        self.current_scope = "global"
        self.current_token_idx = 0
        self.current_token = None
        self.line_number = 1
        
        # Language-specific translation maps
        self.type_map = {
            "dose": "int",
            "quant": "float",
            "seq": "str",
            "allele": "bool"
        }
        
        self.keyword_map = {
            "dom": "True",
            "rec": "False",
            "gene": "main",
            "if": "if",
            "elif": "elif",
            "else": "else",
            "while": "while",
            "for": "for",
            "express": "print",
            "void": ""
        }
        
        self.operator_map = {
            "&&": "and",
            "||": "or",
            "!": "not ",
            "!=": "!=",
            "==": "==",
            ">=": ">=",
            "<=": "<=",
            ">": ">",
            "<": "<",
            "+": "+",
            "-": "-",
            "*": "*",
            "/": "/",
            "%": "%"
        }

    def add_line(self, line, end_line=True):
        """
        Add a line of code with appropriate indentation.
        
        Args:
            line: The line of code to add
            end_line: Whether to append a newline character (default: True)
        """
        indentation = "    " * self.current_indent
        if end_line:
            self.output_code.append(f"{indentation}{line}")
        else:
            # If end_line is False, we're starting a line that will be completed later
            self.output_code.append(f"{indentation}{line}")
    
    def get_next_token(self):
        """Move to the next token and return it."""
        while self.current_token_idx < len(self.tokens):
            token = self.tokens[self.current_token_idx]
            self.current_token_idx += 1
            
            # Skip spaces and update line number for newlines
            if token[1] == "space":
                continue
            elif token[1] == "newline":
                self.line_number += 1
                continue
            
            self.current_token = token
            return token
            
        self.current_token = None
        return None
    
    def peek_next_token(self):
        """Look at the next token without consuming it."""
        i = self.current_token_idx
        while i < len(self.tokens):
            if self.tokens[i][1] not in ["space", "newline"]:
                return self.tokens[i]
            i += 1
        return None
    
    def generate_code(self):
        """
        Generate code in the target language from the tokens.
        Returns a string with the generated code.
        """
        # Add language-specific imports or setup
        if self.output_lang == "python":
            self.add_line("# Generated Python code from GenomeX")
            self.add_line("")
        
        # Reset token pointer
        self.current_token_idx = 0
        
        # Process tokens until we reach the end
        while self.get_next_token() is not None:
            self.process_current_token()
        
        # Add main function call if needed
        if self.output_lang == "python":
            self.add_line("")
            self.add_line("if __name__ == \"__main__\":")
            self.current_indent += 1
            self.add_line("main()")
            self.current_indent -= 1
        
        # Join all lines of code
        return "\n".join(self.output_code)
    
    def process_current_token(self):
        """Process the current token and generate code accordingly."""
        token = self.current_token
        
        if token is None:
            return
        
        # Get token value and type
        token_value, token_type = token
        
        # Process based on token type
        if token_value == "_G":
            self.process_global_declaration()
        elif token_value == "_L":
            self.process_local_declaration()
        elif token_value == "act":
            self.process_function_declaration()
        elif token_type == "Identifier" and self.peek_next_token() and self.peek_next_token()[0] in ["=", "+=", "-=", "*=", "/=", "%="]:
            self.process_assignment()
        elif token_value == "if":
            self.process_if_statement()
        elif token_value == "for":
            self.process_for_loop()
        elif token_value == "while":
            self.process_while_loop()
        elif token_value == "do":
            self.process_do_while_loop()
        elif token_value == "express":
            self.process_express_statement()
    
    def process_global_declaration(self):
        """Process global variable declaration."""
        # Get the variable type
        type_token = self.get_next_token()
        if type_token is None or type_token[0] not in ["dose", "quant", "seq", "allele"]:
            return
        
        var_type = type_token[0]
        python_type = self.type_map.get(var_type, "Any")
        
        # Process variable names and initializations
        self.process_variable_declarations(var_type, is_global=True)
    
    def process_local_declaration(self):
        """Process local variable declaration."""
        # Get the variable type
        type_token = self.get_next_token()
        if type_token is None or type_token[0] not in ["dose", "quant", "seq", "allele"]:
            return
        
        var_type = type_token[0]
        python_type = self.type_map.get(var_type, "Any")
        
        # Process variable names and initializations
        self.process_variable_declarations(var_type, is_global=False)
    
    def process_variable_declarations(self, var_type, is_global=False):
        """Process variable declarations of a specific type."""
        python_type = self.type_map.get(var_type, "Any")
        
        # Initialize variables for tracking declarations
        var_names = []
        var_inits = {}
        
        # Process each variable in the comma-separated list
        while True:
            # Get variable name
            var_token = self.get_next_token()
            if var_token is None or var_token[1] != "Identifier":
                break
                
            var_name = var_token[0]
            var_names.append(var_name)
            
            # Update symbol table
            self.symbol_table[var_name] = {
                "type": var_type,
                "scope": "global" if is_global else "local"
            }
            
            # Check for initialization
            next_token = self.get_next_token()
            if next_token and next_token[0] == "=":
                # Process initialization expression
                init_value = self.process_expression()
                var_inits[var_name] = init_value
            elif next_token and next_token[0] == ",":
                # Continue to next variable
                continue
            elif next_token and next_token[0] == ";":
                # End of declaration
                break
        
        # Generate code for the declarations
        for var_name in var_names:
            if var_name in var_inits:
                # Variable with initialization
                if is_global:
                    self.add_line(f"{var_name} = {var_inits[var_name]}")
                else:
                    self.add_line(f"{var_name} = {var_inits[var_name]}")
            else:
                # Variable without initialization
                default_value = self.get_default_value(var_type)
                if is_global:
                    self.add_line(f"{var_name} = {default_value}")
                else:
                    self.add_line(f"{var_name} = {default_value}")
    
    def get_default_value(self, var_type):
        """Get the default value for a variable type."""
        if var_type == "dose":
            return "0"
        elif var_type == "quant":
            return "0.0"
        elif var_type == "seq":
            return '""'
        elif var_type == "allele":
            return "False"
        return "None"
    
    def process_function_declaration(self):
        """Process function or gene (main) declaration."""
        # Skip 'act' token
        function_type_token = self.get_next_token()
        
        if function_type_token is None:
            return
            
        func_name = None
        return_type = None
        
        if function_type_token[0] == "gene":
            # Main function
            func_name = "main"
            return_type = None
            self.in_gene = True
        elif function_type_token[0] == "void":
            # Void function
            name_token = self.get_next_token()
            if name_token and name_token[1] == "Identifier":
                func_name = name_token[0]
                return_type = None
        else:
            # Regular function with identifier and return type
            func_name = function_type_token[0]
            return_type = "Any"  # Default return type
        
        if func_name is None:
            return
            
        # Update function tracking
        self.in_function = True
        self.current_scope = "local"
        
        # Start processing function declaration
        self.add_line(f"def {func_name}():")
        self.current_indent += 1
        
        # Look for opening parenthesis
        open_paren = self.get_next_token()
        if open_paren is None or open_paren[0] != "(":
            self.current_indent -= 1
            return
            
        # Parse parameters
        parameters = []
        while True:
            param_token = self.get_next_token()
            if param_token is None:
                break
                
            if param_token[0] == ")":
                # End of parameters
                break
                
            if param_token[0] in ["dose", "quant", "seq", "allele"]:
                # Parameter type
                param_type = param_token[0]
                python_type = self.type_map.get(param_type, "Any")
                
                # Parameter name
                param_name_token = self.get_next_token()
                if param_name_token and param_name_token[1] == "Identifier":
                    param_name = param_name_token[0]
                    parameters.append((param_name, param_type))
                    
                    # Update symbol table
                    self.symbol_table[param_name] = {
                        "type": param_type,
                        "scope": "parameter"
                    }
                
                # Check for comma or closing parenthesis
                next_token = self.get_next_token()
                if next_token and next_token[0] == ",":
                    continue
                elif next_token and next_token[0] == ")":
                    break
        
        # Update function definition with parameters
        if parameters:
            param_str = ", ".join(name for name, _ in parameters)
            # Go back and update the function signature
            self.output_code[-1] = f"def {func_name}({param_str}):"
        
        # Look for opening brace
        open_brace = self.get_next_token()
        if open_brace is None or open_brace[0] != "{":
            self.current_indent -= 1
            return
            
        # Process function body (until we find a closing brace)
        nesting_level = 1
        while True:
            token = self.get_next_token()
            if token is None:
                break
                
            if token[0] == "{":
                nesting_level += 1
            elif token[0] == "}":
                nesting_level -= 1
                if nesting_level == 0:
                    # End of function body
                    break
            
            # Process the current token within the function body
            self.process_current_token()
        
        # Add a default return statement for non-void functions if needed
        if return_type != None and not self.has_return_statement():
            default_return = self.get_default_value(return_type)
            self.add_line(f"return {default_return}")
        
        # Reset function tracking
        self.in_function = False
        self.in_gene = False
        self.current_scope = "global"
        self.current_indent -= 1
    
    def has_return_statement(self):
        """Check if the function has a return statement."""
        # This is a simplified check, might not catch all return statements
        for line in self.output_code[-10:]:  # Check the last few lines
            if "return " in line:
                return True
        return False
    
    def process_assignment(self):
        """Process variable assignment."""
        var_name = self.current_token[0]
        
        # Get assignment operator
        op_token = self.get_next_token()
        if op_token is None:
            return
            
        op = op_token[0]
        
        # Process right-hand side expression
        rhs = self.process_expression()
        
        # Generate assignment code
        if op == "=":
            self.add_line(f"{var_name} = {rhs}")
        else:
            # Compound assignment (+=, -=, etc.)
            python_op = op
            self.add_line(f"{var_name} {python_op} {rhs}")
        
        # Look for semicolon
        semi_token = self.get_next_token()
        if semi_token is None or semi_token[0] != ";":
            # Missing semicolon, but we'll continue anyway
            pass
    
    def process_expression(self):
        """Process an expression and return its code representation."""
        components = []
        nesting_level = 0
        
        while True:
            token = self.get_next_token()
            if token is None:
                break
                
            value, token_type = token
            
            if value == "(":
                components.append("(")
                nesting_level += 1
            elif value == ")":
                components.append(")")
                nesting_level -= 1
                if nesting_level < 0:
                    # We've reached the end of this expression
                    break
            elif value == ";":
                # End of expression
                break
            elif value == ",":
                # End of this expression in a comma-separated list
                break
            elif token_type == "numlit":
                # Numeric literal
                components.append(value)
            elif token_type == "string literal":
                # String literal - keep the quotes
                components.append(value)
            elif value in ["dom", "rec"]:
                # Boolean literals
                components.append(self.keyword_map[value])
            elif token_type == "Identifier":
                # Variable
                components.append(value)
            elif value in self.operator_map:
                # Operator
                components.append(self.operator_map[value])
            elif value in ["+", "-", "*", "/", "%"]:
                # Arithmetic operator
                components.append(value)
        
        # Reassemble the expression
        expression = " ".join(components)
        
        # Handle any adjustments for specific language syntax
        if self.output_lang == "python":
            # Replace && with and, || with or, etc.
            expression = expression.replace(" && ", " and ")
            expression = expression.replace(" || ", " or ")
            expression = expression.replace("!", "not ")
        
        return expression
    
    def process_if_statement(self):
        """Process if statement."""
        # Skip 'if' token
        self.add_line("if ", end_line=False)
        
        # Look for opening parenthesis
        open_paren = self.get_next_token()
        if open_paren is None or open_paren[0] != "(":
            self.add_line("True:")  # Default condition if missing
            self.current_indent += 1
            self.add_line("pass")
            self.current_indent -= 1
            return
            
        # Process condition
        condition = self.process_condition()
        self.add_line(f"{condition}:")
        
        # Look for opening brace
        open_brace = self.get_next_token()
        if open_brace is None or open_brace[0] != "{":
            self.current_indent += 1
            self.add_line("pass")
            self.current_indent -= 1
            return
            
        # Process if body
        self.current_indent += 1
        
        # Process statements until closing brace
        nesting_level = 1
        while True:
            token = self.get_next_token()
            if token is None:
                break
                
            if token[0] == "{":
                nesting_level += 1
            elif token[0] == "}":
                nesting_level -= 1
                if nesting_level == 0:
                    # End of if body
                    break
            
            # Process the current token within the if body
            self.process_current_token()
        
        self.current_indent -= 1
        
        # Check for elif or else
        next_token = self.peek_next_token()
        if next_token:
            if next_token[0] == "elif":
                self.get_next_token()  # Consume 'elif'
                self.process_elif_statement()
            elif next_token[0] == "else":
                self.get_next_token()  # Consume 'else'
                self.process_else_statement()
    
    def process_condition(self):
        """Process a condition and return its code representation."""
        components = []
        nesting_level = 0
        
        while True:
            token = self.get_next_token()
            if token is None:
                break
                
            value, token_type = token
            
            if value == "(":
                components.append("(")
                nesting_level += 1
            elif value == ")":
                components.append(")")
                nesting_level -= 1
                if nesting_level < 0:
                    # We've reached the end of this condition
                    break
            elif token_type == "numlit":
                # Numeric literal
                components.append(value)
            elif token_type == "string literal":
                # String literal - keep the quotes
                components.append(value)
            elif value in ["dom", "rec"]:
                # Boolean literals
                components.append(self.keyword_map[value])
            elif token_type == "Identifier":
                # Variable
                components.append(value)
            elif value in self.operator_map:
                # Logical or comparison operator
                components.append(self.operator_map[value])
            elif value in ["+", "-", "*", "/", "%"]:
                # Arithmetic operator
                components.append(value)
        
        # Reassemble the condition
        condition = " ".join(components)
        
        # Handle any adjustments for specific language syntax
        if self.output_lang == "python":
            # Replace && with and, || with or, etc.
            condition = condition.replace(" && ", " and ")
            condition = condition.replace(" || ", " or ")
            if condition.startswith("!"):
                condition = "not " + condition[1:]
        
        return condition
    
    def process_elif_statement(self):
        """Process elif statement."""
        self.add_line("elif ", end_line=False)
        
        # Look for opening parenthesis
        open_paren = self.get_next_token()
        if open_paren is None or open_paren[0] != "(":
            self.add_line("True:")  # Default condition if missing
            self.current_indent += 1
            self.add_line("pass")
            self.current_indent -= 1
            return
            
        # Process condition
        condition = self.process_condition()
        self.add_line(f"{condition}:")
        
        # Look for opening brace
        open_brace = self.get_next_token()
        if open_brace is None or open_brace[0] != "{":
            self.current_indent += 1
            self.add_line("pass")
            self.current_indent -= 1
            return
            
        # Process elif body
        self.current_indent += 1
        
        # Process statements until closing brace
        nesting_level = 1
        while True:
            token = self.get_next_token()
            if token is None:
                break
                
            if token[0] == "{":
                nesting_level += 1
            elif token[0] == "}":
                nesting_level -= 1
                if nesting_level == 0:
                    # End of elif body
                    break
            
            # Process the current token within the elif body
            self.process_current_token()
        
        self.current_indent -= 1
        
        # Check for another elif or else
        next_token = self.peek_next_token()
        if next_token:
            if next_token[0] == "elif":
                self.get_next_token()  # Consume 'elif'
                self.process_elif_statement()
            elif next_token[0] == "else":
                self.get_next_token()  # Consume 'else'
                self.process_else_statement()
    
    def process_else_statement(self):
        """Process else statement."""
        self.add_line("else:")
        
        # Look for opening brace
        open_brace = self.get_next_token()
        if open_brace is None or open_brace[0] != "{":
            self.current_indent += 1
            self.add_line("pass")
            self.current_indent -= 1
            return
            
        # Process else body
        self.current_indent += 1
        
        # Process statements until closing brace
        nesting_level = 1
        while True:
            token = self.get_next_token()
            if token is None:
                break
                
            if token[0] == "{":
                nesting_level += 1
            elif token[0] == "}":
                nesting_level -= 1
                if nesting_level == 0:
                    # End of else body
                    break
            
            # Process the current token within the else body
            self.process_current_token()
        
        self.current_indent -= 1
    
    def process_for_loop(self):
        """Process for loop statement."""
        # Skip 'for' token
        
        # Look for opening parenthesis
        open_paren = self.get_next_token()
        if open_paren is None or open_paren[0] != "(":
            self.add_line("for _ in range(0):")  # Default loop if syntax is wrong
            self.current_indent += 1
            self.add_line("pass")
            self.current_indent -= 1
            return
            
        # Process initialization, condition, and update parts
        
        # Part 1: Initialization
        if self.get_next_token() and self.current_token[0] == "dose":
            # Get variable name
            var_token = self.get_next_token()
            if var_token and var_token[1] == "Identifier":
                loop_var = var_token[0]
                
                # Parse initialization value
                equals_token = self.get_next_token()
                if equals_token and equals_token[0] == "=":
                    init_val = self.get_next_token()[0] if self.get_next_token() else "0"
                else:
                    init_val = "0"
                
                # Skip semicolon
                self.get_next_token()
                
                # Part 2: Condition
                condition_var = self.get_next_token()[0] if self.get_next_token() else loop_var
                condition_op = self.get_next_token()[0] if self.get_next_token() else "<"
                condition_val = self.get_next_token()[0] if self.get_next_token() else "10"
                
                # Skip semicolon
                self.get_next_token()
                
                # Part 3: Update
                update_var = self.get_next_token()[0] if self.get_next_token() else loop_var
                update_op = self.get_next_token()[0] if self.get_next_token() else "++"
                
                # Skip closing parenthesis
                self.get_next_token()
                
                # Convert to Python for loop using range
                if condition_op == "<" and update_op in ["++", "+=1"]:
                    # Simple increment loop
                    self.add_line(f"for {loop_var} in range({init_val}, {condition_val}):")
                elif condition_op == "<=" and update_op in ["++", "+=1"]:
                    # Inclusive upper bound
                    self.add_line(f"for {loop_var} in range({init_val}, {condition_val} + 1):")
                elif condition_op == ">" and update_op in ["--", "-=1"]:
                    # Decrement loop
                    self.add_line(f"for {loop_var} in range({init_val}, {condition_val}, -1):")
                elif condition_op == ">=" and update_op in ["--", "-=1"]:
                    # Inclusive lower bound for decrement
                    self.add_line(f"for {loop_var} in range({init_val}, {condition_val} - 1, -1):")
                else:
                    # More complex loop structure
                    self.add_line(f"{loop_var} = {init_val}")
                    self.add_line(f"while {loop_var} {self.operator_map.get(condition_op, condition_op)} {condition_val}:")
                    
                    # Increment handled at the end of the loop body
                    if update_op == "++":
                        self.post_loop_increment = f"{update_var} += 1"
                    elif update_op == "--":
                        self.post_loop_increment = f"{update_var} -= 1"
                    else:
                        self.post_loop_increment = f"{update_var} {update_op} 1"
            else:
                # Invalid for loop syntax
                self.add_line("for _ in range(0):")
                self.current_indent += 1
                self.add_line("pass")
                self.current_indent -= 1
                return
        else:
            # Invalid for loop syntax
            self.add_line("for _ in range(0):")
            self.current_indent += 1
            self.add_line("pass")
            self.current_indent -= 1
            return
            
        # Look for opening brace
        open_brace = self.get_next_token()
        if open_brace is None or open_brace[0] != "{":
            self.current_indent += 1
            self.add_line("pass")
            self.current_indent -= 1
            return
            
        # Process for loop body
        self.current_indent += 1
        
        # Process statements until closing brace
        nesting_level = 1
        while True:
            token = self.get_next_token()
            if token is None:
                break
                
            if token[0] == "{":
                nesting_level += 1
            elif token[0] == "}":
                nesting_level -= 1
                if nesting_level == 0:
                    # End of for loop body
                    break
            
            # Process the current token within the for loop body
            self.process_current_token()
        
        # Add increment for while-based loops
        if hasattr(self, 'post_loop_increment'):
            self.add_line(self.post_loop_increment)
            delattr(self, 'post_loop_increment')
        
        self.current_indent -= 1
    
    def process_while_loop(self):
        """Process while loop statement."""
        # Skip 'while' token
        self.add_line("while ", end_line=False)
        
        # Look for opening parenthesis
        open_paren = self.get_next_token()
        if open_paren is None or open_paren[0] != "(":
            self.add_line("True:")  # Default condition if missing
            self.current_indent += 1
            self.add_line("pass")
            self.current_indent -= 1
            return
            
        # Process condition
        condition = self.process_condition()
        self.add_line(f"{condition}:")
        
        # Look for opening brace
        open_brace = self.get_next_token()
        if open_brace is None or open_brace[0] != "{":
            self.current_indent += 1
            self.add_line("pass")
            self.current_indent -= 1
            return
            
        # Process while loop body
        self.current_indent += 1
        
        # Process statements until closing brace
        nesting_level = 1
        while True:
            token = self.get_next_token()
            if token is None:
                break
                
            if token[0] == "{":
                nesting_level += 1
            elif token[0] == "}":
                nesting_level -= 1
                if nesting_level == 0:
                    # End of while loop body
                    break
            
            # Process the current token within the while loop body
            self.process_current_token()
        
        self.current_indent -= 1
    
    def process_do_while_loop(self):
        """Process do-while loop statement."""
        # Skip 'do' token
        
        # In Python, we need to implement do-while using a while True with a conditional break
        self.add_line("while True:")
        
        # Look for opening brace
        open_brace = self.get_next_token()
        if open_brace is None or open_brace[0] != "{":
            self.current_indent += 1
            self.add_line("pass")
            self.add_line("break")  # Exit loop immediately if no body
            self.current_indent -= 1
            return
            
        # Process do-while loop body
        self.current_indent += 1
        
        # Process statements until closing brace
        nesting_level = 1
        while True:
            token = self.get_next_token()
            if token is None:
                break
                
            if token[0] == "{":
                nesting_level += 1
            elif token[0] == "}":
                nesting_level -= 1
                if nesting_level == 0:
                    # End of do-while loop body
                    break
            
            # Process the current token within the do-while loop body
            self.process_current_token()
        
        # Look for 'while' keyword
        while_token = self.get_next_token()
        if while_token is None or while_token[0] != "while":
            # Missing 'while', add a default break condition
            self.add_line("break")
            self.current_indent -= 1
            return
            
        # Look for opening parenthesis
        open_paren = self.get_next_token()
        if open_paren is None or open_paren[0] != "(":
            # Missing opening parenthesis, add a default break condition
            self.add_line("break")
            self.current_indent -= 1
            return
            
        # Process condition
        condition = self.process_condition()
        
        # Add the break condition (note: we invert the condition since we break when it's False)
        self.add_line(f"if not ({condition}):")
        self.current_indent += 1
        self.add_line("break")
        self.current_indent -= 1
        
        # Reset indentation level
        self.current_indent -= 1
        
        # Look for semicolon
        semi_token = self.get_next_token()
        if semi_token is None or semi_token[0] != ";":
            # Missing semicolon, but we'll continue anyway
            pass
    
    def process_express_statement(self):
        """Process express statement (print statement in Python)."""
        # Skip 'express' token
        
        # Look for opening parenthesis
        open_paren = self.get_next_token()
        if open_paren is None or open_paren[0] != "(":
            self.add_line("print()")  # Default print if syntax is wrong
            return
            
        # Process arguments (comma-separated expressions)
        args = []
        
        # Parse values until closing parenthesis
        nesting_level = 1
        current_arg = []
        
        while True:
            token = self.get_next_token()
            if token is None:
                break
                
            value, token_type = token
            
            if value == "(":
                current_arg.append("(")
                nesting_level += 1
            elif value == ")":
                nesting_level -= 1
                if nesting_level == 0:
                    # End of arguments
                    if current_arg:
                        args.append(" ".join(current_arg))
                    break
                else:
                    current_arg.append(")")
            elif value == ",":
                if nesting_level == 1:
                    # End of current argument
                    if current_arg:
                        args.append(" ".join(current_arg))
                        current_arg = []
                else:
                    # Comma within nested expression
                    current_arg.append(",")
            elif token_type == "numlit":
                current_arg.append(value)
            elif token_type == "string literal":
                current_arg.append(value)
            elif value in ["dom", "rec"]:
                current_arg.append(self.keyword_map[value])
            elif token_type == "Identifier":
                current_arg.append(value)
            elif value in self.operator_map:
                current_arg.append(self.operator_map[value])
            elif value in ["+", "-", "*", "/", "%"]:
                current_arg.append(value)
        
        # Generate the print statement
        if args:
            args_str = ", ".join(args)
            self.add_line(f"print({args_str})")
        else:
            self.add_line("print()")
        
        # Look for semicolon
        semi_token = self.get_next_token()
        if semi_token is None or semi_token[0] != ";":
            # Missing semicolon, but we'll continue anyway
            pass

def generate_python_code(tokens):
    """
    Generate Python code from GenomeX tokens.
    
    Args:
        tokens: List of tokens from lexical analysis
        
    Returns:
        str: Generated Python code
    """
    generator = CodeGenerator(tokens, "python")
    return generator.generate_code()

def generate_code(tokens, target_language="python"):
    """
    Generate code in the specified target language from GenomeX tokens.
    
    Args:
        tokens: List of tokens from lexical analysis
        target_language: Target language for code generation (default: "python")
        
    Returns:
        str: Generated code in the target language
    """
    generator = CodeGenerator(tokens, target_language)
    return generator.generate_code()

if __name__ == "__main__":
    # Example usage when run as a script
    import GenomeX_Lexer as gxl
    
    # Parse input file
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            input_text = f.read()
        
        # Get tokens from lexer
        tokens, found_error = gxl.parseLexer(input_text)
        
        if not found_error:
            # Generate Python code
            python_code = generate_python_code(tokens)
            
            # Print or save the generated code
            if len(sys.argv) > 2:
                with open(sys.argv[2], 'w') as f:
                    f.write(python_code)
            else:
                print(python_code)
        else:
            print("Lexical errors found. Cannot generate code.")
    else:
        print("Usage: python GenomeX_CodeGen.py input_file [output_file]")
