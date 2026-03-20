# INDMoney App Review Pulse: Architecture & Roadmap

This document outlines the phased architecture, data flow, and technical stack for the automated **INDMoney Weekly Product Pulse** pipeline.

## 🏗️ Phase-Wise Architecture

The pipeline is divided into modular phases, orchestrated by a central `main.py`.

### Phase 1: Ingestion & Cleaning
- **Objective:** Scrape latest reviews and prepare them for analysis by removing noise and sensitive data.
- **Logic:**
    - Use `google-play-scraper` to fetch up to 200 recent reviews for `com.indmoney.app`.
    - Filter: Language must be English.
    - Filter: Remove reviews with fewer than 5 words.
    - Anonymization: Remove potential PII (emails, phone numbers) using regex.
- **Output:** `output/v1_raw_reviews.json`

### Phase 2: Theme Discovery (Groq + Gemini 2.5 Flash)
- **Objective:** Discover, consolidate, and classify reviews into 3–5 distinct product themes.

#### Phase 2A: Batch Theme Extraction (Groq)
- **Logic:** Process reviews in batches (e.g., 20 per batch).
- **Constraints:**
    - Extract 3–5 themes per batch.
    - Each theme must be **2–3 words only**.
    - **No vague themes** like "general", "other", or "misc".
    - **No duplicates** or overlapping themes within a single batch.
- **Output:** `output/v2a_theme_candidates.json`

#### Phase 2B: Theme Consolidation (Gemini 2.5 Flash)
- **Logic:** Merge all candidates from 2A into a final set of **3–5 themes** (prefers 5 if meaningful).
- **Constraints:**
    - Ensure **no overlapping meanings** between themes.
    - Create clear, distinct categories with consistent naming.
- **Output:** `output/v2b_consolidated_themes.json`

#### Phase 2C: Review Classification (Groq)
- **Logic:** High-speed mapping of all original reviews to the final themes.
- **Constraints:**
    - **Each review must be assigned exactly ONE theme**.
    - Must choose from the final 3–5 themes only; **no new themes allowed**.
- **Output:** `output/v2c_classified_reviews.json`

### Phase 3: Pulse Report Synthesis (Gemini 2.5 Flash)
- **Objective:** Generate a high-level executive summary of the week’s sentiment.
- **Constraints:**
    - **Avoid generic summaries**; focus on specific pain points and wins.
    - **Use real user language** (referencing specific phrases from reviews).
    - **Action Items must be specific and actionable** (e.g., "Fix KYC button lag" instead of "Improve UI").
    - **Constraint:** ≤250 words.
- **Output:** `output/v3_weekly_pulse.md`

### Phase 4: Email Automation
- **Objective:** Dispatch the report to the team.
- **Logic:** Convert `weekly_pulse.md` into a styled email and send via Gmail SMTP.

### Phase 5: Interface (CLI + Web UI)
- **Objective:** Manual triggers, monitoring, and report preview using **Streamlit**.

### Phase 6: Scheduler (GitHub Actions)
- **Objective:** Automate the pipeline via CRON on a weekly basis.

---

## 🔄 Orchestrator Flow (main.py)

The `main.py` script serves as the central controller, ensuring a linear execution of all phases:

1.  **Phase 1 (Scraper):** Fetch & Clean → `v1_raw_reviews.json`
2.  **Phase 2A (Extractor):** Batch extraction → `v2a_theme_candidates.json`
3.  **Phase 2B (Consolidator):** Merge themes → `v2b_consolidated_themes.json`
4.  **Phase 2C (Classifier):** Assign reviews → `v2c_classified_reviews.json`
5.  **Phase 3 (Report):** Synthesize findings → `v3_weekly_pulse.md`
6.  **Phase 4 (Email):** Dispatch to Stakeholders

---

## 📂 Folder Structure

```text
indmoney-pulse/
├── src/
│   ├── phase1_ingestion/       # Scraping & cleaning
│   ├── phase2_theme_engine/    # Multi-step discovery
│   │   ├── extractor.py        # 2A: Batch extraction (Groq)
│   │   ├── consolidator.py     # 2B: Theme reduction (Gemini)
│   │   └── classifier.py       # 2C: Categorization logic (Groq)
│   ├── phase3_pulse_generator/ # Gemini report synthesis
│   ├── phase4_automation/      # Email service
│   └── phase5_interface/       # Streamlit & CLI
├── output/                     # Storable intermediate data (v1 to v3)
├── .github/workflows/          # Phase 6: Scheduling
│   └── weekly_pulse.yml
├── config/                     # Settings (gitignored)
├── main.py                     # Central orchestrator
└── requirements.txt
```

---

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Language** | Python 3.10+ |
| **Classification LLM** | **Groq (Llama-3-70b)** - Ultra-fast batch processing. |
| **Synthesis LLM** | **Gemini 2.5 Flash** - Consolidation & report generation. |
| **Interface** | **Streamlit** |
| **Email** | **Gmail SMTP** |
| **Scheduler** | **GitHub Actions** |

## 🔒 Constraints & Security
- **Theme Count:** 3–5 themes (flexible, data-driven).
- **PII:** Scrubbed in Phase 1 before LLM ingestion.
- **Data Persistence:** JSON outputs are saved at every sub-phase for auditing.
