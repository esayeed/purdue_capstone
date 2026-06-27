# Technology Plan — Purdue Capstone E-Commerce Platform

> **Purpose:** Map every technology decision to the Unit 2 Project Scope Statement so the team knows what to build, when, and why.  
> **Project:** Cloud-Based E-Commerce Platform for Direct Customer Ordering & Logistics  
> **Course:** IT473 Capstone  
> **Date:** June 26, 2026

---

## 1. How This Document Is Organized

Each section follows this pattern:
1. **Business Need** (from Unit 2 Scope Statement)
2. **Technology Choice**
3. **Azure Service / Tool**
4. **When We Build It** (Unit #)
5. **How We Test It Before Coding**
6. **Risks & Mitigations**

---

## 2. Application Hosting

### Business Need
> "Develop a cloud-hosted e-commerce application."

### Technology Choice
**Docker container running Django + Gunicorn**

### Azure Service
**Azure App Service (Web App for Containers)**
- **Tier:** Free (F1) for Unit 4–5 testing; Standard (S1) for Unit 6–8 production features
- **Why:** Native Docker support, GitHub Actions integration, automatic HTTPS, log streaming, staging slots

### When We Build It
- **Unit 4:** Deploy first container to App Service (F1)
- **Unit 6:** Upgrade to S1 for staging slots and custom domains
- **Unit 8:** Configure slot swap (staging → production) in CI/CD pipeline

### How We Test It Before Coding
1. **Local Docker testbed:** `docker compose up` runs PostgreSQL + Django locally. Verify at `http://localhost:8000` and `http://localhost:8000/health/`.
2. **Container build test:** `docker build -t purdue-capstone .` must complete without errors.
3. **Azure dry-run:** Push image to Azure Container Registry and deploy to a temporary App Service to confirm the image pulls and starts.

### Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| Image too large / build fails | Use `python:3.12-slim-bookworm` base; multi-stage build if needed |
| App Service cold start slow | Keep container lightweight; use Free tier only for demos |
| Port binding issues | Gunicorn binds to `0.0.0.0:8000`; App Service maps port 8000 automatically |

---

## 3. Database

### Business Need
> "Implement a Microsoft SQL Server database environment responsible for storing customer information, product catalogs, inventory data, order information, and reporting metrics."

### Technology Choice
**Microsoft SQL Server — Azure SQL Database**

### Azure Service
**Azure SQL Database (Single Database)**
- **Tier:** General Purpose — Serverless (auto-pauses when idle) or S0 (10 DTUs)
- **Why:** Managed service (no OS patching), TDE encryption enabled by default, geo-replica ready, integrates with Django via `mssql-django`

### When We Build It
- **Unit 4:** Provision SQL Server + Database; run initial migrations
- **Unit 5:** Create tables from Django models; seed test data
- **Unit 6:** Enable Private Endpoint (remove public internet access); verify TDE
- **Unit 7:** Monitor query performance; add read replica if needed for analytics

### How We Test It Before Coding
1. **Local simulation:** PostgreSQL runs in Docker locally with identical schema. Django models and migrations are tested locally first.
2. **Connection test script:** `scripts/test_db_connection.py` validates connectivity to any database engine (PostgreSQL or SQL Server) and lists tables.
3. **Saturday test:** Deploy Azure SQL Database, set firewall rules, run `test_db_connection.py` against the live Azure endpoint. If it fails, debug driver/encryption/firewall before writing application logic.

### Dual-Environment Strategy
| Environment | Engine | Driver | Purpose |
|-------------|--------|--------|---------|
| Local Dev | PostgreSQL | `psycopg[binary]` | Fast iteration, no Azure dependency |
| Azure Prod | SQL Server | `mssql-django` + `pyodbc` + ODBC Driver 18 | Meets capstone rubric |

**Switching is one environment variable:** `DB_ENGINE=postgresql` vs `DB_ENGINE=mssql`.

### Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| `mssql-django` compatibility issues | Test locally with SQL Server Express or Azure SQL Edge Docker image before Saturday |
| ODBC Driver 18 not installed in container | Dockerfile now installs `msodbcsql18` automatically |
| Firewall blocks App Service | Use "Allow Azure services" rule during testing; replace with Private Endpoint in Unit 6 |
| Migration conflicts between PostgreSQL and SQL Server | Keep migrations simple (no raw SQL); test migrations on both engines |

---

## 4. Static & Media File Storage

### Business Need
> "Product images, documents, and static assets must be served efficiently."

### Technology Choice
**Azure Blob Storage** for images/documents + **Azure CDN** for edge caching

### Azure Service
- **Blob Storage:** Standard LRS (locally redundant) tier
- **CDN:** Azure Front Door or Azure CDN (Standard Microsoft)

### When We Build It
- **Unit 5:** Create Blob Storage account and container; upload product images
- **Unit 5:** Create CDN endpoint linked to Blob Storage
- **Unit 6:** Secure Blob Storage with SAS tokens or managed identity

### How We Test It Before Coding
1. **Local placeholder:** Store images in `media/` folder locally; Django `ImageField` uses local filesystem.
2. **CDN simulation:** Not needed locally — CDN is a transparent optimization. Test by verifying image URLs are publicly accessible after upload.
3. **Upload test:** Write a small script that uploads a test image to Blob Storage and returns the CDN URL. If this works, the Django integration will work.

### Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| CDN misconfiguration | Use Azure portal's "Quick start" wizard; verify with `curl -I <cdn-url>` |
| Blob public access disabled | Set container access level to "Blob (anonymous read)" for product images |
| Cost overruns | LRS is cheapest; set lifecycle policy to move old images to Cool tier |

---

## 5. Networking & Security

### Business Need
> "The infrastructure will include virtual private networking, load balancing, firewall protection, HTTPS encryption, authentication controls, authorization mechanisms, error logging, alert monitoring, and automated backup procedures."

### Technology Choices
| Requirement | Technology |
|-------------|------------|
| Virtual private networking | Azure Virtual Network (VNet) + 3 subnets (web, app, db) |
| Load balancing + WAF | Azure Application Gateway + WAF_v2 |
| Firewall rules | Network Security Groups (NSGs) per subnet |
| HTTPS encryption | App Service managed certificate (automatic) + TLS 1.3 |
| Authentication | Django built-in auth + Azure AD (optional, Unit 6+) |
| Secrets management | Azure Key Vault |
| Monitoring | Azure Monitor + Application Insights |
| Backups | Azure SQL automated backups + Blob Storage versioning |

### When We Build It
- **Unit 4:** Basic App Service + SQL firewall rules (open to Azure services)
- **Unit 6:** VNet, NSGs, Key Vault, Private Endpoint for SQL, Application Gateway + WAF
- **Unit 7:** Monitor dashboards, alert rules for CPU and HTTP 5xx

### How We Test It Before Coding
1. **NSG simulation:** Not applicable locally; verified in Azure portal after deployment.
2. **HTTPS test:** Visit `https://<app>.azurewebsites.net` — certificate should be valid and auto-renewing.
3. **WAF test:** Use a tool like `nmap` or an online scanner to verify common ports are closed and OWASP rules block SQL injection payloads.
4. **Key Vault test:** Store a fake secret, retrieve it via Azure CLI, confirm the app can read it using Managed Identity.

### Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| Private Endpoint breaks app connectivity | Document working config; test before/after each change |
| WAF false positives block legitimate traffic | Start with OWASP "Detection" mode before "Prevention" |
| Key Vault access denied | Assign "Key Vault Secrets User" role to App Service managed identity |

---

## 6. CI/CD Pipeline

### Business Need
> "Deploy the solution using modern cloud infrastructure and CI/CD methodologies."

### Technology Choice
**GitHub Actions**

### Why GitHub Actions
- Repo already lives on GitHub (`esayeed/purdue_capstone`)
- Free for public repositories
- Native integration with Azure App Service (official `azure/webapps-deploy` action)
- Team can trigger deployments from VS Code via Git push

### Pipeline Stages
```
Push to main
    ├── Build Docker image
    ├── Run Django checks
    ├── Run pytest (if tests exist)
    ├── Push image to Azure Container Registry
    └── Deploy to App Service staging slot
        └── Manual approval → swap to production (Unit 8)
```

### When We Build It
- **Unit 4:** Create basic workflow that builds the image (no deploy yet)
- **Unit 8:** Full pipeline with staging slot, tests, and automated deployment

### How We Test It Before Coding
1. **Local dry-run:** The `build-and-test` job in `.github/workflows/azure-deploy.yml` runs on every PR. If it passes, the deploy stage will likely pass too.
2. **Manual deploy first:** Before automating, manually run `az acr build` and `az webapp deploy` from your laptop. Once that works, codify the steps into GitHub Actions.
3. **Secrets validation:** Confirm `AZURE_CREDENTIALS`, `AZURE_ACR_NAME`, and `AZURE_APP_NAME` are set as GitHub repository secrets.

### Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| GitHub Actions fails silently | Add `set -x` to shell steps; use `actions/upload-artifact` for logs |
| Service principal expires | Set calendar reminder 80 days before expiration; rotate secrets |
| Deployment succeeds but app crashes | Add a `/health/` smoke test step after deploy; rollback on failure |

---

## 7. Monitoring & Observability

### Business Need
> "Monitoring and alerting systems will provide visibility into application health, performance issues, and security-related events."

### Technology Choice
**Azure Monitor + Application Insights**

### When We Build It
- **Unit 6:** Enable Application Insights for the App Service
- **Unit 7:** Create custom dashboard (CPU, memory, requests, failures); set alert rules

### How We Test It Before Coding
1. **Local logging:** Django logs to stdout in Docker; view with `docker compose logs -f web`.
2. **Azure test:** After enabling Application Insights, generate 404 errors and slow requests. Confirm they appear in the "Failures" and "Performance" blades within 5 minutes.

---

## 8. Analytics & Reporting

### Business Need
> "An analytics dashboard will be developed to display customer satisfaction metrics, sales information, inventory trends, and logistics performance indicators."

### Technology Choices
| Requirement | Technology | When |
|-------------|------------|------|
| Operational reporting | Django Admin + custom views | Unit 5–6 |
| Business intelligence dashboard | Power BI Embedded or Django charts | Unit 7 |
| Data warehouse (optional) | Azure Synapse Analytics | Beyond capstone scope |

### How We Test It Before Coding
1. **Django admin:** Verify models are registered in `admin.py` and data appears after seeding.
2. **Chart test:** Use a library like `Chart.js` with static JSON data first. Once the UI looks right, wire it to a Django API endpoint.

---

## 9. Summary Table: Technology → Unit Mapping

| Technology | Azure Service / Tool | Unit 4 | Unit 5 | Unit 6 | Unit 7 | Unit 8 |
|------------|---------------------|--------|--------|--------|--------|--------|
| App Hosting | App Service (Docker) | ✅ Deploy | ✅ Upgrade S1 | ✅ Slots | ✅ Scale | ✅ CI/CD |
| Database | Azure SQL Database | ✅ Provision | ✅ Schema | ✅ Private EP | ✅ Monitor | ✅ Backup test |
| Blob Storage | Blob Storage + CDN | | ✅ Create | ✅ Secure | | |
| Networking | VNet + NSG + App Gateway | | | ✅ Deploy | ✅ Health probes | |
| Security | Key Vault + WAF + TDE | | | ✅ Enable | ✅ Verify | |
| Monitoring | Monitor + App Insights | | | ✅ Enable | ✅ Dashboard | ✅ Alerts |
| CI/CD | GitHub Actions | ✅ Build | | | | ✅ Deploy |
| Analytics | Django Admin / Power BI | | | | ✅ Dashboard | |

---

## 10. Pre-Coding Test Configurations

Before writing full application features, run these validation configs in order:

### Test 1: Local Docker Smoke Test
```bash
cp .env.example .env
docker compose up --build -d
curl http://localhost:8000/health/
# Expected: ok
```

### Test 2: Database Connectivity (Local)
```bash
docker compose exec web python scripts/test_db_connection.py
# Expected: [PASS] Database connection successful.
```

### Test 3: Azure SQL Connectivity (Saturday)
```bash
export DB_ENGINE=mssql
export DB_HOST=sql-capstone-2502c.database.windows.net
export DB_NAME=food-distributor-db
export DB_USER=dbadmin
export DB_PASSWORD='***'
python scripts/test_db_connection.py
# Expected: [PASS] Database connection successful.
```

### Test 4: Django Migrations on Azure SQL
```bash
docker run --rm -e DB_ENGINE=mssql -e DB_HOST=... -e DB_NAME=... \
  -e DB_USER=... -e DB_PASSWORD=... -e DJANGO_SECRET_KEY=... \
  purduecapstoneacr.azurecr.io/purdue-capstone:latest \
  python manage.py migrate
# Expected: All migrations apply without errors.
```

### Test 5: Seed Data Validation
```bash
docker compose exec web python scripts/seed_db.py
docker compose exec web python manage.py shell -c "from apps.main.models import Product; print(Product.objects.count())"
# Expected: 10
```

### Test 6: CI/CD Build Validation
```bash
# On every push to any branch, GitHub Actions runs:
# 1. django-admin check
# 2. pytest (if tests exist)
# Verify the build badge is green before merging to main.
```

---

*Plan created: June 26, 2026*  
*Sources: Unit 2 Project Scope Statement, Unit 3 Assignment Instructions, Microsoft Azure documentation*
