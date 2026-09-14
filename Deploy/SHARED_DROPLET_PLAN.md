# School Timetable — shared droplet with Zyrowaste

Deploy **School_Timetable_Fresh** on the same DigitalOcean droplet as Zyrowaste.

| | |
|--|--|
| **Public IP (SSH + HTTP)** | `143.244.128.22` |
| **Zyrowaste** | `https://zyrowaste.com` — `/opt/zyrowaste` — ports **80/443** |
| **This app (v1)** | `http://143.244.128.22:8080/` — `/opt/school-timetable` — host port **8080** |

**Full context, architecture, Zyrowaste safety changes, and verification:**  
see `D:\Zyrowaste_v3_jenkins-1\deploy\documentation\deployment\shared-droplet-school-timetable-plan.md`

---

## Changes in this repo (summary)

1. **`Deploy/droplet.env.example`** — `PROD_HOST`, `DEPLOY_PATH`, `APP_PORT=8080`, GHCR `IMAGE_NAME`.
2. **`Deploy/.env.example`** — local copy for `Deploy/scripts/*.sh` (gitignored `Deploy/.env`).
3. **`Deploy/examples/`** — template copies only (compose, Dockerfile, scripts, nginx); see `Deploy/examples/README.md`.
4. **`docker-compose.yml`** — project name `school-timetable`; `8080:80` via `APP_PORT`.
5. **`Deploy/scripts/deploy.sh`** — `docker compose -p school-timetable`; `/opt/school-timetable`; healthcheck after up.
6. **`Deploy/scripts/healthcheck.sh`** — `PROD_HOST` + `APP_PORT` for `/health`.
7. **`Deploy/scripts/rollback.sh`** — same compose `-p` scoping.
8. **`Jenkinsfile`** — push image to registry; optional **`DEPLOY_TO_PROD`** via SSH to `143.244.128.22`.

## Before first deploy

- Zyrowaste side: set **`FRESH_CLEAN_DEPLOY=false`** and narrow Docker prune (see full plan Phase B).
- DigitalOcean firewall: allow **TCP 8080** if using public `:8080` URL.
- On droplet: `docker login ghcr.io` and `/opt/school-timetable/.env.production`.

## Troubleshooting (Docker on the droplet)

### `Bind for 0.0.0.0:80 failed: port is already allocated`

Host port **80** is taken (Zyrowaste nginx). Do **not** use `-p 80:…` for this app. Use **`-p 8080:80`**, not `-p 80:8080` (container nginx listens on **80**, not 8080).

### `policy-rc.d denied execution of start` during `docker build`

Harmless during image build. nginx starts when the container runs (`CMD nginx …`).

### Quick manual run after `docker build -t timetable-app .`

```bash
docker rm -f timetable-app 2>/dev/null || true
docker run -d --name timetable-app --restart unless-stopped -p 8080:80 timetable-app
curl -f http://127.0.0.1:8080/health
```

Implementation order and checklists are in the full plan linked above.
