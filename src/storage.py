import json
import os
import shutil
from datetime import datetime
from src.encryption import encrypt_data, load_key, get_config_path

# Load configuration safely at import time
#try:
    #CONFIG_PATH = get_config_path()
    #with open(CONFIG_PATH, "r") as config_file:
        #config = json.load(config_file)
        #PASSWORD_FILE = config["PASSWORD_FILE"]
        #KEY_FILE = config["KEY_FILE"]
        #key = load_key(KEY_FILE)
#except Exception as e:
    #print(f"[WARNING] Failed to load config: {e}")
    #config = {}
    #PASSWORD_FILE = None
    #KEY_FILE = None
    #key = None

def load_config():
    """Loads the configuration file."""

    CONFIG_PATH = get_config_path()

    try:
        with open(CONFIG_PATH, "r") as config_file:
            return json.load(config_file)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def save_password(name, email, password, PASSWORD_FILE, key):
    """Saves a new password."""
    if not key or not PASSWORD_FILE:
        print("Error: Missing key or password file path.")
        return

    data = load_passwords(PASSWORD_FILE)
    encrypted_password = encrypt_data(password, key)
    for entry in data:
        if entry["name"].lower() == name.lower():
            print("A password with this name already exists!")
            return
    data.append({"name": name, "email": email, "password": encrypted_password})
    save_passwords(data, PASSWORD_FILE)
    print("Password saved successfully!")

def save_passwords(data, PASSWORD_FILE):
    """Saves passwords to the JSON file."""
    try:
        with open(PASSWORD_FILE, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error saving passwords: {e}")

def load_passwords(PASSWORD_FILE):
    """Loads passwords from the JSON file."""
    try:
        with open(PASSWORD_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
