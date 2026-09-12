# LifeLine AI

### Explainable Emergency Response Decision System

LifeLine AI is a full-stack prototype that helps emergency-response teams compare alternative routes and recommend the safest and fastest option using explainable scoring.

## Features
- React + TypeScript emergency dashboard
- Python FastAPI REST backend
- Explainable route scoring
- Traffic, delay, congestion and intervention-risk factors
- Route recommendation with reasons
- Emergency incident history
- Responsive UI

## Architecture
React + TypeScript → FastAPI → Decision Engine → SQLite

## Run locally

### Backend
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

API: http://127.0.0.1:8000
Swagger: http://127.0.0.1:8000/docs

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open the URL shown by Vite (normally http://localhost:5173).

## API
- `GET /api/health`
- `GET /api/routes`
- `POST /api/analyze`
- `GET /api/incidents`

## Project purpose
This is a recruitment-ready MVP demonstrating Python, REST APIs, TypeScript/React, data modeling, decision logic and explainable recommendations. It is a prototype and does not replace certified emergency-dispatch systems.
