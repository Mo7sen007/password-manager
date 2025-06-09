import os
from random import choice
from src.backup import restore_key, restore_passwords
from src.storage import load_passwords, save_passwords,load_config,get_config_path
from src.encryption import decrypt_data, encrypt_data, load_key, generate_key
import json
from src.authenticate import register_user,login_register
 


def get_config_dir():
    """Get the fixed config directory based on the operating system."""
    if os.name == "nt":
        return os.path.join(os.getenv("APPDATA"), "password-manager")
    else:
        return os.path.join(os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config")), "password-manager")




def init_config():
    """Ensure the config file is always stored in the fixed directory."""
    
    print("initializing...")

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
    created_account = False
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
    else:

        with open(CONFIG_PATH, "w") as f:
            json.dump(config_data, f, indent=4)
        print("Config file created.")
        
    if not(os.path.exists(config_data["USER_CREDENTIALS_FILE"])):
        print("couldld not find user credentials ")
        login_register(config_data, USER_CREDENTIALS_PATH)
        created_account = True
    # Write new or updated config
    with open(CONFIG_PATH, "w") as config_file:
        json.dump(config_data, config_file, indent=4)
    return created_account
    
