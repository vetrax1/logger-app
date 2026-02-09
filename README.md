# LoggerBuddy

> A tiny, production-minded multi-service demo that proves the full DevOps flow: **UI → API → Database**, packaged with **Docker Compose**, designed to be **reproducible**, **debuggable**, and **ready to grow into Jenkins CI + GitOps (Argo CD) + AKS**.

---

## ✨ What this project is

LoggerBuddy is a simple “log message” app used as a learning and portfolio-ready DevOps artifact.

It demonstrates:

* **Multi-service architecture** (frontend + backend + PostgreSQL)
* **Service discovery** via Docker Compose DNS (service names)
* **Config injection** via environment variables
* **Persistence** via named volumes
* **Reliability** with health checks and startup ordering
* **Operability** with clear debug commands and runbook-style docs

---

## 🧠 Architecture

### High-level flow

1. **User** opens the UI in the browser.
2. UI sends an HTTP request to the **Backend API**.
3. Backend stores and retrieves logs from **PostgreSQL**.
4. Database data persists on a **named volume**.

### Architecture diagram (sketch)

```text
                  (User)
                    |
                    | 1) HTTP GET
                    v
          +---------------------+
          |  Frontend (NGINX)   |
          |  Static HTML UI     |
          +---------------------+
                    |
                    | 2) HTTP POST /log
                    |    HTTP GET  /recent
                    v
          +---------------------+
          |  Backend (Flask API)|
          |  Business logic +   |
          |  SQL queries        |
          +---------------------+
                    |
                    | 3) TCP 5432 (Postgres protocol)
                    v
          +---------------------+
          |  PostgreSQL (DB)    |
          |  Table: logs        |
          +---------------------+
                    |
                    | 4) Persistent storage
                    v
          +---------------------+
          |  Volume: pgdata     |
          |  /var/lib/postgresql|
          |  /data              |
          +---------------------+

      * All services communicate on the Compose network: loggernet
      * DNS inside the network resolves service names (e.g., `db`)
```

---

## 📁 Repository structure

```text
.
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
├── frontend/
│   ├── Dockerfile
│   └── index.html
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
└── db/
    └── init.sql
```

---

## ✅ Prerequisites

* Docker Engine installed
* Docker Compose v2 available (`docker compose`)

Verify:

```bash
docker --version
docker compose version
```

---

## 🚀 Quickstart (Run in 3 minutes)

### 1) Configure environment variables

Copy the example file:

```bash
cp .env.example .env
```

Update `.env` (choose a strong password):

```env
DB_PASSWORD=ChangeMeStrongPassword
```

### 2) Build and run

```bash
docker compose up -d --build
```

### 3) Open the app

* Frontend UI: `http://localhost:8080`
* Backend API: `http://localhost:5000`

---

## 🔌 API Endpoints

### Health checks

* `GET /health` → confirms API is alive
* `GET /db-check` → confirms API can connect to Postgres and execute a query

Example:

```bash
curl http://localhost:5000/health
curl http://localhost:5000/db-check
```

### Logging

* `POST /log` → store a message

```bash
curl -X POST -d "message=Hello LoggerBuddy" http://localhost:5000/log
```

### Read logs

* `GET /recent` → returns the last 10 log entries (most recent first)

```bash
curl http://localhost:5000/recent
```

---

## 🗄️ Database

### Schema

Postgres initializes a simple `logs` table on first boot (via `db/init.sql`):

```sql
CREATE TABLE IF NOT EXISTS logs (
  id SERIAL PRIMARY KEY,
  message TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Under the hood: initialization behavior

* The Postgres container executes SQL files inside `/docker-entrypoint-initdb.d/` **only when the data directory is empty**.
* Because we mount a named volume (`pgdata`), that initialization runs **once** per volume lifecycle.

---

## 💾 Persistence (prove your data survives restarts)

### Persistence test

1. Add a few logs
2. Stop services

```bash
docker compose down
```

3. Start services again

```bash
docker compose up -d
```

4. Confirm logs still exist

```bash
curl http://localhost:5000/recent
```

### ⚠️ Destroying data intentionally (dev-only)

```bash
docker compose down -v
```

This removes containers **and** volumes.

---

## 🔎 Observability (how to inspect what’s happening)

### View running services

```bash
docker compose ps
```

### Tail logs

```bash
docker compose logs -f backend
```

### Exec into containers

```bash
docker compose exec backend sh
```

### Query database directly (gold standard verification)

```bash
docker compose exec db psql -U loggeruser -d loggerdb -c "SELECT * FROM logs ORDER BY id DESC LIMIT 5;"
```

---

## 🧯 Troubleshooting (fast fixes)

### 1) Backend can’t connect to DB

**Symptoms:** `/db-check` fails or backend logs show connection errors.

**Fix:**

* Confirm DB is healthy:

```bash
docker compose ps
```

* View DB logs:

```bash
docker compose logs db
```

* Verify DNS resolution from backend:

```bash
docker compose exec backend sh -c "getent hosts db || nslookup db"
```

### 2) `init.sql` didn’t run / table missing

If the `pgdata` volume already existed, Postgres will not re-run init scripts.

**Dev reset:**

```bash
docker compose down -v
docker compose up -d --build
```

### 3) Password auth failed

* Confirm `.env` exists and matches the compose variables.
* Restart the stack:

```bash
docker compose down
docker compose up -d
```

---

## 🔐 Security notes (lab-safe habits)

* `.env` is not committed (secrets stay local).
* DB is **not** exposed to the host by default (no `5432:5432` mapping).
* In production you would store secrets in a manager (Azure Key Vault) and inject them securely.

---

## 🧭 Roadmap (where this goes next)

This project is intentionally designed to grow into a full DevOps delivery chain:

1. **Jenkins CI**

   * checkout → lint → test → build images → scan images
2. **Registry**

   * Docker Hub now → **Azure Container Registry (ACR)** later
3. **GitOps (Argo CD)**

   * Jenkins updates GitOps repo image tag → Argo CD syncs to AKS
4. **AKS deployment**

   * Helm/Kustomize manifests, Ingress, TLS, autoscaling


---

## 🙌 Credits

Built as part of the **#100DaysOfDevOps** journey under **TechdotSam**.
 
