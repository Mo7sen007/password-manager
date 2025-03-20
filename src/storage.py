import json
from encryption import encrypt_data
from encryption import load_key

CONFIG_PATH = "../data/config.json"

def load_config():
    with open(CONFIG_PATH, "r") as config:
        return json.load(config)

config = load_config()

PASSWORD_FILE = config["PASSWORD_FILE"]
KEY_FILE = config["KEY_FILE"]


key = load_key(KEY_FILE)

def save_password(name, email, password, PASSWORD_FILE):
    """Saves a new password."""
    data = load_passwords(PASSWORD_FILE)
    encrypted_password = encrypt_data(password, key)
    for entry in data:
        if entry["name"].lower() == name.lower():
            print("A password with this name already exists!")
            return
    data.append({"name": name, "email": email, "password": encrypted_password})
    save_passwords(data,PASSWORD_FILE)
    print("Password saved successfully!")


def save_passwords(data, PASSWORD_FILE):
    """Saves passwords to the JSON file."""
    with open(PASSWORD_FILE, "w") as file:
        json.dump(data, file, indent=4)

def load_passwords(PASSWORD_FILE):
    """Loads passwords from the JSON file."""
    try:
        with open(PASSWORD_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []