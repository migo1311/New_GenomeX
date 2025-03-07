import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from GenomeX_Lexer import display_lexical_error, parseLexer
import GenomeX_Lexer

# Create the main application window
root = tk.Tk()
root.title("GenomeX 🧬")
root.geometry("1440x1024")

# Load icons
settings_icon = ImageTk.PhotoImage(Image.open("settings_icon.png").resize((40, 40)))
genome_icon = ImageTk.PhotoImage(Image.open("genome_icon.png").resize((50, 50)))

# Style configuration
style = ttk.Style()
style.theme_use("clam")

# Header with icons
header_frame = ttk.Frame(root)
header_frame.pack(fill=tk.X, padx=20, pady=10)

title_label = ttk.Label(header_frame, text="GenomeX", font=("Inter", 32))
title_label.pack(side=tk.LEFT)

genome_label = ttk.Label(header_frame, image=genome_icon)
genome_label.pack(side=tk.LEFT, padx=10)

settings_button = ttk.Button(header_frame, image=settings_icon)
settings_button.pack(side=tk.RIGHT, padx=10)

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

# Add scrollbar
editor_scrollbar = ttk.Scrollbar(editor_frame)
editor_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

line_numbers = tk.Text(editor_frame, width=4, padx=4, takefocus=0, border=0, 
                      state="disabled", bg='#f0f0f0')
line_numbers.pack(side=tk.LEFT, fill=tk.Y)

text_editor = tk.Text(editor_frame, wrap=tk.NONE)
text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Configure scrollbar
editor_scrollbar.config(command=on_text_scroll)
text_editor.config(yscrollcommand=editor_scrollbar.set)

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
    update_line_numbers()

# Buttons (Run & Clear)
bottom_frame = ttk.Frame(root)
bottom_frame.pack(fill=tk.X, pady=10, padx=20)

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

notebook.add(lexical_tab, text="Lexical Status")
notebook.add(syntax_tab, text="Syntax Result")
notebook.add(semantic_tab, text="Semantic Error")
notebook.pack(fill=tk.BOTH, expand=True)

lexical_panel = tk.Text(lexical_tab, wrap=tk.WORD)
lexical_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

syntax_panel = tk.Text(syntax_tab, wrap=tk.WORD)
syntax_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

semantic_panel = tk.Text(semantic_tab, wrap=tk.WORD)
semantic_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

def highlight_errors(text_editor, line_number, lexeme):
    start_index = f"{line_number}.0"
    end_index = f"{line_number}.end"

    # Find lexeme position in the line
    text_content = text_editor.get(start_index, end_index)
    if lexeme in text_content:
        start_idx = text_content.index(lexeme)
        text_editor.tag_add("error", f"{line_number}.{start_idx}", f"{line_number}.{start_idx + len(lexeme)}")
    else:
        text_editor.tag_add("error", start_index, end_index)  # Highlight full line if lexeme isn't found
    
    text_editor.tag_config("error", foreground="red", underline=True)

# Function to execute lexer and display results
def run_lexer():
    input_text = text_editor.get("1.0", tk.END).strip()
    
    # Clear previous output
    tree.delete(*tree.get_children())
    lexical_panel.delete("1.0", tk.END)

    # Inject lexical_panel into the Lexer module so errors can be displayed
    GenomeX_Lexer.lexical_panel = lexical_panel  

    # Run Lexer and get tokens
    tokens = GenomeX_Lexer.parseLexer(input_text)
    
    if not tokens:
        display_lexical_error("No tokens found or input is invalid.")
    else:
        for idx, (lexeme, token) in enumerate(tokens):
            tree.insert("", "end", values=(idx + 1, lexeme, token))

btn_run.config(command=run_lexer)

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

settings_button.config(command=lambda: apply_light_mode() if text_editor.cget("background") == "#1F1F1F" else apply_dark_mode())
apply_light_mode()  # Default theme

# Run the application
root.mainloop()