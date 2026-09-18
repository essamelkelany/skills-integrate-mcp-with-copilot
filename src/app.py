"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


def build_member_record(email: str, name: str | None = None, grade: str | None = None, status: str = "active"):
    normalized_email = email.strip().lower()
    normalized_name = (name or normalized_email.split("@")[0].replace(".", " ")).strip()
    if not normalized_name:
        normalized_name = normalized_email.split("@")[0].replace(".", " ").title()

    return {
        "name": normalized_name.title(),
        "email": normalized_email,
        "grade": grade or "N/A",
        "status": status,
        "activities": [],
    }


# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}

members = {}
for activity_name, activity in activities.items():
    for email in activity["participants"]:
        normalized_email = email.strip().lower()
        if normalized_email not in members:
            members[normalized_email] = build_member_record(normalized_email)
        if activity_name not in members[normalized_email]["activities"]:
            members[normalized_email]["activities"].append(activity_name)


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/members")
def get_members():
    return [members[email] for email in sorted(members)]


@app.get("/members/{email}")
def get_member(email: str):
    normalized_email = email.strip().lower()
    if normalized_email not in members:
        raise HTTPException(status_code=404, detail="Member not found")
    return members[normalized_email]


@app.post("/members", status_code=201)
def create_member(member: dict):
    email = (member.get("email") or "").strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    if email in members:
        raise HTTPException(status_code=400, detail="Member already exists")

    new_member = build_member_record(
        email=email,
        name=member.get("name"),
        grade=member.get("grade"),
        status=member.get("status", "active"),
    )
    members[email] = new_member
    return new_member


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    normalized_email = email.strip().lower()
    if normalized_email not in members:
        members[normalized_email] = build_member_record(normalized_email)

    activity = activities[activity_name]
    if normalized_email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(
            status_code=400,
            detail="Activity is full"
        )

    members[normalized_email]["activities"].append(activity_name)
    activity["participants"].append(normalized_email)
    return {"message": f"Signed up {normalized_email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    normalized_email = email.strip().lower()
    activity = activities[activity_name]
    if normalized_email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    activity["participants"].remove(normalized_email)
    if activity_name in members.get(normalized_email, {}).get("activities", []):
        members[normalized_email]["activities"].remove(activity_name)
    return {"message": f"Unregistered {normalized_email} from {activity_name}"}
