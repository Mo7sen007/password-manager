import threading
import time
import os
import json
from src.storage import load_config, load_passwords, save_passwords

def restore_key() -> bool:
    """Restores the key file from the backup."""
    config = load_config()
    key_file = config["KEY_FILE"]

    backup_dir = os.path.join(os.path.dirname(key_file), "backups")
    backup_path = os.path.join(backup_dir, "key_backup")

    if not os.path.exists(backup_path):
        print("No backup key file found.")
        return False

    if os.path.exists(key_file):
        confirm = input("A key file already exists. Overwrite it? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Restore canceled.")
            return False

    with open(backup_path, "rb") as backup_file:
        key_data = backup_file.read()

    with open(key_file, "wb") as key_file_obj:
        key_file_obj.write(key_data)

    print("Key file restored successfully.")
    return True

def backup_key() -> bool:
    """Creates a backup of the key file and verifies it."""
    config = load_config()
    key_file = config["KEY_FILE"]

    backup_dir = os.path.join(os.path.dirname(key_file), "backups")
    os.makedirs(backup_dir, exist_ok=True)

    with open(key_file, "rb") as file:
        key = file.read()

    backup_path = os.path.join(backup_dir, "key_backup")

    with open(backup_path, "wb") as backup_file:
        backup_file.write(key)

    with open(backup_path, "rb") as backup_file:
        backup_key = backup_file.read()

    return bool(backup_key)


def restore_passwords() -> bool:
    """Restores passwords from the backup file."""
    config = load_config()
    password_file = config["PASSWORD_FILE"]

    backup_dir = os.path.join(os.path.dirname(password_file), "backups")
    backup_path = os.path.join(backup_dir, "passwords_backup.json")

    # Check if backup exists
    if not os.path.exists(backup_path):
        print("No password backup found!")
        return False

    # Read backup file
    try:
        with open(backup_path, "r") as backup_file:
            backup_data = json.load(backup_file)
    except json.JSONDecodeError:
        print("Backup file is corrupted!")
        return False

    # Confirm before overwriting existing passwords
    if os.path.exists(password_file):
        confirm = input("A password file already exists. Overwrite it? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Restore canceled.")
            return False

    # Save restored passwords
    save_passwords(backup_data, password_file)
    print("Passwords restored successfully!")
    return True

def backup_passwords() -> None:
    """Creates a backup of the password file."""
    config = load_config()
    password_file = config["PASSWORD_FILE"]
    backup_dir = os.path.join(os.path.dirname(password_file), "backups")

    os.makedirs(backup_dir, exist_ok=True)

    # Load password data
    passwords = load_passwords(password_file)

    backup_path = os.path.join(backup_dir, "passwords_backup.json")

    with open(backup_path, "w") as backup_file:
        json.dump(passwords, backup_file, indent=4)

    print(f"Backup saved: {backup_path}")



def auto_backup(interval:int=86400) -> None:  # 1 day
    """Runs the backup function at a fixed interval in the background."""
    while True:
        print("Creating automatic backup...")
        backup_passwords()
        print("Backup completed!")
        time.sleep(interval)

def start_auto_backup(interval:int=3600)->None:
    backup_passwords()
    backup_thread = threading.Thread(target=auto_backup, args=(interval,), daemon=True)
    backup_thread.start()
    print(f"Auto-backup running every {interval} seconds...")
