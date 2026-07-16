# Drone Activity Map Dashboard

A small full-stack application for ingesting simulated drone telemetry data, storing it in PostgreSQL, and displaying drone activity on an interactive map.

The project demonstrates backend API design, ingestion pipeline logic, PostgreSQL persistence, Angular frontend integration, MapLibre map rendering, and a clean layered architecture.

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

The frontend displays the processed drone records on a map using MapLibre, with filters and a pipeline control panel.

---

## Important Note

The drone telemetry data is simulated and does not represent real drone operations.
Real map coordinates are used only for visibility on the frontend map.

---

## Project Structure

```text
drone-activity-map-dashboard/
│
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   └── config.py          # Environment settings (DATABASE_URL, etc.)
│   │   │
│   │   ├── db/
│   │   │   └── database.py        # SQLAlchemy engine, session, Base
│   │   │
│   │   ├── models/
│   │   │   ├── drone.py           # DroneRecord table
│   │   │   └── pipeline.py        # PipelineRun table
│   │   │
│   │   ├── routers/
│   │   │   ├── drones.py          # /api/drones endpoints
│   │   │   └── pipeline.py        # /api/pipeline endpoints
│   │   │
│   │   ├── schemas/
│   │   │   ├── drone.py           # Pydantic validation schemas
│   │   │   └── pipeline.py
│   │   │
│   │   ├── services/
│   │   │   └── pipeline_service.py # Ingestion pipeline logic
│   │   │
│   │   └── main.py
│   │
│   ├── tests/
│   │   └── test_drones.py
│   │
│   ├── Dockerfile
│   └── requirements.txt
│
├── data/
│   └── drone_records.json         # Sample input file (valid + invalid records)
│
├── frontend/
│   ├── public/
│   │   └── drone-icon-pin.png
│   │
│   ├── src/app/
│   │   ├── core/
│   │   │   ├── models/drone-record.model.ts
│   │   │   └── services/
│   │   │       ├── drone-api.service.ts
│   │   │       └── pipeline-api.service.ts
│   │   │
│   │   └── features/dashboard/
│   │       ├── components/
│   │       │   ├── drone-map/
│   │       │   ├── filter-panel/
│   │       │   └── pipeline-runs-table/
│   │       │
│   │       └── pages/dashboard-page/
│   │
│   ├── angular.json
│   ├── package.json
│   └── README.md
│
├── .env
├── docker-compose.yml
└── README.md   (this file)
```

---

## Database Schema

The schema is defined via SQLAlchemy models and created automatically at startup with `Base.metadata.create_all()` — there is no separate migrations tool (e.g. Alembic) in this exercise; see "Assumptions & Trade-offs" below.

### `drone_records`
| Column | Type | Notes |
|---|---|---|
| `id` | Integer, PK | Auto-increment |
| `drone_id` | String | Required |
| `drone_type` | String | e.g. Quadcopter, Fixed Wing, VTOL |
| `operator_id` | String | |
| `latitude` | Float | -90 to 90 |
| `longitude` | Float | -180 to 180 |
| `altitude_m` | Float | >= 0 |
| `speed_kmh` | Float | |
| `battery_percent` | Integer | 0 to 100 |
| `timestamp` | DateTime | |
| `status` | String | active / landed / lost_signal |

A **unique constraint on `(drone_id, timestamp)`** prevents the same telemetry point from being inserted twice, which makes the pipeline safe to re-run on the same input file (idempotent ingestion).

### `pipline_runs`
*(table name as defined in the SQLAlchemy model — note the intentional match to the code, not a typo introduced here)*

| Column | Type | Notes |
|---|---|---|
| `id` | Integer, PK | |
| `started_at` | DateTime | |
| `finished_at` | DateTime | Nullable until the run completes |
| `status` | String | started / completed / failed |
| `total_records` | Integer | Records read from the input file |
| `valid_records` | Integer | Records successfully inserted |
| `invalid_records` | Integer | Records skipped (failed validation or duplicates) |
| `error_message` | String | Nullable, populated on failure |

---

## Data Ingestion & Deduplication Flow

The pipeline reads a raw telemetry JSON file from `data/drone_records.json` and, for each record:

