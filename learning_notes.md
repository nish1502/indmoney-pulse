# INDMoney Pulse: Learning Notes & Post-Mortem

This document summarizes the technical learnings, challenges, and solutions encountered while building Phase 1 of the **INDMoney Pulse** intelligence pipeline.

---

## 🧩 Core Technical Learnings

### 1. Robust Data Cleaning (PII & Surrogates)
- **Challenge**: Raw app reviews contain surrogates (U+D800 range) and non-standard characters that crash standard `utf-8` parsers.
- **Learning**: `errors='surrogatepass'` is essential for Python's `open()` function when dealing with scraped data that might contain emojis or malformed characters.
- **Fix**: Centralized `_strip_surrogates` utility in `cleaner.py` to pre-clean data before it enters the LLM pipeline.

### 2. LLM Orchestration & Rate Limiting
- **Challenge**: Groq's free-tier has strict TPD (Tokens Per Day) and RPM (Requests Per Minute) limits. Large batches of reviews often triggered `429 Too Many Requests`.
- **Learning**: Implemented a **Small-Batch Strategy (20 reviews/batch)** with dynamic sleep timers and exponential backoff retry logic.
- **Fix**: Upgraded the `classifier.py` and `extractor.py` modules with robust `for attempt in range(max_retries)` loops.

---

## 🚨 Critical Errors & Solutions

### Error: `name 'os' is not defined`
- **Root Cause**: Missing import in the `Phase 1 Cleaner` module after refactoring.
- **Solution**: Re-added `import os` and verified CSV generation logic works within the symlinked Docker environment.

### Error: `UnicodeDecodeError: 'utf-8' codec can't decode...`
- **Root Cause**: The `trend_analyzer.py` was reading the previously saved `v2c_previous.json` without surrogate handling.
- **Solution**: Patched all file read/write operations across the repo to use `encoding='utf-8', errors='surrogatepass'`.

### Error: `json.JSONDecodeError` in Classification
- **Root Cause**: Groq (Llama-3-8b) sometimes wrapped JSON in markdown blocks (```json) or returned a dictionary when a list was expected.
- **Solution**: Added a format normalization layer that strips markdown wrappers and extracts lists from nested dictionaries.

---

## 💡 AI Implementation Tips
- **Deterministic Prompts**: Using `response_format={"type": "json_object"}` is powerful but requires models that support it (like Llama-3.1). For lists, it's safer to post process the string.
- **Symlinked Storage**: In full-stack splits (FastAPI + Next.js), use symlinks for shared storage (`backend/output -> ../output`) to avoid doubling disk usage while keeping modules decoupled.

---

**INDMoney Pulse v1.0** - *Built for Speed, Accuracy, and Executive Readability.*
