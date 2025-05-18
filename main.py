import json
import os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet, InvalidToken
from base64 import b64encode, b64decode
from getpass import getpass

# user's master key
password = getpass("Enter a master key: ").encode()

def load_salt():
    with open("key.json", 'r') as f:
        data = json.load(f)
        if isinstance(data, dict) and 'salt' in data:
            return b64decode(salt_dict['salt'])
        elif isinstance(data, str):
                return b64decode(data)
        else:
            raise ValueError("Invalid key.json format")

if os.path.exists("key.json"):
    salt = load_salt()
else:
    salt = os.urandom(16)
    salt_b64 = b64encode(salt).decode('utf-8') # decode for json
    salt_dict = {
        'salt': salt_b64
    }
    with open("key.json", 'w') as f:
        json.dump(salt_dict, f)


kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100_000,
)

key = b64encode(kdf.derive(password))
fernet = Fernet(key)

def menu():
    print("=== PASSWORD VAULT ===")
    print("1. Add new credential")
    print("2. View all credentials")
    print("3. Delete a credential")
    print("4. Exit")


TASKS_FILE = "data.json"


def load_data():

    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_data(data):
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        return json.dump(data, f, indent=2)


def add_credentials(service, username, password):
    data = load_data() # data is a dict that stores password info
    new_data = {
        'id': max([d["id"] for d in data], default=0) + 1,
        'service': service,
        'username': username,
        'password': password
    }
    data.append(new_data)
    save_data(data)
    print("\n")


def show_credentials():
    data = load_data()

    if not data:
        print("No credentials found.\n")
        return

    for d in data:
        try:
            decrypted_password = fernet.decrypt(d['password'].encode()).decode()
        except InvalidToken:
             decrypted_password = "[Decryption failed: wrong master key?]"
        print(f"#{d['id']} Service: {d['service']}")
        print(f"   Username: {d['username']}")
        print(f"   Password: {decrypted_password}")
    print('\n')


def delete_credential(number):
    data = load_data()
    try:
        d_index = next(i for i, t in enumerate(data) if t['id'] == number)
    except StopIteration:
        return 'error'
    data.pop(d_index)
    save_data(data)


def main():
    while True:
        menu()
        try:
            choice = int(input("Choose an option: "))
        except Exception as e:
            print(f"Invalid choice, error code {e}")
        try:
            if choice == 1:
                service = str(input("Enter service name: "))
                username = str(input("Enter username: "))
                password = str(input("Enter password: "))
                add_credentials(service, username, fernet.encrypt(
                    password.encode()).decode())
                print(f"Credential added successfully!")
            elif choice == 2:
                show_credentials()
            elif choice == 3:
                number = int(input("Enter an id: "))
                result = delete_credential(number)
                if result == 'error':
                    print(f"Credential #{number} is not found!")
                else:
                    print(f"Credential #{number} deleted!")
            elif choice == 4:
                break
        except Exception as e:
            print(f"Error: {e}")


main()
