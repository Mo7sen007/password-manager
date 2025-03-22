import bcrypt
import json
import os
import src.storage as st
CONFIG_PATH = "../data/config.json"

config = st.load_config()

USER_CREDENTIALS_FILE = config["USER_CREDENTIALS_FILE"]  # Path to store hashed passwords

def hash_password(password):
    """ Hash a password using bcrypt. """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed

def verify_password(password, hashed_password):
    """ Verify a password against the stored hash. """
    return bcrypt.checkpw(password.encode(), hashed_password)

def register_user(username, password):
    """ Register a new user and store the hashed password. """
    if os.path.exists(USER_CREDENTIALS_FILE):
        with open(USER_CREDENTIALS_FILE, "r") as file:
            users = json.load(file)
    else:
        users = {}

    if username in users:
        return False  # Username already exists

    users[username] = hash_password(password).decode()  # Store hash as string
    with open(USER_CREDENTIALS_FILE, "w") as file:
        json.dump(users, file)

    return True  # Registration successful

def authenticate_user(username, password):
    """ Authenticate a user by verifying their password. """
    if not os.path.exists(USER_CREDENTIALS_FILE):
        return False  # No users registered

    with open(USER_CREDENTIALS_FILE, "r") as file:
        users = json.load(file)

    if username not in users:
        return False  # User not found

    return verify_password(password, users[username].encode()) 

def login_register():
    print("Welcome to Password Manager!")
    if not os.path.exists(USER_CREDENTIALS_FILE):
        print("Make an account")
        username = input("Enter your username: ")
        password = input("Enter your master password: ")
        register_user(username, password)
    while True:
        username = input("Enter your username: ")
        password = input("Enter your master password: ")

        if authenticate_user(username, password):
            print("Login successful!")
            break  # Proceed to the main functionality of your password manager
        else:
            print("Invalid username or password. Try again.")