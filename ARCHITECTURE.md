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
        Pipeline --> P4[Phase 4: Email Delivery (SMTP)]
        Pipeline --> P5[Phase 5: Fee Explainer (LLM)]
        Pipeline --> P6[Phase 6: Intelligence Export (MCP)]
        
        P1 -- Writing --> Data[(/output JSON/MD Store)]
        P3 -- Reading/Writing --> Data
        P5 -- Reading/Writing --> Data
        P6 -- Writing --> Notes[(External Notes/Doc)]
    end
    
    subgraph "External Services"
        P2 --- GroqAPI(Groq Llama-3-70b)
        P2 --- GeminiAPI(Gemini 2.5 Flash)
        P3 --- GeminiAPI
        P4 --- SMTP(Gmail SMTP Service)
        P5 --- GeminiAPI
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
| `/report` | `GET` | Fetches the latest synthesized report, theme data, and fee explanation. |
| `/send-email` | `POST` | Sends the current report to a specified email address (Approval-Gated in UI). |
| `/export-notes` | `POST` | Appends current pulse + fee data to a persistent intelligence doc (MCP-simulated). |
| `/health` | `GET` | Returns system status and API uptime. |

### 🛠️ Key Architectural Controls

#### A. Pipeline Flow (Approval-Gated)
The system follows an "Extract-Synthesize-Review-Dispatch" model:
1.  **Extract & Synthesize**: `/run` executes Phases 1, 2, 3, and 5 automatically.
2.  **Review**: The user reviews the output via the `/report` endpoint on the frontend.
3.  **Dispatch (Gated)**: Phase 4 (Email) and Phase 6 (Notes Export) are only triggered via explicit user action from the dashboard.

#### B. Fee Explainer Module (Phase 5)
A specialized LLM prompt converts raw internal fee structures into a user-friendly 6-bullet explanation.
- **Scenario Focus**: Covers common charges (e.g., US Stock Withdrawal Fee or Mutual Fund Exit Load).
- **Compliance**: Uses neutral, facts-only tone with official source links.

#### C. Intelligence Export (Phase 6 - MCP)
Simulates a Model Context Protocol (MCP) server integration to append results to external notebooks or documentation systems.
- **Schema**: `{ date, weekly_pulse, fee_scenario, explanation_bullets, source_links }`.

---

### 2. Frontend Layer (Next.js)
A modern, responsive web interface built with Next.js and Tailwind CSS.

**Core UI Features:**
- **Dashboard Overview**: Displays top themes, impact scores, and sentiment trends.
- **Report Viewer**: Renders the full markdown report and fee explanation dynamically.
- **Control Center**: Manual trigger buttons for the pipeline, email delivery, and notes export.
- **Progress Tracking**: Uses polling on `/status` to show real-time stage updates to the user.

---

## 📂 Updated Folder Structure

```text
indmoney-pulse/
├── backend/                    # Containerized FastAPI Service
│   ├── src/                    # Core Pipeline Logic (Phases 1-6)
│   │   ├── phase5_fee_explainer/ # Structured Fee Explanations
│   │   └── phase6_intelligence_export/ # MCP Integration logic
│   ├── api/                    # FastAPI Routes & Status Management
│   ├── main.py                 # FastAPI Entry point
│   ├── Dockerfile              # Backend Container Configuration
│   └── requirements.txt        # Backend Dependencies
├── frontend/                   # Next.js Application
├── output/                     # JSON & Markdown Data Store (Ephemeral)
├── .github/workflows/          # Deployment & Automation
└── .env                        # Environment Variables (Gitignored)
```

---

## 🛠️ Infrastructure & Deployment

### Data Persistence Notice
The `/output` directory is mapped as a local volume in Docker. However, in standard Railway/Docker deployments, this storage is **ephemeral**. 
- Data will persist across container restarts but may be lost on new deployments or if the disk is wiped.
- **MCP Integration**: Designed to bridge this gap by pushing final results to persistent external platforms.

### Scheduling (GitHub Actions)
The weekly scheduler is updated to be status-aware:
1. Call `GET /status`.
2. Proceed to call `POST /run` **only if** the status is `idle`.
3. Log an alert if the system is stuck in `running` or `failed` state.
