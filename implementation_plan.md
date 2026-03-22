# INDMoney Pulse: Full-Stack Transformation Plan

This plan outlines the systematic transition from a synchronous Python pipeline to a production-grade full-stack architecture.

---

## 🛠️ Phase 1: Foundation & Directory Refactoring
**Goal:** Restructure the project to decouple the backend logic from the future frontend and prepare for containerization.

1.  **Create Root Subdirectories:**
    - `backend/`: To house the FastAPI server and core pipeline logic.
    - `frontend/`: To house the Next.js application.
2.  **Migrate Backend Assets:**
    - Move `src/` directory to `backend/src/`.
    - Move `main.py` to `backend/main.py`.
    - Copy `.env` and `requirements.txt` into `backend/`.
3.  **Clean Root Directory:**
    - Remove legacy artifacts like `app.py` (Streamlit) once the Next.js frontend is initialized.
    - Update `.gitignore` to handle both Python and JavaScript environments.

---

## ⚙️ Phase 2: Backend Layer (FastAPI)
**Goal:** Build a robust, non-blocking API to orchestrate the pipeline and track its status.

1.  **Initialize FastAPI App:**
    - Create `backend/app/main.py` with the FastAPI app instance.
    - Implement a centralized `StatusManager` to handle in-memory state (`idle`, `running`, `failed`).
2.  **Endpoint Implementation:**
    - **`GET /health`**: Simple uptime check.
    - **`GET /status`**: Returns the current state and last run metadata for frontend polling.
    - **`POST /run`**: 
        - [X] Implement `BackgroundTasks` to trigger the pipeline asynchronously.
        - [X] Add a guard to return `409 Conflict` if the state is already `running`.
    - **`GET /report`**: Serves the generated JSON data from the `output/` directory.
    - **`POST /send-email`**: Exposes the Phase 4 email logic via an API call.

---

## 🎨 Phase 3: Frontend Layer (Next.js)
**Goal:** Create a high-performance, responsive UI for visualizing product health and triggers.

1.  **Initialize Next.js Project:**
    - Use `npx create-next-app` with Tailwind CSS in the `frontend/` directory.
2.  **Dashboard Components:**
    - **Theme Cards:** Interactive cards showing theme distribution and impact scores.
    - **Trend Indicators:** Visual cues (↑ ↓ →) for sentiment changes.
    - **Report Viewer:** A markdown-rendering component for `v3_weekly_pulse.md`.
3.  **Interactions & Polling:**
    - Implement the "Trigger Pipeline" button.
    - Setup a polling hook (using `useEffect` or SWR) to hit the `/status` endpoint every 3–5 seconds during a run.

---

## 🐳 Phase 4: Containerization & DevOps
**Goal:** Ensure the system is portable and deployable to production environments.

1.  **Dockerize Backend:**
    - Create a `backend/Dockerfile` using `python:3.10-slim`.
    - Ensure external environment variables are passed correctly.
2.  **GitHub Actions Integration:**
    - Create a workflow for automated deployments to **Railway** (Backend) and **Vercel** (Frontend).
    - Create a separate CRON workflow for the **Weekly Scheduler** that calls the production `/run` endpoint after checking `/status`.

---

## 🚀 Immediate Next Steps
1.  **[PROPOSED]** Move `src/` to `backend/src/`.
2.  **[PROPOSED]** Create the initial FastAPI `backend/main.py` to wrap the existing `main.py` logic.
3.  **[PROPOSED]** Setup the basic Next.js structure in `frontend/`.

**Should we start with the backend folder refactoring now?**
