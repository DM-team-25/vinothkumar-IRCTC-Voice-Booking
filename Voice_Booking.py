import random
import speech_recognition as sr
from connect_mysql import get_connection

# -------- Voice helper -------- #
def listen_command(prompt):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(prompt)
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio).strip()
        print(f"You said: {text}")
        return text
    except:
        print("Could not understand. Please repeat.")
        return listen_command(prompt)

# -------- Passenger Booking -------- #
def passenger_booking(train_id):
    # Train ID validation
    if not (str(train_id).isdigit() and len(str(train_id)) == 5):
        print("Invalid Train ID. It must be exactly 5 digits.")
        return

    conn = get_connection()
    cursor = conn.cursor()

    # Get available coaches for train
    cursor.execute("""
        SELECT coach_code, seats_available 
        FROM coaches 
        WHERE train_id = %s
    """, (train_id,))
    coaches = cursor.fetchall()

    if not coaches:
        print("No coaches found for this train.")
        return

    print("\nAvailable Categories:")
    for coach in coaches:
        print(f"{coach[0]} - Seats Available: {coach[1]}")

    # 2️Voice choice
    coach_choice = listen_command("Please say the coach category (SL, A1, A2, B1, B2):").upper()

    valid_coaches = {c[0]: c[1] for c in coaches}
    if coach_choice not in valid_coaches:
        print("Invalid coach category.")
        return

    if valid_coaches[coach_choice] <= 0:
        print("No seats available in this coach.")
        return

    # Allocate seat
    seat_no = random.randint(1, valid_coaches[coach_choice])
    print(f"Seat Allocated: {seat_no} in {coach_choice} Coach.")

    # Reduce seat count
    cursor.execute("""
        UPDATE coaches 
        SET seats_available = seats_available - 1
        WHERE train_id = %s AND coach_code = %s
    """, (train_id, coach_choice))
    conn.commit()

    # Get passenger details
    passenger_type = listen_command("Say passenger type: Adult or Child:").capitalize()
    name = listen_command("Please say the passenger's full name:")
    age = listen_command("Please say the passenger's age:")
    gender = listen_command("Please say the passenger's gender (Male/Female/Other):").capitalize()

    #Validation
    if not name or not age.isdigit():
        print("Invalid passenger details. Booking failed.")
        return

    # Insert passenger record
    cursor.execute("""
        INSERT INTO Passengers (train_id, coach_code, seat_no, type, name, age, gender)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (train_id, coach_choice, seat_no, passenger_type, name, int(age), gender))
    conn.commit()

    # Confirm from DB
    cursor.execute("""
        SELECT * FROM Passengers 
        WHERE train_id=%s AND coach_code=%s AND seat_no=%s
    """, (train_id, coach_choice, seat_no))
    record = cursor.fetchone()

    if record:
        print("\nBooking Confirmed & Stored in Database!")
        print(f"Passenger: {name} | Age: {age} | Gender: {gender} | Type: {passenger_type}")
        print(f"Train ID: {train_id} | Coach: {coach_choice} | Seat No: {seat_no}")
    else:
        print("Booking failed to save in DB.")

    cursor.close()
    conn.close()


# -------- Run directly for testing -------- #
if __name__ == "__main__":
    # Prompt for Train ID when running directly
    train_id_input = input("Enter 5-digit Train ID: ")
    passenger_booking(train_id=train_id_input)
