from cryptography.fernet import Fernet
import os
import json


def get_config_path():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(BASE_DIR, "..", "data", "config.json")
    config_path = os.path.abspath(config_path)
    return config_path

config_path = get_config_path()

with open(config_path, "r") as config:
    config = json.load(config)
    KEY_FILE = config["KEY_FILE"]

if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)

def generate_key(KEY_FILE : str): 
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)

def load_key(KEY_FILE :str ) -> bytes:
    with open(KEY_FILE, "rb") as key_file:
        return key_file.read()

def encrypt_data(data : str, key : bytes) -> str:
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(data.encode()).decode()
    return encrypted_data

def decrypt_data(encrypted_data : str, key: bytes) -> str:
    cipher = Fernet(key)
    decrypted_data = cipher.decrypt(encrypted_data.encode()).decode()
    return decrypted_data
