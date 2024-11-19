import json

settings_file = 'gpt_code_extractor_settings.json'
version_number = 1

def load_settings():
    global version_number
    try:
        with open(settings_file, 'r') as f:
            settings = json.load(f)
            version_number = settings.get('version_number', 1)
            return settings
    except (FileNotFoundError, json.JSONDecodeError):
        print("Settings file not found or corrupted, creating a new one.")
        save_settings({})
        return {}

def save_settings(settings):
    global version_number
    settings['version_number'] = version_number
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=4)
