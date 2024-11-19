import shelve
import os

settings_file = os.path.join(os.path.dirname(__file__), 'app_settings')

default_settings = {
    'version_number': 1,
    'accent_color': "#3498db",
    'tabs_data': {},
    'macros': []
}

def load_settings():
    with shelve.open(settings_file) as db:
        return {key: db.get(key, default_settings[key]) for key in default_settings}

def save_settings(settings):
    with shelve.open(settings_file, writeback=True) as db:
        for key, value in settings.items():
            db[key] = value
