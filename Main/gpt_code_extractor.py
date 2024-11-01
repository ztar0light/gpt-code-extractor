import os
import shutil
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, simpledialog, colorchooser
from tkinter.scrolledtext import ScrolledText
import pyperclip
import json
import subprocess
import sys

version_number = 1
tabs_data = {}
macros = []
selected_archive_folder = ''
accent_color = "#3498db"
bg_color = "#2e2e2e"
fg_color = "#ffffff"
highlight_bg = "#444444"
treeview_bg = "#333333"

def get_app_directory():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

settings_file = os.path.join(get_app_directory(), 'gpt_code_extractor_settings.json')

def load_settings():
    global version_number, macros, tabs_data, accent_color
    try:
        with open(settings_file, 'r') as f:
            settings = json.load(f)
            version_number = settings.get('version_number', 1)
            macros = settings.get('macros', [])
            tabs_data = settings.get('tabs_data', {})
            accent_color = settings.get('accent_color', accent_color)
            apply_theme()
            log_console.insert(tk.END, "Settings loaded successfully.\n")
    except (FileNotFoundError, json.JSONDecodeError):
        log_console.insert(tk.END, "Settings file not found or corrupted, creating a new one.\n")
        save_settings()

def save_settings():
    global version_number, macros, tabs_data, accent_color
    settings = {
        'version_number': version_number,
        'macros': macros,
        'tabs_data': tabs_data,
        'accent_color': accent_color
    }
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=4)
    log_console.insert(tk.END, "Settings saved successfully.\n")

def apply_theme():
    app.configure(bg=bg_color)
    for widget in app.winfo_children():
        widget.configure(bg=bg_color, fg=fg_color)
    accent_widgets = [
        tab_control, macro_frame, output_tree, archive_tree_frame,
        project_dir_button, output_dir_button, archive_dir_button,
        extract_code_button, archive_button, remove_output_button,
        add_tab_button, add_macro_button, accent_color_button
    ]
    for widget in accent_widgets:
        widget.configure(bg=accent_color)

def choose_accent_color():
    global accent_color
    color = colorchooser.askcolor(title="Choose Accent Color", initialcolor=accent_color)
    if color[1]:
        accent_color = color[1]
        apply_theme()
        save_settings()

def switch_project_tab(event):
    current_tab = tab_control.tab(tab_control.select(), "text")
    if current_tab:
        save_tab_data(current_tab)
        load_tab_data(current_tab)

def load_tab_data(tab_name):
    if tab_name in tabs_data:
        data = tabs_data[tab_name]
        project_dir_entry.delete(0, tk.END)
        project_dir_entry.insert(0, data.get('project_dir', ''))
        output_dir_entry.delete(0, tk.END)
        output_dir_entry.insert(0, data.get('output_dir', ''))
        archive_dir_entry.delete(0, tk.END)
        archive_dir_entry.insert(0, data.get('archive_root', ''))
        log_console.delete(1.0, tk.END)
        log_console.insert(tk.END, data.get('log_content', ''))
        text_box.delete(1.0, tk.END)
        text_box.insert(tk.END, data.get('input_code', ''))
    else:
        project_dir_entry.delete(0, tk.END)
        project_dir_entry.insert(0, "NO TAB SELECTED")
        output_dir_entry.delete(0, tk.END)
        output_dir_entry.insert(0, "NO TAB SELECTED")
        archive_dir_entry.delete(0, tk.END)
        archive_dir_entry.insert(0, "NO TAB SELECTED")
        text_box.delete(1.0, tk.END)
        text_box.insert(tk.END, "NO TAB SELECTED")
        log_console.delete(1.0, tk.END)
        log_console.insert(tk.END, "NO TAB SELECTED")

def save_tab_data(tab_name):
    tabs_data[tab_name] = {
        'project_dir': project_dir_entry.get(),
        'output_dir': output_dir_entry.get(),
        'archive_root': archive_dir_entry.get(),
        'log_content': log_console.get(1.0, tk.END),
        'input_code': text_box.get(1.0, tk.END)
    }
    save_settings()

def add_project_tab():
    tab_name = simpledialog.askstring("Tab Name", "Enter a name for the new project tab:")
    if not tab_name:
        return
    tab = ttk.Frame(tab_control)
    tab_control.add(tab, text=tab_name)
    tabs_data[tab_name] = {}
    tab_control.select(tab)

def add_macro(name, command):
    macros.append({'name': name, 'command': command})
    save_settings()
    update_macro_buttons()

def remove_macro(index):
    if 0 <= index < len(macros):
        del macros[index]
        save_settings()
        update_macro_buttons()

def update_macro_buttons():
    for widget in macro_frame.winfo_children():
        widget.destroy()
    for index, macro in enumerate(macros):
        tk.Button(macro_frame, text=macro['name'], command=lambda cmd=macro['command']: subprocess.run(cmd, shell=True), width=20).pack(pady=2)
        tk.Button(macro_frame, text="Remove", command=lambda idx=index: remove_macro(idx), width=20, bg="red").pack(pady=2)

