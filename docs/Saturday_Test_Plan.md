# Saturday Test Plan — Azure Deployment & Database Connectivity

> **Purpose:** A step-by-step playbook for Saturday's team session to (1) deploy the Docker container to Azure App Service and (2) verify connectivity to Azure SQL Database.  
> **Assumptions:** Local Docker build already works (see `Local_Testbed_Setup.md`).  
> **Duration:** 2–3 hours  
> **Team Members Needed:** Esam (lead), Marc (Azure admin), others (observe/learn)

---

## Pre-Saturday Checklist (Do Friday Night)

- [ ] Local `docker compose up` runs successfully
- [ ] `docker build -t purdue-capstone .` completes without errors
- [ ] Marc (or designated Azure admin) has an active Azure subscription
- [ ] GitHub repo is up to date with the latest code
- [ ] Everyone has the Azure CLI installed: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

---

## Part A: Deploy Docker Container to Azure App Service (60–90 min)

### Step A1: Log In to Azure

```bash
az login
```

A browser window opens. Sign in with the Azure admin account.

### Step A2: Create Resource Group

```bash
az group create \
  --name rg-purdue-capstone \
  --location eastus
```

**What is a Resource Group?** A folder in Azure that holds all the services for this project. Deleting the group later deletes everything inside it.

### Step A3: Create Azure Container Registry (ACR)

```bash
az acr create \
  --resource-group rg-purdue-capstone \
  --name purduecapstoneacr \
  --sku Basic \
  --location eastus
```

**Why ACR?** Azure needs a place to store your Docker image. ACR is like Docker Hub but private and inside Azure.

### Step A4: Log In to ACR

```bash
az acr login --name purduecapstoneacr
```

### Step A5: Build and Push Docker Image

```bash
# Tag your local image for ACR
docker build -t purduecapstoneacr.azurecr.io/purdue-capstone:latest .

# Push to ACR
docker push purduecapstoneacr.azurecr.io/purdue-capstone:latest
```

**Troubleshooting:** If `docker push` fails with "denied", re-run `az acr login` and ensure the ACR name is correct.

### Step A6: Create App Service Plan

```bash
az appservice plan create \
  --resource-group rg-purdue-capstone \
  --name capstone-plan \
  --sku B1 \
  --is-linux
```

**What is an App Service Plan?** The "server" that runs your app. B1 is the cheapest paid tier ($~13/month) with a dedicated CPU. For pure testing, you can use F1 (Free) but it has limitations (no custom domains, no staging slots).

### Step A7: Create the Web App (Container Mode)

```bash
az webapp create \
  --resource-group rg-purdue-capstone \
  --plan capstone-plan \
  --name purdue-food-distributor \
  --deployment-container-image-name purduecapstoneacr.azurecr.io/purdue-capstone:latest
```

**Note:** Replace `purdue-food-distributor` with a globally unique name (e.g., `purdue-food-distributor-2502c`). App Service URLs must be unique worldwide.

### Step A8: Enable ACR Pull Permissions

```bash
az webapp identity assign \
  --resource-group rg-purdue-capstone \
  --name purdue-food-distributor

# Get the principal ID
SP_ID=$(az webapp identity show \
  --resource-group rg-purdue-capstone \
  --name purdue-food-distributor \
  --query principalId \
  --output tsv)

# Grant ACR pull access
az role assignment create \
  --assignee $SP_ID \
  --scope $(az acr show --name purduecapstoneacr --query id --output tsv) \
  --role "AcrPull"
```

### Step A9: Verify Deployment

Wait 2–3 minutes, then visit:

```
https://purdue-food-distributor.azurewebsites.net
```

You should see your Django app running.

Also test:
```
https://purdue-food-distributor.azurewebsites.net/health/
```

Expected: `ok`

---

## Part B: Provision Azure SQL Database & Test Connectivity (60–90 min)

### Step B1: Create SQL Server

```bash
az sql server create \
  --resource-group rg-purdue-capstone \
  --name sql-capstone-2502c \
  --location eastus \
  --admin-user dbadmin \
  --admin-password '<STRONG_PASSWORD_HERE>'
```

**Password requirements:** At least 8 characters, uppercase, lowercase, number, and special character.

### Step B2: Create SQL Database

```bash
az sql db create \
  --resource-group rg-purdue-capstone \
  --server sql-capstone-2502c \
  --name food-distributor-db \
  --service-objective S0
```

**Tiers explained:**
- **S0** (Standard, 10 DTUs): ~$15/month. Sufficient for capstone testing.
- **S2** (Standard, 50 DTUs): ~$30/month. Use if you need more performance in Unit 7.
- **Serverless:** Pay per second of usage. Good if the database is only active during meetings.

### Step B3: Allow Azure Services to Access SQL Server

```bash
az sql server firewall-rule create \
  --resource-group rg-purdue-capstone \
  --server sql-capstone-2502c \
  --name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

**What does this do?** Allows any Azure service (including your App Service) to connect to the database. For production (Unit 6), we will replace this with a Private Endpoint.

### Step B4: Get the Connection String

```bash
az sql db show-connection-string \
  --client ado.net \
  --name food-distributor-db \
  --server sql-capstone-2502c
