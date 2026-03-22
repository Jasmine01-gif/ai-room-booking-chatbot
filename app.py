from flask import Flask, request, jsonify, render_template, redirect, url_for
import pickle
import sqlite3
import spacy
from datetime import datetime, timedelta

app = Flask(__name__)

# Load ML model
model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

# Load NLP model
nlp = spacy.load("en_core_web_sm")


# -------- INTENT PREDICTION --------
def predict_intent(message):
    X = vectorizer.transform([message])
    return model.predict(X)[0]


# -------- EXTRACT BOOKING DETAILS --------
def extract_booking_details(text):

    doc = nlp(text)

    date = None
    time = None
    room = None

    text_lower = text.lower()

    # spaCy entity detection
    for ent in doc.ents:
        if ent.label_ == "DATE":
            date = ent.text
        elif ent.label_ == "TIME":
            time = ent.text

    # manual support for today/tomorrow
    if "tomorrow" in text_lower:
        date = "tomorrow"
    elif "today" in text_lower:
        date = "today"

    # room detection
    if "room a" in text_lower:
        room = "Room A"
    elif "room b" in text_lower:
        room = "Room B"
    elif "room c" in text_lower:
        room = "Room C"
    else:
        room = "Room A"

    return room, date, time


# -------- HOME PAGE --------
@app.route("/")
def home():
    return render_template("index.html")


# -------- CHATBOT --------
@app.route("/chat", methods=["POST"])
def chat():

    message = request.json["message"]
    intent = predict_intent(message)

    if intent == "book":

        room, date, time = extract_booking_details(message)

        if date is None:
            date = "today"

        if time is None:
            time = "not specified"

        conn = sqlite3.connect("bookings.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM bookings WHERE room=? AND date=? AND time=?",
            (room, date, time)
        )

        existing_booking = cursor.fetchone()

        if existing_booking:
            response = f"{room} is already booked for {date} at {time}"

        else:
            cursor.execute(
                "INSERT INTO bookings(room,date,time) VALUES(?,?,?)",
                (room, date, time)
            )

            conn.commit()

            response = f"{room} booked for {date} at {time}"

        conn.close()

    elif intent == "cancel":
        response = "Your booking has been cancelled."

    elif intent == "check":
        response = "Room A is available."

    else:
        response = "Sorry, I didn't understand."

    return jsonify({"reply": response})


# -------- ADMIN DASHBOARD --------
@app.route("/admin")
def admin():

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM bookings")
    bookings = cursor.fetchall()

    conn.close()

    return render_template("admin.html", bookings=bookings)


# -------- DELETE BOOKING --------
@app.route("/delete/<int:id>")
def delete_booking(id):

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM bookings WHERE id=?", (id,))
    conn.commit()

    conn.close()

    return redirect(url_for("admin"))


# -------- CALENDAR VIEW --------
@app.route("/calendar")
def calendar():

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    cursor.execute("SELECT room, date, time FROM bookings")
    data = cursor.fetchall()

    conn.close()

    events = []

    for booking in data:

        room, date, time = booking

        # convert today/tomorrow to real date
        if date.lower() == "today":
            event_date = datetime.today().strftime("%Y-%m-%d")

        elif date.lower() == "tomorrow":
            event_date = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")

        else:
            event_date = date

        events.append({
            "title": f"{room} - {time}",
            "start": event_date
        })

    return render_template("calendar.html", events=events)


# -------- RUN SERVER --------
if __name__ == "__main__":
    app.run(debug=True)