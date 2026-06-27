# Azure Deployment Options Guide for Purdue Capstone

> **Purpose:** Help the team understand Azure compute options so we can pick the right service for hosting our Django e-commerce app.  
> **Target Audience:** Team members new to Azure (especially Esam, King Natie, Marriette).  
> **Date:** June 26, 2026

---

## TL;DR — Recommendation

For this capstone project, use **Azure App Service (Web App for Containers)**. It is the simplest path from a Docker container to a live URL, integrates directly with GitHub Actions, supports custom domains, and has a generous free tier. The other options add complexity we do not need at this stage.

---

## Option 1: Azure App Service (Web App for Containers) ⭐ RECOMMENDED

### What It Is
App Service is Azure's managed platform for running web applications. You give it code (Python, Node.js, etc.) or a Docker image, and Azure handles the server, operating system, scaling, load balancing, and SSL certificates for you.

### How It Works with Our Project
```
GitHub Repo → GitHub Actions → Build Docker Image → Push to Azure Container Registry 
                                                                    ↓
                                                           Azure App Service
                                                                    ↓
                                                              Live URL (HTTPS)
```

### Why It Fits Our Capstone
| Feature | Why It Helps Us |
|---------|-----------------|
| **Docker support** | We can deploy our existing `Dockerfile` with zero changes |
| **GitHub Actions integration** | Push to `main` → auto-deploy (Unit 8 requirement) |
| **Free/Shared tier (F1)** | Costs $0 for development and testing |
| **Standard tier (S1)** | Supports staging slots, custom domains, and auto-scaling (Units 6–7) |
| **Built-in HTTPS** | SSL certificate handled automatically |
| **Log streaming** | View container logs in real time from the Azure portal |
| **Easy rollback** | Swap between staging and production slots instantly |

### Cost
- **Free tier (F1):** $0 — 1 GB RAM, 1 GB disk, shared CPU. Good for demos and early testing.
- **Basic tier (B1):** ~$13/month — dedicated CPU, custom domain support.
- **Standard tier (S1):** ~$73/month — staging slots, auto-scaling, 1.75 GB RAM.

For the capstone, start on **F1 or B1** and upgrade to **S1** only when you need staging slots in Unit 8.

### How We Will Use It
1. Build our Django app into a Docker image locally (this weekend).
2. Push the image to **Azure Container Registry (ACR)** or have App Service build directly from GitHub.
3. App Service pulls the image and serves it at `https://<your-app>.azurewebsites.net`.
4. Connect to Azure SQL Database using environment variables (no secrets in code).

---

## Option 2: Azure Container Apps

### What It Is
Container Apps is a serverless container platform. It runs Docker containers but abstracts away even more of the infrastructure than App Service. It is designed for microservices (many small apps talking to each other).

### How It Works with Our Project
```
GitHub Actions → Build Docker Image → Push to ACR → Container Apps Revision
                                                    ↓
                                            Live URL (HTTPS via built-in ingress)
```

### Pros and Cons
| Pros | Cons |
|------|------|
| Scales to zero (costs nothing when idle) | More complex networking setup |
| Built-in load balancing and traffic splitting | No persistent filesystem (uploaded files need Blob Storage) |
| Good for microservices | Harder to debug for beginners |
| Cheaper at very low traffic | No native staging slot concept |

### Verdict
**Overkill for our capstone.** We have one monolithic Django app, not 5+ microservices. The learning curve is steeper and the debugging experience is worse for beginners.

---

## Option 3: Azure Container Instances (ACI)

### What It Is
ACI is the simplest way to run a single Docker container in Azure. You give it an image and it runs. No orchestration, no scaling rules, no load balancer.

### How It Works with Our Project
```
Docker Image → Push to ACR → Azure Container Instance
                                    ↓
                            Public IP + Port
```

### Pros and Cons
| Pros | Cons |
|------|------|
| Extremely simple — one command to run | No built-in HTTPS (you must add your own) |
| Fast startup (~seconds) | No auto-scaling at all |
| Pay per second of usage | No persistent storage without mounting Azure Files |
| Good for one-off jobs | Not designed for long-running web apps |

### Verdict
**Not suitable for our capstone.** ACI is designed for batch jobs, scheduled tasks, or temporary containers. A production Django web app needs HTTPS, scaling, and a stable domain name — all of which require extra work with ACI.

---

## Side-by-Side Comparison

| Criteria | App Service ⭐ | Container Apps | Container Instances |
|----------|---------------|----------------|---------------------|
| **Best for** | Single web apps | Microservices | One-off tasks |
| **Docker support** | ✅ Yes | ✅ Yes | ✅ Yes |
| **HTTPS out-of-the-box** | ✅ Yes | ✅ Yes | ❌ No |
| **Auto-scaling** | ✅ Yes (Standard+) | ✅ Yes (built-in) | ❌ No |
| **Staging slots** | ✅ Yes (Standard+) | ⚠️ Revisions | ❌ No |
| **GitHub Actions ease** | ✅ Very easy | ⚠️ Moderate | ⚠️ Moderate |
| **Free tier available** | ✅ Yes | ✅ Yes ( Consumption ) | ❌ No |
| **Persistent files** | ✅ Yes (slow, but works) | ❌ No | ⚠️ Azure Files mount |
| **Beginner friendly** | ✅ Yes | ⚠️ Medium | ⚠️ Medium |
| **Fits capstone rubric** | ✅ Perfect | ⚠️ Overkill | ❌ Wrong tool |

---

## Azure SQL Database — How It Connects

No matter which compute option we choose, the database connection works the same way:

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  Your Browser   │──────▶│  Azure App Svc   │──────▶│ Azure SQL DB    │
│                 │      │  (Django Docker) │      │ (food-distributor-db)
└─────────────────┘      └──────────────────┘      └─────────────────┘
                                │                           │
                                ▼                           ▼
                        Reads connection              Stores customers,
                        string from env var           products, orders,
                        (no hardcoded secrets)        inventory, tracking
```

### Connection String Format
```
Driver={ODBC Driver 18 for SQL Server};Server=tcp:<server>.database.windows.net,1433;Database=<db>;Uid=<user>;Pwd=<pass>;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;
```

Django will use `mssql-django` (which wraps `pyodbc`) to translate ORM queries into SQL Server commands.

---

## Recommended Azure Service Stack (Unit-by-Unit)

| Unit | Service | Tier | Purpose |
|------|---------|------|---------|
| **Unit 4** | App Service | Free (F1) | Get Django running on Azure |
| **Unit 4** | Azure SQL Database | General Purpose — Serverless | Database with pay-per-use |
| **Unit 5** | Blob Storage | Standard LRS | Product images |
| **Unit 5** | Container Registry | Basic | Store Docker images |
| **Unit 6** | Key Vault | Standard | Secrets management |
| **Unit 6** | Application Insights | Pay-as-you-go | Monitoring |
| **Unit 7** | App Service | Standard S1 | Auto-scaling, staging slots |
| **Unit 8** | GitHub Actions | Free | CI/CD pipeline |

---

## Next Steps

1. **Before Saturday:** Run the app locally with Docker using the `Local_Testbed_Setup.md` guide.
2. **Saturday:** Follow the `Saturday_Test_Plan.md` to deploy the Docker container to Azure App Service and test Azure SQL connectivity.
3. **Unit 4+:** Upgrade the App Service tier and add Blob Storage, Key Vault, and monitoring.

---

*Guide created: June 26, 2026*  
*Sources: Microsoft Azure documentation, Purdue IT473 Project Scope Statement*
