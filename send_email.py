import smtplib
import os
import random
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("PASSWORD")

JSONBIN_BIN_ID = os.environ.get("JSONBIN_BIN_ID")
JSONBIN_API_KEY = os.environ.get("JSONBIN_API_KEY")

RECIPIENT = "Jonahking10@gmail.com"


# ----------------------------
# JSONBIN HELPERS
# ----------------------------

def load_state():
    try:
        r = requests.get(
            f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}/latest",
            headers={"X-Master-Key": JSONBIN_API_KEY},
        )
        return r.json().get("record", {})
    except Exception as e:
        print("load_state error:", e)
        return {}


def save_state(state):
    try:
        requests.put(
            f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}",
            headers={
                "Content-Type": "application/json",
                "X-Master-Key": JSONBIN_API_KEY,
            },
            json=state,
        )
    except Exception as e:
        print("save_state error:", e)


# ----------------------------
# WORKOUT LOADING
# ----------------------------

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


# ----------------------------
# WEIGHTING (uses history)
# ----------------------------

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


def weighted_sample(options, k, history, category):
    selected = []
    pool = options[:]

    for _ in range(min(k, len(pool))):
        weights = [get_weight(item, history, category) for item in pool]

        filtered = [(item, w) for item, w in zip(pool, weights) if w > 0]

        if not filtered:
            return random.sample(options, min(k, len(options)))

        items, weights = zip(*filtered)
        choice = random.choices(items, weights=weights, k=1)[0]

        selected.append(choice)
        pool.remove(choice)

    return selected


# ----------------------------
# BUILD WORKOUT
# ----------------------------

def build_workout(history):
    sections = load_workouts()

    return {
        "warmup": weighted_sample(sections["WARMUP"], 3, history, "warmup"),
        "strength": weighted_sample(sections["STRENGTH"], 4, history, "strength"),
        "rotation": weighted_sample(sections["ROTATION"], 2, history, "rotation"),
        "flexibility": weighted_sample(sections["FLEXIBILITY"], 4, history, "flexibility"),
    }


# ----------------------------
# LOAD STATE
# ----------------------------

state = load_state()

current = state.get("currentWorkout")
history = state.get("completedHistory", [])


today_id = datetime.now().strftime("%Y-%m-%d")


# ----------------------------
# DECIDE WORKOUT
# ----------------------------

if current and not current.get("completed"):
    print("Reusing unfinished workout")
    workout = current["workout"]
    workout_id = current["id"]

else:
    print("Generating new workout")

    workout = build_workout(history)
    workout_id = today_id

    state["currentWorkout"] = {
        "id": workout_id,
        "completed": False,
        "workout": workout
    }

    save_state(state)


# ----------------------------
# EMAIL SETUP
# ----------------------------

msg = MIMEMultipart("alternative")
msg["Subject"] = "Golf Workout"
msg["From"] = EMAIL
msg["To"] = RECIPIENT

done_link =  "https://github.com/JonahBKing/golf_workout_daily/issues/1"


html = f"""
<html>
  <body style="font-family:Arial;background:#f5f5f5;padding:20px;">

    <div style="max-width:600px;margin:auto;background:white;padding:20px;">

      <h2>⛳ Golf Workout</h2>

      <p style="color:#666;">
        Complete today’s session to unlock the next workout.
      </p>

      <hr>

      <h3>🔥 Warm-Up</h3>
      <ul>{''.join(f'<li>{x}</li>' for x in workout['warmup'])}</ul>

      <h3>💪 Strength</h3>
      <ul>{''.join(f'<li>{x}</li>' for x in workout['strength'])}</ul>

      <h3>🔄 Rotation</h3>
      <ul>{''.join(f'<li>{x}</li>' for x in workout['rotation'])}</ul>

      <h3>🧘 Flexibility</h3>
      <ul>{''.join(f'<li>{x}</li>' for x in workout['flexibility'])}</ul>

    <div style="margin-top:25px;">
        <a href="{done_link}"
           style="background:#28a745;color:white;
           padding:12px 18px;border-radius:6px;
           text-decoration:none;display:inline-block;">
         ✅ Mark Workout Complete
        </a>
    </div>

    </div>

  </body>
</html>
"""

msg.attach(MIMEText("Golf workout ready", "plain"))
msg.attach(MIMEText(html, "html"))


# ----------------------------
# SEND EMAIL
# ----------------------------

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(EMAIL, PASSWORD)
    server.send_message(msg)


print("Email sent")
