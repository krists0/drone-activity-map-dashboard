# Drone Activity Map Dashboard

A small full-stack application for ingesting simulated drone telemetry data, storing it in PostgreSQL, and displaying drone activity on an interactive map.

The project demonstrates backend API design, ingest pipeline logic, PostgreSQL persistence, Angular frontend integration, MapLibre map rendering, and clean layered architecture.

---

## Tech Stack

### Backend
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic / Pydantic Settings

### Frontend
- Angular
- TypeScript
- MapLibre GL JS
- CARTO basemap style

### Infrastructure
- Docker Compose
- PostgreSQL container

---

## Project Objective

The system receives simulated drone telemetry records from a JSON file.

Each record represents a drone position at a specific timestamp.

The backend is responsible for:

1. Loading raw drone records from a JSON file.
2. Validating required fields and allowed values.
3. Skipping invalid records.
4. Normalizing data where needed.
5. Storing valid records in PostgreSQL.
6. Saving pipeline run status and processing counters.

The frontend displays the processed drone records on a map using MapLibre.

---

## Important Note

The drone telemetry data is simulated and does not represent real drone operations.

Real map coordinates are used only for visibility on the frontend map.

---

## Current Project Structure

```text
drone-activity-map-dashboard/
│
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   └── config.py
│   │   │
│   │   ├── db/
│   │   │   └── database.py
│   │   │
│   │   ├── models/
│   │   │   ├── drone.py
│   │   │   └── pipeline.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── drone.py
│   │   │   └── pipeline.py
│   │   │
│   │   ├── services/
│   │   │   └── pipeline_service.py
│   │   │
│   │   ├── routers/
│   │   │   ├── drones.py
│   │   │   └── pipeline.py
│   │   │
│   │   └── main.py
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   └── app/
│   │       ├── core/
│   │       │   ├── models/
│   │       │   │   └── drone-record.model.ts
│   │       │   └── services/
│   │       │       └── drone-api.service.ts
│   │       │
│   │       └── features/
│   │           └── dashboard/
│   │               └── components/
│   │                   └── drone-map/
│   │
│   └── Dockerfile
│
├── data/
│   └── drone_records.json
│
├── docker-compose.yml
├── README.md
└── .gitignore