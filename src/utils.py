import pyperclip
import re
import os
import copy as cp
from typing import List, Optional
from tabulate import tabulate
from random import choice
from string import ascii_letters, digits, punctuation
from src import authenticate as auth
from src.backup import restore_key, restore_passwords
from src.storage import load_passwords, save_passwords,load_config
from src.encryption import decrypt_data, encrypt_data, load_key, generate_key
 
config_file = load_config()
PASSWORD_FILE = config_file["PASSWORD_FILE"]
KEY_FILE = config_file["KEY_FILE"]
if KEY_FILE is None:
    print("Critical Error: Encryption key is missing. Exiting.")
    user_input = input("Creat new key (yes/no): ").strip()
    if user_input == "yes":
        generate_key(KEY_FILE)
def check_and_restore_files() -> None:
    """Checks if the key or password file is missing and asks the user if they want to restore them."""
    config = load_config()
    key_file = config["KEY_FILE"]
    password_file = config["PASSWORD_FILE"]

    missing_files = []

    if not os.path.exists(key_file):
        missing_files.append("key")

    if not os.path.exists(password_file):
        missing_files.append("passwords")

    if not missing_files:
        return  # Both files exist, no action needed

    print("Warning: The following files are missing:", ", ".join(missing_files))

    for file_type in missing_files:
        restore = input(f"Do you want to attempt restoring the {file_type} file? (yes/no): ").strip().lower()
        if restore == "yes":
            if file_type == "key":
                restored = restore_key()
            else:
                restored = restore_passwords()

            if restored:
                print(f"The {file_type} file has been successfully restored.")
            else:
                print(f"Failed to restore the {file_type} file.")

def password_generator(length : int) -> str:
    MAX_LENGTH = 30
    if length > MAX_LENGTH:
        length = MAX_LENGTH
        print("Can not exeed 30 character")
    password = "".join(choice(ascii_letters + digits + punctuation) for _ in range(length))
    if password:
        return password
    else:
        return "Error couldn't generate password"

def copy_to_clipboard(password : str) -> None :
    if password:
        pyperclip.copy(password)
        print("Password copied to clipboard!")
    else:
        print("Error couldn't copy password")
    return
    


def similarity_score(entry: str, name: str) -> int:
    entry = entry.lower()
    name = name.lower()
    if entry == name:
        return 10 # Score for exact match
    else:
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

def highlight_match(text: str, query: str, color: str) -> str:
    """Highlights the query in the text using the specified color (red, green, or blue)."""
    
    color_codes = {
        "red": "\033[1;31m",
        "green": "\033[1;32m",
        "blue": "\033[1;34m",
        "reset": "\033[0m"
    }

    if color not in color_codes:
        raise ValueError("Invalid color. Choose from 'red', 'green', or 'blue'.")

    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return pattern.sub(lambda m: f"{color_codes[color]}{m.group(0)}{color_codes['reset']}", text)


def add_password_number(table: list) -> list:
    for i in range(len(table)):
        table[i][0] = f"password n°{i+1}"
    return table

def enter_password() -> tuple[str, str, str] | None:
    """Prompts user to enter a new password."""
    name = input("Enter the name of the password: ").strip()
    email = input("Enter the email or username: ").strip()
    suggest_password = input("suggest a password (yes/no): ").strip()
    if suggest_password == "yes":
        length = 0
        while length == 0:
            length = int(input("Enter the length of the password: "))
            password = password_generator(length)
        print(f"Generated Password: {password}")
    else:
        password = input("Enter your password: ")

    if not name or not email or not password:
        print("Error: Name, email, and password cannot be empty.")
        return None

    return name, email, password