1. **Load** — reads the raw JSON array from the input file.
2. **Validate** — checks the record against the rules in section 3.3 of the assignment (non-empty `drone_id`, coordinate ranges, non-negative altitude, battery 0–100, valid timestamp, allowed `status` values). Records that fail are skipped and counted as invalid.
3. **Deduplicate** — checks the database for an existing record with the same `drone_id` + `timestamp`. If found, the record is skipped and also counted as invalid, so re-running the pipeline on the same file never creates duplicate rows and the counters (`total = valid + invalid`) always stay consistent.
4. **Store** — remaining valid records are inserted into `drone_records`.
5. **Log** — a `pipline_runs` row is created with the counters and final status (`completed` or `failed`, with `error_message` set if the run crashed, e.g. missing input file).

In short: the pipeline is **idempotent** — running it twice on the same input file will not duplicate data, and the second run will simply report a higher `invalid_records` count.

---

## Architecture

- **`DashboardPageComponent`** — the smart parent component. Owns the drone list and pipeline-run history, calls the backend services, and passes data down to its children.
- **`FilterPanelComponent`** — holds the filter form state locally until the user clicks "Apply", then emits the chosen filters upward.
- **`DroneMapComponent`** — a presentational component that renders markers on the MapLibre map whenever the drone list input changes.
- **`PipelineRunsTable`** — displays the run history table and exposes the "Run Pipeline" trigger button.

---

## Setup & Run Instructions

### 1. Configure environment variables

Copy or create a `.env` file in the project root with:

```env
POSTGRES_DB=drone_dashboard
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/drone_dashboard
```

(Defaults above match `docker-compose.yml`; adjust if you use different credentials.)

### 2. Run everything with Docker Compose (recommended)

From the project root:
```bash
docker-compose up --build
```
This builds and starts PostgreSQL, the FastAPI backend, and the Angular frontend together.

- Frontend: `http://localhost:4200`
- Backend Swagger docs: `http://localhost:8000/docs`

### 3. Run manually instead (without Docker for backend/frontend)

Start only the database in Docker:
```bash
docker-compose up -d postgres
```

**Backend** (in a first terminal):
```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```
Swagger docs: `http://localhost:8000/docs`

**Frontend** (in a second terminal):
```bash
cd frontend
npm install
ng serve
```
App: `http://localhost:4200`

---

## API Endpoints Reference

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/pipeline/run` | Triggers the ingestion pipeline on `data/drone_records.json`. |
| GET | `/api/pipeline/runs` | Returns pipeline run history. |
| GET | `/api/drones` | Returns drone records, with optional filters (`drone_type`, `status`, `operator_id`, `min_battery`, `from_date`, `to_date`). |
| GET | `/api/drones/{id}` | Returns a single drone record, or 404 if not found. |

---

## Example Input Data

`data/drone_records.json` contains a mix of **valid and intentionally invalid** records, so a single pipeline run demonstrates both successful ingestion and validation rejection — for example, records with an empty `drone_id`, an out-of-range latitude, a negative altitude, or an invalid `status` value are all skipped and counted under `invalid_records`.

---

## Running Automated Tests

### Backend

```bash
cd backend
pip install pytest httpx
python -m pytest -v
```

Covers: field-level validation rules (latitude/longitude bounds, battery range, altitude, timestamp, status), the `/api/drones` filters, `/api/drones/{id}` (found and not-found cases), the pipeline service directly (valid/invalid counting, missing-file handling), and `/api/pipeline/runs` history.

### Frontend

```bash
cd frontend
ng test --include=src/app/features/dashboard/components/**/*.spec.ts --watch=false
```

Covers: the filter panel (form state, reset behavior, DOM interactions), and the pipeline runs table (rendering rows, status badges, empty state, and the run-trigger button).

---

## Assumptions & Trade-offs

- **No separate migrations tool.** The database schema is created via `Base.metadata.create_all()` at startup rather than Alembic migrations, to keep the setup simple for this exercise.
- **Backend tests run against the real configured database**, not an isolated in-memory test database. This was a deliberate simplification for this exercise; in a production setting, tests would run against a dedicated/ephemeral test database (e.g. an in-memory SQLite DB or a disposable test container) to keep them fully independent and repeatable.
- **Deduplication counts repeated records as "invalid".** Re-running the pipeline on an unchanged input file is safe (no duplicate rows), but it will report `invalid_records` for every record that already exists, since there's no separate "skipped/duplicate" counter in the schema.
- **Pagination is not implemented** on `/api/drones` — acceptable for the small dataset in this exercise, but would be needed at scale.
- **Bonus features implemented:** low-battery and lost-signal styling in the map popup, Docker Compose for all three services.
- **Bonus features not implemented:** "latest position only" map view, drone path history, and a background task runner (Celery/Prefect) — the pipeline runs synchronously on request.