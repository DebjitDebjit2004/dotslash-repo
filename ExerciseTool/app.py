from flask import Flask, render_template, request, jsonify, flash, session
from twilio.rest import Client
import sqlite3
import caldav
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
import os
from icalendar import Calendar, Alarm, Event

load_dotenv()

app = Flask(__name__, template_folder="template", static_folder="static", static_url_path="/")

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
NEXTCLOUD_URL = os.getenv('NEXTCLOUD_URL')
NEXTCLOUD_USERNAME = os.getenv('NEXTCLOUD_USERNAME')
NEXTCLOUD_PASSWORD = os.getenv('NEXTCLOUD_PASSWORD')
app.secret_key = os.getenv("APP_KEY")

timezone = pytz.timezone("Asia/Kolkata")
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def get_db():
    conn = sqlite3.connect('diabetes_exercises.db')
    return conn


def get_user_db():
    conn = sqlite3.connect("user.db")
    return conn


def create_user_table(phone_number):
    conn = get_user_db()
    cursor = conn.cursor()
    table_name = f"user_{phone_number}"
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT,
            start_date DATE,
            end_date DATE
        )
    """)
    conn.commit()
    return conn, table_name


def get_user_calendar(phone_number):
    try:
        client = caldav.DAVClient(NEXTCLOUD_URL, username=NEXTCLOUD_USERNAME, password=NEXTCLOUD_PASSWORD)
        principal = client.principal()
        calendar_name = f"User_{phone_number}_Calendar"
        calendars = principal.calendars()

        for calendar in calendars:
            if calendar.name == calendar_name:
                return calendar, calendar.url

        new_calendar = principal.make_calendar(name=calendar_name)
        print(f"Calendar {calendar_name} created.")
        return new_calendar, new_calendar.url
    except Exception as e:
        print(f"Error getting or creating calendar: {e}")
        return None


def send_whatsapp_message(phone_number, message):
    message = twilio_client.messages.create(
        body=message,
        from_='whatsapp:' + TWILIO_PHONE_NUMBER,
        to='whatsapp:+91' + phone_number
    )
    return message.sid


def add_event_to_nextcloud(calendar, start_date, title, description, start_hour):
    try:
        start_time = datetime.strptime(start_date, "%Y-%m-%d").replace(hour=int(start_hour))
        end_time = datetime.strptime(start_date, "%Y-%m-%d").replace(hour=int(start_hour) + 1)
        timezone = pytz.timezone('UTC')
        start_time = timezone.localize(start_time)
        end_time = timezone.localize(end_time)

        ical_event = Event()
        ical_event.add('dtstart', start_time)
        ical_event.add('dtend', end_time)
        ical_event.add('summary', title)
        ical_event.add('description', description)

        alarm = Alarm()
        alarm.add('trigger', timedelta(minutes=-15))
        alarm.add('action', 'DISPLAY')
        alarm.add('description', f"Reminder: {title}")
        ical_event.add_component(alarm)

        cal = Calendar()
        cal.add('prodid', '-//My App//My Calendar//EN')
        cal.add('version', '2.0')
        cal.add_component(ical_event)

        calendar.add_event(cal.to_ical().decode("utf-8"))
    except Exception as e:
        print(f"Error adding event: {e}")
        return None


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/create-challenge', methods=['POST'])
def create_challenge():
    session["event"] = True
    data = request.get_json()
    phone_number = data['phone_number']
    start_hour = data['time']

    start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
    end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')

    if start_date > end_date or start_date == end_date:
        return jsonify({"error": "Start date cannot be after the end date"}), 400

    conn, table_name = create_user_table(phone_number)
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE phone_number = ?", (phone_number,))
    number_of_rows = cursor.fetchone()[0]

    if number_of_rows >= 1:
        return jsonify({"warning": "Challenge already exists and started"}), 400
    try:
        cursor.execute(f"""
            INSERT INTO {table_name} (phone_number, start_date, end_date) 
            VALUES (?, ?, ?)
        """, (phone_number, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
        conn.commit()

        calendar, calendar_url = get_user_calendar(phone_number)
        if not calendar:
            return "Could not access or create calendar ,error"

        db_conn = get_db()
        db_cursor = db_conn.cursor()
        db_cursor.execute("SELECT exercise_name, description FROM exercises")
        exercises = db_cursor.fetchall()
        db_conn.close()
        current_date = start_date
        while current_date <= end_date:
            day_index = (current_date - start_date).days % len(exercises)
            exercise_name, description = exercises[day_index]
            add_event_to_nextcloud(
                calendar,
                current_date.strftime('%Y-%m-%d'),
                exercise_name,
                description,
                start_hour
            )
            current_date += timedelta(days=1)
        send_whatsapp_message(phone_number,
                              f"Challenge set from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}!\n Calendar-URL: {calendar_url}")

        flash("Challenge started successfully!", "success")
        return jsonify({"message": "Challenge started successfully!"})
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        conn.close()


@app.route('/discontinue-challenge', methods=['POST'])
def discontinue_challenge():
    data = request.get_json()
    phone_number = data['phone_number']

    conn, table_name = create_user_table(phone_number)
    cursor = conn.cursor()

    try:
        cursor.execute(f"SELECT * FROM {table_name} ORDER BY start_date DESC LIMIT 1")
        challenge = cursor.fetchone()

        if challenge:
            cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (challenge[0],))
            conn.commit()

            calendar, _ = get_user_calendar(phone_number)
            if not calendar:
                return jsonify({"error": "Could not access or create calendar"}), 500

            all_event = calendar.events()
            for event in all_event:
                event.delete()

            send_whatsapp_message(phone_number, "Your exercise challenge has been discontinued.")
            return jsonify({"message": "Challenge discontinued successfully!"})

        return jsonify({"message": "No active challenge found."}), 404
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        conn.close()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5555, debug=True)
