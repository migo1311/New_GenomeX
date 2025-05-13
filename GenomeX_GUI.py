import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
# from PIL import Image, ImageTk
from tkinter import simpledialog
from GenomeX_Lexer import display_lexical_error, display_lexical_pass
import GenomeX_Lexer
import GenomeX_Syntax  # Add this import
import GenomeX_CodeGen  # Add this import
import GenomX_Semantic 

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

# Configure custom ttk styles for a modern look
class RoundedButton(tk.Canvas):
    def __init__(self, parent, width, height, corner_radius, padding=0, color="#5e35b1", text="", command=None, **kwargs):
        tk.Canvas.__init__(self, parent, width=width, height=height, highlightthickness=0, **kwargs)
        self.command = command
        self.color = color
        self.hover_color = "#7c4dff"

        # Create rounded rectangle
        self.rect = self.create_rounded_rect(padding, padding, width-padding, height-padding, corner_radius, fill=color)
        self.text_item = self.create_text(width/2, height/2, text=text, fill="white", font=("Segoe UI", 10, "bold"))

        # Bind events
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, **kwargs, smooth=True)

    def _on_press(self, event):
        self.itemconfig(self.rect, fill="#4527a0")

    def _on_release(self, event):
        self.itemconfig(self.rect, fill=self.hover_color)
        if self.command:
            self.command()

    def _on_enter(self, event):
        self.itemconfig(self.rect, fill=self.hover_color)
        self.config(cursor="hand2")

    def _on_leave(self, event):
        self.itemconfig(self.rect, fill=self.color)
        self.config(cursor="")

# Style configuration
style = ttk.Style()
style.theme_use("clam")

# Setup custom styles for a more professional look
style.configure("TFrame", background="#ffffff")
style.configure("TLabel", background="#ffffff", foreground="#5e35b1", font=("Segoe UI", 32, "bold"))
style.configure("TButton", font=("Segoe UI", 10), background="#5e35b1", foreground="white", padding=8)
style.map("TButton", background=[("active", "#7c4dff"), ("pressed", "#4527a0")])
style.configure("Treeview", font=("Consolas", 10), rowheight=22)
style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#ede7f6")
style.configure("TNotebook", background="#ffffff")
style.configure("TNotebook.Tab", font=("Segoe UI", 10), padding=[12, 4], background="#ede7f6")
style.map("TNotebook.Tab", background=[("selected", "#5e35b1")], foreground=[("selected", "white")])
style.configure("TLabelframe", background="#ffffff", foreground="#5e35b1", padding=10)
style.configure("TLabelframe.Label", font=("Segoe UI", 11, "bold"), background="#ffffff", foreground="#5e35b1")

# Create a custom color scheme for syntax highlighting
code_colors = {
    "keywords": "#7c4dff",      # Purple for keywords
    "strings": "#4caf50",       # Green for strings
    "numbers": "#f57c00",       # Orange for numbers
    "comments": "#9e9e9e",      # Gray for comments
    "functions": "#2196f3",     # Blue for function names
    "background": "#ffffff",    # White background
    "text": "#212121",          # Dark gray text
    "line_numbers": "#9575cd"   # Light purple for line numbers
}

# Header with icons
header_frame = ttk.Frame(root)
header_frame.pack(fill=tk.X, padx=20, pady=10)

title_label = ttk.Label(header_frame, text="GenomeX", font=("Segoe UI", 32, "bold"))
title_label.pack(side=tk.LEFT)

# Main layout with subtle shadow effects
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

# Left panel (Code Editor) with better visual design
editor_frame = ttk.Frame(main_frame, style="Card.TFrame")
editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Add vertical scrollbar
editor_scrollbar = ttk.Scrollbar(editor_frame, orient=tk.VERTICAL)
editor_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Add horizontal scrollbar
editor_horizontal_scrollbar = ttk.Scrollbar(editor_frame, orient=tk.HORIZONTAL)
editor_horizontal_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

# Style the line numbers with a subtle background
line_numbers = tk.Text(editor_frame, width=4, padx=4, takefocus=0, border=0, 
                      state="disabled", bg='#f5f5f7', fg=code_colors["line_numbers"], font=("Consolas", 13))
line_numbers.pack(side=tk.LEFT, fill=tk.Y)

# Modern text editor with slightly increased font size for better readability
text_editor = tk.Text(editor_frame, wrap=tk.NONE, yscrollcommand=editor_scrollbar.set, 
                      xscrollcommand=editor_horizontal_scrollbar.set, 
                      font=("Consolas", 13), bg=code_colors["background"], 
                      fg=code_colors["text"], insertbackground="#5e35b1",
                      borderwidth=0, relief="flat")
