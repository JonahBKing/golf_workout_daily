import smtplib
import os
import random

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("PASSWORD")

RECIPIENT = "Jonahking10@gmail.com"


def load_workouts():
    sections = {
        "WARMUP": [],
        "STRENGTH": [],
        "ROTATION": [],
        "FLEXIBILITY": []
    }

    current = None

    with open("workouts.txt") as f:
        for line in f:
            line = line.strip()

            if line.endswith(":"):
                current = line.replace(":", "")

            elif line and current:
                sections[current].append(line)

    return sections


def choose_random(options, count):
    return random.sample(
        options,
        min(count, len(options))
    )


def build_workout():
    sections = load_workouts()

    return {
        "warmup": choose_random(
            sections["WARMUP"],
            3
        ),

        "strength": choose_random(
            sections["STRENGTH"],
            4
        ),

        "rotation": choose_random(
            sections["ROTATION"],
            2
        ),

        "flexibility": choose_random(
            sections["FLEXIBILITY"],
            4
        )
    }


workout = build_workout()


msg = MIMEMultipart("alternative")

msg["Subject"] = "⛳ Golf Workout"
msg["From"] = EMAIL
msg["To"] = RECIPIENT


html = f"""
<html>

<head>
<meta name="viewport"
content="width=device-width, initial-scale=1.0">
</head>

<body style="
margin:0;
padding:0;
background:#f5f5f5;
font-family:Arial,sans-serif;
">

<div style="
max-width:600px;
margin:0 auto;
background:white;
padding:20px;
">

<h2 style="
font-size:22px;
margin-bottom:10px;
">
⛳ Golf Workout
</h2>

<p style="
font-size:14px;
color:#666;
">
Built for swing power, mobility, and consistency
</p>

<hr style="margin:15px 0;">

<h3>🔥 Warm-Up</h3>

<ul style="
font-size:16px;
line-height:1.6;
padding-left:20px;
">
{''.join(f'<li>{x}</li>' for x in workout['warmup'])}
</ul>

<h3>💪 Strength</h3>

<ul style="
font-size:16px;
line-height:1.6;
padding-left:20px;
">
{''.join(f'<li>{x}</li>' for x in workout['strength'])}
</ul>

<h3>🔄 Rotation</h3>

<ul style="
font-size:16px;
line-height:1.6;
padding-left:20px;
">
{''.join(f'<li>{x}</li>' for x in workout['rotation'])}
</ul>

<h3>🧘 Flexibility</h3>

<ul style="
font-size:16px;
line-height:1.6;
padding-left:20px;
">
{''.join(f'<li>{x}</li>' for x in workout['flexibility'])}
</ul>

<hr style="margin-top:25px;">

<p style="
font-size:12px;
color:#999;
text-align:center;
">
Daily automated workout
</p>

</div>

</body>
</html>
"""


msg.attach(
    MIMEText(
        "Today's golf workout is ready.",
        "plain"
    )
)

msg.attach(
    MIMEText(
        html,
        "html"
    )
)


with smtplib.SMTP_SSL(
    "smtp.gmail.com",
    465
) as server:

    server.login(
        EMAIL,
        PASSWORD
    )

    server.send_message(
        msg
    )


print("Workout email sent")
