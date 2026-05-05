import smtplib
from email.mime.text import MIMEText
from datetime import datetime

EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("PASSWORD")

RECIPIENT = "Jonahking10@gmail.com"

def get_day():
    start_day = 1
    today = datetime.now().timetuple().tm_yday
    return (today % 30) + 1

def get_workout(day):
    with open("workouts.txt") as f:
        data = f.read().split("Day ")
    for entry in data:
        if entry.startswith(str(day)):
            return "Day " + entry
    return "Rest day"

day = get_day()
workout = get_workout(day)

msg = MIMEText(workout)
msg["Subject"] = f"Golf Workout Day {day}"
msg["From"] = EMAIL
msg["To"] = RECIPIENT

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(EMAIL, PASSWORD)
    server.send_message(msg)