text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Insert default text into the text editor
text_editor.insert("1.0", "")

# Configure vertical scrollbar
editor_scrollbar.config(command=on_text_scroll)

# Configure horizontal scrollbar
editor_horizontal_scrollbar.config(command=text_editor.xview)

# Bind events
text_editor.bind("<KeyRelease>", update_line_numbers)
text_editor.bind("<MouseWheel>", lambda e: on_text_scroll("scroll", -1 if e.delta > 0 else 1, "units"))
text_editor.bind("<Configure>", update_line_numbers)

# Right panel (Lexical Tokenization) with shadow and rounded corners
table_frame = ttk.LabelFrame(main_frame, text="Lexical Tokenization")
table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=5)

columns = ("ID", "Lexeme", "Token")
tree = ttk.Treeview(table_frame, columns=columns, show='headings')

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100, anchor='center')

tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

def clear_editor():
    text_editor.delete(1.0, tk.END)
    tree.delete(*tree.get_children())
    lexical_panel.delete(1.0, tk.END)
    syntax_panel.delete(1.0, tk.END)
    semantic_panel.delete(1.0, tk.END)
    codegen_panel.delete(1.0, tk.END)

    update_line_numbers()

# Buttons (Run & Clear) with rounded corners
bottom_frame = ttk.Frame(root)
bottom_frame.pack(fill=tk.X, pady=10, padx=20)

# Create custom rounded buttons instead of ttk buttons
btn_clear = RoundedButton(bottom_frame, width=100, height=36, corner_radius=18, 
                        text="Clear", color="#f44336", command=clear_editor)
btn_clear.pack(side=tk.RIGHT, padx=10)

btn_undo = RoundedButton(bottom_frame, width=100, height=36, corner_radius=18, 
                        text="Undo", color="#673ab7", command=lambda: undo_text())
btn_undo.pack(side=tk.RIGHT, padx=10)

btn_run = RoundedButton(bottom_frame, width=100, height=36, corner_radius=18, 
                       text="Run", color="#4caf50", command=lambda: run_analysis())
btn_run.pack(side=tk.RIGHT)

# Notebook (Tabs for results) with improved styling
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
notebook.add(codegen_tab, text="Code Gen")
notebook.pack(fill=tk.BOTH, expand=True)

# Create styled output panels with monospaced font and better padding
def create_styled_text_widget(parent):
    text_widget = tk.Text(parent, wrap=tk.WORD, padx=15, pady=15,
                          font=("Consolas", 13), borderwidth=0, relief="flat",
                          background="#f8f5ff", foreground="#2d2d2d")
    
    # Configure tags for colored output
    text_widget.tag_configure("error", foreground="#f44336", font=("Consolas", 12, "bold"))
    text_widget.tag_configure("success", foreground="#4caf50", font=("Consolas", 12, "bold"))
    text_widget.tag_configure("warning", foreground="#ff9800", font=("Consolas", 12))
    text_widget.tag_configure("info", foreground="#2196f3", font=("Consolas", 12))
    text_widget.tag_configure("cmd", foreground="#9c27b0", font=("Consolas", 12))
    text_widget.tag_configure("output", foreground="#212121", font=("Consolas", 12))
    
    return text_widget

lexical_panel = create_styled_text_widget(lexical_tab)
lexical_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

syntax_panel = create_styled_text_widget(syntax_tab)
syntax_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

semantic_panel = create_styled_text_widget(semantic_tab)
semantic_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

codegen_panel = create_styled_text_widget(codegen_tab)
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
        text_editor.tag_add("error", start_index, end_index)  # Highlight full line if lexeme isn't found
    
    text_editor.tag_config("error", foreground="#f44336", underline=True)

# Enhanced display functions with colored text
def display_with_color(panel, text, tag="output"):
    panel.insert(tk.END, text, tag)
    panel.see(tk.END)

# Override the display functions in the lexer
original_display_error = GenomeX_Lexer.display_lexical_error
original_display_pass = GenomeX_Lexer.display_lexical_pass

def custom_display_lexical_error(error_msg):
    if hasattr(GenomeX_Lexer, 'lexical_panel'):
        GenomeX_Lexer.lexical_panel.insert(tk.END, "❌ Error: ", "error")
        GenomeX_Lexer.lexical_panel.insert(tk.END, f"{error_msg}\n", "output")
    return original_display_error(error_msg)

def custom_display_lexical_pass(pass_msg):
    if hasattr(GenomeX_Lexer, 'lexical_panel'):
        GenomeX_Lexer.lexical_panel.insert(tk.END, "✅ Success: ", "success")
        GenomeX_Lexer.lexical_panel.insert(tk.END, f"{pass_msg}\n", "output")
    return original_display_pass(pass_msg)

GenomeX_Lexer.display_lexical_error = custom_display_lexical_error
GenomeX_Lexer.display_lexical_pass = custom_display_lexical_pass

# Function to execute lexer and syntax analyzer and display results
def run_analysis():
    input_text = text_editor.get("1.0", tk.END).strip()
    
    # Get the currently selected tab before performing analysis
    current_tab = notebook.index("current")
    
    # Clear previous output
    tree.delete(*tree.get_children())
    lexical_panel.delete("1.0", tk.END)
    syntax_panel.delete("1.0", tk.END)
    semantic_panel.delete("1.0", tk.END)
    codegen_panel.delete("1.0", tk.END)

    # Inject lexical_panel into the Lexer module so errors can be displayed
    GenomeX_Lexer.lexical_panel = lexical_panel  

    # Run Lexer and get tokens
    tokens, found_error = GenomeX_Lexer.parseLexer(input_text)

    # Display tokens in the lexical tokenization table regardless of errors
    for idx, (lexeme, token) in enumerate(tokens):
        tree.insert("", "end", values=(idx + 1, lexeme, token))
        
    if found_error:
        # Display error message but still show valid tokens
        display_with_color(lexical_panel, "⚠️ Lexical Analysis: ", "warning")
        display_with_color(lexical_panel, "Errors found\n", "output")
        # Switch to lexical tab to show the error message
        notebook.select(0)
        
    elif not tokens:
        display_with_color(lexical_panel, "No tokens found.\n", "warning")
        notebook.select(0)
    else:
        # Show that lexical analysis passed successfully
        display_with_color(lexical_panel, "✅ Lexical Analysis: ", "success")
        display_with_color(lexical_panel, "All tokens processed successfully\n", "output")
        
        # After successful lexical analysis, run syntax analysis
        syntax_errors = GenomeX_Syntax.parseSyntax(tokens, syntax_panel)
        
        if syntax_errors:
            # If there are syntax errors, switch to syntax tab
            display_with_color(syntax_panel, "⚠️ Syntax Analysis: ", "warning")
            display_with_color(syntax_panel, "Errors detected\n", "output")
            notebook.select(1)  # Index 1 is the syntax tab

        else:
            # Show syntax analysis passed
            display_with_color(syntax_panel, "✅ Syntax Analysis: ", "success")
            display_with_color(syntax_panel, "No syntax errors found\n", "output")
            
            # Run semantic analysis only if syntax analysis passed
            semantic_success = GenomX_Semantic.parseSemantic(tokens, semantic_panel)
            
            if not semantic_success:
                # If there are semantic errors, switch to semantic tab
                display_with_color(semantic_panel, "⚠️ Semantic Analysis: ", "warning")
                display_with_color(semantic_panel, "Errors detected\n", "output")
                notebook.select(2)  # Index 2 is the semantic tab

            else:
                # Show semantic analysis passed
                display_with_color(semantic_panel, "✅ Semantic Analysis: ", "success")
                display_with_color(semantic_panel, "No semantic errors found\n", "output")
                
                # Only run code generation if both syntax and semantic analysis passed
                # Get generated Python code but don't display it to the user
                display_with_color(codegen_panel, "⏳ Generating code and executing...\n", "info")
                success, python_code = GenomeX_CodeGen.parseCodeGen(tokens, codegen_panel)
                
                if success:
                    # The codegen panel is already populated by parseCodeGen
                    # Switch to code execution tab
                    notebook.select(3)

# Define the undo function
def undo_text():
    try:
        text_editor.edit_undo()
        update_line_numbers()
    except tk.TclError:
        messagebox.showinfo("Undo", "Nothing to undo")

# Add undo keybinding 
text_editor.bind("<Control-z>", lambda event: undo_text())
text_editor.bind("<Control-r>", lambda event: run_analysis())

# Add undo capability to the text widget
text_editor.config(undo=True, maxundo=-1, autoseparators=True)

