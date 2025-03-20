import pyperclip
import argparse
import re
import json
from tabulate import tabulate
from random import choice
from string import ascii_letters, digits, punctuation
from storage import load_passwords, save_password, save_passwords
from encryption import decrypt_data, encrypt_data, load_key
 
config_path = "../data/config.json"

with open(config_path, "r") as config:
    config = json.load(config)
    PASSWORD_FILE = config["PASSWORD_FILE"]
    KEY_FILE = config["KEY_FILE"]

def password_generator(length):
    """Generates a random password with the specified criteria."""

    password = "".join(choice(ascii_letters + digits + punctuation) for _ in range(length))
    return password

def copy_to_clipboard(password):
    pyperclip.copy(password)
    print("Password copied to clipboard!")


def similarity_score(entry: str, name: str) -> int:
    """Calculates a similarity score based on common letters and order."""
    entry = entry.lower()
    name = name.lower()
    score = 0
    match_count = 0
    last_index = -1  # To track character order

    for char in name:
        index = entry.find(char, last_index + 1)  # Search after last found position
        if index != -1:
            match_count += 1 if index == last_index + 1 else 0.5  # Consecutive chars get higher score
            last_index = index
    if match_count == 0 :
        return 0
    else:
        score = match_count / len(name) 
        return score

def highlight_match(text: str, query: str) -> str:
    """Highlight the matching part of the name in green for better visibility."""
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return pattern.sub(lambda m: f"\033[1;32m{m.group(0)}\033[0m", text)
def add_password_number(table):
    for i in range(len(table)):
        table[i][0] = f"password n°{i+1}"
    return table

def enter_password():
    """Prompts user to enter a new password."""
    name = input("Enter the name of the password: ").strip()
    email = input("Enter the email or username: ").strip()
    suugest_password = input("suggest a password (yes/no): ").strip()
    if suugest_password == "yes":
        length = 0
        while length == 0:
            length = int(input("Enter the length of the password: "))
            password = password_generator(length)
        print(f"Generated Password: {password}")
    else:
        password = input("Enter your password: ").strip()

    if not name or not email or not password:
        print("Error: Name, email, and password cannot be empty.")
        return None

    return name, email, password

def search_password(name, display_result, redirect_result, copy):
    """Searches for a password by name with ranking."""
    key = load_key(KEY_FILE)
    data = load_passwords(PASSWORD_FILE)
    results = []
    found_passwords = 0
    for entry in data:
        if entry["name"] == name:
            score = 10
        else:
            score = similarity_score(entry["name"], name)
        if score >= 0.4:
            found_passwords += 1
            decrypted_password = decrypt_data(entry["password"],key)
            results.append(["", highlight_match(entry["name"], name), entry["email"], decrypted_password, score])

    if display_result == 1:
        if results:
            # Sort by best similarity score (higher is better)
            results.sort(key=lambda x: x[4], reverse=True)
            results = add_password_number(results)
            results = [[r[0], r[1], r[2], r[3]] for r in results]  # Keep all columns
            headers = ["password number", "Name", "Username", "Password"]
            redirected = results
            print(f"Found {len(results)} passwords")
            print("\n" + tabulate(results, headers=headers, tablefmt="grid"))
            if copy == 1:
                while True:
                    copy_password = input("Enter the number that you want it to be copied: ").strip()
                    if copy_password.isdigit():
                        copy_password = int(copy_password) - 1
                        if copy_password < 0 or copy_password > len(results):
                            print("Invalid input, number is out of range")
                        else:
                            break
                    else:
                        print("Invalid input, number must be an integer")
                for entry in data:
                    if highlight_match(entry["name"],name) == results[copy_password][1] and entry["email"] == results[copy_password][2]:
                        copy_to_clipboard(decrypt_data(entry['password'], key))

        else:
            print("No password found.")
    if redirect_result == 1:
        #if results:
            #results.sort(key=lambda x: x[4], reverse=True)
            #results = [[r[0], r[1], r[2], r[3]] for r in results]
        return results


def update_password(name):
    """Updates a password by name."""
    key = load_key(KEY_FILE)
    password_upadted = False
    data = load_passwords(PASSWORD_FILE)
    results = search_password(name, 1, 1, 0)

    if not results:
        print("No password found to update.")
        return
    while True:
        id_password = input("Number of password that you want to change: ") 
        if id_password.isdigit():
            id_password = (int(id_password)) - 1 # Convert to zero-based index
            break
        print("Invalid input, try again")
    if id_password < 0 or id_password >= len(results):
        print("Error: Invalid password number.")
        return
    new_name = input("Enter new name:  ").strip()
    new_username = input("Enter new user name: ").strip()
    generat_new_password =  input("Suggest a new password?(yes or no)")
    if generat_new_password == "yes":
        length = 0
        while length == 0:
            length = int(input("Enter the length of the password: "))
            new_password = password_generator(length)
        print(f"Generated Password: {new_password}")
    else:
        new_password = input("Enter the new password: ").strip()
    
    # Update the password in the original data
    for entry in data:
        if highlight_match(entry["name"],name) == results[id_password][1] and entry["email"] == results[id_password][2]:
            password_upadted = True
            if new_name:
                entry["name"] = new_name
            if new_username:
                entry["email"] = new_username  # Correct field update
            if new_password:
                entry["password"] = encrypt_data(new_password,key)
            copy_password = input("copy new password(yes/no)")
            if copy_password != "no":
                copy_to_clipboard(decrypt_data(entry['password'], key)) 
            break 

    save_passwords(data,PASSWORD_FILE)
    if password_upadted:
        print("Password updated successfully!")
    else:
        print("Couldn't save password")


def delete_password(name):
    """Deletes a password by name with confirmation."""
    results = search_password(name, 1, 1, 0)
    
    while True:
        id_password = input("Number of password that you want to delete: ") 
        if id_password.isdigit():
            id_password = (int(id_password)) - 1 # Convert to zero-based index
            break
        print("Invalid input, try again")
    if id_password < 0 or id_password >= len(results):
        print("Error: Invalid password number.")
        return
    data = load_passwords(PASSWORD_FILE)
    password_to_delete = results[id_password][1]  # Get the name of the password to delete
    # Create a new list excluding the selected password
    new_data = [entry for entry in data if highlight_match(entry["name"],name) != password_to_delete]
    if len(new_data) == len(data):
        print("Password not found.")
    else:
        confirm = input(f"Are you sure you want to delete '{password_to_delete}'? (yes/no): ").strip()
        if confirm == "yes":
            save_passwords(new_data, PASSWORD_FILE)
            print("Password deleted successfully.")
        else:
            print("Deletion canceled.")

def view_all():
    """Displays all saved passwords."""
    key = load_key(KEY_FILE)
    results = []
    data = load_passwords(PASSWORD_FILE)
    if not data:
        print("No passwords saved.")
        return

    print(f"\n-Found {len(data)} passwords-")
    for i, entry in enumerate(data, start=1):
        decrypted_password = decrypt_data(entry['password'], key)
        results.append([f"Password {i}",entry["name"], entry["email"], decrypted_password])
    if results:
        headers = ["Nb","Name", "Username", "Password"]
        print("\n"+tabulate(results, headers=headers, tablefmt="grid"))


def authentication():
    attemps = 0
    MASTER_KEY = '1'
    authenticated = False
    print("Welcome to password manager ")
    master_key = ""
    while master_key != MASTER_KEY and authenticated == False:
        master_key = input("Master password:")
        if master_key == MASTER_KEY:
            authenticated = True
            return authenticated
        attemps = attemps + 1
        if attemps == 3:
            print("Too many failed attempts")
            break