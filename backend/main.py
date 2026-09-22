from datetime import datetime, timezone
from typing import List
import heapq
from fastapi import FastAPI ,HTTPException
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

LOCATIONS ={
    "City Center": (30.3165, 78.0322),
    "Clock Tower": (30.3256, 78.0437),
    "Rajpur Road": (30.3600, 78.0700),
    "ISBT Junction": (30.3165, 78.0330),
    "Market Road": (30.3200, 78.0400),
    "Ring Road":(30.3300,78.0600),
    "Medical District": (30.3500, 78.0800),

}

ROADS =[
    ("City Center","Clock Tower",1.8,30),
    ("City Center","ISBT Junction",2.5,35),
    ("Clock Tower","Market Road",1.5,30),
    ("Market Road","Rajpur Road",3.0,35),
    ("Rajpur Road","Medical District",4.0,45),
    ("Ring Road","Rajpur Road",2.5,40),
    ("Ring Road","Medical District",6.6,50),
    ("ISBT Junction","Ring Road",4.0,40),



]

GRAPH = {
    location:[] 
    for location in LOCATIONS
}

for start, end, distance, speed in ROADS:
    travel_time =(distance/speed)*60

    GRAPH[start].append({
        "to":end,
        "distance":distance,
        "time":travel_time
    }) 
    GRAPH[end].append({
        "to":start,
        "distance":distance,
        "time": travel_time
    })
    print("GRAPH TEST:", GRAPH)

def shortest_path(origin: str,destination: str):

    if origin not in GRAPH:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid origin location: {origin}"
        )

    if destination not in GRAPH:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid destination location: {origin}"

        )    
    distances ={
        location: float("inf")
        for location in GRAPH
    }        

    previous ={
        location:None
        for location in GRAPH
    }
    distances[origin] = 0

    priority_queue =[(0, origin)]

    while priority_queue:

        current_distance,current = heapq.heappop(priority_queue)

        if current_distance > distances[current]:
            continue
        if current == destination:
            break

        for edge in GRAPH[current]:

            new_distance =(
                current_distance + edge["distance"]
                )

            if new_distance <distances[edge["to"]]:

                 distances[edge["to"]] = new_distance
                 previous[edge["to"]]  = current

                 heapq.heappush(
                    priority_queue,
                    (new_distance,
                    edge["to"])
                 )   
        if distances[destination] ==float("inf"):
            raise HTTPException(
            status_code=404,
            detail=f"No route available from{origin} to{destination}"
        )    


        path =[]
        current = destination

        while current is not None:
            path.append(current)
            current = previous[current]

        path.reverse()

        total_distance = distances[destination]

        total_time =0
        for i in range(len(path)- 1):

            current_node = path[i]
            next_node =path[i+1]

            for edge in GRAPH[current_node]:

                if edge["to"] == next_node:
                    total_time+= edge["time"]
                    break
        return{
            "route": path,
            "total_distance_km":round(total_distance, 2),
            "estimated_travel_time_min":round(total_time,1)
        }                           

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

class RouteRequest(BaseModel):
    origin:str
    destination: str    


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

    score = (
        route["eta_min"] * weights["eta"]
        + route["traffic"] * weights["traffic"]
        + route["risk"] * weights["risk"] * severity_factor
        + route["intervention"] * weights["intervention"]
        + max(route["delay"], 0) * weights["delay"]
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

@app.post("/api/shortest-route")
def calculate_shortest_route(request:RouteRequest):

    result = shortest_path(
        request.origin,
        request.destination
    )

    return {
        "success": True,
        "origin": request.origin,
        "destination": request.destination,
        **result
    }


@app.post("/api/analyze")
def analyze(request: AnalysisRequest):
    analyzed = []

    for route in ROUTES:
        score, reasons = score_route(route, request.severity, request.emergency_type)
        analyzed.append({
            **route,
            "score": score,
            "reasons": reasons,
        })

    analyzed.sort(key=lambda item: item["score"])
    recommended = analyzed[0]

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
