from cryptography.fernet import Fernet
import os
import json

def get_config_path():
    """Returns the absolute path to the config file, ensuring cross-platform compatibility."""
    if os.name == "nt":  # Windows
        CONFIG_DIR = os.path.join(os.getenv("APPDATA"), "password-manager")
    else:  # Linux/macOS
        CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "password-manager")

    CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")


    os.makedirs(CONFIG_DIR, exist_ok=True)

    return CONFIG_PATH


def generate_key(KEY_FILE_PATH : str): 
    if not os.path.exists(KEY_FILE_PATH):
        key = Fernet.generate_key()
        with open(KEY_FILE_PATH, "wb") as key_file:
            key_file.write(key)
    print("Generated key!")

def load_key(KEY_FILE_PATH :str ) -> bytes | None:
    if not os.path.exists(KEY_FILE_PATH):
        print("Error: Can't find the KEY_FILE! Error code: 631xx")
        return None
    with open(KEY_FILE_PATH, "rb") as key_file:
        return key_file.read()

def encrypt_data(data : str, key : bytes) -> str:
    try:
        cipher = Fernet(key)
        encrypted_data = cipher.encrypt(data.encode()).decode()
        return encrypted_data
    except Exception as e:
        print(f"Error: Encryption failed: {e}, Error code: 632xx")
        return ""

def decrypt_data(encrypted_data : str, key: bytes) -> str:
    try:
        cipher = Fernet(key)
        decrypted_data = cipher.decrypt(encrypted_data.encode()).decode()
        return decrypted_data
    except Exception as e:
        print(f"Error: Decryption failed:{e}, Error code: 633xx")
        return ""