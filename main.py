from collections import defaultdict

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
async def analytics(
    body: AnalyticsRequest,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    positive_totals = defaultdict(float)

    revenue = 0.0

    for event in body.events:
        if event.amount > 0:
            revenue += event.amount
            positive_totals[event.user] += event.amount

    top_user = max(positive_totals, key=positive_totals.get) if positive_totals else None

    return {
        "email": EMAIL,
        "total_events": len(body.events),
        "unique_users": len({event.user for event in body.events}),
        "revenue": revenue,
        "top_user": top_user,
    }
