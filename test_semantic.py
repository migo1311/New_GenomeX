import sys
import GenomeX_Lexer as gxl
import GenomX_Semantic as gxs

def test_concat_error():
    # Read the test file
    with open('test_concat.gx', 'r') as f:
        code = f.read()
    
    # Tokenize the code
    tokens = gxl.tokenize(code)
    
    # Create a semantic analyzer
    analyzer = gxs.SemanticAnalyzer(tokens)
    
    # Run the analysis
    analyzer.parse()
    
    # Check for errors
    for error in analyzer.errors:
        print(error)
    
    # Check if we have the expected error about concatenation
    has_concat_error = any("Cannot concatenate dose and seq directly" in error for error in analyzer.errors)
    print(f"\nTest result: {'PASS' if has_concat_error else 'FAIL'}")
    print(f"Found concatenation error: {has_concat_error}")

if __name__ == "__main__":
    test_concat_error() 