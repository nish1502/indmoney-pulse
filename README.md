# INDMoney Pulse: Automated Weekly Product Intelligence

**INDMoney Pulse** is an AI-powered pipeline that transforms thousands of Play Store reviews into a sharp executive report, identifies key product themes, and provides structured explanations for common fee scenarios.

---

## 🏗️ Architecture Overview

The system is a full-stack application composed of:
- **FastAPI Backend**: Orchestrates a 6-phase AI pipeline (Ingestion, Theme Engine, Pulse Synthesis, Email, Fee Explainer, and MCP Intelligence Export).
- **Next.js Frontend**: A high-fidelity dashboard for product managers to monitor system status, review reports, and trigger manual "approval-gated" exports.

---

## 🚀 Getting Started

### 1. Environmental Setup
Ensure your `.env` (in the `backend/` directory) contains:
```env
GROQ_API_KEY=your_key
GEMINI_API_KEY=your_key
EMAIL_ID=your_gmail
EMAIL_PASSWORD=your_app_password
```

### 2. Run the Application
Start the backend and frontend services using the provided Docker configuration or manually:

**Backend (FastAPI)**:
```bash
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8001
```

**Frontend (Next.js)**:
```bash
cd frontend
npm run dev
```

---

## 🛠️ Pipeline Modules (Phases 1-6)

1.  **Phase 1: Ingestion & Redaction**: Fetches public reviews (last 12 weeks), scrubs PII, and exports to both JSON and CSV.
2.  **Phase 2: AI Theme Engine**: Small-batch classification (Groq) followed by high-level theme consolidation.
3.  **Phase 3: Pulse Synthesis**: Generates a prioritized, <250-word executive report.
4.  **Phase 4: Email Automation (SMTP)**: Delivers reports via Gmail SMTP (Manual approval-gated).
5.  **Phase 5: Fee Explainer (Exit Load)**: Generates a structured (≤6 bullet) explanation for "Mutual Fund Exit Loads" with official source links.
6.  **Phase 6: Intelligence Export (MCP)**: Appends the pulse and fee results to a persistent `intelligence_notes.md` file, simulating a Model Context Protocol (MCP) action.

---

## 💰 Fee Scenario: Mutual Fund Exit Load
The system explains the "Exit Load" scenario for INDMoney users with a neutral, facts-only tone.

**Sources Used:**
- [INDMoney - What is Exit Load in Mutual Funds?](https://www.indmoney.com/articles/mutual-funds/what-is-exit-load-in-mutual-funds)
- [INDMoney Mutual Fund App FAQs](https://www.indmoney.com/mutual-funds)
- [SEBI Guidelines on Exit Load](https://www.sebi.gov.in/)
- [Kotak Mutual Fund - Understanding Exit Load](https://www.kotakmf.com/learning-center/exit-load)

---

## 🎯 PM Handbook Rules
- **No Praise**: The pulse focuses only on friction and growth opportunities.
- **Strictly 3x3x3**: Every report contains exactly 3 themes, 3 quotes, and 3 actionable ideas.
- **Financial Risk First**: Any [HIGH] priority action must address transactional or financial safety.
- **Fact Discovery**: The Fee Explainer is strictly informational and contains no recommendations or comparisons.

---

## 🏁 Milestone 1 Deliverables (Audit Ready)
- **Weekly Note**: Found in `backend/output/v3_weekly_pulse.md`.
- **Fee Explainer**: Found in `backend/output/v5_fee_explanation.md`.
- **Intelligence Notes**: Found in `backend/output/intelligence_notes.md`.
- **Reviews CSV**: Exported to `backend/output/v1_reviews_for_audit.csv`.
- **Approval Gating**: Handled via the manual triggers on the Next.js Dashboard.
