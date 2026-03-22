# INDMoney Pulse: Production Architecture

This document outlines the production-ready full-stack architecture for the **INDMoney Weekly Product Pulse** system. 

The system is transitioning from a standalone Python script into a robust API-first application with a React-based frontend and containerized backend.

---

## 🏗️ System Overview

The updated architecture separates the pipeline logic into a stateless FastAPI backend and a dynamic Next.js frontend, orchestrated via Docker and automated by GitHub Actions.

### 🧩 High-Level System Diagram

```mermaid
graph TD
    User([User/Browser]) <--> Frontend[Next.js Frontend - Vercel]
    GitHubActions[GitHub Actions Scheduler] -- 1. GET /status --> Backend
    GitHubActions -- 2. POST /run --> Backend
    Frontend -- API Polling --> Backend[FastAPI Backend - Railway/Docker]
    
    subgraph "FastAPI Backend Layer"
        Backend --> Pipeline[Core Processing Pipeline]
        Pipeline --> P1[Phase 1: Ingestion & Cleaning]
        Pipeline --> P2[Phase 2: Theme Engine (Groq/Gemini)]
        Pipeline --> P3[Phase 3: Pulse Generator (Gemini)]
        Pipeline --> P4[Phase 4: Email Automation]
        
        P1 -- Writing --> Data[(/output JSON/MD Store)]
        P3 -- Reading/Writing --> Data
        P4 -- Reading --> Data
    end
    
    subgraph "External Services"
        P2 --- GroqAPI(Groq Llama-3-70b)
        P2 --- GeminiAPI(Gemini 2.5 Flash)
        P3 --- GeminiAPI
        P4 --- SMTP(Gmail SMTP Service)
    end
```

---

## 🚀 Layered Architecture

### 1. Backend Layer (FastAPI)
The central orchestrator transitions from `main.py` to a FastAPI service running in a Docker container.

#### API Design (RESTful)
| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/run` | `POST` | Triggers the full pipeline as a **background task**. Returns immediately. |
| `/status` | `GET` | Returns current system state (`idle`, `running`, `failed`) and last run metadata. |
| `/report` | `GET` | Fetches the latest synthesized report and theme data. |
| `/send-email` | `POST` | Sends the current report to a specified email address. |
| `/health` | `GET` | Returns system status and API uptime. |

### 🛠️ Key Architectural Controls

#### A. Execution Model
The pipeline is executed as a **non-blocking background task** using FastAPI's `BackgroundTasks`. 
- When `/run` is called, the server acknowledges the request with a `202 Accepted` status and starts the pipeline.
- The main thread is never blocked, ensuring the API remains responsive.

#### B. Status Tracking & Polling
System state is managed via a dedicated `/status` endpoint.
- **States:** `idle` (ready), `running` (in-progress), `failed` (error encountered).
- **Metadata:** Includes `last_run_timestamp` and `last_run_status`.
- **Client Behavior:** The Next.js frontend uses **polling** (every 3–5 seconds) to check the status rather than persistent WebSockets.

#### C. Concurrency Control
To prevent data corruption and resource exhaustion, the system enforces a **Single Execution Rule**:
- Only one pipeline run is allowed at any given time.
- An in-memory lock (Boolean flag) tracks the active state.
- If `/run` is triggered while the state is `running`, the API returns a `409 Conflict` or simply ignores the request.

#### D. Failure Handling
The pipeline follows a "Fail Fast" principle:
- If any phase (1–4) fails, the entire pipeline execution **stops immediately**.
- The error is captured and logged for debugging.
- The `/status` endpoint reflects the `failed` state.
- **Data Integrity:** Since each phase writes to its own versioned file (`v1`, `v2`, etc.), a failure in a later phase does not overwrite or corrupt the successful outputs from the previous run.

---

### 2. Frontend Layer (Next.js)
A modern, responsive web interface built with Next.js and Tailwind CSS.

**Core UI Features:**
- **Dashboard Overview:** Displays top themes, impact scores, and sentiment trends.
- **Report Viewer:** Renders the full markdown report dynamically.
- **Control Center:** Manual trigger button for the pipeline and email delivery.
- **Progress Tracking:** Uses polling on `/status` to show real-time stage updates to the user.

---

## 📂 Updated Folder Structure

```text
indmoney-pulse/
├── backend/                    # Containerized FastAPI Service
│   ├── src/                    # Core Pipeline Logic (Phases 1-4)
│   ├── api/                    # FastAPI Routes & Status Management
│   ├── main.py                 # FastAPI Entry point
│   ├── Dockerfile              # Backend Container Configuration
│   └── requirements.txt        # Backend Dependencies
├── frontend/                   # Next.js Application
│   ├── components/             # Reusable UI Blocks
│   ├── pages/                  # Route-based Views
│   └── public/                 # Static Assets
├── output/                     # JSON & Markdown Data Store (Ephemeral)
├── .github/workflows/          # Deployment & Automation
│   ├── deploy-backend.yml      # Railway Deploy
│   ├── deploy-frontend.yml     # Vercel Deploy
│   └── weekly-run.yml          # Scheduler: Checks status -> Triggers /run
└── .env                        # Environment Variables (Gitignored)
```

---

## 🛠️ Infrastructure & Deployment

### Data Persistence Notice
The `/output` directory is mapped as a local volume in Docker. However, in standard Railway/Docker deployments, this storage is **ephemeral**. 
- Data will persist across container restarts but may be lost on new deployments or if the disk is wiped.
- This is acceptable for the current prototype/demo phase; future versions may require S3 or a database for long-term retention.

### Scheduling (GitHub Actions)
The weekly scheduler is updated to be status-aware:
1. Call `GET /status`.
2. Proceed to call `POST /run` **only if** the status is `idle`.
3. Log an alert if the system is stuck in `running` or `failed` state.

---

## 🛡️ Non-Functional Requirements
- **Simplicity:** No complex message queues or external databases are required.
- **Security:** API keys and credentials managed via cloud-native secrets.
- **Separation of Concerns:** Frontend is entirely decoupled from Python-specific logic.
