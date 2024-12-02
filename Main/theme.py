import tkinter as tk
from tkinter.colorchooser import askcolor

def apply_theme(root):
    root.configure(bg="#333")  # Dark background

    # Apply to all widgets
    for widget in root.winfo_children():
        if isinstance(widget, (tk.Button, tk.Label, tk.Entry, tk.Text)):
            widget.configure(bg="#444", fg="#ddd", relief=tk.FLAT)
        elif isinstance(widget, tk.Frame):
            widget.configure(bg="#333")

def choose_accent_color(root):
    color = askcolor()[1]
    if color:
        for widget in root.winfo_children():
            if isinstance(widget, tk.Button):
                widget.configure(bg=color)
