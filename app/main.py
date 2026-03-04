from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import HTMLResponse
from pathlib import Path
# Note: we import the modules first, then use them
from app.api.v1 import auth, sessions, focus, emotion, journal, decision, analytics
from app.models.base import Base
from app.db.session import engine
from fastapi.staticfiles import StaticFiles


# 1. Create the app instance FIRST
app = FastAPI(title="Attention AI Backend")

# 2. Create database tables
# This looks at all models linked to 'Base' and creates them in Postgres
Base.metadata.create_all(bind=engine)

# 3. Include the routers AFTER app is defined
app.include_router(auth.router)
app.include_router(sessions.router)
app.include_router(focus.router)
app.include_router(emotion.router)
app.include_router(journal.router)
app.include_router(decision.router)
app.include_router(analytics.router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")



# @app.get("/", response_class=HTMLResponse)
# def serve_frontend():
#     with open("app/static/index.html", "r", encoding="utf-8") as f:
#         return f.read()
# @app.get("/", response_class=HTMLResponse)
# def serve_ui():
#     return Path("app/static/index.html").read_text(encoding="utf-8")

@app.get("/", response_class=HTMLResponse)
def serve_login():
    return Path("app/static/login.html").read_text(encoding="utf-8")

@app.get("/dashboard", response_class=HTMLResponse)
def serve_dashboard():
    return Path("app/static/dashboard.html").read_text(encoding="utf-8")

@app.get("/monitor", response_class=HTMLResponse)
def serve_monitor():
    return Path("app/static/monitor.html").read_text(encoding="utf-8")

@app.get("/analytics", response_class=HTMLResponse)
def serve_analytics():
    return Path("app/static/analytics.html").read_text(encoding="utf-8")

@app.get("/journal", response_class=HTMLResponse)
def serve_journal():
    return Path("app/static/journal.html").read_text(encoding="utf-8")

@app.get("/focus_boosters", response_class=HTMLResponse)
def serve_focus_boosters():
    return Path("app/static/focus_boosters.html").read_text(encoding="utf-8")