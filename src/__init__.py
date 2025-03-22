import os
import json

# Store `data/` in the working directory
BASE_DIR = os.getcwd()
DATA_DIR = os.path.join(BASE_DIR, "data")
CONFIG_PATH = os.path.join(DATA_DIR, "config.json")
PASSWORD_PATH = os.path.join(DATA_DIR, "passwords.json")
KEY_PATH = os.path.join(DATA_DIR, "secret.key")
USER_CREDENTIALS_PATH = os.path.join(DATA_DIR, "user_credentials.json")

config_data = {
    "PASSWORD_FILE": PASSWORD_PATH,
    "KEY_FILE": KEY_PATH,
    "USER_CREDENTIALS_FILE": USER_CREDENTIALS_PATH
}

def init_config():
    os.makedirs(DATA_DIR, exist_ok=True) 

    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as config_file:
            try:
                existing_data = json.load(config_file)
            except json.JSONDecodeError:
                print("⚠️ Warning: Config file is corrupted. Recreating it.")
                existing_data = {}

        if existing_data != config_data:
            print("⚠️ Alert: Overwriting outdated config file!")

    # ✅ Write new or updated config
    with open(CONFIG_PATH, "w") as config_file:
        json.dump(config_data, config_file, indent=4)
    
    print(f"✅ Config file saved at {CONFIG_PATH}")

# Run when the app starts
init_config()
