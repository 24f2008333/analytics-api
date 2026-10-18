
from collections import defaultdict

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError


API_KEY = "ak_8hbvb6opk0qiil7012ptwusw"
EMAIL = "24f2008333@ds.study.iitm.ac.in"

app = FastAPI(title="Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Event(BaseModel):
    user: str
    amount: float
    ts: int


class AnalyticsRequest(BaseModel):
    events: list[Event]


@app.get("/")
async def health():
    return {"status": "ok"}


@app.post("/analytics")
async def analytics(request: Request):
    # Check the API key before reading or validating the request body.
    supplied_key = request.headers.get("X-API-Key")

    if supplied_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )

    # Parse and validate the JSON body.
    try:
        json_body = await request.json()
        body = AnalyticsRequest(**json_body)
    except (ValueError, TypeError, ValidationError):
        raise HTTPException(
            status_code=422,
            detail="Invalid request body",
        )

    total_events = len(body.events)
    unique_users = len({event.user for event in body.events})

    revenue = 0.0
    user_totals = defaultdict(float)

    for event in body.events:
        if event.amount > 0:
            revenue += event.amount
            user_totals[event.user] += event.amount

    top_user = (
        max(user_totals, key=user_totals.get)
        if user_totals
        else None
    )

    return {
        "email": EMAIL,
        "total_events": total_events,
        "unique_users": unique_users,
        "revenue": revenue,
        "top_user": top_user,
    }
