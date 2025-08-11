import re
import bcrypt
from connect_mysql import get_connection

def validate_username(username):
    return re.fullmatch(r'^[A-Za-z0-9_]{4,20}$', username)

def validate_password(password):
    return (len(password) >= 8 and
            re.search(r'[A-Z]', password) and
            re.search(r'[a-z]', password) and
            re.search(r'\d', password) and
            re.search(r'[@#$%&]', password))

def validate_email(email):
    return re.fullmatch(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', email)

def validate_phone(phone):
    return re.fullmatch(r'^[6-9]\d{9}$', phone)

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_username_exists(username):
    conn = get_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        return cursor.fetchone() is not None

def check_email_exists(email):
    conn = get_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        return cursor.fetchone() is not None

def check_phone_exists(phone):
    conn = get_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE phone = %s", (phone,))
        return cursor.fetchone() is not None

def register_user():
    print("\n--- Register New Account ---")
    while True:
        username = input("Enter username: ")
        if not validate_username(username):
            print("Invalid username format.")
            continue
        if check_username_exists(username):
            print("Username already exists.")
            continue
        break

    while True:
        password = input("Enter password: ")
        if not validate_password(password):
            print("Weak password. Must include uppercase, lowercase, digit, and special character.")
            continue
        break

    while True:
        email = input("Enter Gmail: ")
        if not validate_email(email):
            print("Invalid Gmail format or domain.")
            continue
        if check_email_exists(email):
            print("Email already exists.")
            continue
        break

    while True:
        phone = input("Enter 10-digit phone number: ")
        if not validate_phone(phone):
            print("Invalid phone format.")
            continue
        if check_phone_exists(phone):
            print("Phone number already exists.")
            continue
        break

    password_hash = hash_password(password)

    conn = get_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password_hash, email, phone) VALUES (%s, %s, %s, %s)",
            (username, password_hash, email, phone)
        )
        conn.commit()
        print("Registration successful!\nWelcome to IRCTC, Happy Journey!")

def login_user():
    print("\n--- Login ---")
    username = input("Enter username: ")
    password = input("Enter password: ")

    conn = get_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
        row = cursor.fetchone()
        if not row:
            print("Username not found.")
            return False
        stored_hash = row[0]
        if bcrypt.checkpw(password.encode(), stored_hash.encode()):
            print(f"Hello, {username}! Login successful.")
            return True
        else:
            print("Incorrect password.")
            return False

def update_user():
    print("\n--- Update Account ---")
    username = input("Enter your username to update: ")

    conn = get_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if not cursor.fetchone():
            print("User not found.")
            return

        new_email = input("Enter new Gmail: ")
        if not validate_email(new_email):
            print("Invalid Gmail.")
            return

        new_phone = input("Enter new phone number: ")
        if not validate_phone(new_phone):
            print("Invalid phone number.")
            return

        cursor.execute("UPDATE users SET email = %s, phone = %s WHERE username = %s",
                       (new_email, new_phone, username))
        conn.commit()
        print("Account updated successfully.")

def delete_user():
    print("\n--- Delete Account ---")
    username = input("Enter username: ")
    password = input("Enter password: ")

    conn = get_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
        row = cursor.fetchone()
        if not row:
            print("User not found.")
            return

        if not bcrypt.checkpw(password.encode(), row[0].encode()):
            print("Incorrect password.")
            return

        cursor.execute("DELETE FROM users WHERE username = %s", (username,))
        conn.commit()
        print("Account deleted successfully.")
        
def main():
    print("=== Welcome to IRCTC ===")
    while True:
        print("\nUser Details:")
        print("1. REGISTER NEW ACCOUNT")
        print("2. LOGIN USER ACCOUNT")
        print("3. UPDATE YOUR ACCOUNT")
        print("4. DELETE YOUR ACCOUNT")
        print("5. EXIT")
        choice = input("Enter choice: ")

        if choice == '1':
            register_user()
        elif choice == '2':
            return login_user()  # returns True or False to main.py
        elif choice == '3':
            update_user()
        elif choice == '4':
            delete_user()
        elif choice == '5':
            print("Goodbye!")
            return None
        else:
            print("Invalid choice.")