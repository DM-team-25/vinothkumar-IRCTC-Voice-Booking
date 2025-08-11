import random
import speech_recognition as sr
import re
from V_IRCTC import get_connection

# Voice input helper and voice search function
def get_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Please say your search query...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text.lower()
    except sr.UnknownValueError:
        print("Sorry, I could not understand the audio.")
    except sr.RequestError:
        print("Could not request results from the speech service.")
    return None

def voice_search():
    query = get_voice_input()
    if not query:
        return

    if "pnr" in query:
        pnr_numbers = re.findall(r'\d+', query)
        if pnr_numbers:
            search_by_pnr(pnr_numbers[0])
        else:
            print("No PNR number detected in your voice input.")
    elif "from" in query and "to" in query:
        parts = query.split()
        try:
            from_index = parts.index("from")
            to_index = parts.index("to")
            source = parts[from_index + 1]
            dest = parts[to_index + 1]
            search_by_route(source, dest)
        except (ValueError, IndexError):
            print("Could not parse source and destination from your voice input.")
    else:
        search_by_name(query)

# Your train selection and coach selection functions
def prompt_train_selection(trains):
    """
    If multiple trains found, prompt user to pick one by ID.
    If one train found, select it automatically.
    """
    if not trains:
        print("No trains found.")
        return None

    if len(trains) == 1:
        train = trains[0]
        print(f"\nOne train found: {train[1]} ({train[0]})")
        return train

    # Multiple trains found - show list and ask for selection
    print(f"\nMultiple trains found. Please select one:")
    print(f"{'Train ID':<10} {'Train Name':<40} {'From':<20} {'To':<20} {'Start':<10} {'Arrival':<10}")
    print("-" * 120)
    for t in trains:
        print(f"{t[0]:<10} {t[1]:<40} {t[2]:<20} {t[3]:<20} {str(t[4]):<10} {str(t[5]):<10}")

    while True:
        selected_id = input("\nEnter Train ID to select your train: ").strip()
        for t in trains:
            if str(t[0]) == selected_id:
                return t
        print("Invalid Train ID. Please try again.")

def select_coach_for_train(train):
    coach_config = {
        "SL": {"count": 10, "seat_count": 60, "price_range": (300, 500)},
        "A1": {"count": 2, "seat_count": 60, "price_range": (800, 1500)},
        "A2": {"count": 2, "seat_count": 60, "price_range": (800, 1500)},
        "B1": {"count": 2, "seat_count": 60, "price_range": (800, 1500)},
        "B2": {"count": 2, "seat_count": 60, "price_range": (800, 1500)},
    }

    print("\nAvailable Coach Types:")
    for ctype in coach_config.keys():
        print(f" - {ctype}")

    while True:
        selected_coach = input("Select your coach type (e.g., SL, A1, A2): ").strip().upper()
        if selected_coach in coach_config:
            break
        print("Invalid coach type selected. Please try again.")

    info = coach_config[selected_coach]
    total_seats = info["count"] * info["seat_count"]
    seat_price = random.randint(info['price_range'][0], info['price_range'][1])

    # Randomly allocate seat number from total seats
    seat_number = random.randint(1, total_seats)
    seats_per_coach = info["seat_count"]

    coach_number = (seat_number - 1) // seats_per_coach + 1
    seat_in_coach = (seat_number - 1) % seats_per_coach + 1

    seat_label = f"{selected_coach}{coach_number}-{seat_in_coach}"

    print(f"\nYou selected coach: {selected_coach}")
    print(f"Number of coaches: {info['count']}")
    print(f"Seats per coach: {seats_per_coach}")
    print(f"Total seats in this coach type: {total_seats}")
    print(f"Randomly allocated price per seat: ₹{seat_price}")
    print(f"Your allocated seat is: {seat_label}")

    print(f"\nBooking summary: Train '{train[1]}' ({train[0]}) with coach {selected_coach}, seat {seat_label} at price ₹{seat_price}")

    return selected_coach, seat_price, seat_label


# Search functions updated to auto prompt coach selection after train selection
def search_by_pnr(pnr=None):
    if pnr is None:
        pnr = input("Enter PNR (Train ID): ").strip()
    
    if not pnr.isdigit() or len(pnr) != 5:
        print("\nInvalid PNR number. Must be exactly 5 digits.\n")
        return

    conn = get_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM TrainDetails WHERE train_id = %s", (pnr,))
        trains = cursor.fetchall()

    train = prompt_train_selection(trains)
    if train:
        select_coach_for_train(train)

def search_by_name(name=None):
    if name is None:
        name = input("Enter Train Name: ").strip()
    if not name:
        print("\nInvalid train name. Please enter a valid name.\n")
        return

    conn = get_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM TrainDetails WHERE train_name LIKE %s", (f"%{name}%",))
        trains = cursor.fetchall()

    train = prompt_train_selection(trains)
    if train:
        select_coach_for_train(train)

def search_by_route(source=None, dest=None):
    if source is None:
        source = input("Enter Source Station: ").strip()
    if dest is None:
        dest = input("Enter Destination Station: ").strip()

    if not source or not dest:
        print("\nPlease enter both source and destination stations.\n")
        return

    conn = get_connection()
    with conn:
        cursor = conn.cursor()
        query = """
            SELECT * FROM TrainDetails
            WHERE source_station LIKE %s AND destination_station LIKE %s
        """
        cursor.execute(query, (f"%{source}%", f"%{dest}%"))
        trains = cursor.fetchall()

    train = prompt_train_selection(trains)
    if train:
        select_coach_for_train(train)

def show_all_trains():
    conn = get_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM TrainDetails ORDER BY train_name")
        trains = cursor.fetchall()

    train = prompt_train_selection(trains)
    if train:
        select_coach_for_train(train)

# Main menu with voice search included
def main():
    print("=== Train Search System ===")
    while True:
        print("\nTrain Search Menu:")
        print("1. Search by PNR (Train ID)")
        print("2. Search by Train Name")
        print("3. Search by Source and Destination (Route)")
        print("4. Voice Search")
        print("5. Show All Trains")
        print("6. Exit")

        choice = input("Enter choice: ")

        if choice == '1':
            search_by_pnr()
        elif choice == '2':
            search_by_name()
        elif choice == '3':
            search_by_route()
        elif choice == '4':
            voice_search()
        elif choice == '5':
            show_all_trains()
        elif choice == '6':
            print("Exiting Train Search. Goodbye!")
            break
        else:
            print("\nInvalid choice. Please try again.\n")

if __name__ == "__main__":
    main()
