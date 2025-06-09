import bcrypt
import json
import os
import getpass
import src.storage as st
from src.backup import backup_key

CONFIG_PATH = "../data/config.json"

try:
    config = st.load_config()
    USER_CREDENTIALS_FILE = config["USER_CREDENTIALS_FILE"]
except Exception as e:
    config = {}
    USER_CREDENTIALS_FILE = None
    print(f"Warning: Failed to load config — {e}")
print("debuging:")
print(USER_CREDENTIALS_FILE)
def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)

def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password)

def register_user(username: str, password: str):
    if not USER_CREDENTIALS_FILE:
        print("Configuration error: USER_CREDENTIALS_FILE not set")
        return False

    if os.path.exists(USER_CREDENTIALS_FILE):
        with open(USER_CREDENTIALS_FILE, "r") as file:
            users = json.load(file)
    else:
        users = {}

    if username in users:
        return False

    users[username] = hash_password(password).decode()
    with open(USER_CREDENTIALS_FILE, "w") as file:
        json.dump(users, file)

    if backup_key():
        print("Made backup of key")
    else:
        print("Warning: couldn't make backup of key")

    return True

def authenticate_user(username, password):
    if not USER_CREDENTIALS_FILE or not os.path.exists(USER_CREDENTIALS_FILE):
        return False

    with open(USER_CREDENTIALS_FILE, "r") as file:
        users = json.load(file)

    return username in users and verify_password(password, users[username].encode())

def login_register():
    print("Welcome to Password Manager!")
    key_file = config.get("KEY_FILE")
    if not USER_CREDENTIALS_FILE and not os.path.exists(key_file or ""):
        print("Create an account")
        username = input("Enter your username: ")
        password = getpass.getpass("Enter your master password: ")
        register_user(username, password)
    elif not USER_CREDENTIALS_FILE and os.path.exists(key_file):
        print("Error: couldn't find USER_CREDENTIALS_FILE")
        return 2

    attempts = 3
    while attempts > 0:
        username = input("Enter your username: ")
        password = getpass.getpass("Enter your master password: ")

        if authenticate_user(username, password):
            print("Login successful!")
            return 1
        else:
            print("Invalid username or password. Try again.")
            attempts -= 1
    return 3

def main():
    login_register()

if __name__ == "__main__":
    main()
