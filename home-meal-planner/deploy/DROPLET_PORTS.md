# DigitalOcean — shared 1GB droplet ports

Typical layout on this project's droplet:

| Host port | Status   | Common use              |
|-----------|----------|-------------------------|
| 8080      | USED     | Other app (e.g. Zyrowaste) |
| 8081      | USED     | Jenkins (dedicated)     |
| 8090      | USED     | School timetable nginx  |
| 8000      | FREE     | **Home Meal Planner (default)** |
| 8001–8003 | FREE     | Spare / debug           |

## Deploy Home Meal Planner

On the server, in `home-meal-planner/`:

```bash
cp .env.example .env
# WEB_PORT=8000 is already set for this droplet

docker compose up --build -d
docker compose ps
curl -sf http://127.0.0.1:8000/api/meals/health
```

Open: `http://YOUR_DROPLET_IP:8000/`

### Firewall

```bash
sudo ufw allow 8000/tcp comment 'home-meal-planner'
sudo ufw status
```

### Change port

Edit `.env`:

```env
WEB_PORT=8002
```

Then:

```bash
docker compose down
docker compose up -d
```

**Do not** bind `8080`, `8081`, or `8090` on this droplet unless you stop the services already using them.

### Memory (1GB)

Both containers are lightweight. If the host is tight on RAM:

```bash
docker stats --no-stream home-meal-web home-meal-api
```

Data persists in Docker volume `home-meal-planner_planner_data` (SQLite + API cache).
