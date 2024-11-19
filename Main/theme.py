import tkinter as tk  # Import tkinter to access widget types
from tkinter import colorchooser
from settings import save_settings

def apply_theme(app, accent_color="#3498db"):
    """Apply theme settings to the app and all widgets with the specified accent color."""
    bg_color = "#2e2e2e"
    fg_color = "#ffffff"
    app.configure(bg=bg_color)
    
    for widget in app.winfo_children():
        if isinstance(widget, (tk.Button, tk.Label, tk.Entry)):
            widget.configure(bg=bg_color, fg=fg_color)
        if isinstance(widget, tk.Button):
            widget.configure(bg=accent_color)

def choose_and_apply_accent_color(app, app_settings):
    """Choose a new accent color and apply it across the application."""
    color = colorchooser.askcolor(title="Choose Accent Color", initialcolor=app_settings.get("accent_color", "#3498db"))
    if color[1]:  # If a color was chosen
        app_settings['accent_color'] = color[1]
        save_settings(app_settings)
        apply_theme(app, color[1])
