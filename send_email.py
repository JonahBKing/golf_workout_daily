import smtplib
import os
import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import json

EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("PASSWORD")

RECIPIENT = "Jonahking10@gmail.com"
RECIPIENT2 = "kaylavonburg@gmail.com"

def save_workout(workout):
    try:
        with open("history.json")  as f:
            history = json.load(f)
    except:
        history = []

    history.insert(0, workout) # newest
    history = history[:3] # last 3 days

    with open ("history.json", "w") as f:
        json.dump(history, f)

def load_history():
    try:
        with open("history.json") as f:
            return json.load(f)
    except:
        return []

def get_weight(item, history, category):
    for i, day in enumerate(history):
        if item in day.get(category, []):
            if i == 0:
                return 0     
            elif i == 1:
                return 0.3    
            elif i == 2:
                return 0.6   
    return 1.0  



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

def weighted_sample(options, k, history, category):
    selected = []
    pool = options[:]

    for _ in range(min(k, len(pool))):
        weights = [get_weight(item, history, category) for item in pool]

        # remove zero-weight items (yesterday)
        filtered = [(item, w) for item, w in zip(pool, weights) if w > 0]

        if not filtered:
            return random.sample(options, min(k, len(options)))

        items, weights = zip(*filtered)
        choice = random.choices(items, weights=weights, k=1)[0]

        selected.append(choice)
        pool.remove(choice)

    return selected


def build_workout():
    sections = load_workouts()
    history = load_history()

    return {
        "warmup": weighted_sample(sections["WARMUP"], 3, history, "warmup"),
        "strength": weighted_sample(sections["STRENGTH"], 4, history, "strength"),
        "rotation": weighted_sample(sections["ROTATION"], 2, history, "rotation"),
        "flexibility": weighted_sample(sections["FLEXIBILITY"], 4, history, "flexibility"),
    }

workout = build_workout()

msg = MIMEMultipart("alternative")
msg["Subject"] = f"⛳ Golf Workout"
msg["From"] = EMAIL
msg["To"] = RECIPIENT


html = f"""
<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
  </head>

  <body style="margin:0;padding:0;background:#f5f5f5;font-family:Arial, sans-serif;">

    <div style="max-width:600px;margin:0 auto;background:white;padding:20px;">

      <h2 style="font-size:22px;margin-bottom:10px;">
        ⛳ Golf Workout
      </h2>

      <p style="font-size:14px;color:#666;">
        Built for swing power, mobility, and consistency
      </p>

      <hr style="margin:15px 0;">

      <h3 style="font-size:18px;">🔥 Warm-Up</h3>
      <ul style="font-size:16px;line-height:1.6;padding-left:20px;">
        {''.join(f'<li>{x}</li>' for x in workout['warmup'])}
      </ul>

      <h3 style="font-size:18px;">💪 Strength</h3>
      <ul style="font-size:16px;line-height:1.6;padding-left:20px;">
        {''.join(f'<li>{x}</li>' for x in workout['strength'])}
      </ul>

      <h3 style="font-size:18px;">🔄 Rotation</h3>
      <ul style="font-size:16px;line-height:1.6;padding-left:20px;">
        {''.join(f'<li>{x}</li>' for x in workout['rotation'])}
      </ul>

      <h3 style="font-size:18px;">🧘 Flexibility</h3>
      <ul style="font-size:16px;line-height:1.6;padding-left:20px;">
        {''.join(f'<li>{x}</li>' for x in workout['flexibility'])}
      </ul>

      <a href="https://your-app.vercel.app/api/done"
      style="background:#28a745;color:white;
      padding:12px 20px;border-radius:6px;
      text-decoration:none;">
      ✅ Mark Workout Complete
      </a>

    </div>

  </body>
</html>
"""

msg.attach(MIMEText("Today's golf workout is ready.", "plain"))
msg.attach(MIMEText(html, "html"))

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(EMAIL, PASSWORD)
    server.send_message(msg)


save_workout(workout)
