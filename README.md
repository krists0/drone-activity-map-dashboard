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
- Angular (v18+)
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
│ ├── app/
│ │ ├── core/
│ │ │ └── config.py
│ │ │
│ │ ├── db/
│ │ │ └── database.py
│ │ │
│ │ ├── models/
│ │ │ ├── drone.py
│ │ │ └── pipeline.py
│ │ │
│ │ ├── schemas/
│ │ │ ├── drone.py
│ │ │ └── pipeline.py
│ │ │
│ │ ├── services/
│ │ │ └── pipeline_service.py
│ │ │
│ │ ├── routers/
│ │ │ ├── drones.py
│ │ │ └── pipeline.py
│ │ │
│ │ └── main.py
│ │
│ ├── tests/
│ ├── requirements.txt
│ └── Dockerfile
│
├── frontend/
│ ├── src/
│ │ └── app/
│ │ ├── core/
│ │ │ ├── models/
│ │ │ │ └── drone-record.model.ts
│ │ │ └── services/
│ │ │ ├── drone-api.service.ts
│ │ │ └── pipeline-service.ts
│ │ │
│ │ └── features/
│ │ └── dashboard/
│ │ ├── components/
│ │ │ ├── drone-map/
│ │ │ ├── filter-panel/
│ │ │ └── pipeline-runs-table/
│ │ │
│ │ └── pages/
│ │ └── dashboard-page/
│ │
│ └── Dockerfile
│
├── data/
│ └── drone_records.json
│
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

## Data Ingestion & Deduplication Flow (Crucial Logic)

The backend pipeline reads raw telemetry JSON files from the shared local `data/` directory and executes sequentially:

1. **Extraction**: Loads raw drone arrays from `drone_records.json` [3.1].
2. **Validation**: Enforces core strict data boundaries (e.g., non-negative altitude, battery within 0-100%, valid coordinates) [3.3].
3. **⚠️ Strict Deduplication (Idempotency Protection)**:
To prevent corrupting the database logs with identical telemetry overlays, the pipeline performs a comparative search inside the database on the unique composite of `(drone_id, timestamp)` before saving [3.1].
- **First Run**: Valid entries are newly generated and inserted (`valid_records` counter increments) [3.2].
- **Subsequent Runs**: If the pipeline is triggered multiple times without new data, the duplication guard flags existing state composites and fires a `continue` skip loop [3.1]. This gracefully logs `valid_records: 0` in the history logs to maintain absolute database integrity [3.1, 3.2].
4. **Validation Counters**: Invalid raw items (e.g., negative altitudes) always fail validation rules upfront and safely increment the `invalid_records` tracking dashboard index across every deployment run [3.1, 3.2].

---

## Architectural Layout Design

To ensure an enterprise-grade Separation of Concerns (SoC), the frontend relies on a clean, centralized reactive state pattern:

- **`DashboardPageComponent` (The Smart Parent)**: Manages core state structures, orchestrates data streams, and serves as the single source of truth [4.2]. It handles direct asynchronous network HTTP communications with the FastAPI servers [4.2].
- **`FilterPanelComponent` (The Input Controller)**: Houses temporary form states until the user fires the `Apply Filters` command [4.2]. It passes clean, localized parameters up to the parent shell.
- **`DroneMapComponent` (The Visual Presentation Layer)**: A clean display component that listens to downstream reactive state changes [4.1, 4.2]. It automatically clears previous instances and renders updated map coordinates via an internal `@Input` setter [4.1, 4.2].
- **`PipelineRunsTable` (The Execution Hub)**: Collects analytics counters and houses the control button interface to safely dispatch ingestion cycles [4.3].

---

## One-Click Terminal Commands (Installation & Run)

### Method A: Docker Compose Deployment (Recommended - No Local Setup Needed)
If you have Docker installed, you can build and start the PostgreSQL Database, Python Backend, and Angular Frontend **all at once** with a single command [7.6]:

```bash
# Run this from the root directory to install and launch everything automatically
docker-compose up --build
```
- **Frontend App UI:** `http://localhost:4200`
- **Backend Swagger API Docs:** `http://localhost:8000/docs`

---

### Method B: Manual Local Installation
If you prefer running the components individually, open your terminal windows and run these specific grouped blocks:

#### 1. Start the Python Backend Application
```bash
cd backend
# 1. Create virtual environment, activate it, install all libraries, and start the app at once:
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload
```
*(Windows users shell shortcut alternative: `python -m venv .venv; .venv\Scripts\activate; pip install -r requirements.txt; uvicorn app.main:app --reload`)*

#### 2. Start the Angular Frontend Application
Open a completely separate second terminal window and run:
```bash
cd frontend
# 2. Install all node dependencies and fire up the development server at once:
npm install && ng serve
```
Open your internet browser canvas interface directly to: `http://localhost:4200`

---

## API Endpoints Reference

| Method | Endpoint | Purpose |
| :--- | :--- | :--- |
| **POST** | `/api/pipeline/run` | Triggers the local raw telemetry ingestion loop [3.4]. |
| **GET** | `/api/pipeline/runs` | Returns historical processing log metric summaries [3.4]. |
| **GET** | `/api/drones` | Fetches filtered drone tracking indices [3.4]. |
| **GET** | `/api/drone/{id}` | Fetches a single drone record object state by unique identifier [3.4]. |





## Running Automated Unit Tests

### Backend Tests (Python & Pytest)
To execute backend database validation guards and query API parameter criteria verification tests, run from the `backend/` folder:
```bash
pip install pytest httpx
python -m pytest -v
```

### Frontend Tests (Angular & Jasmine/Karma)
To execute frontend layout creation tracking and UI input component controller clear filter state automation checks, run from the `frontend/` folder:

filters
```bash
ng test --include=src/app/features/dashboard/components/filter-panel/filter-panel.spec.ts --watch=false
```

