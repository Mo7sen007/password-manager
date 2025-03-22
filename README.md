# Password Manager v 1.3.1

A simple and secure password manager that allows users to store, encrypt, and retrieve their passwords safely.

## Features
- Securely store passwords using encryption
- Generate strong passwords
- Search and retrieve stored passwords
- Copy passwords to clipboard
- User authentication for added security

## Installation
### Prerequisites
Ensure you have Python installed on your system. You can download it from [python.org](https://www.python.org/).
Install xclip for Linux

### Clone the Repository
```sh
git clone https://github.com/Mo7sen007/password-manager.git
cd password-manager
```

### Install Dependencies
```sh
pip install .
```

## Usage
### Running the Application
```sh
password-manager
```

### Options
- **Add a Password**: Store a new password securely.
- **Retrieve a Password**: Search for a stored password.
- **Generate a Password**: Create a strong, random password.
- **Copy to Clipboard**: Copy a password without displaying it.

## Configuration
The application uses a `config.json` file to store settings. Ensure you configure it correctly before use.

## Security
- Passwords are encrypted using `cryptography.fernet`
- User authentication is required for access
- Sensitive data is stored securely in `data/`

## Contributing
1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Commit changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Open a pull request

## License
This project is licensed under the MIT License.

---
Developed by Amir

