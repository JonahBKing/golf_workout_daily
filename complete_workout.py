import os
import requests

JSONBIN_BIN_ID = os.environ["JSONBIN_BIN_ID"]
JSONBIN_API_KEY = os.environ["JSONBIN_API_KEY"]
WORKOUT_ID = os.environ["WORKOUT_ID"]


def load_state():
    r = requests.get(
        f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}/latest",
        headers={"X-Master-Key": JSONBIN_API_KEY},
    )
    return r.json()["record"]


def save_state(state):
    requests.put(
        f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}",
        headers={
            "Content-Type": "application/json",
            "X-Master-Key": JSONBIN_API_KEY,
        },
        json=state,
    )


state = load_state()

current = state.get("currentWorkout")

if current and current["id"] == WORKOUT_ID:
    current["completed"] = True

    state.setdefault("completedHistory", []).append({
        "id": current["id"],
        "workout": current["workout"]
    })

    save_state(state)

print("Workout marked complete:", WORKOUT_ID)
