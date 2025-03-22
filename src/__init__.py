import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "..", "data", "config.json")
PASSWORD_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "passwords.json"))
KEY_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "secret.key"))
USER_CREDENTIALS_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "user_credentials.json"))

config_data = {
    "PASSWORD_FILE": PASSWORD_PATH,
    "KEY_FILE": KEY_PATH,
    "USER_CREDENTIALS_FILE": USER_CREDENTIALS_PATH
}

def init_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as config_file:
            try:
                existing_data = json.load(config_file)
            except json.JSONDecodeError:
                print("Warning: Config file is corrupted. Recreating it.")
                existing_data = {}

        if existing_data != config_data:
            print("Alert: Overwriting outdated config file!")
    
    with open(CONFIG_PATH, "w") as config_file:
        json.dump(config_data, config_file, indent=4)

init_config()