# Define themes
def apply_dark_mode():
    root.configure(bg="#212121")
    style.configure("TFrame", background="#212121")
    style.configure("TLabel", background="#212121", foreground="#d1c4e9", font=("Segoe UI", 32, "bold"))
    style.configure("Treeview", background="#2d2d2d", foreground="#f5f5f7", fieldbackground="#2d2d2d", font=("Consolas", 10), rowheight=22)
    style.configure("TNotebook", background="#212121")
    style.configure("TNotebook.Tab", font=("Segoe UI", 10), padding=[12, 4], background="#2d2d2d")
    style.map("TNotebook.Tab", background=[("selected", "#673ab7")], foreground=[("selected", "#f5f5f7")])
    style.configure("TLabelframe", background="#212121", foreground="#d1c4e9", padding=10)
    style.configure("TLabelframe.Label", font=("Segoe UI", 11, "bold"), background="#212121", foreground="#d1c4e9")
    
    for col in columns:
        tree.heading(col, text=col, anchor="center")
        tree.column(col, anchor="center", width=100, minwidth=100, stretch=True)
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#1d1d1f", foreground="#d1c4e9")
    
    # Update all text areas with dark mode colors
    text_editor.configure(background="#2d2d2d", foreground="#f5f5f7", insertbackground="#b39ddb")
    line_numbers.configure(background="#212121", foreground="#9575cd")
    
    # Update the output panels
    for panel in [lexical_panel, syntax_panel, semantic_panel, codegen_panel]:
        panel.configure(background="#2d2d2d", foreground="#f5f5f7")
        # Re-configure tags for dark mode
        panel.tag_configure("error", foreground="#ff8a80")
        panel.tag_configure("success", foreground="#b9f6ca")
        panel.tag_configure("warning", foreground="#ffd180")
        panel.tag_configure("info", foreground="#80d8ff")
        panel.tag_configure("cmd", foreground="#ea80fc")
        panel.tag_configure("output", foreground="#f5f5f7")
    
    # Update button colors for dark mode
    btn_run.color = "#388e3c"
    btn_run.hover_color = "#4caf50"
    btn_run.itemconfig(btn_run.rect, fill="#388e3c")
    
    btn_undo.color = "#512da8"
    btn_undo.hover_color = "#673ab7"
    btn_undo.itemconfig(btn_undo.rect, fill="#512da8")
    
    btn_clear.color = "#c62828"
    btn_clear.hover_color = "#f44336"
    btn_clear.itemconfig(btn_clear.rect, fill="#c62828")

def apply_light_mode():
    root.configure(bg="#ffffff")
    style.configure("TFrame", background="#ffffff")
    style.configure("TLabel", background="#ffffff", foreground="#5e35b1", font=("Segoe UI", 32, "bold"))
    style.configure("Treeview", background="#ffffff", foreground="#1d1d1f", fieldbackground="#ffffff", font=("Consolas", 10), rowheight=22)
    style.configure("TNotebook", background="#ffffff")
    style.configure("TNotebook.Tab", font=("Segoe UI", 10), padding=[12, 4], background="#ede7f6")
    style.map("TNotebook.Tab", background=[("selected", "#5e35b1")], foreground=[("selected", "white")])
    style.configure("TLabelframe", background="#ffffff", foreground="#5e35b1", padding=10)
    style.configure("TLabelframe.Label", font=("Segoe UI", 11, "bold"), background="#ffffff", foreground="#5e35b1")
    
    for col in columns:
        tree.heading(col, text=col, anchor="center")
        tree.column(col, anchor="center", width=100, minwidth=100, stretch=True)
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#ede7f6", foreground="#5e35b1")
    
    # Update all text areas with light mode colors
    text_editor.configure(background="#ffffff", foreground="#2d2d2d", insertbackground="#5e35b1")
    line_numbers.configure(background="#f5f5f7", foreground="#9575cd")
    
    # Update the output panels
    for panel in [lexical_panel, syntax_panel, semantic_panel, codegen_panel]:
        panel.configure(background="#f8f5ff", foreground="#2d2d2d")
        # Re-configure tags for light mode
        panel.tag_configure("error", foreground="#f44336")
        panel.tag_configure("success", foreground="#4caf50")
        panel.tag_configure("warning", foreground="#ff9800")
        panel.tag_configure("info", foreground="#2196f3")
        panel.tag_configure("cmd", foreground="#9c27b0")
        panel.tag_configure("output", foreground="#212121")
    
    # Update button colors for light mode
    btn_run.color = "#4caf50"
    btn_run.hover_color = "#66bb6a"
    btn_run.itemconfig(btn_run.rect, fill="#4caf50")
    
    btn_undo.color = "#673ab7"
    btn_undo.hover_color = "#7c4dff"
    btn_undo.itemconfig(btn_undo.rect, fill="#673ab7")
    
    btn_clear.color = "#f44336"
    btn_clear.hover_color = "#ef5350"
    btn_clear.itemconfig(btn_clear.rect, fill="#f44336")

# Add theme toggle button in the header
# Use a global variable to track the current theme
current_theme = "light"  # Default theme

