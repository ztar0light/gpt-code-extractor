import os
import shutil
from tkinter import messagebox

def populate_tree(tree, directory):
    """Populates the tree view with files and folders from the specified directory."""
    tree.delete(*tree.get_children())  # Clear existing items
    if not os.path.exists(directory):
        return

    for item in os.listdir(directory):
        tree.insert('', 'end', text=item)

def process_extraction(text_box, output_dir_entry, log_console):
    """Extracts code from the text box and writes files to the output directory."""
    log_console.insert("end", "Starting extraction...\n")
    output_dir = output_dir_entry.get()
    
    if not output_dir or not os.path.exists(output_dir):
        messagebox.showwarning("Output Directory Missing", "Please specify a valid output directory.")
        log_console.insert("end", "Extraction aborted: Invalid output directory.\n")
        return

    text = text_box.get("1.0", "end-1c")
    lines = text.splitlines()
    filename = None
    content = []
    
    for line in lines:
        if line.startswith("Filename: "):  # Start of a new file
            if filename and content:
                write_file(output_dir, filename, "\n".join(content), log_console)
            filename = line.split("Filename: ")[1].strip()
            content = []
        else:
            content.append(line)
    
    if filename and content:  # Write the last file
        write_file(output_dir, filename, "\n".join(content), log_console)

    log_console.insert("end", "Extraction completed.\n")

def write_file(directory, filename, content, log_console):
    """Writes content to a file in the specified directory."""
    filepath = os.path.join(directory, filename)
    with open(filepath, 'w') as f:
        f.write(content)
    log_console.insert("end", f"File '{filename}' created.\n")

def archive_extracted_files(output_dir, archive_dir, log_console):
    """Archives extracted files from the output directory to the archive directory."""
    if not os.path.exists(output_dir):
        messagebox.showerror("Error", "Output directory does not exist.")
        return
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)  # Create the archive directory if it doesn't exist

    for filename in os.listdir(output_dir):
        source_path = os.path.join(output_dir, filename)
        destination_path = os.path.join(archive_dir, filename)
        
        if os.path.exists(destination_path):
            base, ext = os.path.splitext(filename)
            version = 1
            while os.path.exists(destination_path):
                destination_path = os.path.join(archive_dir, f"{base}_v{version}{ext}")
                version += 1

        shutil.move(source_path, destination_path)
        log_console.insert("end", f"Archived {filename} to {archive_dir}\n")

def remove_file_from_output(log_console, output_dir_entry):
    """Removes selected file/folder from output directory."""
    output_dir = output_dir_entry.get()
    if not os.path.exists(output_dir):
        log_console.insert("end", "Output directory does not exist.\n")
        return
    selected_item = output_tree.selection()
    if selected_item:
        item_text = output_tree.item(selected_item, "text")
        full_path = os.path.join(output_dir, item_text)
        if os.path.isfile(full_path):
            os.remove(full_path)
            log_console.insert("end", f"Removed file: {item_text}\n")
        elif os.path.isdir(full_path):
            shutil.rmtree(full_path)
            log_console.insert("end", f"Removed folder: {item_text}\n")
        output_tree.delete(selected_item)
