
import json
import os


# Define the expected default settings structure
default_settings = {
    "Settings": {
        "Brands": {
            "HP": None,
            "Lenovo": None,
            "Dell": None,
            "Fujitsu": None,
            "Surface": None
        },
        "Types": {
            "Mini": None,
            "SFF": None,
            "Tower": None,
            "Laptop": None
        },
        "WindowsVersions": {
            "Windows 10 Home": None,
            "Windows 10 Pro": None,
            "Windows 11 Home": None,
            "Windows 11 Pro": None
        },
        "Location":{
            "E:/": None
        }
    }
}

settings_file = "settings.json"

#files path 
db_file = os.path.join(os.getcwd(), "database/local_database.json")
settings_file = os.path.join(os.getcwd(), "settings.json")

def load_settings_data():
    """Load settings from the settings.json file or create it if missing."""
    if not os.path.exists(settings_file):
        # Create the settings file with default structure if it doesn't exist
        with open(settings_file, "w") as file:
            json.dump(default_settings, file, indent=4)
        return default_settings
    
    try:
        # Read and return the file content
        with open(settings_file, "r") as file:
            data = json.load(file)
            # Ensure the loaded data is valid
            if not isinstance(data, dict) or "Settings" not in data:
                raise json.JSONDecodeError("Invalid format", settings_file, 0)
            return data
    except (json.JSONDecodeError, FileNotFoundError):
        # Restore default settings if file is corrupted or unreadable
        with open(settings_file, "w") as file:
            json.dump(default_settings, file, indent=4)
        return default_settings
    
def load_db():
    if not os.path.exists(db_file):
        with open(db_file, "w") as file:
            json.dump({}, file)
    with open(db_file, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}

def save_db(data):
    with open(db_file, "w") as file:
        json.dump(data, file, indent=4)

