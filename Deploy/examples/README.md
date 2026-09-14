# Deploy examples (templates only)

These files are **documentation templates**. They are not used automatically by Docker or Jenkins.

| Example | Use |
|---------|-----|
| [`droplet.env.example`](droplet.env.example) | Environment variables for droplet + Jenkins deploy |
| [`docker-compose.example.yml`](docker-compose.example.yml) | Same as repo root `docker-compose.yml` |
| [`Dockerfile.example`](Dockerfile.example) | Same as repo root `Dockerfile` |
| [`nginx/default.conf.example`](nginx/default.conf.example) | Nginx config baked into the image |
| [`scripts/*.example`](scripts/) | Reference copies of deploy / healthcheck / rollback |

**Runnable scripts** live in [`../scripts/`](../scripts/). **Production compose** is [`../../docker-compose.yml`](../../docker-compose.yml).

Shared droplet summary: [`../SHARED_DROPLET_PLAN.md`](../SHARED_DROPLET_PLAN.md).
