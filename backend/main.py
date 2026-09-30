import sqlite3
from datetime import datetime, timezone
from typing import List
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="LifeLine AI API",
    version="1.0.0",
    description="Explainable emergency-response route decision API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROUTES = [
    {
        "id": "R1",
        "name": "City Center → Medical District",
        "distance_km": 7.4,
        "eta_min": 14,
        "traffic": 32,
        "congestion": "Low",
        "risk": 12,
        "intervention": 1,
        "delay": 0,
    },
    {
        "id": "R2",
        "name": "Ring Road → Medical District",
        "distance_km": 9.1,
        "eta_min": 12,
        "traffic": 46,
        "congestion": "Medium",
        "risk": 18,
        "intervention": 2,
        "delay": -2,
    },
    {
        "id": "R3",
        "name": "Market Road → Medical District",
        "distance_km": 5.8,
        "eta_min": 18,
        "traffic": 71,
        "congestion": "High",
        "risk": 35,
        "intervention": 4,
        "delay": 6,
    },
]

INCIDENTS = [
    {
        "id": "INC-1042",
        "type": "Cardiac emergency",
        "location": "Rajpur Road",
        "status": "Active",
        "priority": "Critical",
        "time": "09:18",
    },
    {
        "id": "INC-1041",
        "type": "Road accident",
        "location": "ISBT Junction",
        "status": "Resolved",
        "priority": "High",
        "time": "08:51",
    },
    {
        "id": "INC-1040",
        "type": "Medical transfer",
        "location": "Clock Tower",
        "status": "Resolved",
        "priority": "Medium",
        "time": "08:24",
    },
]


class AnalysisRequest(BaseModel):
    emergency_type: str = Field(default="Cardiac emergency")
    severity: int = Field(default=5, ge=1, le=5)

class RouteFeedback(BaseModel):
    quality:str = Field(default="poor")

FEEDBACK_DB ="route_feedback.db"
POOR_FEEDBACK_PENALTY = 20
POOR_FEEDBACK_THRESHOLD = 3

def init_feedback_db():
    conn = sqlite3.connect(FEEDBACK_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS route_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            route_id TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_feedback_db()

def get_route_feedback(route_id:str):
    conn = sqlite3.connect(FEEDBACK_DB)
    count = conn.execute(
        """
        SELECT COUNT(*)
        FROM route_feedback
        WHERE route_id = ? AND quality ='poor'
        """,
        (route_id,)
    ).fetchone()[0]
    conn.close()
    return count



def score_route(route: dict, severity: int, emergency_type: str) -> tuple[float, list[str]]:
    # Lower score is better.
    # Different emergency types use different priorities.
    profiles = {
        "Cardiac emergency": {
            "eta": 7.0,
            "traffic": 0.16,
            "risk": 0.65,
            "intervention": 1.5,
            "delay": 3.5
        },
        "Road accident": {
            "eta": 2.8,
            "traffic": 0.38,
            "risk": 1.20,
            "intervention": 4.0,
            "delay": 2.0
        },
        "Critical medical transfer": {
            "eta": 6.0,
            "traffic": 0.24,
            "risk": 0.80,
            "intervention": 2.5,
            "delay": 3.0
        },
        "Fire emergency": {
            "eta": 2.8,
            "traffic": 0.48,
            "risk": 0.95,
            "intervention": 2.0,
            "delay": 4.5
        },
    }

    weights = profiles.get(
        emergency_type,
        profiles["Cardiac emergency"]
    )

    severity_factor = 1 + (severity - 1) * 0.18

    poor_feedback_count = get_route_feedback(route["id"])

    quality_penalty =(
        poor_feedback_count * POOR_FEEDBACK_PENALTY
    )

    score = (
        route["eta_min"] * weights["eta"]
        + route["traffic"] * weights["traffic"]
        + route["risk"] * weights["risk"] * severity_factor
        + route["intervention"] * weights["intervention"]
        + max(route["delay"], 0) * weights["delay"]
        + quality_penalty
    )

    reasons = []

    if route["eta_min"] <= 14:
        reasons.append("Fast estimated arrival time")

    if route["traffic"] <= 40:
        reasons.append("Low traffic load")

    if route["risk"] <= 15:
        reasons.append("Lower route risk")

    if route["intervention"] <= 1:
        reasons.append("Minimal intervention required")

    if route["delay"] > 0:
        reasons.append(
            f"Expected {route['delay']} min delay"
        )

    if poor_feedback_count > 0:
        reasons.append(
            f"{poor_feedback_count} poor-quality feedback report(s),"
            f"+{quality_penalty} routing penalty"
        )    

    if poor_feedback_count >= POOR_FEEDBACK_THRESHOLD:
        reasons.append(
            "Excluded from routing due to repeated poor-quality feedback"
        )

    return round(score, 2), reasons


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "LifeLine AI"}


