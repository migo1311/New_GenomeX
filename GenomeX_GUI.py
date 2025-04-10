import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
# from PIL import Image, ImageTk
from GenomeX_Lexer import display_lexical_error, display_lexical_pass
import GenomeX_Lexer
import GenomeX_Syntax  # Add this import
import GenomX_Semantic  # Add this import
import GenomeX_CodeGen

# Create the main application window
root = tk.Tk()
root.title("GenomeX 🧬")
root.geometry("1440x1024")
import re
import GenomeX_Lexer as gxl
import GenomeX_Syntax as gxs
import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
import sys
from itertools import chain
# Load icons
# settings_icon = ImageTk.PhotoImage(Image.open("settings_icon.png").resize((40, 40)))
# genome_icon = ImageTk.PhotoImage(Image.open("genome_icon.png").resize((50, 50)))

# Style configuration
style = ttk.Style()
style.theme_use("clam")

# Header with icons
header_frame = ttk.Frame(root)
header_frame.pack(fill=tk.X, padx=20, pady=10)

title_label = ttk.Label(header_frame, text="GenomeX", font=("Inter", 32))
title_label.pack(side=tk.LEFT)

# genome_label = ttk.Label(header_frame, image=genome_icon)
# genome_label.pack(side=tk.LEFT, padx=10)

# settings_button = ttk.Button(header_frame, image=settings_icon)
# settings_button.pack(side=tk.RIGHT, padx=10)

# Main layout
main_frame = ttk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

# Define scroll functions first
def on_text_scroll(*args):
    if len(args) == 2:
        text_editor.yview_moveto(args[1])
        line_numbers.yview_moveto(args[1])
    else:
        text_editor.yview(*args)
        line_numbers.yview(*args)

def update_line_numbers(event=None):
    line_numbers.config(state="normal")
    line_numbers.delete("1.0", tk.END)
    line_count = text_editor.get("1.0", tk.END).count('\n')
    lines = '\n'.join(str(i) for i in range(1, line_count + 1))
    line_numbers.insert("1.0", lines)
    line_numbers.config(state="disabled")
    line_numbers.yview_moveto(text_editor.yview()[0])

# Left panel (Code Editor)
editor_frame = ttk.Frame(main_frame)
editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Add vertical scrollbar
editor_scrollbar = ttk.Scrollbar(editor_frame, orient=tk.VERTICAL)
editor_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Add horizontal scrollbar
editor_horizontal_scrollbar = ttk.Scrollbar(editor_frame, orient=tk.HORIZONTAL)
editor_horizontal_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

line_numbers = tk.Text(editor_frame, width=4, padx=4, takefocus=0, border=0, 
                      state="disabled", bg='#f0f0f0')
line_numbers.pack(side=tk.LEFT, fill=tk.Y)

text_editor = tk.Text(editor_frame, wrap=tk.NONE, yscrollcommand=editor_scrollbar.set, xscrollcommand=editor_horizontal_scrollbar.set)
text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Insert default text into the text editor

# text_editor.insert("1.0", "")
# text_editor.insert("1.0", "act gene () {\n\n\n\n\n}")

# Configure vertical scrollbar
editor_scrollbar.config(command=on_text_scroll)

# Configure horizontal scrollbar
editor_horizontal_scrollbar.config(command=text_editor.xview)

# Bind events
text_editor.bind("<KeyRelease>", update_line_numbers)
text_editor.bind("<MouseWheel>", lambda e: on_text_scroll("scroll", -1 if e.delta > 0 else 1, "units"))
text_editor.bind("<Configure>", update_line_numbers)
# Right panel (Lexical Tokenization)
table_frame = ttk.LabelFrame(main_frame, text="Lexical Tokenization")
table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=5)

columns = ("ID", "Lexeme", "Token")
tree = ttk.Treeview(table_frame, columns=columns, show='headings')

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100, anchor='center')

tree.pack(fill=tk.BOTH, expand=True)

def clear_editor():
    text_editor.delete(1.0, tk.END)
    tree.delete(*tree.get_children())
    lexical_panel.delete(1.0, tk.END)
    syntax_panel.delete(1.0, tk.END)
    semantic_panel.delete(1.0, tk.END)
    codegen_panel.delete(1.0, tk.END)
    update_line_numbers()

