import sys
import os

# Add current script directory to sys.path to help with imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from V_IRCTC import main as user_main
from Train_details import main as train_main
from Voice_Booking import passenger_booking
from passenger_Details import get_passenger_details_and_store

def main():
    print("=== IRCTC Main System ===")

    logged_in = False

    while True:
        print("\nMain Menu:")
        print("1. User Management (Register, Login, Update, Delete)")
        print("2. Train Details")
        print("3. Voice Ticket Booking")
        print("4. Exit")

        choice = input("Enter choice: ")

        if choice == '1':
            logged_in = user_main()
        elif choice == '2':
            train_main()
        elif choice == '3':
            if not logged_in:
                print("Please login first via User Management (option 1).")
                continue

            train_id = input("Enter 5-digit Train ID to book: ").strip()

            # Get passenger details (name, age, gender, payment, etc.) and store in DB
            details = get_passenger_details_and_store(train_id=train_id)

            print("\nCollected Passenger Details:")
            for key, value in details.items():
                print(f"{key.capitalize()}: {value}")

            print("\nProcessing booking...")
            passenger_booking(train_id, details)  # This prints booking confirmation & seat info

        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