@app.get("/api/routes")
def get_routes():
    return ROUTES


@app.get("/api/incidents")
def get_incidents():
    return INCIDENTS


@app.post("/api/analyze")
def analyze(request: AnalysisRequest):
    analyzed = []

    for route in ROUTES:

        poor_feedback_count = get_route_feedback(route["id"])

        score, reasons = score_route(
            route,
            request.severity,
            request.emergency_type
        )

        excluded = (
            poor_feedback_count >= POOR_FEEDBACK_THRESHOLD
        )
        analyzed.append({
            **route,
            "score": score,
            "reasons":reasons,

            "poor_feedback_count": poor_feedback_count,
            "quality_penalty": (
                poor_feedback_count * POOR_FEEDBACK_PENALTY
            ),
            "excluded": excluded,
        })


    available_routes = [
        route
        for route in analyzed
        if not route["excluded"]
    ]

    if not available_routes:
        raise HTTPException(
            status_code=400,
            details=(
                "All available routes have been excluded"
                "due to repeated poor-quality feedback."
            )
        )

    available_routes.sort(
        key=lambda item: item["score"]
    )   

    recommended = available_routes[0]

    analyzed.sort(
        key=lambda item: item["score"]
    )

    explanation = (
        f"{recommended['name']} is recommended because it has an estimated "
        f"{recommended['eta_min']} minute arrival time, {recommended['traffic']}% "
        f"traffic load, and a route-risk score of {recommended['risk']}. "
        f"The decision score is {recommended['score']}."
    )

    return {
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "emergency_type": request.emergency_type,
        "severity": request.severity,
        "recommended_route": recommended,
        "routes": analyzed,
        "explanation": explanation,
    }


@app.post("/api/routes/{route_id}/feedback")
def submit_route_feedback(
    route_id:str,
    feedback: RouteFeedback
):
    route = next(
        (r for r in ROUTES if r["id"] == route_id),
        None
    )
    if route is None:
        raise HTTPException(
            status_code=404,
            detail="Route not found"
        )


    if feedback.quality !="poor":
        raise HTTPException(
            status_code=404,
            detail="only poor quality feedback is currently supported "
        )    

    conn = sqlite3.connect(FEEDBACK_DB)

    conn.execute(
        """
        INSERT INTO route_feedback
        (route_id, quality, created_at)
        VALUES (?, ?, ?)
        """,
        (
            route_id,
            feedback.quality,
            datetime.now(timezone.utc).isoformat()
        )
    )
    conn.commit()
    conn.close()

    count = get_route_feedback(route_id)

    return {
        "message": "Route feedback recorded",
        "route_id": route_id,
        "quality":feedback.quality,

        "poor_feedback_count": count,
        "quality_penalty": (
            count * POOR_FEEDBACK_PENALTY
        ),

        "excluded": (
            count >= POOR_FEEDBACK_THRESHOLD
        ),

        "eta_min": route["eta_min"]
    }