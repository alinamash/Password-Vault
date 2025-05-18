import json
import os
from cryptography.fernet import Fernet

key = Fernet.generate_key()

with open("key.key", "wb") as key_file:
    key_file.write(key)
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
    data = load_data()
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
        print(f"#{d['id']} Service: {d['service']}")
        print(f"   Username: {d['username']}")
        print(f"   Password: {fernet.decrypt(d['password']).decode()}")
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