def search_password(name: str, display_result: int, redirect_result: int, copy: int) -> Optional[List[List[str]]]:
    """
    Searches for a password by name and performs actions based on user input.

    Args:
        name (str): The name to search for.
        display_result (int): If 1, displays results in a table.
        redirect_result (int): If 1, returns results for further processing.
        copy (int): If 1, allows user to copy a selected password.

    Returns:
        Optional[List[List[str]]]: Returns a list of password entries if `redirect_result` is set to 1, otherwise None.
    """
    key = load_key(KEY_FILE)
    stored_passwords = load_passwords(PASSWORD_FILE)
    
    password_matches = get_matching_passwords(stored_passwords, name, key)
    
    if not password_matches:
        print("No password found.")
        return None

    # Sort results by similarity (higher first)
    password_matches.sort(key=lambda x: x[4], reverse=True)
    password_matches = add_password_number(password_matches)

    # Remove similarity scores after sorting
    password_matches = [[r[0], r[1], r[2], r[3]] for r in password_matches]

    # Display results if required
    if display_result:
        display_results(password_matches, name)

    # Handle password copying
    if copy:
        password_number = get_valid_password_number(len(password_matches))
        if password_number >= 0:
            copy_selected_password(stored_passwords, password_matches, password_number)
        else:
            pass

    return password_matches if redirect_result else None

def get_matching_passwords(data: List[dict], name: str, key: bytes) -> List[List[str]]:
    """Finds passwords matching a given name with a similarity score above 0.4."""
    matches = []
    for entry in data:
        score = similarity_score(entry["name"], name)
        if score >= 0.4:
            decrypted_password = decrypt_data(entry["password"], key)
            matches.append(["", entry["name"], entry["email"], decrypted_password, score])
    return matches

def display_results(password_matches: List[List[str]], name: str):
    """Displays the found passwords in a formatted table with highlighted matches."""
    highlighted_results = cp.deepcopy(password_matches)
    for entry in highlighted_results:
        entry[1] = highlight_match(entry[1], name, color = "green")

    headers = ["Password Number", "Name", "Username", "Password"]
    print(f"Found {len(password_matches)} passwords")
    print("\n" + tabulate(highlighted_results, headers=headers, tablefmt="grid"))

def get_valid_password_number(max_index: int) -> int:
    """Prompts the user for a valid password selection."""
    while True:
        user_input = input("Enter the number you want to copy: ").strip()
        if user_input == "" :
            return -1
        if user_input.isdigit():
            password_number = int(user_input) - 1
            if 0 <= password_number < max_index:
                return password_number
            print("Invalid input, number is out of range.")
        else:
            print("Invalid input, please enter an integer.")

def copy_selected_password(data: List[dict], password_matches: List[List[str]], password_number: int):
    """Copies the selected password to the clipboard."""
    selected_entry = password_matches[password_number]
    for entry in data:
        if entry["name"] == selected_entry[1] and entry["email"] == selected_entry[2]:
            copy_to_clipboard(selected_entry[3])
            break

def update_password(account_name: str):
    """Updates an existing password entry."""
    
    key = load_key(KEY_FILE)
    passwords = load_passwords(PASSWORD_FILE)
    
    # Search for matching passwords
    matching_entries = search_password(account_name, display_result=1, redirect_result=1, copy=0)

    if not matching_entries:
        print("No password found to update.")
        return
    
    # Select a password entry to update
    entry_index = get_valid_password_index(matching_entries)
    if entry_index is None:
        return
    
    # Get new user inputs
    new_name = input("Enter new account name (leave empty to keep current): ").strip()
    new_username = input("Enter new username (leave empty to keep current): ").strip()
    new_password = get_new_password()

    # Update the selected entry in the database
    if update_entry_in_database(passwords, matching_entries[entry_index], new_name, new_username, new_password, key):
        print("Password updated successfully!")
    else:
        print("Couldn't update password.")


def get_valid_password_index(entries: list) -> int | None:
    """Prompts the user to select a valid password entry index."""
    
    while True:
        user_input = input("Enter the number of the password: ").strip()
        
        if not user_input.isdigit():
            print("Invalid input. Please enter a valid number.")
            continue
        
        index = int(user_input) - 1  # Convert to zero-based index
        if 0 <= index < len(entries):
            return index
        else:
            print("Error: Invalid password number. Please try again.")
    
    return None


