import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("PASSWORD")

RECIPIENT = "Jonahking10@gmail.com"

print("EMAIL:", EMAIL)
print("PASSWORD length:", len(PASSWORD) if PASSWORD else None)


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

msg = MIMEMultipart("alternative")
msg["Subject"] = f"⛳ Golf Workout Day {day}"
msg["From"] = EMAIL
msg["To"] = RECIPIENT

html = f"""
<html>
  <body style="font-family: Arial; line-height: 1.5;">
    <h2>⛳ Golf Workout – Day {day}</h2>
    
    <p><b>Today's Focus:</b> Strength + Rotation</p>

    <pre style="background:#f4f4f4;padding:10px;border-radius:8px;">
{workout}
    </pre>

    <hr>
    <p style="font-size:12px;color:gray;">
      Built for swing power, stability, and mobility.
    </p>
  </body>
</html>
"""

msg.attach(MIMEText(html, "html"))



with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(EMAIL, PASSWORD)
    server.send_message(msg)
