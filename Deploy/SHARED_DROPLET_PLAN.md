# School Timetable — shared droplet with Zyrowaste

| Service | URL / port |
|---------|------------|
| Zyrowaste | `https://zyrowaste.com` — **80/443** |
| Existing Jenkins | `http://143.244.128.22:8080/` |
| **Timetable app** | `http://143.244.128.22:8090/` — `APP_PORT=8090` |
| **Timetable Jenkins** (optional 2nd instance) | `http://143.244.128.22:8081/` — `JENKINS_HTTP_PORT=8081` |

8090 is the **Docker app** (`timetable-app`). Do not run Jenkins on 8090.

Full plan: `D:\Zyrowaste_v3_jenkins-1\deploy\documentation\deployment\shared-droplet-school-timetable-plan.md`

## Manual run (matches current server)

```bash
docker run -d --name timetable-app --restart unless-stopped -p 8090:80 timetable-app
curl -f http://127.0.0.1:8090/health
```

## Dedicated Jenkins on 8081

See comments in `Deploy/droplet.env.example` for a separate `JENKINS_HOME` and `--httpPort=8081`.
