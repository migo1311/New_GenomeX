import sys
import GenomeX_Lexer as gxl
import GenomX_Semantic as gxs

def test_negative_float_splicing():
    # Read the test file
    with open('test_splicing.gx', 'r') as f:
        code = f.read()
    
    # Tokenize the code
    tokens = gxl.tokenize(code)
    
    # Create a semantic analyzer
    analyzer = gxs.SemanticAnalyzer(tokens)
    
    # Run the analysis
    analyzer.parse()
    
    # Print all errors found
    print("Semantic errors found:")
    for error in analyzer.errors:
        print(f"- {error}")
    print()
    
    # Check if we have the expected error about negative quant values
    has_negative_quant_error = any("negative quant values are not allowed" in error for error in analyzer.errors)
    print(f"Test result: {'PASS' if has_negative_quant_error else 'FAIL'}")
    print(f"Found negative quant error: {has_negative_quant_error}")

if __name__ == "__main__":
    test_negative_float_splicing() 