# Deployment Guide

## Recommended: Render Cron Job

This assignment is a **batch scraper**: it runs `python main.py`, generates files, and exits. A Render Cron Job is therefore a better deployment fit than a continuously running web service or background worker.

The repository includes `render.yaml` configured as a Docker-based cron job. The sample schedule is `0 4 * * *` (04:00 UTC / 09:30 IST daily). You can change the schedule in Render or in `render.yaml`.

### Deploy from GitHub

1. Create a GitHub repository and push this project.
2. In Render, create a **New Blueprint Instance** and connect the repository.
3. Render reads `render.yaml` and creates the cron job.
4. The Docker image installs `requirements.txt` and runs:

```text
python main.py
```

Render supports Docker-based services and cron jobs, and a Dockerfile can define the runtime command. citeturn0search2turn0search12

### Important: output persistence

Render's default filesystem is ephemeral. The generated CSV, JSON, and log are runtime artifacts and should not be treated as permanent storage. For a production version, upload the outputs to object storage or write the records to a database. Render documents this ephemeral-filesystem behavior and the available persistent-storage options. citeturn0search3

## Run locally with Docker

```bash
docker build -t scraping-assignment .
docker run --rm -v "${PWD}/output:/app/output" -v "${PWD}/logs:/app/logs" scraping-assignment
```

PowerShell:

```powershell
docker build -t scraping-assignment .
docker run --rm -v "${PWD}/output:/app/output" -v "${PWD}/logs:/app/logs" scraping-assignment
```

## Why there is no public URL

The assessment is a command-line/batch pipeline, not a web application. A cron deployment runs the scraper but does not expose a public HTTP URL. Render documents cron jobs as services that run commands on a schedule. citeturn0search9

If the interviewer specifically requires a public dashboard/URL, we can add a small optional web dashboard without changing the required `python main.py` pipeline.
