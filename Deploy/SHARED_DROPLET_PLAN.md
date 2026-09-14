# School Timetable — shared droplet with Zyrowaste

Deploy **School_Timetable_Fresh** on the same DigitalOcean droplet as Zyrowaste.

| | |
|--|--|
| **Public IP (SSH + HTTP)** | `143.244.128.22` |
| **Zyrowaste** | `https://zyrowaste.com` — `/opt/zyrowaste` — ports **80/443** |
| **Jenkins (this project)** | `http://143.244.128.22:8090/` — host **8090** |
| **Timetable app (v1)** | `http://143.244.128.22:444/` — `/opt/school-timetable` — host **444** |

**Full context, architecture, Zyrowaste safety changes, and verification:**  
see `D:\Zyrowaste_v3_jenkins-1\deploy\documentation\deployment\shared-droplet-school-timetable-plan.md`

---

## Changes in this repo (summary)

1. **`Deploy/droplet.env.example`** — `APP_PORT=444`, `JENKINS_HTTP_PORT=8090`, GHCR `IMAGE_NAME`.
2. **`docker-compose.yml`** — `444:80` via `APP_PORT`.
3. **`Jenkinsfile`** — `APP_PORT=444`, `JENKINS_HTTP_PORT=8090`; deploy publishes app on **444** only.
4. **`Deploy/scripts/deploy.sh`** / **`healthcheck.sh`** — defaults use port **444**.

## Before first deploy

- Zyrowaste: **`FRESH_CLEAN_DEPLOY=false`** and scoped Docker prune (full plan Phase B).
- DigitalOcean firewall: **TCP 444** (app) and **8090** (Jenkins) as needed.
- On droplet: `docker login ghcr.io` and `/opt/school-timetable/.env.production` with `APP_PORT=444`.

## Manual run

```bash
docker rm -f timetable-app 2>/dev/null || true
docker run -d --name timetable-app --restart unless-stopped -p 444:80 timetable-app
curl -f http://127.0.0.1:444/health
```

Do **not** bind **80/443** (Zyrowaste) or **8090** (Jenkins UI for this project).