def add_macro_dialog():
    dialog = tk.Toplevel(app)
    dialog.title("Add Macro")
    tk.Label(dialog, text="Macro Name:").pack(pady=5)
    macro_name_entry = tk.Entry(dialog)
    macro_name_entry.pack(pady=5)
    tk.Label(dialog, text="Macro Command:").pack(pady=5)
    macro_command_entry = tk.Entry(dialog)
    macro_command_entry.pack(pady=5)
    def add_macro_from_dialog():
        macro_name = macro_name_entry.get()
        macro_command = macro_command_entry.get()
        add_macro(macro_name, macro_command)
        dialog.destroy()
    tk.Button(dialog, text="Add Macro", command=add_macro_from_dialog).pack(pady=10)

def clear_console():
    log_console.delete(1.0, tk.END)

def archive_extracted_files(output_dir, archive_root, log_console):
    global version_number
    if not selected_archive_folder:
        messagebox.showerror("Error", "Please select an archive folder in the tree view.")
        return
    versioned_archive_dir = os.path.join(selected_archive_folder, f".version-{version_number}")
    os.makedirs(versioned_archive_dir, exist_ok=True)
    log_console.insert(tk.END, "Archiving files...\n")
    log_content = f"Archive Version {version_number}\n"
    for filename in os.listdir(output_dir):
        filepath = os.path.join(output_dir, filename)
        if os.path.isfile(filepath):
            archive_filepath = os.path.join(versioned_archive_dir, filename)
            shutil.copy(filepath, archive_filepath)
            log_console.insert(tk.END, f"Archived file: {archive_filepath}\n")
            log_content += f"Archived file: {filename}\n"
    version_number += 1
    save_settings()
    log_file = os.path.join(versioned_archive_dir, f"archive_log_v{version_number}.txt")
    with open(log_file, 'w') as log_f:
        log_f.write(log_content)
    log_console.insert(tk.END, f"Archiving completed. Log generated: {log_file}\n")
    scan_archive_logs()
    visualize_directory_tree(archive_root, archive_tree_frame)

def process_extraction():
    input_text = text_box.get(1.0, tk.END)
    output_dir = output_dir_entry.get()
    archive_root = archive_dir_entry.get()
    if not output_dir or not archive_root:
        messagebox.showwarning("Input Error", "Please specify both the output directory and the archive root folder.")
        return
    log_console.insert(tk.END, "Starting extraction...\n")
    gpt_instructions = {'folders': ['assets', 'css'], 'files': ['main.py', 'index.html', 'styles.css']}
    create_project_structure(output_dir, gpt_instructions['files'], gpt_instructions)
    for filename in gpt_instructions['files']:
        filepath = os.path.join(output_dir, filename)
        if os.path.exists(filepath):
            overwrite = messagebox.askyesno("File Exists", f"{filename} exists. Overwrite?")
            if not overwrite:
                log_console.insert(tk.END, f"Skipped file: {filename}\n")
                continue
        with open(filepath, 'w') as file:
            file.write(f"// Code for {filename}\n")
            log_console.insert(tk.END, f"File '{filename}' created successfully in {output_dir}\n")
    log_console.insert(tk.END, "Extraction completed.\n")
    scan_archive_logs()
    visualize_directory_tree(output_dir, directory_tree_frame)

def remove_file_from_output():
    selected_item = output_tree.selection()
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select a file or folder to remove.")
        return
    item_path = output_tree.item(selected_item)["text"]
    path = os.path.join(output_dir_entry.get(), item_path)
    if os.path.isfile(path):
        os.remove(path)
        log_console.insert(tk.END, f"File removed: {path}\n")
    elif os.path.isdir(path):
        shutil.rmtree(path)
        log_console.insert(tk.END, f"Folder removed: {path}\n")
    else:
        log_console.insert(tk.END, f"Error: Could not locate {path}\n")
    visualize_directory_tree(output_dir_entry.get(), output_tree)

def visualize_directory_tree(path, tree_frame, selectable=False):
    for widget in tree_frame.winfo_children():
        widget.destroy()
    tree = ttk.Treeview(tree_frame)
    tree.pack(fill=tk.BOTH, expand=True)
    def insert_item(parent, path):
        for p in sorted(os.listdir(path)):
            abs_path = os.path.join(path, p)
            if os.path.isdir(abs_path):
                node = tree.insert(parent, 'end', text=p, open=False)
                insert_item(node, abs_path)
            else:
                tree.insert(parent, 'end', text=p)
    insert_item('', path)
    if selectable:
        tree.bind("<Double-1>", lambda e: select_archive_folder(tree))

def select_archive_folder(tree):
    global selected_archive_folder
    item = tree.selection()
    if item:
        selected_archive_folder = tree.item(item, "text")
        log_console.insert(tk.END, f"Selected archive folder: {selected_archive_folder}\n")