def get_new_password() -> str:
    """Prompts the user for a new password or generates one."""
    
    choice = input("Generate a new password? (yes/no): ").strip().lower()
    
    if choice == "yes":
        while True:
            length = input("Enter the password length: ").strip()
            if length.isdigit() and int(length) > 0:
                new_password = password_generator(int(length))
                print(f"Generated Password: {new_password}")
                return new_password
            else:
                print("Invalid length. Enter a positive number.")
    
    return input("Enter the new password (leave empty to keep current): ").strip()


def update_entry_in_database(data: list, entry: list, new_name: str, new_username: str, new_password: str, key) -> bool:
    """Updates the selected password entry in the database and saves the changes."""
    
    for record in data:
        if record["name"] == entry[1] and record["email"] == entry[2]:
            if new_name:
                record["name"] = new_name
            if new_username:
                record["email"] = new_username
            if new_password:
                record["password"] = encrypt_data(new_password, key)

            # Ask if the user wants to copy the new password
            if new_password and input("Copy new password to clipboard? (yes/no): ").strip().lower() == "yes":
                copy_to_clipboard(new_password)

            save_passwords(data, PASSWORD_FILE)
            return True
    
    return False


def delete_password(account_name: str) -> None:
    """Deletes a saved password based on the user's selection."""
    
    matching_entries = search_password(account_name, display_result=1, redirect_result=1, copy=0)
    
    if not matching_entries:
        print("No password found to delete.")
        return

    # Get valid password selection
    entry_index = get_valid_password_index(matching_entries)
    if entry_index is None:
        return

    # Load passwords from the file
    data = load_passwords(PASSWORD_FILE)
    password_to_delete = matching_entries[entry_index][1]  # Extract the account name

    # Create a new list without the selected entry
    updated_data = [entry for entry in data if entry["name"] != password_to_delete]

    if len(updated_data) == len(data):
        print("Error: Password not found.")
    else:
        # Ask for confirmation before deleting
        confirm = input(f"Are you sure you want to delete '{highlight_match(password_to_delete,account_name, color = "red" )}'? (yes/no): ").strip().lower()
        if confirm == "yes":
            save_passwords(updated_data, PASSWORD_FILE)
            print("Password deleted successfully.")
        else:
            print("Deletion canceled.")


def view_all() -> None:
    """Displays all saved passwords."""
    
    key = load_key(KEY_FILE)
    data = load_passwords(PASSWORD_FILE)
    
    if not data:
        print("No passwords saved.")
        return

    print(f"\n- Found {len(data)} passwords -")
    
    results = [
        [f"Password {i+1}", entry["name"], entry["email"], decrypt_data(entry["password"], key)]
        for i, entry in enumerate(data)
    ]
    api_data = results.copy()
    headers = ["No.", "Account Name", "Username", "Password"]
    print("\n" + tabulate(results, headers=headers, tablefmt="grid"))
    return api_data
def compare_password_and_username(password: str, username: str, entry_email: str, entry_password:str, guessed_passwords: list) -> bool:
    """Check if email and password match while ensuring they haven't been guessed before."""
    return (
        entry_email == username
        and entry_password == password
        and password not in guessed_passwords
        and username not in guessed_passwords
    )

def restore() -> bool:
    """Restore account by verifying two known passwords before allowing user to reset credentials."""
    print("To restore your account, provide two known username-password pairs.")

    key = load_key(KEY_FILE)
    data = load_passwords(PASSWORD_FILE)
    verified = False
    passwords_guessed_correctly = 0
    guessed_passwords = []

    for _ in range(2):  # Allow two attempts to verify known passwords
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        if username in guessed_passwords and password in guessed_passwords:
            print("Can't enter the same usernaem and password twice!")
        for entry in data:
            decrypted_password = decrypt_data(entry["password"], key)
            if compare_password_and_username(password, username, entry["email"], decrypted_password, guessed_passwords):
                print("Correct")
                passwords_guessed_correctly += 1
                guessed_passwords.extend([username, password])  

        if passwords_guessed_correctly == 2:
            verified = True
            print("\nCreate a new account:")
            new_username = input("New Username: ").strip()
            new_password = input("New Master password: ").strip()
            auth.register_user(new_username, new_password)
            break  # Exit after successful restoration

    return verified

