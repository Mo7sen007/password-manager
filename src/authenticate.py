import bcrypt
import json
import os
import getpass
import src.storage as st
from src.backup import backup_key
from src.encryption import generate_key

def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)

def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password)

def register_user(username: str, password: str, USER_CREDENTIALS_FILE_PATH ):
    if not USER_CREDENTIALS_FILE_PATH:
        print("Configuration error: USER_CREDENTIALS_FILE not set")
        return False

    if os.path.exists(USER_CREDENTIALS_FILE_PATH):
        with open(USER_CREDENTIALS_FILE_PATH, "r") as file:
            users = json.load(file)
    else:
        users = {}

    if username in users:
        return False

    users[username] = hash_password(password).decode()
    with open(USER_CREDENTIALS_FILE_PATH, "w") as file:
        json.dump(users, file)

    if backup_key():
        print("Made backup of key")
    else:
        print("Warning: couldn't make backup of key")

    return True

def authenticate_user(username, password, USER_CREDENTIALS_FILE_PATH):
    if not USER_CREDENTIALS_FILE_PATH or not os.path.exists(USER_CREDENTIALS_FILE_PATH):
        return False

    with open(USER_CREDENTIALS_FILE_PATH, "r") as file:
        users = json.load(file)

    return username in users and verify_password(password, users[username].encode())

def login_register(config, USER_CREDENTIALS_FILE_PATH):
    key_file = config["KEY_FILE"]

    if not os.path.exists(USER_CREDENTIALS_FILE_PATH) and not os.path.exists(key_file):
        print("Create an account")
        username = input("Enter your username: ")
        password = getpass.getpass("Enter your master password: ")
        
        generate_key(key_file)

        register_user(username, password, USER_CREDENTIALS_FILE_PATH)
    elif not os.path.exists(USER_CREDENTIALS_FILE_PATH) and os.path.exists(key_file):
        print("Error: couldn't find USER_CREDENTIALS_FILE")
        return 2

    attempts = 3
    while attempts > 0:
        username = input("Enter your username: ")
        password = getpass.getpass("Enter your master password: ")

        if authenticate_user(username, password, USER_CREDENTIALS_FILE_PATH):
            print("Login successful!")
            return 1
        else:
            print("Invalid username or password. Try again.")
            attempts -= 1
    return 3