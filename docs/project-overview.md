# LifeLine AI — Project Overview

## Problem
Emergency responders often need to make route decisions while traffic conditions, delays and route risks are changing.

## Solution
LifeLine AI creates an explainable route recommendation by combining:
- estimated arrival time
- traffic load
- route risk
- intervention requirement
- expected delay
- emergency severity

## Why it is explainable
Instead of returning only a route, the API returns the score and the factors that contributed to the recommendation.

## Technology
- Frontend: React, TypeScript, Vite
- Backend: Python, FastAPI, Pydantic
- Decision engine: weighted multi-factor scoring
- Data: prototype in-memory dataset; can be extended to PostgreSQL/real-time traffic APIs

## Future scope
- live map integration
- real traffic APIs
- ambulance GPS telemetry
- hospital capacity integration
- authentication and role-based access
- ML-based travel-time prediction
- SUMO/traffic simulation
