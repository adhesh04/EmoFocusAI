import time
import requests
import pygetwindow as gw

BACKEND_URL = "http://127.0.0.1:8000/telemetry/signal"
SESSION_ID = 1
TOKEN = "PASTE_JWT_TOKEN"

PRODUCTIVE = ["code", "studio", "pdf", "terminal"]

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

def window_score():
    win = gw.getActiveWindow()
    if not win:
        return 0.5, "unknown"

    title = win.title.lower()
    score = 1.0 if any(p in title for p in PRODUCTIVE) else 0.3
    return score, title

while True:
    score, name = window_score()

    requests.post(
        BACKEND_URL,
        json={
            "session_id": SESSION_ID,
            "window_name": name,
            "window_score": score
        },
        headers=headers
    )

    time.sleep(3)