def toggle_theme():
    global current_theme
    if current_theme == "light":
        apply_dark_mode()
        current_theme = "dark"
        theme_toggle_button.itemconfig(theme_toggle_button.text_item, text="☀️")
    else:
        apply_light_mode()
        current_theme = "light"
        theme_toggle_button.itemconfig(theme_toggle_button.text_item, text="🌙")

theme_toggle_button = RoundedButton(header_frame, width=40, height=40, corner_radius=20, 
                                   text="🌙", color="#5e35b1", 
                                   command=toggle_theme)
theme_toggle_button.pack(side=tk.RIGHT, padx=10)

# Apply light mode as default
apply_light_mode()

# Initialize line numbers
update_line_numbers()

# Add search functionality
class SearchBox:
    def __init__(self, parent, text_widget):
        self.parent = parent
        self.text_widget = text_widget
        self.search_frame = ttk.Frame(parent)
        self.search_frame.place(relx=0.5, rely=0, anchor="n")
        
        # Create search widgets
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        # Find buttons
        self.prev_btn = RoundedButton(self.search_frame, width=80, height=30, corner_radius=15,
                                    text="Previous", color="#5e35b1", command=self.find_previous)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.next_btn = RoundedButton(self.search_frame, width=80, height=30, corner_radius=15,
                                    text="Next", color="#5e35b1", command=self.find_next)
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        # Close button
        self.close_btn = RoundedButton(self.search_frame, width=30, height=30, corner_radius=15,
                                     text="✕", color="#f44336", command=self.hide)
        self.close_btn.pack(side=tk.LEFT, padx=5)
        
        # Bind events
        self.search_var.trace_add("write", self.on_search_change)
        self.search_entry.bind("<Return>", lambda e: self.find_next())
        self.search_entry.bind("<Shift-Return>", lambda e: self.find_previous())
        self.search_entry.bind("<Escape>", lambda e: self.hide())
        
        # Initially hide the search box
        self.search_frame.place_forget()
        
        # Configure search highlight tag
        self.text_widget.tag_configure("search_highlight", background="#ffeb3b", foreground="#000000")
        self.text_widget.tag_configure("search_highlight_current", background="#ffc107", foreground="#000000")
        
        self.current_match = None
        self.matches = []
        self.current_match_index = -1

    def show(self):
        self.search_frame.place(relx=0.5, rely=0, anchor="n")
        self.search_entry.focus_set()
        self.search_entry.select_range(0, tk.END)

    def hide(self):
        self.search_frame.place_forget()
        self.text_widget.tag_remove("search_highlight", "1.0", tk.END)
        self.text_widget.tag_remove("search_highlight_current", "1.0", tk.END)
        self.text_widget.focus_set()

    def on_search_change(self, *args):
        search_term = self.search_var.get()
        if not search_term:
            self.text_widget.tag_remove("search_highlight", "1.0", tk.END)
            self.text_widget.tag_remove("search_highlight_current", "1.0", tk.END)
            self.matches = []
            self.current_match_index = -1
            return

        # Remove existing highlights
        self.text_widget.tag_remove("search_highlight", "1.0", tk.END)
        self.text_widget.tag_remove("search_highlight_current", "1.0", tk.END)
        
        # Find all matches
        self.matches = []
        start_pos = "1.0"
        while True:
            start_pos = self.text_widget.search(search_term, start_pos, tk.END, nocase=True)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(search_term)}c"
            self.matches.append((start_pos, end_pos))
            self.text_widget.tag_add("search_highlight", start_pos, end_pos)
            start_pos = end_pos

        if self.matches:
            self.current_match_index = 0
            self.highlight_current_match()

    def highlight_current_match(self):
        if not self.matches:
            return
        
        # Remove current match highlight
        self.text_widget.tag_remove("search_highlight_current", "1.0", tk.END)
        
        # Add highlight to current match
        start_pos, end_pos = self.matches[self.current_match_index]
        self.text_widget.tag_add("search_highlight_current", start_pos, end_pos)
        
        # Ensure the current match is visible
        self.text_widget.see(start_pos)

    def find_next(self):
        if not self.matches:
            return
        
        self.current_match_index = (self.current_match_index + 1) % len(self.matches)
        self.highlight_current_match()

    def find_previous(self):
        if not self.matches:
            return
        
        self.current_match_index = (self.current_match_index - 1) % len(self.matches)
        self.highlight_current_match()

# Create the search box instance
search_box = None

def show_search_box(event=None):
    global search_box
    if search_box is None:
        search_box = SearchBox(root, text_editor)
    search_box.show()

# Add Ctrl+F binding
text_editor.bind("<Control-f>", show_search_box)

# Run the application
root.mainloop()
