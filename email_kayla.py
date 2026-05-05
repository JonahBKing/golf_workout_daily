EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("PASSWORD")

RECIPIENT = "kaylavonburg@gmail.com"

def get_day():
    start_day = 1
    today = datetime.now().timetuple().tm_yday
    return (today % 30) + 1


day = get_day()
workout = get_workout(day)

msg = MIMEText(Hi Kayla, I think I found a use for chatgpt)
msg["Subject"] = f"HI Kayla - Test {day}"
msg["From"] = EMAIL
msg["To"] = RECIPIENT

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(EMAIL, PASSWORD)
    server.send_message(msg)