# Buttons (Run & Clear)
bottom_frame = ttk.Frame(root)
bottom_frame.pack(fill=tk.X, pady=10,  padx=20)

btn_clear = ttk.Button(bottom_frame, text="Clear", width=10, command=clear_editor)
btn_clear.pack(side=tk.RIGHT, padx=10)

btn_run = ttk.Button(bottom_frame, text="Run", width=10)
btn_run.pack(side=tk.RIGHT)

# Notebook (Tabs for results)
out_frame = ttk.Frame(root)
out_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

notebook = ttk.Notebook(out_frame)
lexical_tab = ttk.Frame(notebook)
syntax_tab = ttk.Frame(notebook)
semantic_tab = ttk.Frame(notebook)
codegen_tab = ttk.Frame(notebook)

notebook.add(lexical_tab, text="Lexical Status")
notebook.add(syntax_tab, text="Syntax Result")
notebook.add(semantic_tab, text="Semantic Error")
notebook.add(codegen_tab, text="Python Code")
notebook.pack(fill=tk.BOTH, expand=True)

lexical_panel = tk.Text(lexical_tab, wrap=tk.WORD)
lexical_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

syntax_panel = tk.Text(syntax_tab, wrap=tk.WORD)
syntax_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

semantic_panel = tk.Text(semantic_tab, wrap=tk.WORD)
semantic_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

codegen_panel = tk.Text(codegen_tab, wrap=tk.WORD)
codegen_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

def highlight_errors(text_editor, line_number, lexeme):
    start_index = f"{line_number}.0"
    end_index = f"{line_number}.end"

    # Find lexeme position in the line
    text_content = text_editor.get(start_index, end_index)
    if lexeme in text_content:
        start_idx = text_content.index(lexeme)
        text_editor.tag_add("error", f"{line_number}.{start_idx}", f"{line_number}.{start_idx + len(lexeme)}")
    else:
        text_editor.tag_add("error", start_index, end_index)  # Highligz    ht full line if lexeme isn't found
    
    text_editor.tag_config("error", foreground="red", underline=True)

# Function to execute lexer and syntax analyzer and display results
def run_analysis():
    input_text = text_editor.get("1.0", tk.END).strip()
    
    # Get the currently selected tab before performing analysis
    current_tab = notebook.index("current")
    
    # Clear previous output
    tree.delete(*tree.get_children())
    lexical_panel.delete(1.0, tk.END)
    syntax_panel.delete(1.0, tk.END)
    semantic_panel.delete(1.0, tk.END)
    codegen_panel.delete(1.0, tk.END)

    # Inject lexical_panel into the Lexer module so errors can be displayed
    GenomeX_Lexer.lexical_panel = lexical_panel  

    # Run Lexer and get tokens
    tokens, found_error  = GenomeX_Lexer.parseLexer(input_text)
    
    if found_error or not tokens:
        display_lexical_error("No tokens found or input is invalid.")
        # For errors, switch to lexical tab to show the error message
        notebook.select(0)
        # Display valid tokens in the lexical tokenization table
        for idx, (lexeme, token) in enumerate(tokens):
            tree.insert("", "end", values=(idx + 1, lexeme, token))
        
    else:
        for idx, (lexeme, token) in enumerate(tokens):
            tree.insert("", "end", values=(idx + 1, lexeme, token))
        
        # After successful lexical analysis, run syntax analysis
        syntax_errors = GenomeX_Syntax.parseSyntax(tokens, syntax_panel)
        display_lexical_pass("You are lexer free")

        if syntax_errors:
            # If there are syntax errors, switch to syntax tab
            notebook.select(1)  # Index 1 is the syntax tab
        else:
            # After successful syntax analysis, run semantic analysis
            semantic_success = GenomX_Semantic.parseSemantic(tokens, semantic_panel)
            
            if not semantic_success:
                # If there are semantic errors, switch to semantic tab
                notebook.select(2)  # Index 2 is the semantic tab
            else:
                # If semantic analysis passes, run the code generator
                success, generated_code = GenomeX_CodeGen.parseCodeGen(tokens, codegen_panel)
                
                # Switch to CodeGen tab to show the results
                notebook.select(3)  # Index 3 is the CodeGen tab
                
                if success:
                    # Show Python code
                    codegen_panel.delete("1.0", tk.END)
                    codegen_panel.insert(tk.END, "// Python code generated successfully\n\n", "success")
                    codegen_panel.insert(tk.END, generated_code)
                    codegen_panel.tag_config("success", foreground="green")
                else:
                    # Already handled by parseCodeGen with appropriate message
                    pass

