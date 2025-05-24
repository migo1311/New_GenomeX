import GenomX_Semantic as sm
import GenomeX_Lexer as lx
import io
import sys

test_code = """
act gene() {
    _L dose Distance, Time, Speed;

    Distance = stimuli("Enter distance (in meters): ");
    Time = stimuli("Enter time (in seconds): ");

    Speed = Distance / Time;

    express("The speed is: " + seq(Speed) + " m/s");
}
"""

class DummyPanel:
    def __init__(self):
        self.output = []
    
    def delete(self, *args):
        pass
    
    def insert(self, *args):
        if len(args) >= 2:
            self.output.append(args[1])
    
    def tag_configure(self, *args):
        pass

# First run the lexer to generate tokens
tokens, found_error = lx.parseLexer(test_code)

if found_error:
    print("Lexical error found. Cannot proceed with semantic analysis.")
else:
    # Create a dummy panel to capture output
    dummy_panel = DummyPanel()
    
    # Redirect stdout to capture debug output
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    
    # Run the semantic analysis on the tokens
    result = sm.parseSemantic(tokens, dummy_panel)
    
    # Restore stdout
    sys.stdout = old_stdout
    
    # Print any errors found
    analyzer = result
    if analyzer.errors:
        print("Semantic errors found:")
        for error in analyzer.errors:
            print(f"  - {error}")
    else:
        print("No semantic errors were found!")
    
    print("\nTest complete.") 