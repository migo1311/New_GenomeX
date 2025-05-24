import GenomeX_Lexer as gxl
import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
import sys
import ply.lex as lex
import ply.yacc as yacc

# Create a simple parser for the GenomeX language subset in the example
class GenomeXParser:
    # Only define tokens actually used in the grammar
    tokens = [
        'IDENTIFIER', 'NUMLIT', 'QUANTLITERAL',
        'MINUS', 'PLUS',  # Add PLUS for the + operator
        'EQUALS', 
        'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
        'SEMICOLON',
        'DOSE', 'LOCAL', 'GLOBAL', 'GENE', 'EXPRESS', 'ACT',
        'COMMENT',
        'QUANT', 'SEQ'  # Add additional data type tokens
    ]
    
    # Define precedence rules
    precedence = (
        ('left', 'PLUS', 'MINUS'),
    )
    
    # Define starting symbol
    start = 'program'
    
    def __init__(self, output_text):
        self.output_text = output_text
        self.parser = None
        self.lexer = None
        self.input_tokens = []
        self.token_generator = None
        self.has_error = False
        self.line_mapping = {}
        self.current_line = 1
        self.main_function_seen = False
        self.token_positions = {}  # Store token positions for better error reporting
        self.error_count = 0
        self.max_errors = 10  # Maximum number of errors to report
        self.previous_token = None  # Track previous token for better error messages
        self.missing_semicolon_detected = False  # Flag to prevent duplicate error messages
        self.current_scope = "global"  # Track current scope (global or function)
        
        # Define reserved words mapping
        self.reserved = {
            'dose': 'DOSE',
            '_L': 'LOCAL',
            '_G': 'GLOBAL',
            'gene': 'GENE',
            'express': 'EXPRESS',
            'act': 'ACT',
            'quant': 'QUANT',
            'seq': 'SEQ',
        }
    
    # Create a token() method that PLY requires
    def token(self):
        if self.token_generator is None:
            return None
        tok = next(self.token_generator, None)
        if tok:
            self.previous_token = tok
        return tok
    
    # Process tokens and prepare them for the parser
    def process_tokens(self, tokens):
        self.input_tokens = tokens
        
        # Create PLY-compatible tokens
        processed_tokens = []
        token_position = 0
        
        for token in tokens:
            token_value, token_type = token
            self.token_positions[token_position] = (self.current_line, token_value)
            token_position += 1
            
            # Convert token types to PLY format
            if token_type == "Identifier":
                token_type = "IDENTIFIER"
            elif token_type == "numlit":
                token_type = "NUMLIT"
            elif token_type == "quantliteral":
                token_type = "QUANTLITERAL"
            elif token_type == "newline":
                self.current_line += 1
                continue  # Skip newlines in parser
            elif token_type == "comment":
                token_type = "COMMENT"
            elif token_type == "multiline":
                continue  # Skip multiline comments in parser
            
            # Map operators
            operator_mapping = {
                '+': 'PLUS',  # Add PLUS operator
                '-': 'MINUS',
                '=': 'EQUALS',
                '(': 'LPAREN', ')': 'RPAREN', '{': 'LBRACE', '}': 'RBRACE',
                ';': 'SEMICOLON'
            }
            
            if token_type in operator_mapping:
                token_type = operator_mapping[token_type]
            elif token_value in self.reserved:
                token_type = self.reserved[token_value]
            
            # Verify token type is valid
            if token_type not in self.tokens:
                if token_type not in ["newline", "string literal"]:  # Skip known tokens we don't use
                    print(f"Warning: Skipping token '{token_type}' for value '{token_value}'")
                continue
            
            # Store line information
            self.line_mapping[len(processed_tokens)] = self.current_line
            
            # Create a LexToken object that PLY expects
            t = lex.LexToken()
            t.type = token_type
            t.value = token_value
            t.lineno = self.current_line
            t.lexpos = len(processed_tokens)
            
            processed_tokens.append(t)
        
        # Create a generator to yield tokens
        def token_generator():
            for t in processed_tokens:
                yield t
        
        self.token_generator = token_generator()
        return processed_tokens
    
    # Build the parser
    def build(self):
        # Create a parser that uses this instance for the grammar rules
        self.parser = yacc.yacc(module=self, debug=True, write_tables=False)
    
    # Parse the input tokens
    def parse(self, tokens):
        self.process_tokens(tokens)
        self.missing_semicolon_detected = False
        self.current_scope = "global"  # Start in global scope
        
        try:
            result = self.parser.parse(lexer=self)
            
            if not self.has_error and not self.main_function_seen:
                self.report_error("No main function (gene) found in the program. GenomeX requires a main 'gene()' function.")
            
            if not self.has_error:
                self.output_text.insert(tk.END, "You May Push!\n")
                return False
            return True
            
        except Exception as e:
            self.report_error(f"Parser error: {str(e)}")
            import traceback
            traceback.print_exc()
            return True
    
    def report_error(self, message, line=None):
        """Centralized error reporting function"""
        self.has_error = True
        self.error_count += 1
        
        if self.error_count > self.max_errors:
            if self.error_count == self.max_errors + 1:
                self.output_text.insert(tk.END, f"Too many errors, stopping analysis.\n")
            return
        
        line_info = f" at line {line}" if line is not None else ""
        self.output_text.insert(tk.END, f"Error{line_info}: {message}\n")
        print(f"Error{line_info}: {message}")
    
    # Error rule for syntax errors
    def p_error(self, p):
        if p is None:
            self.report_error("Unexpected end of file. Make sure all code blocks are properly closed.")
            return
        
        # Try to get the next token for context
        next_token = self.parser.token()
        
        # Perform custom error detection based on specific token patterns
        error_msg = self.check_for_specific_errors(p, next_token)
        
        if error_msg is None:
            # Default error handling if no specific error was detected
            error_msg = self.generate_default_error_message(p, next_token)
            
        self.report_error(error_msg, p.lineno)
        
        # Error recovery: Skip the current token and continue parsing
        if next_token:
            # Put the token back in the stream
            self.parser.restart()
        else:
            # No more tokens, can't recover
            return
    
    def check_for_specific_errors(self, p, next_token):
        """Check for specific error patterns and generate appropriate messages"""
        
        # Check for missing semicolon after variable without creating duplicate errors
        if (self.previous_token and self.previous_token.type == 'RPAREN' and 
            p.type in ['RBRACE', 'EXPRESS', 'LOCAL', 'GLOBAL', 'IDENTIFIER']):
            # Only report once
            if not self.missing_semicolon_detected:
                self.missing_semicolon_detected = True
                return f"Missing semicolon ';' after expression"
        
        # Check for missing identifier in variable declaration: _L dose ;
        if (p.type == 'SEMICOLON' and self.previous_token and 
            self.previous_token.type in ['DOSE', 'QUANT', 'SEQ']):
            return f"Missing identifier after '{self.previous_token.value}'"
        
        # Check for missing identifier between data type and equals: _L dose = value;
        if (p.type == 'EQUALS' and self.previous_token and 
            self.previous_token.type in ['DOSE', 'QUANT', 'SEQ']):
            return f"Missing identifier between '{self.previous_token.value}' and '='"
        
        # Check for missing data type: _L identifier; or _G identifier;
        if (p.type == 'IDENTIFIER' and self.previous_token and 
            (self.previous_token.type == 'LOCAL' or self.previous_token.type == 'GLOBAL')):
            prefix = "_L" if self.previous_token.type == 'LOCAL' else "_G"
            return f"Missing data type (dose, quant, or seq) after '{prefix}'"
        
        # Check for missing prefix based on scope: dose identifier;
        if (p.type == 'DOSE' or p.type == 'QUANT' or p.type == 'SEQ') and (
            not self.previous_token or (self.previous_token.type != 'LOCAL' and self.previous_token.type != 'GLOBAL')):
            if not (self.previous_token and self.previous_token.type == 'ACT'):  # Ignore act dose
                if self.current_scope == "global":
                    return f"Missing '_G' prefix before '{p.value}' (global variable declaration)"
                else:
                    return f"Missing '_L' prefix before '{p.value}' (local variable declaration)"
        
        # Check for missing equals in assignment with string literal
        if (next_token and next_token.type == 'IDENTIFIER' and 
            p.type in ['DOSE', 'QUANT', 'SEQ'] and self.previous_token and 
            (self.previous_token.type == 'LOCAL' or self.previous_token.type == 'GLOBAL')):
            # This is a potential case like _L dose identifier string_literal
            return None  # We'll handle this in a specific grammar rule
            
        return None  # No specific error detected
    
    def generate_default_error_message(self, p, next_token):
        """Generate default error messages based on token types"""
        
        if p.type == 'LPAREN':
            return f"Syntax error after '('. Expected expression or ')'."
        elif p.type == 'RPAREN':
            return f"Syntax error after ')'. Missing semicolon ';'?"
        elif p.type == 'LBRACE':
            return f"Syntax error after '{{'. Expected statement or '}}'."
        elif p.type == 'RBRACE':
            # Check if missing semicolon likely caused this error
            if self.previous_token and self.previous_token.type in ['RPAREN', 'IDENTIFIER', 'NUMLIT']:
                return f"Missing semicolon ';' before '}}'"
            else:
                return f"Unexpected '}}'. Check for missing opening brace or extra closing brace."
        elif p.type == 'SEMICOLON':
            return f"Unexpected ';'. Check for empty statements or missing expression."
        elif p.type == 'EQUALS':
            return f"Syntax error after '='. Expected an expression."
        elif p.type == 'PLUS':
            return f"Syntax error after '+'. Expected a value or expression."
        elif p.type == 'MINUS':
            return f"Syntax error after '-'. Expected a value or expression."
        elif p.type == 'GENE':
            return f"Invalid 'gene' declaration. Expected format: 'gene() {{ ... }}'."
        elif p.type == 'EXPRESS':
            return f"Invalid 'express' statement. Expected format: 'express(expression);'."
        elif p.type == 'LOCAL':
            return f"Invalid local variable declaration. Expected format: '_L dose|quant|seq identifier = value;'."
        elif p.type == 'GLOBAL':
            return f"Invalid global variable declaration. Expected format: '_G dose|quant|seq identifier = value;'."
        elif p.type == 'DOSE':
            prefix = "_G" if self.current_scope == "global" else "_L"
            return f"Invalid 'dose' usage. Expected format: '{prefix} dose identifier'."
        elif p.type == 'QUANT':
            prefix = "_G" if self.current_scope == "global" else "_L"
            return f"Invalid 'quant' usage. Expected format: '{prefix} quant identifier'."
        elif p.type == 'SEQ':
            prefix = "_G" if self.current_scope == "global" else "_L"
            return f"Invalid 'seq' usage. Expected format: '{prefix} seq identifier'."
        elif p.type == 'ACT':
            return f"Invalid 'act' keyword usage. Expected format: 'act gene() {{ ... }}'."
        elif next_token and p.type == 'IDENTIFIER' and next_token.type != 'EQUALS' and next_token.type != 'SEMICOLON':
            return f"Unexpected token after identifier '{p.value}'. Expected '=' or ';'."
        
        # Default error message if no specific context is matched
        default_msg = f"Syntax error at '{p.value}'"
        if next_token:
            default_msg += f" followed by '{next_token.value}'"
        return default_msg
        
    # Additional grammar rules for error detection
    
    # Express statement with missing semicolon
    def p_express_statement_missing_semicolon(self, p):
        '''express_statement_error : EXPRESS LPAREN expression RPAREN'''
        self.report_error(f"Missing semicolon ';' after express statement", p.lineno(1))
        self.missing_semicolon_detected = True
        p[0] = ('express_statement', p[3])  # Continue with a valid node
    
    # Grammar rules
    
    # Starting rule
    def p_program(self, p):
        '''program : global_declarations
                   | global_declarations main_function
                   | main_function'''
        if len(p) == 2:
            if isinstance(p[1], tuple) and p[1][0] == 'main_function':
                p[0] = ('program', [], p[1])
            else:
                p[0] = ('program', p[1], None)
        else:
            p[0] = ('program', p[1], p[2])
    
    def p_global_declarations(self, p):
        '''global_declarations : global_declaration
                              | global_declarations global_declaration'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]
            
    def p_global_declaration(self, p):
        '''global_declaration : global_variable_declaration
                             | global_variable_declaration_error'''
        p[0] = p[1]
        
    def p_main_function(self, p):
        '''main_function : GENE LPAREN RPAREN LBRACE statements RBRACE
                         | ACT GENE LPAREN RPAREN LBRACE statements RBRACE'''
        # Set the scope to function when entering the function
        self.current_scope = "function"
        self.main_function_seen = True
        
        if len(p) == 7:  # Without 'act'
            p[0] = ('main_function', p[5])
        else:  # With 'act'
            p[0] = ('main_function', ('act',), p[6])
            
        # Reset scope to global when exiting the function
        self.current_scope = "global"
        
    def p_statements(self, p):
        '''statements : statement
                      | statements statement
                      | COMMENT
                      | statements COMMENT
                      | express_statement_error
                      | statements express_statement_error
                      | variable_declaration_error
                      | statements variable_declaration_error
                      | '''  # Allow empty statements
        if len(p) == 1:  # Empty
            p[0] = []
        elif len(p) == 2:
            if p[1] == 'COMMENT':  # Skip comments
                p[0] = []
            else:  # Single statement
                p[0] = [p[1]]
        elif len(p) == 3:
            if p[2] == 'COMMENT':  # Skip comments
                p[0] = p[1]
            else:  # Multiple statements
                p[0] = p[1] + [p[2]]
            
    def p_statement(self, p):
        '''statement : variable_declaration
                     | express_statement
                     | COMMENT'''
        if p[1] == 'COMMENT':
            p[0] = None  # Skip comments
        else:
            p[0] = p[1]
    
    def p_express_statement(self, p):
        '''express_statement : EXPRESS LPAREN expression RPAREN SEMICOLON'''
        p[0] = ('express_statement', p[3])
    
    # Error patterns for variable declarations
    def p_variable_declaration_error(self, p):
        '''variable_declaration_error : LOCAL DOSE SEMICOLON
                                      | LOCAL QUANT SEMICOLON
                                      | LOCAL SEQ SEMICOLON
                                      | LOCAL DOSE EQUALS expression SEMICOLON
                                      | LOCAL QUANT EQUALS expression SEMICOLON
                                      | LOCAL SEQ EQUALS expression SEMICOLON
                                      | LOCAL IDENTIFIER SEMICOLON
                                      | LOCAL IDENTIFIER EQUALS expression SEMICOLON
                                      | DOSE IDENTIFIER SEMICOLON
                                      | QUANT IDENTIFIER SEMICOLON
                                      | SEQ IDENTIFIER SEMICOLON
                                      | LOCAL DOSE IDENTIFIER
                                      | LOCAL QUANT IDENTIFIER
                                      | LOCAL SEQ IDENTIFIER
                                      | GLOBAL DOSE SEMICOLON
                                      | GLOBAL QUANT SEMICOLON
                                      | GLOBAL SEQ SEMICOLON
                                      | GLOBAL DOSE EQUALS expression SEMICOLON
                                      | GLOBAL QUANT EQUALS expression SEMICOLON
                                      | GLOBAL SEQ EQUALS expression SEMICOLON
                                      | GLOBAL IDENTIFIER SEMICOLON
                                      | GLOBAL IDENTIFIER EQUALS expression SEMICOLON
                                      | GLOBAL DOSE IDENTIFIER
                                      | GLOBAL QUANT IDENTIFIER
                                      | GLOBAL SEQ IDENTIFIER'''
        # Error messages based on the pattern
        prefix = "_L" if p[1] == "_L" else "_G"
        
        if len(p) == 4 and p[3] == ';':  # _L|_G dose|quant|seq ;
            if p[2] in ['dose', 'quant', 'seq']:
                self.report_error(f"Missing identifier after '{p[2]}'", p.lineno(1))
            else:  # _L|_G identifier ;
                self.report_error(f"Missing data type (dose, quant, or seq) after '{prefix}'", p.lineno(1))
        elif len(p) == 6:  # _L|_G dose|quant|seq = expr;  or  _L|_G identifier = expr;
            if p[2] in ['dose', 'quant', 'seq']:
                self.report_error(f"Missing identifier between '{p[2]}' and '='", p.lineno(1))
            else:
                self.report_error(f"Missing data type (dose, quant, or seq) after '{prefix}'", p.lineno(1))
        elif len(p) == 4 and p[1] in ['dose', 'quant', 'seq']:  # dose|quant|seq identifier;
            if self.current_scope == "global":
                self.report_error(f"Missing '_G' prefix before '{p[1]}' (global variable declaration)", p.lineno(1))
            else:
                self.report_error(f"Missing '_L' prefix before '{p[1]}' (local variable declaration)", p.lineno(1))
        elif len(p) == 4:  # _L|_G dose|quant|seq identifier (missing semicolon)
            self.report_error(f"Missing semicolon ';' after declaration", p.lineno(1))
            
        p[0] = None  # This is an error node
    
    # Global variable declarations with proper grammar
    def p_global_variable_declaration_error(self, p):
        '''global_variable_declaration_error : DOSE IDENTIFIER SEMICOLON
                                             | QUANT IDENTIFIER SEMICOLON
                                             | SEQ IDENTIFIER SEMICOLON'''
        # These are missing the _G prefix in global scope
        self.report_error(f"Missing '_G' prefix before '{p[1]}' (global variable declaration)", p.lineno(1))
        p[0] = None
    
    def p_global_variable_declaration(self, p):
        '''global_variable_declaration : GLOBAL DOSE IDENTIFIER EQUALS expression SEMICOLON
                                       | GLOBAL DOSE IDENTIFIER SEMICOLON
                                       | GLOBAL QUANT IDENTIFIER EQUALS expression SEMICOLON
                                       | GLOBAL QUANT IDENTIFIER SEMICOLON
                                       | GLOBAL SEQ IDENTIFIER EQUALS expression SEMICOLON
                                       | GLOBAL SEQ IDENTIFIER SEMICOLON'''
        if len(p) == 7:  # With initializer
            p[0] = ('global_variable_declaration', ('global', p[2]), p[3], p[5])
        else:  # Without initializer
            p[0] = ('global_variable_declaration', ('global', p[2]), p[3], None)
            
    def p_variable_declaration(self, p):
        '''variable_declaration : LOCAL DOSE IDENTIFIER EQUALS expression SEMICOLON
                                | LOCAL DOSE IDENTIFIER SEMICOLON
                                | LOCAL QUANT IDENTIFIER EQUALS expression SEMICOLON
                                | LOCAL QUANT IDENTIFIER SEMICOLON
                                | LOCAL SEQ IDENTIFIER EQUALS expression SEMICOLON
                                | LOCAL SEQ IDENTIFIER SEMICOLON'''
        if len(p) == 7:  # With initializer
            p[0] = ('variable_declaration', ('local', p[2]), p[3], p[5])
        else:  # Without initializer
            p[0] = ('variable_declaration', ('local', p[2]), p[3], None)
            
    def p_expression(self, p):
        '''expression : IDENTIFIER
                      | NUMLIT
                      | QUANTLITERAL
                      | MINUS NUMLIT
                      | expression PLUS expression
                      | expression MINUS expression
                      | LPAREN expression RPAREN'''
        if len(p) == 2:  # Simple expression
            p[0] = p[1]
        elif len(p) == 3:  # Unary expression
            p[0] = ('unary', 'MINUS', p[2])
        elif p[1] == '(':  # Parenthesized expression
            p[0] = p[2]
        else:  # Binary expression
            p[0] = ('binary', p[2], p[1], p[3])


def parseSyntax(tokens, output_text):
    """
    GenomeX syntax analyzer using PLY parser generator.
    
    This implementation uses a simplified grammar focused just on the example code.
    """
    try:
        # Attempt to create and build the parser
        parser = GenomeXParser(output_text)
        try:
            parser.build()
        except yacc.YaccError as e:
            output_text.insert(tk.END, f"Parser build error: {str(e)}\n")
            print(f"Parser build error: {str(e)}")
            return True
        
        # Attempt to parse the input tokens
        return parser.parse(tokens)
    except Exception as e:
        output_text.insert(tk.END, f"Unexpected parser error: {str(e)}\n")
        print(f"Unexpected parser error: {str(e)}")
        import traceback
        traceback.print_exc()
        return True