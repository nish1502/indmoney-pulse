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

def load_reviews(file_path="output/v1_raw_reviews.json"):
    """
    Load cleaned reviews from Phase 1.
    """
    if not os.path.exists(file_path):
        logger.error(f"Input file not found: {file_path}")
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_themes_batch(batch_reviews, max_retries=3):
    """
    Use Groq (llama-3.1-8b-instant) to extract themes from a batch of reviews.
    Using 8b model to stay within free tier TPD limits.
    """
    reviews_text = "\n".join([f"- {r['review']}" for r in batch_reviews])
    
    prompt = f"""
You are a product analyst. Extract 3-5 distinct product themes from these app reviews. 
Themes must be 2-3 words only.

### Reviews:
{reviews_text}

### Output (JSON ONLY):
{{
  "themes": ["Theme 1", "Theme 2", ...]
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
            return data.get("themes", [])
        except Exception as e:
            logger.warning(f"Theme extraction attempt {attempt + 1} failed: {e}")
            time.sleep(10) # Longer sleep for 429
    return []

def run_phase2a():
    """
    Orchestrate theme extraction. 
    Limited to 200 reviews as requested for test.
    """
    logger.info("Starting Phase 2A (Groq 8B Engine): Batch Theme Extraction...")
    
    reviews = load_reviews()
    if not reviews:
        return
        
    # Limit to 200 reviews total
    reviews = reviews[:200]
    
    batch_size = 20
    all_batches_results = []
    
    for i in range(0, len(reviews), batch_size):
        batch = reviews[i:i + batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}...")
        themes = extract_themes_batch(batch)
        all_batches_results.append({"batch": i//batch_size + 1, "themes": themes})
        
    output_path = "output/v2a_theme_candidates.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_batches_results, f, indent=2, ensure_ascii=False)
    logger.info(f"Phase 2A complete. Saved to {output_path}.")

if __name__ == "__main__":
    run_phase2a()
