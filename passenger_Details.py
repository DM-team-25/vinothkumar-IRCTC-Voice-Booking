import speech_recognition as sr
from connect_mysql import get_connection

def listen_command(prompt):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(prompt)
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Sorry, I did not catch that. Please speak again.")
        return None
    except sr.RequestError:
        print("Speech service is down or unavailable.")
        return None

def get_passenger_details_and_store(train_id=None, coach_code=None, seat_no=None):
    """
    Collect passenger details via voice,
    then store them into Passengers table with optional train/coach/seat info.
    """

    name = None
    while not name:
        name = listen_command("Please say the passenger's full name:")

    age = None
    while not age:
        age_text = listen_command("Please say the passenger's age:")
        if age_text and age_text.isdigit():
            age = int(age_text)
        else:
            print("Please say a valid age in numbers.")

    gender = None
    while not gender:
        gender_text = listen_command("Please say the passenger's gender (male, female, other):")
        if gender_text:
            gender_lower = gender_text.lower()
            if gender_lower in ['male', 'female', 'other']:
                gender = gender_lower
            else:
                print("Please say male, female, or other.")

    payment_method = None
    while not payment_method:
        payment_text = listen_command("Please say the payment method (card, online):")
        if payment_text:
            payment_lower = payment_text.lower()
            if payment_lower in ['card', 'online']:
                payment_method = payment_lower
            else:
                print("Please say card or online.")

    passenger_info = {
        "name": name,
        "age": age,
        "gender": gender,
        "payment_method": payment_method
    }

    # Connect to DB and insert
    conn = get_connection()
    cursor = conn.cursor()

   
    insert_query = """
    INSERT INTO Passengers (train_id, coach_code, seat_no, name, age, gender, payment_method)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    try:
        cursor.execute(insert_query, (
            train_id,
            coach_code,
            seat_no,
            name,
            age,
            gender
        ))
        conn.commit()
        print("\nPassenger details stored in database successfully!")
    except Exception as error:
        print(f"\nError saving passenger details: {error}")
    finally:
        cursor.close()
        conn.close()

    return passenger_info

if __name__ == "__main__":
    # Example usage: you can pass train_id etc. if known; else None
    details = get_passenger_details_and_store(train_id=None, coach_code=None, seat_no=None)
    print("\nCollected Passenger Details:")
    for key, value in details.items():
        print(f"{key.capitalize()}: {value}")
