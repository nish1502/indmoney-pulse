import os
import json
import logging
import time
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def load_theme_candidates(file_path="output/v2a_theme_candidates.json"):
    """
    Load all theme candidates from Phase 2A batches.
    """
    if not os.path.exists(file_path):
        logger.error(f"Input file not found: {file_path}")
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        batches = json.load(f)
        
    all_raw_themes = []
    for batch in batches:
        all_raw_themes.extend(batch.get("themes", []))
        
    return all_raw_themes

def consolidate_themes(raw_themes, max_retries=3):
    """
    Use Groq (llama-3.1-8b-instant) to merge and consolidate themes into 5 final categories.
    """
    unique_themes = sorted(list(set(raw_themes)))
    logger.info(f"Total raw themes: {len(raw_themes)}")
    logger.info(f"Unique themes: {len(unique_themes)}")
    
    if not unique_themes:
        return []
        
    theme_list_str = "\n".join([f"- {t}" for t in unique_themes])
    
    prompt = f"""
I have a list of raw product themes extracted from app reviews in batches. 
Consolidate them into exactly 5 SHARP product themes.

### Raw Theme List:
{theme_list_str}

### Rules:
1. Return exactly 5 final themes as a JSON output with the key "final_themes".
2. Priority themes:
   - "App Performance": For speed, crashes.
   - "UI Problems": For layout, visuals.
   - "Account Issues": For KYC, login, bank links.
   - "High Charges": For fees, deductions.
   - "Payments & Rewards": For UPI, cashback, praise.
3. If "Trading Features" is found, swap one of the above for it (prioritize over UI).

### Output Format (JSON ONLY):
{{
  "final_themes": ["App Performance", "Trading Features", "Account Issues", "High Charges", "Payments & Rewards"]
}}
"""

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            data = json.loads(content.strip())
            return data.get("final_themes", [])[:5]
        except Exception as e:
            logger.warning(f"Consolidation attempt {attempt + 1} failed: {e}")
            time.sleep(10)
    return []

def run_phase2b():
    """
    Orchestrate theme consolidation using Groq 8B.
    """
    logger.info("Starting Phase 2B (Groq 8B Engine): Theme Consolidation...")
    raw_themes = load_theme_candidates()
    if not raw_themes:
        return
    final_themes = consolidate_themes(raw_themes)
    if final_themes:
        output_path = "output/v2b_consolidated_themes.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({"final_themes": final_themes}, f, indent=2, ensure_ascii=False)
        logger.info(f"Phase 2B complete. Saved to {output_path}.")
    else:
        logger.error("Failed to generate final themes.")

if __name__ == "__main__":
    run_phase2b()