```

Copy the output. It looks like:
```
Server=tcp:sql-capstone-2502c.database.windows.net,1433;Database=food-distributor-db;User ID=dbadmin;Password=<STRONG_PASSWORD_HERE>;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;
```

### Step B5: Convert to Django Format

Django uses a different connection format. Create an environment variable for the App Service:

```bash
az webapp config appsettings set \
  --resource-group rg-purdue-capstone \
  --name purdue-food-distributor \
  --settings \
    "DJANGO_SECRET_KEY=<GENERATE_A_LONG_RANDOM_STRING>" \
    "DJANGO_DEBUG=0" \
    "DJANGO_ALLOWED_HOSTS=purdue-food-distributor.azurewebsites.net" \
    "DB_ENGINE=mssql" \
    "DB_NAME=food-distributor-db" \
    "DB_USER=dbadmin" \
    "DB_PASSWORD=<STRONG_PASSWORD_HERE>" \
    "DB_HOST=sql-capstone-2502c.database.windows.net" \
    "DB_PORT=1433"
```

**Generate a secret key:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### Step B6: Update Django Settings for Azure SQL

The `settings.py` must support both PostgreSQL (local) and SQL Server (Azure). This is already handled by environment variables in the updated `config/settings.py`.

Verify the App Service has the correct settings:
```bash
az webapp config appsettings list \
  --resource-group rg-purdue-capstone \
  --name purdue-food-distributor \
  --output table
```

### Step B7: Restart the App Service

```bash
az webapp restart \
  --resource-group rg-purdue-capstone \
  --name purdue-food-distributor
```

### Step B8: Test Database Connectivity

**Method 1 — Via the App (Best)**

Create a test view in Django that queries the database and returns a simple count. Then visit:
```
https://purdue-food-distributor.azurewebsites.net/health/db/
```

If it returns `{"status": "ok", "db": "connected"}`, the database connection works.

**Method 2 — Via Azure Cloud Shell**

Open Azure Cloud Shell in the portal and run:
```bash
sqlcmd -S sql-capstone-2502c.database.windows.net -d food-distributor-db -U dbadmin -P '<PASSWORD>' -Q "SELECT COUNT(*) FROM sys.tables;"
```

**Method 3 — Local Test Script**

Use the provided `scripts/test_db_connection.py` locally with the Azure credentials:
```bash
export DB_HOST=sql-capstone-2502c.database.windows.net
export DB_NAME=food-distributor-db
export DB_USER=dbadmin
export DB_PASSWORD='<PASSWORD>'
python scripts/test_db_connection.py
```

### Step B9: Run Django Migrations on Azure SQL

**Option A — Azure SSH Console (Easiest)**
1. Go to the Azure Portal → App Service → SSH
2. In the browser-based terminal:
```bash
cd /app
python manage.py migrate
python manage.py createsuperuser
```

**Option B — Run Migration as a One-Off Container Locally**
```bash
# Run a temporary container with Azure env vars
docker run --rm -it \
  -e DB_ENGINE=mssql \
  -e DB_HOST=sql-capstone-2502c.database.windows.net \
  -e DB_NAME=food-distributor-db \
  -e DB_USER=dbadmin \
  -e DB_PASSWORD='<PASSWORD>' \
  -e DJANGO_SECRET_KEY='<SECRET>' \
  purduecapstoneacr.azurecr.io/purdue-capstone:latest \
  python manage.py migrate
```

---

## Part C: Validation Checklist (Run as a Team)

Before ending the Saturday session, confirm every item below:

| # | Test | Method | Pass/Fail |
|---|------|--------|-----------|
| 1 | App Service URL loads | Browser visit | |
| 2 | Health check returns `ok` | Browser visit `/health/` | |
| 3 | Admin panel loads | Browser visit `/admin/` | |
| 4 | Superuser can log in | Manual login | |
| 5 | Database migrations ran | SSH console: `python manage.py showmigrations` | |
| 6 | No secrets in code | Review `settings.py` — only `os.getenv` | |
| 7 | Environment variables set in App Service | Portal → Configuration | |
| 8 | ACR image pull works | Portal → Deployment Center → Logs | |
| 9 | SQL firewall allows Azure services | Portal → SQL Server → Networking | |
| 10 | Database connectivity test passes | Visit `/health/db/` or run `scripts/test_db_connection.py` | |

---

## Part D: Rollback Plan (If Something Breaks)

If the Azure deployment fails and you cannot debug it during the session:

1. **Revert to local Docker:** Continue development locally. Azure deployment can be retried independently.
2. **Delete and recreate:**
   ```bash
   az group delete --name rg-purdue-capstone --yes --no-wait
   ```
   Then re-run Steps A1–A9. The Resource Group deletion removes everything so you start fresh.
3. **Use Azure Free Tier (F1):** If cost is a concern, switch the App Service Plan to F1:
   ```bash
   az appservice plan update --name capstone-plan --sku F1
   ```
   Note: F1 does not support staging slots or custom domains.

---

## Post-Saturday Action Items

| Task | Owner | Due |
|------|-------|-----|
| Screenshot: App Service Overview page | Marc | Saturday night |
| Screenshot: SQL Database Overview page | Marc | Saturday night |
| Screenshot: ACR repository with image | Marc | Saturday night |
| Screenshot: App running at `.azurewebsites.net` | Esam | Saturday night |
| Update `Project Update` document with Unit 4 progress | Scribe | Sunday |
| Open GitHub issue documenting any Azure errors encountered | Esam | Sunday |
| Schedule Unit 4 individual paper writing session | Facilitator | Monday |

---

*Plan created: June 26, 2026*  
*Sources: Microsoft Azure CLI documentation, Django deployment guides, IT473 Project Scope Statement*
