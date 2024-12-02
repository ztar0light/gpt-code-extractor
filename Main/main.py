import tkinter as tk
from tkinter import ttk
from theme import apply_theme, choose_accent_color
from tabs import add_tab, add_macro
from file_operations import extract_files, archive_files, update_file_tree, remove_file_from_tree

class GPTCodeExtractorApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("GPT Code Extractor")
        self.geometry("800x600")
        self.configure(bg="#333")  # Background color for dark mode
        self.resizable(False, False)

        # Apply the dark theme
        apply_theme(self)

        # Accent color chooser
        self.accent_color_button = tk.Button(
            self, text="Choose Accent Color", command=self.choose_accent_color
        )
        self.accent_color_button.pack(pady=10)

        # Tabs and macros buttons
        self.add_tab_button = tk.Button(self, text="Add Tab", command=self.add_tab)
        self.add_tab_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.add_macro_button = tk.Button(self, text="Add Macro", command=self.add_macro)
        self.add_macro_button.pack(side=tk.LEFT, padx=5, pady=5)

        # File tree for managing directories
        self.tree_frame = tk.Frame(self)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(self.tree_frame)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Log output area
        self.log_output = tk.Text(self, height=8, bg="#222", fg="#ddd")
        self.log_output.pack(fill=tk.X)

        # Browse and control buttons
        self.browse_button = tk.Button(self, text="Browse", command=self.browse_directory)
        self.browse_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.extract_button = tk.Button(self, text="Extract", command=self.extract_files)
        self.extract_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.archive_button = tk.Button(self, text="Archive", command=self.archive_files)
        self.archive_button.pack(side=tk.LEFT, padx=5, pady=5)

    def choose_accent_color(self):
        choose_accent_color(self)

    def add_tab(self):
        add_tab(self.tree)

    def add_macro(self):
        add_macro(self.tree)

    def browse_directory(self):
        update_file_tree(self.tree, self.log_output)

    def extract_files(self):
        extract_files(self.tree, self.log_output)

    def archive_files(self):
        archive_files(self.tree, self.log_output)


if __name__ == "__main__":
    app = GPTCodeExtractorApp()
    app.mainloop()