app = tk.Tk()
app.title("GPT-Code-Extractor")
app.configure(bg=bg_color)
app.grid_rowconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=1)
left_frame = tk.Frame(app, bg=bg_color, width=220)
left_frame.grid(row=0, column=0, rowspan=5, sticky="ns", padx=5, pady=5)
left_frame.grid_propagate(False)

tab_control = ttk.Notebook(left_frame)
tab_control.pack(fill=tk.BOTH, expand=True)
tab_control.bind("<<NotebookTabChanged>>", switch_project_tab)

add_tab_button = tk.Button(left_frame, text="Add Tab", command=add_project_tab, bg=accent_color)
add_tab_button.pack(fill=tk.X, pady=5)

macro_frame = tk.Frame(left_frame, bg=bg_color)
macro_frame.pack(fill=tk.BOTH, padx=5, pady=5)
add_macro_button = tk.Button(left_frame, text="Add Macro", command=add_macro_dialog, bg=accent_color)
add_macro_button.pack(fill=tk.X, pady=5)

right_frame = tk.Frame(app, bg=bg_color)
right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
for i in range(5):
    right_frame.grid_rowconfigure(i, weight=1)
right_frame.grid_columnconfigure(0, weight=1)
right_frame.grid_columnconfigure(1, weight=1)

accent_color_button = tk.Button(right_frame, text="Choose Accent Color", command=choose_accent_color, bg=accent_color)
accent_color_button.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

project_dir_label = tk.Label(right_frame, text="Project Directory:", bg=bg_color, fg=fg_color)
project_dir_label.grid(row=1, column=0, sticky="w", padx=5)
project_dir_entry = tk.Entry(right_frame, width=50, bg=highlight_bg, fg=fg_color)
project_dir_entry.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
project_dir_button = tk.Button(right_frame, text="Browse", command=select_project_directory, bg=accent_color)
project_dir_button.grid(row=1, column=1, padx=5, pady=5)

output_dir_label = tk.Label(right_frame, text="Output Directory:", bg=bg_color, fg=fg_color)
output_dir_label.grid(row=2, column=0, sticky="w", padx=5)
output_dir_entry = tk.Entry(right_frame, width=50, bg=highlight_bg, fg=fg_color)
output_dir_entry.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
output_dir_button = tk.Button(right_frame, text="Browse", command=select_output_directory, bg=accent_color)
output_dir_button.grid(row=2, column=1, padx=5, pady=5)

archive_dir_label = tk.Label(right_frame, text="Archive Directory:", bg=bg_color, fg=fg_color)
archive_dir_label.grid(row=3, column=0, sticky="w", padx=5)
archive_dir_entry = tk.Entry(right_frame, width=50, bg=highlight_bg, fg=fg_color)
archive_dir_entry.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
archive_dir_button = tk.Button(right_frame, text="Browse", command=select_archive_root, bg=accent_color)
archive_dir_button.grid(row=3, column=1, padx=5, pady=5)

text_box_label = tk.Label(right_frame, text="Input Code:", bg=bg_color, fg=fg_color)
text_box_label.grid(row=4, column=0, sticky="w", padx=5)
text_box = ScrolledText(right_frame, height=10, width=50, bg=highlight_bg, fg=fg_color, insertbackground=fg_color)
text_box.grid(row=5, column=0, padx=5, pady=5, sticky="nsew")

log_console_label = tk.Label(right_frame, text="Console:", bg=bg_color, fg=fg_color)
log_console_label.grid(row=6, column=0, sticky="w", padx=5)
log_console = ScrolledText(right_frame, height=10, width=50, bg=highlight_bg, fg=fg_color, insertbackground=fg_color)
log_console.grid(row=7, column=0, padx=5, pady=5, sticky="nsew")

directory_tree_frame = tk.Frame(right_frame, bg=treeview_bg)
directory_tree_frame.grid(row=5, column=1, sticky="nsew", padx=5, pady=5)

archive_tree_frame = tk.Frame(right_frame, bg=treeview_bg)
archive_tree_frame.grid(row=7, column=1, sticky="nsew", padx=5, pady=5)

extract_code_button = tk.Button(right_frame, text="Extract Code", command=process_extraction, bg=accent_color)
extract_code_button.grid(row=8, column=0, padx=5, pady=5, sticky="ew")
archive_button = tk.Button(right_frame, text="Archive Files", command=lambda: archive_extracted_files(output_dir_entry.get(), archive_dir_entry.get(), log_console), bg=accent_color)
archive_button.grid(row=8, column=1, padx=5, pady=5, sticky="ew")
remove_output_button = tk.Button(right_frame, text="Remove Output File/Folder", command=remove_file_from_output, bg="#d9534f", fg=fg_color)
remove_output_button.grid(row=9, column=1, padx=5, pady=5, sticky="ew")

load_settings()
apply_theme()
app.mainloop()
