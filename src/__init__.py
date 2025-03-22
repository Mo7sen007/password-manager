import os
import json

def get_config_dir():
    """Get the fixed config directory based on the operating system."""
    if os.name == "nt":  # Windows
        return os.path.join(os.getenv("APPDATA"), "password-manager")
    else:  # Linux/macOS
        return os.path.join(os.path.expanduser("~"), ".config", "password-manager")

CONFIG_DIR = get_config_dir()
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
PASSWORD_PATH = os.path.join(CONFIG_DIR, "passwords.json")
KEY_PATH = os.path.join(CONFIG_DIR, "secret.key")
USER_CREDENTIALS_PATH = os.path.join(CONFIG_DIR, "user_credentials.json")

config_data = {
    "PASSWORD_FILE": PASSWORD_PATH,
    "KEY_FILE": KEY_PATH,
    "USER_CREDENTIALS_FILE": USER_CREDENTIALS_PATH
}

def init_config():
    """Ensure the config file is always stored in the fixed directory."""
    os.makedirs(CONFIG_DIR, exist_ok=True)

    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as config_file:
            try:
                existing_data = json.load(config_file)
            except json.JSONDecodeError:
                print("Warning: Config file is corrupted. Recreating it.")
                existing_data = {}

        if existing_data != config_data:
            print("Alert: Overwriting outdated config file.")

    # Write new or updated config
    with open(CONFIG_PATH, "w") as config_file:
        json.dump(config_data, config_file, indent=4)
    
    

init_config()
