# INDMoney Pulse: Weekly Product Intelligence

Automated pipeline to transform thousands of Play Store reviews into a sharp, 1-page weekly product pulse.

## 🚀 How to Run for a New Week

1. **Environmental Setup**:
   Ensure your `.env` contains:
   ```env
   GROQ_API_KEY=your_key
   GEMINI_API_KEY=your_key
   EMAIL_ID=your_gmail
   EMAIL_PASSWORD=your_app_password
   ```

2. **Trigger Pipeline**:
   Run the orchestrator to fetch the last 12 weeks of reviews, extract themes, and generate the report:
   ```bash
   python main.py
   ```

3. **View Dashboard**:
   Analyze trends and impact scores interactively:
   ```bash
   streamlit run app.py
   ```

---

## 🏗️ Pipeline Flow (3 Steps)

1. **Ingestion & Redaction**: Fetches public reviews from the last 12 weeks and scrubs all PII (emails, names, phones).
2. **AI Theme Engine**: Small-batch classification (Groq) followed by high-level theme consolidation (Gemini).
3. **Pulse Synthesis**: Generates a prioritized, <250-word executive report and delivers it via automated email.

---

## 🏷️ Theme Legend

The AI classifies all feedback into 5 distinct buckets for maximum PM clarity:

- **App Performance**: Speed, lag, crashes, battery drain, and general stability.
- **UI Problems**: Navigation friction, layout issues, font sizes, and dark mode bugs.
- **Account Issues**: KYC verification, bank linking, Aadhaar/PAN errors, and login loops.
- **High Charges**: Brokerage fees, hidden charges, transaction costs, and refund delays.
- **Payments & Rewards**: UPI transaction reliability, cashback tracking, and generic app praise.

---

## 🎯 PM Handbook Rules
- **No Praise**: The pulse focuses only on friction and growth opportunities.
- **Strictly 3x3x3**: Every report contains exactly 3 themes, 3 quotes, and 3 actionable ideas.
- **Financial Risk First**: Any [HIGH] priority action must address transactional or financial safety.
