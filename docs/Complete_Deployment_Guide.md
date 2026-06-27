# Purdue Capstone — Complete Deployment & Configuration Guide
**IT473 Cloud Infrastructure & Data Engineering**  
*Azure E-Commerce Platform for Food Distribution*

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Technology Plan](#2-technology-plan)
3. [Database Design](#3-database-design)
4. [Dual-Environment Architecture](#4-dual-environment-architecture)
5. [Pre-Saturday Checklist](#5-pre-saturday-checklist)
6. [Local Testbed Setup (Do This First)](#6-local-testbed-setup-do-this-first)
7. [Saturday Deployment Walkthrough](#7-saturday-deployment-walkthrough)
8. [Post-Deployment Validation](#8-post-deployment-validation)
9. [CI/CD Pipeline (GitHub Actions)](#9-cicd-pipeline-github-actions)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Project Overview

**Repository:** https://github.com/esayeed/purdue_capstone  
**Runtime:** Django 5.1 + Python 3.12 + Docker  
**Local Database:** PostgreSQL 16 (Docker)  
**Production Database:** Azure SQL Database (MSSQL)  
**Compute Target:** Azure App Service (Linux, Web App for Containers)  
**CI/CD:** GitHub Actions → Azure Container Registry → App Service

**Goal for Saturday:** Get the Django container running on Azure, connect it to Azure SQL Database, apply migrations, seed test data, and confirm end-to-end connectivity.

---

## 2. Technology Plan

| Technology | Purpose | Unit 2 Alignment |
|------------|---------|------------------|
| **Django 5.1** | Full-stack Python web framework | Application layer development |
| **Docker + Compose** | Local testbed & production packaging | Infrastructure & portability |
| **PostgreSQL 16** | Local development database | Development environment |
| **Azure SQL Database** | Production managed SQL | Cloud data platform |
| **Azure App Service** | Managed container hosting | Cloud compute infrastructure |
| **Azure Container Registry** | Private Docker image storage | Artifact management |
| **GitHub Actions** | Automated build & deploy | DevOps & CI/CD |
| **Gunicorn** | WSGI HTTP server | Production runtime |
| **python-dotenv** | Environment configuration | Secure secret management |

**Why Azure App Service?**
- Native Docker container support
- Built-in HTTPS / custom domains
- Deployment slots (staging ↔ production swaps)
- Auto-scaling and health checks
- Free F1 tier available for capstone testing
- Direct GitHub Actions integration

---

## 3. Database Design

### 3.1 E-Commerce Schema

| Table | Description |
|-------|-------------|
| `main_customer` | Registered buyer accounts |
| `main_category` | Product taxonomy (Produce, Dairy, Meat, etc.) |
| `main_product` | SKU, name, price, description, stock |
| `main_productimage` | Image metadata (blob URLs) |
| `main_inventory` | Real-time stock quantity tracking |
| `main_order` | Parent order header |
| `main_orderitem` | Individual line items per order |
| `main_deliverytrack` | Shipping/logistics status |
| `main_orderstatuslog` | Audit trail for order state changes |

### 3.2 Key Relationships
- `Customer` → `Order` (one-to-many)
- `Order` → `OrderItem` (one-to-many)
- `Product` → `Category` (many-to-one)
- `Product` → `Inventory` (one-to-one)
- `Order` → `DeliveryTrack` (one-to-one)
- `Order` → `OrderStatusLog` (one-to-many)

### 3.3 Migration Strategy
1. Apply Django migrations (`manage.py migrate`)
2. Seed categories and products (`scripts/seed_db.py`)
3. Seed sample customers and orders for testing

---

## 4. Dual-Environment Architecture

### 4.1 How It Works

One codebase. One environment variable switches everything:

```bash
# Local development
DB_ENGINE=postgresql
DATABASE_URL=postgres://app_user:app_pass@db:5432/app_db

# Azure production
DB_ENGINE=mssql
DATABASE_URL=sqlserver://user:pass@server.database.windows.net:1433/dbname
```

`config/settings.py` reads `DB_ENGINE` and configures the correct Django database backend:
- `postgresql` → `django.db.backends.postgresql`
- `mssql` → `mssql`

### 4.2 File Map

| File | Purpose |
|------|---------|
| `.env.local` | Local PostgreSQL credentials |
| `.env.azure` | Azure SQL connection string |
| `.env.example` | Safe template (no secrets) |
| `docker-compose.yml` | Spins up local Django + PostgreSQL |
| `Dockerfile` | Production image with ODBC Driver 18 for SQL Server |

### 4.3 Dockerfile Highlights

The production image is based on `python:3.12-slim-bookworm` and installs:
- Build tools (for pyodbc compilation)
- Microsoft ODBC Driver 18 for SQL Server
- All Python dependencies from `requirements.txt`

This ensures the container can talk to Azure SQL Database out of the box.

---

## 5. Pre-Saturday Checklist

Complete these **before** the Saturday session so deployment goes smoothly.

| # | Task | Owner | Status |
|---|------|-------|--------|
| 1 | Clone/pull latest repo from GitHub | Everyone | ☐ |
| 2 | Install Docker Desktop (Windows/Mac) or Docker Engine (Linux) | Everyone | ☐ |
| 3 | Install Azure CLI (`az login` works) | Everyone | ☐ |
| 4 | Run local Docker build and confirm `localhost:8000` loads | Everyone | ☐ |
| 5 | Marc confirms Azure subscription is active + payment method set | Marc | ☐ |
| 6 | Review this guide and `docs/Saturday_Test_Plan.md` | Everyone | ☐ |
| 7 | Create shared Azure resource group name (suggestion: `purdue-capstone-rg`) | Team | ☐ |

---

## 6. Local Testbed Setup (Do This First)

Run these steps **before Saturday** to validate the Docker build and understand the app locally.

### Step 1 — Clone & Enter Directory
```bash
git clone https://github.com/esayeed/purdue_capstone.git
cd purdue_capstone
```

### Step 2 — Create Local Environment File
```bash
cp .env.example .env
```
Verify these values are in `.env`:
```
DEBUG=True
SECRET_KEY=your-local-secret-key-here
DB_ENGINE=postgresql
DATABASE_URL=postgres://app_user:app_pass@db:5432/app_db
POSTGRES_DB=app_db
POSTGRES_USER=app_user
POSTGRES_PASSWORD=app_pass
```

### Step 3 — Build & Start Containers
```bash
docker compose up --build -d
```

### Step 4 — Verify Containers Are Running
```bash
docker ps
```
You should see two containers:
- `purdue_capstone-web-1`
- `purdue_capstone-db-1`

### Step 5 — Run Migrations
```bash
docker compose exec web python manage.py migrate
```

### Step 6 — Seed Test Data
```bash
docker compose exec web python scripts/seed_db.py
```

### Step 7 — Test Endpoints
```bash
# Health check
curl http://localhost:8000/health/
# Expected: ok

# Database health check
curl http://localhost:8000/health/db/
# Expected: {"status": "ok", "db": "connected", "engine": "postgresql"}

# Home page
curl http://localhost:8000/
# Expected: Hello, world! This is your Django starter.
```

### Step 8 — Test DB Connectivity Script
```bash
docker compose exec web python scripts/test_db_connection.py
```
Expected output:
```
[PASS] Database connection successful.
[INFO] Tables found: N
RESULT: All checks passed. Database is ready.
```

### Step 9 — Stop Local Environment
```bash
docker compose down
```
To also wipe the database volume:
```bash
docker compose down -v
```

---

## 7. Saturday Deployment Walkthrough

**Goal:** Get the app running on Azure App Service with Azure SQL Database connectivity.

**Estimated Time:** 2–3 hours  
**Prerequisites:** Azure CLI installed, `az login` successful, Azure subscription active.

### Part A — Azure App Service Setup (60–90 min)

#### A1. Log In & Set Variables
```bash
# Log in to Azure
az login

# Set your variables (edit these)
RESOURCE_GROUP="purdue-capstone-rg"
LOCATION="eastus"
APP_NAME="purdue-capstone-app"
ACR_NAME="purduecapstoneacr"
SQL_SERVER="purdue-capstone-sql"
SQL_DB="purdue_capstone_db"
SQL_USER="sqladmin"
SQL_PASSWORD="YourStrongPassword123!"
```

#### A2. Create Resource Group
```bash
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION
```

#### A3. Create Azure Container Registry
```bash
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true
```

#### A4. Log In to ACR
```bash
az acr login --name $ACR_NAME
```

#### A5. Build & Push Docker Image to ACR
```bash
# From the project root directory
az acr build \
  --registry $ACR_NAME \
  --image purdue-capstone:latest \
  .
```

#### A6. Create App Service Plan
```bash
az appservice plan create \
  --resource-group $RESOURCE_GROUP \
  --name "purdue-capstone-plan" \
  --sku B1 \
  --is-linux
```

#### A7. Create Web App for Containers
```bash
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan "purdue-capstone-plan" \
  --name $APP_NAME \
  --deployment-container-image-name "$ACR_NAME.azurecr.io/purdue-capstone:latest"
```

#### A8. Configure ACR Pull Credentials on App Service
```bash
# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query "username" -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

# Set Web App to pull from ACR
az webapp config container set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --docker-custom-image-name "$ACR_NAME.azurecr.io/purdue-capstone:latest" \
  --docker-registry-server-url "https://$ACR_NAME.azurecr.io" \
  --docker-registry-server-user "$ACR_USERNAME" \
  --docker-registry-server-password "$ACR_PASSWORD"
```

#### A9. Set Environment Variables on App Service
```bash
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --settings \
    DEBUG=False \
    SECRET_KEY="your-production-secret-key-change-this" \
    DB_ENGINE=mssql \
    DATABASE_URL="sqlserver://${SQL_USER}:${SQL_PASSWORD}@${SQL_SERVER}.database.windows.net:1433/${SQL_DB}" \
    ALLOWED_HOSTS="${APP_NAME}.azurewebsites.net"
```

#### A10. Verify App Service Deployment
```bash
# Get the URL
az webapp show \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --query "defaultHostName" \
  -o tsv
```

Visit `https://<APP_NAME>.azurewebsites.net/health/` in a browser.  
If it returns `ok`, your container is running on Azure.

---

### Part B — Azure SQL Database Setup (60–90 min)

#### B1. Create SQL Server
```bash
az sql server create \
  --resource-group $RESOURCE_GROUP \
  --name $SQL_SERVER \
  --location $LOCATION \
  --admin-user $SQL_USER \
  --admin-password $SQL_PASSWORD
```

#### B2. Configure Firewall Rules
```bash
# Allow Azure services to access the server
az sql server firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --server $SQL_SERVER \
  --name AllowAllAzureIPs \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# (Optional) Allow your local machine for testing
# Replace with your actual public IP
az sql server firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --server $SQL_SERVER \
  --name AllowLocalIP \
  --start-ip-address <YOUR_PUBLIC_IP> \
  --end-ip-address <YOUR_PUBLIC_IP>
```

#### B3. Create Database
```bash
az sql db create \
  --resource-group $RESOURCE_GROUP \
  --server $SQL_SERVER \
  --name $SQL_DB \
  --service-objective S0 \
  --collation SQL_Latin1_General_CP1_CI_AS
```

#### B4. Test Connectivity from Local Machine
Create `.env.azure` with your Azure SQL connection string:
```bash
DB_ENGINE=mssql
DATABASE_URL="sqlserver://${SQL_USER}:${SQL_PASSWORD}@${SQL_SERVER}.database.windows.net:1433/${SQL_DB}"
```

Run the test script locally (requires pyodbc installed):
```bash
python scripts/test_db_connection.py
```

**Expected:** `[PASS] Database connection successful.`  
**If it fails:** Check firewall rules and ensure `0.0.0.0` rule exists.

#### B5. Run Migrations Against Azure SQL
```bash
# Export Azure env vars temporarily
export DB_ENGINE=mssql
export DATABASE_URL="sqlserver://${SQL_USER}:${SQL_PASSWORD}@${SQL_SERVER}.database.windows.net:1433/${SQL_DB}"

python manage.py migrate
```

#### B6. Seed Test Data in Azure SQL
```bash
python scripts/seed_db.py
```

#### B7. Verify DB Health from Azure App
```bash
curl https://${APP_NAME}.azurewebsites.net/health/db/
```

**Expected:** `{"status": "ok", "db": "connected", "engine": "mssql"}`

---

## 8. Post-Deployment Validation

Run this checklist immediately after Saturday deployment:

| # | Test | Command / URL | Expected Result |
|---|------|---------------|-----------------|
| 1 | App Service health | `curl https://<app>.azurewebsites.net/health/` | `ok` |
| 2 | DB connectivity | `curl https://<app>.azurewebsites.net/health/db/` | `{"status": "ok", "db": "connected", "engine": "mssql"}` |
| 3 | Home page loads | `curl https://<app>.azurewebsites.net/` | HTML response |
| 4 | Admin reachable | `/admin/` | Django admin login page |
| 5 | DB tables exist | `scripts/test_db_connection.py` | Lists all tables |
| 6 | Seed data present | Query `main_product` table | 10 products exist |
| 7 | HTTPS enforced | Browser padlock icon | Valid certificate |
| 8 | Container logs | `az webapp log tail` | No startup errors |
| 9 | Environment vars set | Azure Portal → Configuration | `DB_ENGINE=mssql` visible |
| 10 | ACR image tagged | `az acr repository show-tags` | `latest` exists |

---

## 9. CI/CD Pipeline (GitHub Actions)

**File:** `.github/workflows/azure-deploy.yml`

The pipeline automates everything from Part A:
1. **Build** — Docker image from `Dockerfile`
2. **Check** — `manage.py check --deploy`
3. **Test** — `manage.py test` (if tests exist)
4. **Push** — Image to Azure Container Registry
5. **Deploy** — Update Azure App Service with new image

### Activating CI/CD (After Saturday)

1. Go to **GitHub repo → Settings → Secrets and variables → Actions**
2. Add these repository secrets:
   - `AZURE_CREDENTIALS` — Service principal JSON from `az ad sp create-for-rbac`
   - `AZURE_ACR_NAME` — Your ACR name (e.g., `purduecapstoneacr`)
   - `AZURE_APP_NAME` — Your App Service name (e.g., `purdue-capstone-app`)
3. Push to `main` branch → GitHub Actions triggers automatically

### Manual Trigger (if needed)
```bash
gh workflow run azure-deploy.yml
```

---

## 10. Troubleshooting

### Local Issues

| Symptom | Fix |
|---------|-----|
| `port already in use` | `docker compose down` or change `ports:` in `docker-compose.yml` |
| `OperationalError: could not connect` | Ensure `db` container is healthy: `docker ps` |
| Migration errors | `docker compose exec web python manage.py migrate --run-syncdb` |
| Static files 404 | `docker compose exec web python manage.py collectstatic --noinput` |

### Azure Issues

| Symptom | Fix |
|---------|-----|
| Container fails to start | Check logs: `az webapp log tail --name <app> --resource-group <rg>` |
| `DB connection failed` | Verify firewall rule `AllowAllAzureIPs` exists on SQL Server |
| `Login timeout` | Check `DATABASE_URL` format and credentials |
| 502 Bad Gateway | App crashed; check `PORT=8000` env var is set |
| Image pull failed | Verify ACR credentials in App Service Container Settings |

### Rollback

If everything breaks and you want to start over:
```bash
az group delete --name $RESOURCE_GROUP --yes --no-wait
```
This deletes **everything** in the resource group. You can recreate it in minutes.

---

## Appendix A — Environment Variable Reference

| Variable | Local Value | Azure Value |
|----------|-------------|-------------|
| `DEBUG` | `True` | `False` |
| `SECRET_KEY` | Random string | Strong random string |
| `DB_ENGINE` | `postgresql` | `mssql` |
| `DATABASE_URL` | `postgres://...` | `sqlserver://...` |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | `<app>.azurewebsites.net` |

### DATABASE_URL Format Examples

**PostgreSQL:**
```
postgres://app_user:app_pass@db:5432/app_db
```

**Azure SQL:**
```
sqlserver://sqladmin:YourStrongPassword123!@purdue-capstone-sql.database.windows.net:1433/purdue_capstone_db
```

---

## Appendix B — Quick Command Reference

```bash
# Local
Docker compose up --build -d
docker compose exec web python manage.py migrate
docker compose exec web python scripts/seed_db.py
docker compose exec web python scripts/test_db_connection.py
curl http://localhost:8000/health/
docker compose down

# Azure
az login
az group create --name purdue-capstone-rg --location eastus
az acr build --registry purduecapstoneacr --image purdue-capstone:latest .
az webapp create --resource-group purdue-capstone-rg --plan purdue-capstone-plan --name purdue-capstone-app --deployment-container-image-name purduecapstoneacr.azurecr.io/purdue-capstone:latest
az sql server create --resource-group purdue-capstone-rg --name purdue-capstone-sql --location eastus --admin-user sqladmin --admin-password YourStrongPassword123!
az sql db create --resource-group purdue-capstone-rg --server purdue-capstone-sql --name purdue_capstone_db --service-objective S0
az webapp log tail --name purdue-capstone-app --resource-group purdue-capstone-rg
```

---

## Appendix C — Team Roles for Saturday

| Role | Responsibility |
|------|----------------|
| **Azure Lead** | Runs CLI commands, manages resource group, ACR, App Service |
| **Database Lead** | Manages Azure SQL Server, firewall rules, migrations, seeding |
| **Validation Lead** | Runs health checks, documents results, captures screenshots |
| **Scribe** | Updates this guide with actual values, notes blockers |

---

*Last updated: June 26, 2026*  
*For questions or issues, refer to the individual docs in the `docs/` folder or open a GitHub issue.*
