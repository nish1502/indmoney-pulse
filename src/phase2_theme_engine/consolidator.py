import os
import json
import logging
import time
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

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
    Use Gemini to merge and consolidate themes into 3-5 final categories.
    """
    unique_themes = sorted(list(set(raw_themes)))
    logger.info(f"Total raw themes: {len(raw_themes)}")
    logger.info(f"Total unique themes: {len(unique_themes)}")
    
    if not unique_themes:
        return []
        
    theme_list_str = "\n".join([f"- {t}" for t in unique_themes])
    
    prompt = f"""
I have a list of raw product themes extracted from app reviews in batches. 
Consolidate them into exactly 5 SHARP product themes.

### Raw Theme List:
{theme_list_str}

### Strict Rules:
1. Return exactly 5 final themes as a JSON output with the key "final_themes".
2. You MUST use these exact names or very close equivalents:
   - "App Performance": For speed, lag, crashes.
   - "UI Problems": For layout, design, visuals.
   - "Account Issues": For KYC, login, bank links.
   - "High Charges": For fees, brokerage, deductions.
   - "Payments & Rewards": For UPI, cashback, rewards, generic praise.
3. STRICT SEPARATION:
   - "Trading Features" (if generated) must ONLY be for SIP, Charts, and Stocks.
   - If "Trading Features" is more important than one of the above, swap it, but NEVER merge Trading with Payments.
   - Generic "good app" or "good cashback" MUST go to "Payments & Rewards".

### Output Format (JSON ONLY):
{{
  "final_themes": ["App Performance", "UI Problems", "Account Issues", "High Charges", "Payments & Rewards"]
}}
"""

    # We use Gemini 2.5 Flash as requested.
    model_name = "models/gemini-1.5-flash"
    generation_config = {
        "temperature": 0.1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 4096,
    }

    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config
    )

    for attempt in range(max_retries):
        content = "" # Reset for each attempt
        try:
            response = model.generate_content(prompt)
            # Log candidate info for debugging truncation
            if response.candidates:
                logger.debug(f"Finish reason: {response.candidates[0].finish_reason}")
            
            content = response.text
            
            # Robust JSON parsing (handles markdown blocks if present)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            print(f"DEBUG: CONTENT TO PARSE: {content}")
            data = json.loads(content.strip())
            
            final_themes = data.get("final_themes", [])
            return final_themes[:5]
            
        except Exception as e:
            logger.warning(f"Consolidation attempt {attempt + 1} failed: {e}")
            if "429" in str(e):
                 logger.info("Rate limit hit. Sleeping 10s...")
                 time.sleep(10)
            elif attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                logger.error(f"Consolidation failed after {max_retries} attempts.")
                return []

def run_phase2b():
    """
    Orchestrate theme consolidation.
    """
    logger.info("Starting Phase 2B: Theme Consolidation...")
    
    if not os.getenv("GEMINI_API_KEY"):
        logger.error("GEMINI_API_KEY not found in environment.")
        return

    raw_themes = load_theme_candidates()
    if not raw_themes:
        logger.warning("No theme candidates to consolidate.")
        return
        
    final_themes = consolidate_themes(raw_themes)
    
    if final_themes:
        output_path = "output/v2b_consolidated_themes.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({"final_themes": final_themes}, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Phase 2B complete. Saved final themes to {output_path}.")
    else:
        logger.error("Failed to generate final themes.")

if __name__ == "__main__":
    run_phase2b()
