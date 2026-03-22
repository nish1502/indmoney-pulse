# INDMoney Pulse: System Audit & Gap Analysis

**Auditor:** Senior TPM & System Architect  
**Status:** Pre-Transition Audit  
**System Maturity:** Prototype (Highly Functional)

---

## 🔍 SECTION 1: REPO & ENVIRONMENT STATE

| Check | Result | Detail |
| :--- | :--- | :--- |
| **Git Initialized?** | ✅ YES | Repository is active on `main` branch. |
| **Remote Connected?**| ❌ NO | `origin` was recently removed. No cloud backup/deployment linked. |
| **Branch Health** | ⚠️ UNSTABLE | Uncommitted changes in `ARCHITECTURE.md`. |
| **.env File** | ✅ YES | Present in root. |
| **Hardcoded Secrets**| ✅ SECURE | None found in `src/`. All API keys/passwords pulled via `os.getenv`. |

---

## ⚙️ SECTION 2: CURRENT SYSTEM CAPABILITIES

### 1. Core Pipeline (`main.py`)
- **Execution:** ✅ Works end-to-end.
- **Success Rate:** High. Recent execution generated all artifacts from Level 1 to Level 3.
- **Execution Model:** ❌ **Synchronous/Blocking.** The entire process hangs until sequential LLM calls complete.

### 2. Phase-wise Functional Audit
- **Phase 1 (Scraper):** ✅ **Operational.** Correct logic for 12-week lookback using `google-play-scraper`. Fetches ~334 reviews currently.
- **Phase 2 (LLM Discovery):** ✅ **Operational.** 
    - **Groq:** Stable batch extraction (Llama-3-70b).
    - **Gemini:** Consolidation (1.5 Flash) is working.
    - **JSON Parsing:** Robust (handles Markdown code blocks).
- **Phase 3 (Report):** ✅ **Valid.** Generates `v3_weekly_pulse.md`.
    - **Constraint Audit:** 3x3 constraint and priority labels ([HIGH], [MEDIUM], [LOW]) are strictly followed.
- **Phase 4 (Email):** ✅ **Operational.** Uses `smtplib` for Gmail. Credentials stored in `.env`.

### 3. Streamlit Dashboard (`app.py`)
- **Runs:** ✅ YES.
- **Reliability:** ⚠️ **Fragile.** Logic assumes all JSON files in `/output/` are perfectly formatted. It will fail silently or display "pending" if one phase succeeds but another fails.

---

## 📂 SECTION 3: DATA & FILE STATE

- **Integrity:** ✅ **High.** `/output` contains versioned files (`v1`, `v2a`, `v2b`, `v2c`, `v3`).
- **Consistency:** ✅ **Current.** Data in `v1_raw_reviews.json` matches March 2026 timestamps.
- **Missing Artifacts:** ❌ **None.** All intermediate states are persisted.

---

## 🔌 SECTION 4: DEPENDENCY & CONFIG HEALTH

- **Libraries:** Basic but sufficient.
- **Known Risks:**
    - `google-generativeai`: Code references `gemini-2.5-flash-lite`. While functional now, this naming is non-standard (standard is `1.5-flash`). Potential breaking point if model visibility changes.
- **Python Version:** 3.12.10 (Stable).

---

## 🧱 SECTION 5: ARCHITECTURE GAP ANALYSIS

| Component | Current State | Target State | Gap |
| :--- | :--- | :--- | :--- |
| **Backend** | CLI Orchestrator (`main.py`) | FastAPI Service | **TOTAL.** No API handlers or routers. |
| **Frontend** | Streamlit (Coupled) | Next.js (Decoupled) | **TOTAL.** No React components or API integration. |
| **Execution** | Blocking Script | Background Task | **TOTAL.** No `BackgroundTasks` or async capability. |
| **Status** | CLI Logs only | `/status` Endpoint | **TOTAL.** No in-memory state tracking. |
| **Deployment**| Local Script | Containerized (Docker) | **TOTAL.** No Dockerfile or Docker Compose. |

---

## 🚨 SECTION 6: CRITICAL RISKS

1.  **Concurrency Collision:** If two users (or the scheduler and a user) trigger the pipeline simultaneously, `/output` files will be corrupted due to race conditions.
2.  **Stateless Storage:** Deployment on Railway/Docker will result in **ephemeral data loss** for `/output` unless volume mapping is perfectly configured.
3.  **Authentication Fragility:** Gmail SMTP via `smtplib` is prone to being blocked if not using App Passwords or if MFA settings change.
4.  **Error Propagation:** If Phase 2 fails, the logic currently doesn't gracefully exit in the UI; it just shows stale data from the previous run.

---

## 📊 SECTION 7: FINAL VERDICT

**Maturity Level:** **Level 2 - Functional Prototype**

### Biggest Bottlenecks:
1.  **Coupled UI:** Streamlit cannot scale to the production-ready interactive dashboard envisioned.
2.  **Blocking IO:** Entire pipeline takes ~1-2 minutes; blocking the UI for this duration is unacceptable for a production web app.

### 🛑 PRE-TRANSITION MUST-FIXES:
- **Clean Model Naming:** Standardize on `gemini-1.5-flash` to avoid API versioning issues.
- **In-Memory Lock:** Before implementing FastAPI, a mechanism to prevent double-execution must be prototyped.
- **Directory Refactoring:** Move current `src` into a `backend/` subtree to prepare for the Next.js split.
