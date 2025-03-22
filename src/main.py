from src import utils as ut
from src import storage
from src import authenticate as auth

config = storage.load_config()
PASSWORD_FILE = config["PASSWORD_FILE"]
KEY_FILE = config["KEY_FILE"]
def main():
    auth.login_register()
    """Command-line interface for the password manager."""
    while True:
        print("\n- Password Manager -")
        print("1. Enter a new password")
        print("2. Search for a password")
        print("3. View all passwords")
        print("4. Update a password")
        print("5. Delete a password")
        print("6. Exit")
        
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            credentials = ut.enter_password()
            if credentials:
                storage.save_password(*credentials, PASSWORD_FILE)
        elif choice == "2":
            search_name = input("Enter the name of the password you are looking for: ").strip()
            if search_name:
                ut.search_password(search_name, 1, 0, 1)
        elif choice == "3":
            ut.view_all()
        elif choice == "4":
            update_name = input("Enter the name of the password you want to update: ").strip()
            if update_name:
                ut.update_password(update_name)
        elif choice == "5":
            delete_name = input("Enter the name of the password you want to delete: ").strip()
            if delete_name:
                ut.delete_password(delete_name)
        elif choice == "6":
            print("Exiting password manager. Stay safe!")
            break
        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":
    main()