# Local Testbed Setup Guide

> **Purpose:** Get the Django e-commerce app running locally in Docker **before Saturday** so you can verify functionality before touching Azure.  
> **Estimated Time:** 30–45 minutes (first run)  
> **Prerequisites:** Docker Desktop installed and running

---

## Step 0: Verify Docker Is Installed

Open a terminal and run:

```bash
docker --version
docker compose version
```

You should see version numbers (e.g., `Docker version 26.x.x`). If not, install Docker Desktop from https://www.docker.com/products/docker-desktop.

---

## Step 1: Copy Environment File

```bash
cd /path/to/purdue_capstone   # wherever you cloned the repo
cp .env.example .env
```

The `.env` file already contains safe local defaults. No changes needed for local testing.

---

## Step 2: Build and Start Containers

```bash
docker compose up --build -d
```

What this does:
- Builds the Django app image from the `Dockerfile`
- Starts a PostgreSQL 16 container
- Starts the Django web container
- Runs migrations automatically on startup

**Wait ~30 seconds** for the database to initialize.

---

## Step 3: Verify Everything Is Running

### Check container status
```bash
docker compose ps
```

Both `db` and `web` should show `Up (healthy)` or `Up`.

### Check the app in your browser
Open http://localhost:8000

You should see:  
`Hello, world! This is your Django starter.`

### Check the health endpoint
Open http://localhost:8000/health/

You should see: `ok`

---

## Step 4: Create a Superuser (for Django Admin)

```bash
docker compose exec web python manage.py createsuperuser
```

Follow the prompts (username, email, password). Then visit http://localhost:8000/admin/ and log in.

---

## Step 5: Add the New Models (Before Saturday)

After the team reviews the `Database_Design.md`, you will add the models to `apps/main/models.py`. Then run:

```bash
docker compose exec web python manage.py makemigrations main
docker compose exec web python manage.py migrate
```

Restart the web container if needed:
```bash
docker compose restart web
```

---

## Step 6: Run the Seed Script (Optional)

Once models are in place:

```bash
docker compose exec web python scripts/seed_db.py
```

This populates the local database with sample categories, products, customers, and orders so the team can see the catalog and ordering flow immediately.

---

## Step 7: Test the Full Order Flow Locally

Use this checklist to confirm the app works end-to-end before Saturday:

| Test | How to Verify | Expected Result |
|------|-------------|---------------|
| Home page loads | Visit `/` | Django starter message or custom home page |
| Health check passes | Visit `/health/` | `ok` |
| Admin panel loads | Visit `/admin/` | Django admin login page |
| Superuser login works | Log in with credentials | Admin dashboard appears |
| Product list page (future) | Visit `/products/` | List of seeded products |
| Order creation (future) | Use admin or API | Order appears in `main_order` table |

---

## Common Issues & Fixes

### Issue: `docker compose up` fails with "port already in use"
**Fix:** Another app is using port 8000 or 5432.
```bash
# Find what's using port 8000
lsof -i :8000
# Then either kill that process or change the port in docker-compose.yml
```

### Issue: Migrations fail with "database does not exist"
**Fix:** The database container hasn't finished initializing.
```bash
docker compose down -v   # Remove old volumes
docker compose up --build -d
sleep 15
docker compose exec web python manage.py migrate
```

### Issue: `docker compose` command not found (older Docker)
**Fix:** Use the legacy command:
```bash
docker-compose up --build -d
```

---

## Daily Local Development Commands

```bash
# Start everything
docker compose up -d

# View logs
docker compose logs -f web

# Run a Django management command
docker compose exec web python manage.py <command>

# Stop everything
docker compose down

# Stop everything AND delete the database (nuclear option)
docker compose down -v
```

---

## What Is Different from Azure?

| Aspect | Local Testbed | Azure Production |
|--------|--------------|------------------|
| **Database** | PostgreSQL (Docker) | Azure SQL Database |
| **Web server** | Gunicorn (Docker) | Gunicorn (App Service container) |
| **Static files** | Collected in container | Collected in container or CDN |
| **Images/assets** | Local filesystem or placeholder | Azure Blob Storage |
| **Secrets** | `.env` file | Azure Key Vault + App Settings |
| **Scaling** | Manual (change worker count) | Auto-scaling rules |
| **SSL** | None (http://localhost) | Automatic HTTPS |

The **application code stays the same**. Only the environment variables and database driver change.

---

## Next Step

Once you confirm the local Docker setup works, proceed to `Saturday_Test_Plan.md` to prepare for the Azure deployment and database connectivity tests.

*Guide created: June 26, 2026*