btn_run.config(command=run_analysis)

# Define themes
def apply_dark_mode():
    root.configure(bg="#181818")
    style.configure("TFrame", background="#181818")
    style.configure("TLabel", background="#181818", foreground="white", font=("Inter", 16))
    style.configure("TButton", background="#363636", foreground="white")
    style.configure("Treeview", background="#1F1F1F", foreground="white", fieldbackground="#1F1F1F")
    style.configure("TNotebook", background="#181818")
    style.configure("TNotebook.Tab", background="#B2B2B2", foreground="#797979")
    style.map("TNotebook.Tab", background=[("selected", "#5B5B5B")], foreground=[("selected", "#FFFFFF")])
    
    for col in columns:
        tree.heading(col, text=col, anchor="center")
        tree.column(col, anchor="center", width=100, minwidth=100, stretch=True)
        style.configure("Treeview.Heading", background="#5B5B5B", foreground="white")
    
    text_editor.configure(background="#1F1F1F", foreground="white", insertbackground="white", font=("Inter", 12))
    line_numbers.configure(background="#1F1F1F", foreground="white", font=("Inter", 12))
    lexical_panel.configure(background="#1F1F1F", foreground="white", font=("Inter", 12))
    syntax_panel.configure(background="#1F1F1F", foreground="white")
    semantic_panel.configure(background="#1F1F1F", foreground="white")
    codegen_panel.configure(background="#1F1F1F", foreground="white")

def apply_light_mode():
    root.configure(bg="#FFFFFF")
    style.configure("TFrame", background="#FFFFFF")
    style.configure("TLabel", background="#FFFFFF", foreground="black", font=("Inter", 16))
    style.configure("TButton", background="#E7E7E7", foreground="black")
    style.configure("Treeview", background="#FFFFFF", foreground="black", fieldbackground="#FFFFFF")
    style.configure("TNotebook", background="#FFFFFF")
    style.configure("TNotebook.Tab", background="#E7E7E7", foreground="black")
    style.map("TNotebook.Tab", background=[("selected", "#E7E7E7")], foreground=[("selected", "black")])
    
    for col in columns:
        tree.heading(col, text=col, anchor="center")
        tree.column(col, anchor="center", width=100, minwidth=100, stretch=True)
        style.configure("Treeview.Heading", background="#FFFFFF", foreground="black")
    
    text_editor.configure(background="#FFFFFF", foreground="black", insertbackground="black", font=("Inter", 12))
    line_numbers.configure(background="#E7E7E7", foreground="black", font=("Inter", 12))
    lexical_panel.configure(background="#FFFFFF", foreground="black", font=("Inter", 12))
    syntax_panel.configure(background="#FFFFFF", foreground="black")
    semantic_panel.configure(background="#FFFFFF", foreground="black")
    codegen_panel.configure(background="#FFFFFF", foreground="black")

# Define the undo function
def undo_text():
    try:
        text_editor.edit_undo()
        update_line_numbers()
    except tk.TclError:
        messagebox.showinfo("Undo", "Nothing to undo")

# Add undo keybinding 
text_editor.bind("<Control-z>", lambda event: undo_text())

# Add undo button
btn_undo = ttk.Button(bottom_frame, text="Undo", width=10, command=undo_text)
btn_undo.pack(side=tk.RIGHT, padx=10)

# Add undo capability to the text widget
text_editor.config(undo=True, maxundo=-1, autoseparators=True)
# settings_button.config(command=lambda: apply_light_mode() if text_editor.cget("background") == "#1F1F1F" else apply_dark_mode())
apply_light_mode()  # Default theme

# Run the application
root.mainloop()
