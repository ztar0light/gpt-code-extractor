import os
import re
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import pyperclip

LINE_LIMIT = 3  # Maximum allowed lines between filename and code block

def extract_code_blocks(text, output_dir, archive_root, log_console):
    """
    Extracts filename and code blocks from the given text and writes them into respective files.
    
    Args:
        text (str): The input text containing filenames and code blocks.
        output_dir (str): The directory where files will be generated.
        archive_root (str): The root folder for archiving older versions.
        log_console (ScrolledText): A widget where log messages will be displayed.
    
    Returns:
        None
    """
    # Pattern to detect file names within backticks or quotes
    filename_pattern = r'(?:Filename:\s*`([^`]+)`|\'([^\'\s]+)\'|"([^\"\s]+)")'
    
    # Pattern to match code blocks inside triple backticks or similar
    code_pattern = r'```(?:python|html|css|javascript|js|txt)?\n([\s\S]*?)```'

    lines = text.split('\n')
    filenames = []
    code_blocks = []
    current_filename = None
    current_code = []
    line_count_after_filename = 0

    for line in lines:
        # Check for filename first
        filename_match = re.search(filename_pattern, line)
        if filename_match:
            # If there is a filename and we're still collecting code for the previous file, discard it
            if current_filename and not current_code:
                log_console.insert(tk.END, f"Ignoring {current_filename} (no code found).\n")

            # Start tracking a new filename
            current_filename = filename_match.group(1) or filename_match.group(2) or filename_match.group(3)
            log_console.insert(tk.END, f"Detected filename: {current_filename}\n")
            line_count_after_filename = 0
            current_code = []  # Reset current code collection
            continue

        # If we're tracking a filename, start counting lines until a code block is found
        if current_filename:
            line_count_after_filename += 1
            code_match = re.search(code_pattern, line)
            
            if code_match:
                # If code is found within the line limit, associate it with the current filename
                if line_count_after_filename <= LINE_LIMIT:
                    current_code.append(code_match.group(1))
                    filenames.append(current_filename)
                    code_blocks.append("\n".join(current_code))
                    log_console.insert(tk.END, f"Code block added for {current_filename}\n")
                else:
                    log_console.insert(tk.END, f"Ignoring {current_filename} (too many lines between filename and code).\n")
                current_filename = None  # Reset for the next filename
                current_code = []
                continue

        # If we exceed the line limit without finding a code block, ignore this filename
        if line_count_after_filename > LINE_LIMIT:
            log_console.insert(tk.END, f"Ignoring {current_filename} (exceeded line limit without code).\n")
            current_filename = None
            current_code = []

    if len(filenames) != len(code_blocks):
        log_console.insert(tk.END, "Error: Mismatch between the number of filenames and code blocks.\n")
        return

    # Initialize progress
    total_files = len(filenames)
    log_console.insert(tk.END, f"Processing {total_files} files...\n")

    # Process each filename and its corresponding code block
    for idx, (filename, code) in enumerate(zip(filenames, code_blocks), start=1):
        log_console.insert(tk.END, f"Processing file {idx}/{total_files}: {filename}\n")
        filepath = os.path.join(output_dir, filename)

        if os.path.exists(filepath):
            # Ask for overwrite or versioning
            overwrite = messagebox.askyesno("File Exists", f"{filename} exists. Overwrite?")
            if not overwrite:
                # Create versioned archive
                versioned_archive_dir = os.path.join(archive_root, os.path.splitext(filename)[0] + ".version")
                os.makedirs(versioned_archive_dir, exist_ok=True)
                
                # Move current file to archive
                archive_filepath = os.path.join(versioned_archive_dir, filename)
                shutil.move(filepath, archive_filepath)
                log_console.insert(tk.END, f"Moved existing file to archive: {archive_filepath}\n")
        
        # Write the new code to the file
        try:
            with open(filepath, 'w') as file:
                file.write(code)
            log_console.insert(tk.END, f"File '{filename}' created successfully in {output_dir}\n")
        except Exception as e:
            log_console.insert(tk.END, f"Error creating '{filename}': {e}\n")
        
        # Update progress
        log_console.see(tk.END)  # Auto-scroll the console


def paste_from_clipboard():
    """
    Pastes the content from the clipboard into the text box.
    """
    clipboard_text = pyperclip.paste()
    text_box.delete(1.0, tk.END)  # Clear the text box
    text_box.insert(tk.END, clipboard_text)


def select_output_directory():
    """
    Opens a dialog for selecting the output directory where files will be generated.
    """
    directory = filedialog.askdirectory()
    output_dir_entry.delete(0, tk.END)
    output_dir_entry.insert(0, directory)


def select_archive_root():
    """
    Opens a dialog for selecting the archive root directory.
    """
    directory = filedialog.askdirectory()
    archive_dir_entry.delete(0, tk.END)
    archive_dir_entry.insert(0, directory)


def process_extraction():
    """
    Processes the extraction of code blocks from the text box and saves them as files.
    """
    input_text = text_box.get(1.0, tk.END)
    output_dir = output_dir_entry.get()
    archive_root = archive_dir_entry.get()

    if not output_dir or not archive_root:
        messagebox.showwarning("Input Error", "Please specify both the output directory and the archive root folder.")
        return

    log_console.insert(tk.END, "Starting extraction...\n")
    log_console.see(tk.END)  # Auto-scroll the console

    extract_code_blocks(input_text, output_dir, archive_root, log_console)

    log_console.insert(tk.END, "Extraction completed.\n")
    log_console.see(tk.END)  # Auto-scroll the console


# Create the main application window
app = tk.Tk()
app.title("GPT-Code-Extractor")

# Create a text box for pasting the input
text_box = ScrolledText(app, height=15, width=70)
text_box.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

# Create a "Paste" button
paste_button = tk.Button(app, text="Paste from Clipboard", command=paste_from_clipboard)
paste_button.grid(row=1, column=0, padx=10, pady=10)

# Create an entry for output directory and a button to select it
output_dir_label = tk.Label(app, text="Output Directory:")
output_dir_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
output_dir_entry = tk.Entry(app, width=50)
output_dir_entry.grid(row=2, column=1, padx=10, pady=5)
output_dir_button = tk.Button(app, text="Browse", command=select_output_directory)
output_dir_button.grid(row=2, column=2, padx=10, pady=5)

# Create an entry for archive root directory and a button to select it
archive_dir_label = tk.Label(app, text="Archive Root Directory:")
archive_dir_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
archive_dir_entry = tk.Entry(app, width=50)
archive_dir_entry.grid(row=3, column=1, padx=10, pady=5)
archive_dir_button = tk.Button(app, text="Browse", command=select_archive_root)
archive_dir_button.grid(row=3, column=2, padx=10, pady=5)

# Create a "Process" button to start extraction
process_button = tk.Button(app, text="Extract & Generate Files", command=process_extraction)
process_button.grid(row=4, column=0, columnspan=3, padx=10, pady=20)

# Create a console for logging
log_console_label = tk.Label(app, text="Console:")
log_console_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")
log_console = ScrolledText(app, height=10, width=70)
log_console.grid(row=6, column=0, columnspan=3, padx=10, pady=10)
log_console.config(state=tk.NORMAL)

# Run the application
app.mainloop()
