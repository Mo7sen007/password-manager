from setuptools import setup, find_packages

setup(
    name="password_manager",
    version="1.0.0",
    author="Mo7sen007",
    author_email="krombopulosmichael007@gmail.com",
    description="A secure password manager with encryption and clipboard support.",
    packages=find_packages(),
    install_requires=[
        "pyperclip",
        "cryptography",
        "tabulate",
        "bcrypt"
    ],
    entry_points={
        "console_scripts": [
            "password-manager=src.main:main"
        ]
    },
    python_requires=">=3.6",
)
