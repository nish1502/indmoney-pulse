# Milestone 1: Weekly Product Pulse & Fee Explainer Implementation Plan

This plan outlines the steps to complete the remaining requirements for Milestone 1, focusing on the **Fee Explainer**, **MCP Notes Integration**, and **CSV Deliverables**.

---

## 🏗️ Workstream 1: Fee Explainer (Phase 5)
**Goal:** Generate a structured, facts-only explanation for a common INDMoney fee scenario.

1.  **Step 1.1: Fee Knowledge Base**
    - Create `backend/src/phase5_fee_explainer/fee_kb.json` with official data for "US Stock Withdrawal Charges" and "Mutual Fund Exit Loads".
    - Include official source links and a "Last Checked" date.
2.  **Step 1.2: Fee Synthesis Service**
    - Implement `backend/src/phase5_fee_explainer/fee_service.py` to process the KB and output a ≤6 bullet structured explanation.
    - Ensure a neutral, facts-only tone via specialized LLM system prompts.
3.  **Step 1.3: Pipeline Integration**
    - Update `backend/main.py` to include Phase 5 in the primary `/run` execution flow.
    - Save results to `output/v5_fee_explanation.json`.

---

## 📝 Workstream 2: Intelligence Export (Phase 6 - MCP)
**Goal:** Append results to a persistent intelligence log with an approval-gated trigger.

1.  **Step 2.1: Notes Manager**
    - Create `backend/src/phase6_intelligence_export/notes_manager.py`.
    - Implement the `append_to_notes` function with the required schema:
      ```json
      {
        "date": "YYYY-MM-DD",
        "weekly_pulse": "...",
        "fee_scenario": "...",
        "explanation_bullets": [],
        "source_links": []
      }
      ```
2.  **Step 2.2: Approval-Gated API**
    - Add a specialized `@app.post("/export-notes")` endpoint in `backend/main.py`.
    - This endpoint will format the final block and append it to a persistent Markdown/Doc store.

---

## 📊 Workstream 3: CSV Compliance & Portability
**Goal:** Provide review data in CSV format as required by the milestone deliverables.

1.  **Step 3.1: CSV Export Utility**
    - Add a conversion function to `backend/src/phase1_ingestion/cleaner.py` (e.g., `export_to_csv()`) to save cleaned reviews to `output/v1_reviews_for_audit.csv`.
2.  **Step 3.2: Input Logic Refinement**
    - Update Phase 1 to allow the system to ingest a local `reviews.csv` if dynamic scraping is skipped.

---

## 🎨 Workstream 4: Dashboard UI Enhancements
**Goal:** Visualize new data and add manual action buttons.

1.  **Step 4.1: Fee Explainer Display**
    - Add a `FeeExplainer` component to the Next.js frontend to show the bulleted fee breakdown.
2.  **Step 4.2: Export Controls**
    - Add an "Export to Team Notes" button in the Dashboard sidebar.
    - Connect the button to the `/export-notes` API endpoint.
3.  **Step 4.3: Status Indicators**
    - Add progress indicators for "Generating Fee Explanation" and "Awaiting Intelligence Export" to the status tracker.

---

## 🏁 Checklist for Milestone Completion
- [ ] Working prototype link (Railway/Vercel)
- [ ] Weekly note MD file in `/output`
- [ ] Notes/Doc snippet showing appended entry
- [ ] Email draft/sent confirmation (SMTP)
- [ ] Reviews CSV sample in `/output`
- [ ] Final README update with Fee Scenario details

**Target Completion Date:** March 25, 2026
