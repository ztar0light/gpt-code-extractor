from tkinter import simpledialog
from settings import save_settings

tabs_data = {}

def add_project_tab(tab_control):
    tab_name = simpledialog.askstring("Tab Name", "Enter a name for the new project tab:")
    if tab_name:
        tab = ttk.Frame(tab_control)
        tab_control.add(tab, text=tab_name)
        tabs_data[tab_name] = {}
        tab_control.select(tab)

def switch_project_tab(event):
    current_tab = event.widget.tab(event.widget.select(), "text")
    if current_tab:
        save_tab_data(current_tab)

def save_tab_data(tab_name):
    # Custom save logic
    pass
