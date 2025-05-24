import sys
import GenomeX_Lexer as gxl
import GenomX_Semantic as gxs

def test_caret_negation():
    # Read the test file
    with open('test_caret.gx', 'r') as f:
        code = f.read()
    
    # Tokenize the code
    tokens = gxl.tokenize(code)
    
    # Create a semantic analyzer
    analyzer = gxs.SemanticAnalyzer(tokens)
    
    # Run the analysis
    analyzer.parse()
    
    # Print any errors found
    print("Semantic errors found:")
    for error in analyzer.errors:
        print(f"- {error}")
    print()
    
    # Check if we have values correctly parsed
    print("Checking variable values:")
    
    # Check if variables are in symbol table with correct negative values
    success = True
    
    def check_variable(analyzer, var_name, expected_value):
        if var_name in analyzer.function_scopes.get('gene', {}):
            actual_value = analyzer.function_scopes['gene'][var_name]['value']
            print(f"{var_name}: {actual_value} (Expected: {expected_value})")
            return actual_value == expected_value
        else:
            print(f"{var_name}: Not found in symbol table")
            return False
    
    # Check dose variables
    success &= check_variable(analyzer, 'A', -2)
    success &= check_variable(analyzer, 'B', 3)
    success &= check_variable(analyzer, 'E', 1)
    success &= check_variable(analyzer, 'F', 2)
    
    # Check quant variables
    success &= check_variable(analyzer, 'C', -2.5)
    success &= check_variable(analyzer, 'D', 3.5)
    success &= check_variable(analyzer, 'G', 1.0)
    success &= check_variable(analyzer, 'H', 3.0)
    
    # Array values can't be directly checked since they're not evaluated at this stage
    
    # Display test result
    print(f"\nTest result: {'PASS' if success and not analyzer.errors else 'FAIL'}")

if __name__ == "__main__":
    test_caret_negation() 