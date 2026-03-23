import os
import json
import logging
from datetime import datetime
from src.phase6_intelligence_export.mcp_client import export_to_gdoc_mcp

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def append_to_notes(file_path="output/intelligence_notes.md"):
    """
    Append Phase 3 (Pulse) and Phase 5 (Fee) results to a persistent notes file.
    This simulates an MCP 'Append to Doc' action.
    """
    logger.info("Starting Phase 6: Intelligence Export (MCP Simulation)...")
    
    # 1. Load Data
    pulse_report = ""
    pulse_path = "output/v3_weekly_pulse.md"
    if os.path.exists(pulse_path):
        with open(pulse_path, 'r', encoding='utf-8', errors='surrogatepass') as f:
            pulse_report = f.read()
            
    fee_data = {}
    fee_path = "output/v5_fee_explanation.json"
    if os.path.exists(fee_path):
        with open(fee_path, 'r', encoding='utf-8', errors='surrogatepass') as f:
            fee_data = json.load(f)

    if not pulse_report and not fee_data:
        logger.error("No data found for export.")
        return False

    # 2. Extract Bullets and Links safely
    # Handling raw text from Gemini might need splitting if not already a list
    explanation = fee_data.get("explanation", "")
    
    # 3. Format the Entry
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Required Schema in Prompt: { date, weekly_pulse, fee_scenario, explanation_bullets, source_links }
    # We will format it as a distinct Markdown Block
    
    entry = f"""
---
### 📅 Intelligence Update: {date_str}

#### ⚡ Weekly Product Pulse
{pulse_report}

#### 💰 Fee Scenario: {fee_data.get('scenario', 'N/A')}
{explanation}

#### 🔗 Sources
{chr(10).join([f"- {url}" for url in fee_data.get('source_links', [])])}

---
"""
    
    # 4. Direct MCP Export to GDocs (Prioritized)
    doc_id = os.getenv("GOOGLE_DOC_ID")
    if doc_id:
        logger.info(f"Attempting Direct MCP Export to GDoc ID: {doc_id}...")
        success = export_to_gdoc_mcp(entry)
        if success:
            logger.info("Successfully exported intelligence via Direct MCP.")
            return True
        else:
            logger.warning("MCP Export failed. Falling back to local append.")

    # 5. Fallback: Append to File
    os.makedirs("output", exist_ok=True)
    try:
        with open(file_path, "a", encoding="utf-8", errors='surrogatepass') as f:
            f.write(entry)
        logger.info(f"Successfully appended entry to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to append to notes: {e}")
        return False

if __name__ == "__main__":
    append_to_notes()
