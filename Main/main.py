import tkinter as tk
from tkinter import ttk, filedialog
from settings import load_settings, save_settings
from theme import apply_theme, choose_and_apply_accent_color
from tabs import add_project_tab, switch_project_tab
from macros import add_macro_dialog
from file_operations import process_extraction, archive_extracted_files, remove_file_from_output, populate_tree
from tkinter.scrolledtext import ScrolledText

# Load initial settings
app_settings = load_settings()
accent_color = app_settings.get('accent_color', "#3498db")

# Create the main application window with custom title bar
app = tk.Tk()
app.title("GPT-Code-Extractor")
app.geometry("900x600")
app.configure(bg="#2e2e2e")
app.overrideredirect(True)  # Custom title bar

# Custom Title Bar with Minimize and Close
title_bar = tk.Frame(app, bg="#1f1f1f", relief="raised", bd=2)
title_bar.pack(fill=tk.X)

title_label = tk.Label(title_bar, text="GPT Code Extractor", bg="#1f1f1f", fg="#ffffff")
title_label.pack(side=tk.LEFT, padx=10)

def minimize_app():
    app.iconify()

def close_app():
    app.quit()

minimize_button = tk.Button(title_bar, text="_", command=minimize_app, bg="#1f1f1f", fg="#ffffff", relief="flat")
minimize_button.pack(side=tk.RIGHT, padx=5)

close_button = tk.Button(title_bar, text="X", command=close_app, bg="#1f1f1f", fg="#ffffff", relief="flat")
close_button.pack(side=tk.RIGHT)

# Left Frame for Tabs and Macros
left_frame = tk.Frame(app, bg="#2e2e2e", width=220)
left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

# Tabs Notebook
tab_control = ttk.Notebook(left_frame)
tab_control.pack(fill=tk.BOTH, expand=True)
tab_control.bind("<<NotebookTabChanged>>", switch_project_tab)

# Add Tab Button
add_tab_button = tk.Button(left_frame, text="Add Tab", command=lambda: add_project_tab(tab_control), bg=accent_color)
add_tab_button.pack(fill=tk.X, pady=5)

# Macro Frame and Button for Adding Macros
macro_frame = tk.Frame(left_frame, bg="#2e2e2e")
macro_frame.pack(fill=tk.BOTH, padx=5, pady=5)
add_macro_button = tk.Button(left_frame, text="Add Macro", command=lambda: add_macro_dialog(macro_frame), bg=accent_color)
add_macro_button.pack(fill=tk.X, pady=5)

# Right Frame for main content
right_frame = tk.Frame(app, bg="#2e2e2e")
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

# Accent Color Picker Button
accent_color_button = tk.Button(right_frame, text="Choose Accent Color", command=lambda: choose_and_apply_accent_color(app, app_settings), bg=accent_color)
accent_color_button.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

# Directory Entries and Browse Buttons
def browse_directory(entry):
    directory = filedialog.askdirectory()
    if directory:
        entry.delete(0, tk.END)
        entry.insert(0, directory)

# Project Directory
project_dir_entry = tk.Entry(right_frame, width=50, bg="#444444", fg="#ffffff")
project_dir_entry.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
project_dir_button = tk.Button(right_frame, text="Browse", command=lambda: browse_directory(project_dir_entry), bg=accent_color)
project_dir_button.grid(row=1, column=1, padx=5, pady=5)

# Output Directory
output_dir_entry = tk.Entry(right_frame, width=50, bg="#444444", fg="#ffffff")
output_dir_entry.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
output_dir_button = tk.Button(right_frame, text="Browse", command=lambda: browse_directory(output_dir_entry), bg=accent_color)
output_dir_button.grid(row=2, column=1, padx=5, pady=5)

# Archive Directory
archive_dir_entry = tk.Entry(right_frame, width=50, bg="#444444", fg="#ffffff")
archive_dir_entry.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
archive_dir_button = tk.Button(right_frame, text="Browse", command=lambda: browse_directory(archive_dir_entry), bg=accent_color)
archive_dir_button.grid(row=3, column=1, padx=5, pady=5)

# Text box for inputting code and log console
text_box = ScrolledText(right_frame, height=10, width=50, bg="#444444", fg="#ffffff")
text_box.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
log_console = ScrolledText(right_frame, height=10, width=50, bg="#444444", fg="#ffffff")
log_console.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

# Tree View for Directory Structure
output_tree = ttk.Treeview(right_frame)
output_tree.grid(row=6, column=0, columnspan=2, sticky="nsew")

# Populate Tree
populate_tree(output_tree, output_dir_entry.get())

# Buttons for extracting, archiving, and removing output
extract_code_button = tk.Button(right_frame, text="Extract Code", command=lambda: process_extraction(text_box, output_dir_entry, log_console), bg=accent_color)
archive_button = tk.Button(right_frame, text="Archive Files", command=lambda: archive_extracted_files(output_dir_entry.get(), archive_dir_entry.get(), log_console), bg=accent_color)
remove_output_button = tk.Button(right_frame, text="Remove Output File/Folder", command=lambda: remove_file_from_output(log_console, output_dir_entry), bg="#d9534f", fg="#ffffff")

extract_code_button.grid(row=7, column=0, padx=5, pady=5, sticky="ew")
archive_button.grid(row=7, column=1, padx=5, pady=5, sticky="ew")
remove_output_button.grid(row=8, column=1, padx=5, pady=5, sticky="ew")

# Apply theme and load settings
apply_theme(app, accent_color)
app.mainloop()
