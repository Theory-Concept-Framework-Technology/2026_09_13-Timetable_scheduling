# Home Meal Planner

Standalone **vegetarian home meal timetable** app: weekly plan (breakfast / lunch / snack / dinner), recipe search, nutrition summaries, and recipe details. Backend proxies free recipe APIs; keys live in `.env` only.

This folder is **separate from** the school timetable project for easier reading and deployment.

## Folder structure

```text
home-meal-planner/
├── README.md                 ← you are here
├── .env.example              ← copy to .env
├── requirements.txt          ← Python API dependencies
├── docker-compose.yml        ← web (nginx) + meal-api
├── run.bat                   ← Docker Compose up
├── run_api.bat               ← local API only (dev)
├── backend/
│   ├── app/                  ← FastAPI application package
│   │   ├── main.py           ← HTTP routes (/api/meals/…)
│   │   ├── config.py         ← settings, paths, blocklists
│   │   ├── models.py         ← Pydantic models
│   │   ├── vegetarian.py     ← veg filter rules
│   │   ├── cache/            ← HTTP response file cache
│   │   ├── db/               ← SQLite meal plans
│   │   ├── providers/        ← local catalog, TheMealDB, USDA FDC
│   │   └── services/         ← search, plans, generator
│   └── data/
│       └── recipes.json      ← extensible Indian veg catalog
├── frontend/
│   ├── index.html            ← single-page UI
│   ├── css/style.css
│   └── js/
│       ├── ui.js             ← navigation + modal
│       └── planner.js        ← API client + dashboards
├── deploy/
│   ├── Dockerfile.api
│   ├── Dockerfile.web
│   └── nginx/default.conf    ← static site + /api proxy
└── data/                     ← created at runtime (gitignored)
    ├── meals.db
    └── meal_cache/
```

## Quick start (Docker)

**Requires Docker Desktop running** (whale icon in the system tray).

```bat
cd home-meal-planner
copy .env.example .env
run.bat
```

Open **http://localhost:8000/** by default (set `WEB_PORT` in `.env`; use **8000** on the shared DigitalOcean droplet where 8080/8081/8090 are taken — see [`deploy/DROPLET_PORTS.md`](deploy/DROPLET_PORTS.md)).

If `run.bat` closes immediately or the site is unreachable, read the error in the window (it now pauses on failure). Usually **Docker Desktop is not started**.

## Quick start (no Docker)

```bat
run_local.bat
```

If the menu still looks **repeated or has no food photos**, the old SQLite plan is cached. Use:

```bat
run_fresh.bat
```

This deletes `data/meals.db`, restarts the app, and builds a new varied plan with images.

This opens two terminals (API on **8000**, static UI on **8080** via `LOCAL_WEB_PORT`) and your browser. Keep both terminals open while using the app.

## Deploy on DigitalOcean (1GB shared droplet)

Use host port **8000** (not 8080/8081/8090 — already in use on the school droplet).

```bash
cd home-meal-planner
cp .env.example .env   # WEB_PORT=8000
docker compose up --build -d
curl -sf http://127.0.0.1:8000/api/meals/health
sudo ufw allow 8000/tcp
```

App URL: `http://<droplet-ip>:8000/`

Details: [`deploy/DROPLET_PORTS.md`](deploy/DROPLET_PORTS.md).

## Local development

**Terminal 1 — API**

```bat
run_api.bat
```

**Terminal 2 — full stack (recommended)**

Use Docker for the frontend so `/api/meals/` is proxied correctly:

```bat
docker compose up web meal-api
```

Or run only `run_api.bat` and point a local nginx at `frontend/` using `deploy/nginx/default.conf` with `meal-api` on port 8000.

## API overview

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/meals/health` | Health check |
| GET | `/api/meals/plans/current` | Active plan + today + week nutrition |
| POST | `/api/meals/plans/generate` | New vegetarian weekly plan |
| GET | `/api/meals/search` | Search + filters |
| GET | `/api/meals/recipes/{id}` | Recipe detail |

## Adding recipes

Edit `backend/data/recipes.json` — each entry supports `meal_types`, `ingredients`, `instructions`, and `nutrition` (marked as catalog / approximate).

## External APIs (optional)

| Variable | Service |
|----------|---------|
| `THEMEALDB_API_KEY` | TheMealDB (default `1` for dev) |
| `USDA_FDC_API_KEY` | USDA FoodData Central nutrition enrichment |

Nutrition is always presented as **approximate**; see API responses and UI disclaimer.

## Relation to school timetable repo

The school app under `../src/meals/` can stay integrated for combined deploy. This project is the **same feature set** in a clean layout you can copy, zip, or move to its own repository.
