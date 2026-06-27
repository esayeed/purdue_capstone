# Unit 3 Team Meeting Agenda — Pre-Saturday Planning

> **Date:** Tomorrow night (Thursday)  
> **Goal:** Review technology plan, assign pre-Saturday tasks, and prepare the team for Saturday's Azure deployment & database connectivity tests.  
> **Duration:** 60 minutes  
> **Required:** All team members (Esam, Marc, King Natie, Marriette)

---

## Pre-Meeting (5 min)

- [ ] Facilitator (Esam) shares screen with this agenda
- [ ] Scribe (Marc) opens shared document for live notes
- [ ] Everyone confirms access to the Nextcloud `purdue_capstone` folder

---

## 1. Technology Plan Review (15 min)

**Presenter:** Esam  
**Materials:** `docs/Technology_Plan.md`

Walk through each section:
1. **Application Hosting:** Azure App Service (Web App for Containers) — why this beats Container Apps / Container Instances
2. **Database:** Dual-environment strategy (PostgreSQL local / Azure SQL production)
3. **Storage:** Blob Storage + CDN for product images
4. **Security:** VNet, NSGs, Key Vault, WAF, Private Endpoint
5. **CI/CD:** GitHub Actions pipeline overview
6. **Monitoring:** Application Insights + Azure Monitor

**Decision needed:** Does the team agree with the App Service recommendation? (Vote: thumbs up/down)

---

## 2. Azure Deployment Options Deep Dive (10 min)

**Presenter:** Esam (with Marc contributing Azure experience)  
**Materials:** `docs/Azure_Deployment_Options_Guide.md`

Cover:
- What is Azure App Service? (managed web hosting)
- What is Azure Container Registry? (Docker image storage)
- What is Azure SQL Database? (managed SQL Server)
- Cost expectations: ~$15–30/month during active development
- How to stay on Free tier (F1) until Unit 6

**Marc's role:** Confirm Azure subscription status and student credit availability.

---

## 3. Database Design Review (10 min)

**Presenter:** Esam  
**Materials:** `docs/Database_Design.md`

Review:
- 9 tables: Customer, Category, Product, ProductImage, Inventory, Order, OrderItem, DeliveryTrack, OrderStatusLog
- Django models ready to drop into `apps/main/models.py`
- Relationship diagram (one-to-many, many-to-many, one-to-one)

**Team task:** Agree on table names and field types. Any missing fields?

---

## 4. Pre-Saturday Individual Tasks (10 min)

| Task | Owner | Due | How to Verify |
|------|-------|-----|---------------|
| Install Docker Desktop | Esam, King Natie, Marriette | Friday | `docker --version` returns a version |
| Run local Docker testbed | Esam | Friday | `curl http://localhost:8000/health/` returns `ok` |
| Confirm Azure subscription active | Marc | Friday | Can log into portal.azure.com |
| Review Database Design doc | All | Friday | Post 1 question or approval in Discord |
| Review Saturday Test Plan | All | Friday | Post 1 question or approval in Discord |
| Install Azure CLI | Marc | Friday | `az --version` returns a version |
| Create GitHub accounts (if missing) | King Natie, Marriette | Friday | Can view https://github.com/esayeed/purdue_capstone |

---

## 5. Saturday Session Planning (10 min)

**Presenter:** Esam  
**Materials:** `docs/Saturday_Test_Plan.md`

Agenda for Saturday (2–3 hours):
1. **Part A:** Deploy Docker container to Azure App Service (60–90 min)
   - Marc leads Azure CLI commands
   - Esam verifies Django app loads at `.azurewebsites.net`
2. **Part B:** Provision Azure SQL Database & test connectivity (60–90 min)
   - Marc provisions SQL Server + Database
   - Esam runs `scripts/test_db_connection.py` against Azure
   - Team runs migrations and seeds test data
3. **Part C:** Validation checklist (15 min)
   - Walk through the 10-item checklist in the test plan
   - Capture screenshots for Unit 4 Project Update

**Required for Saturday:**
- Laptop with Docker and Azure CLI
- Stable internet
- Azure admin credentials (Marc)
- GitHub repo access (everyone)

---

## 6. GitHub & CI/CD Overview (5 min)

**Presenter:** Esam  
**Materials:** `.github/workflows/azure-deploy.yml`

Explain:
- GitHub Actions runs on every push to `main`
- It builds the Docker image, runs Django checks, and deploys to Azure
- Team members can trigger deployments by pushing code from VS Code
- Secrets (`AZURE_CREDENTIALS`, `AZURE_ACR_NAME`, `AZURE_APP_NAME`) are stored in GitHub — not in code

**Action:** After Saturday's successful deployment, Esam will add the real secrets to GitHub.

---

## 7. Questions & Wrap-Up (5 min)

- Open floor for questions
- Confirm Saturday meeting time and location (Discord voice / Zoom)
- Scribe distributes notes within 24 hours

---

## Post-Meeting Action Items

| Task | Owner | Due |
|------|-------|-----|
| Add Django models to `apps/main/models.py` | Esam | Friday |
| Create initial migration | Esam | Friday |
| Test local Docker build with new models | Esam | Friday |
| Post meeting notes to Discord | Marc | Friday night |
| Confirm Azure subscription + student credit | Marc | Friday |
| Install Docker + Azure CLI | King Natie, Marriette | Friday |

---

*Agenda created: June 26, 2026*  
*Sources: Unit 3 Assignment Instructions, Saturday Test Plan, Technology Plan*
