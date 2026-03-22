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

def load_data():
    """
    Load reviews from Phase 1 and consolidated themes from Phase 2B.
    """
    reviews_path = "output/v1_raw_reviews.json"
    themes_path = "output/v2b_consolidated_themes.json"
    
    if not os.path.exists(reviews_path) or not os.path.exists(themes_path):
        logger.error("Required input files not found.")
        return [], []
    
    with open(reviews_path, 'r', encoding='utf-8') as f:
        reviews = json.load(f)
    
    with open(themes_path, 'r', encoding='utf-8') as f:
        themes_data = json.load(f)
        themes = themes_data.get("final_themes", [])
        
    return reviews, themes

def classify_batch(batch_reviews, themes, max_retries=3):
    """
    Send a batch of reviews to Groq (llama-3.1-8b-instant) for classification.
    """
    reviews_input = []
    for idx, r in enumerate(batch_reviews):
        reviews_input.append({
            "id": idx,
            "review": r["review"],
            "date": r["date"]
        })
    
    themes_str = ", ".join([f'"{t}"' for t in themes])
    
    prompt = f"""
Classify each of the following app reviews into EXACTLY ONE of these themes:
Themes: [{themes_str}]

### Rules:
1. Return a JSON list of objects.
2. Each object MUST contain: "review", "date", and "theme".
3. "theme" MUST be exactly one of the provided themes.
4. If a review fits multiple, choose the MOST dominant one.

### Reviews:
{json.dumps(reviews_input, indent=2)}

### Output Format (JSON ONLY):
[
  {{"review": "...", "date": "...", "theme": "..."}},
  ...
]
"""

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": "You are a classification engine. You output valid JSON list of objects only."},
                          {"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            classified = json.loads(content.strip())
            
            if isinstance(classified, dict):
                 for key in classified:
                     if isinstance(classified[key], list):
                         classified = classified[key]
                         break
            
            valid_classified = []
            for item in classified:
                theme = item.get("theme")
                if theme in themes:
                    valid_classified.append({
                        "review": item.get("review"),
                        "date": item.get("date"),
                        "theme": theme
                    })
            
            return valid_classified
        except Exception as e:
            logger.warning(f"Classification attempt {attempt + 1} failed: {e}")
            time.sleep(10) # 10s wait for 429
            
    return []

def run_phase2c():
    """
    Orchestrate the review classification.
    """
    logger.info("Starting Phase 2C (Groq 8B Engine): Review Classification...")
    
    reviews, themes = load_data()
    if not reviews or not themes:
        return
        
    # Limit to 200 reviews
    reviews = reviews[:200]
    
    logger.info(f"Classifying {len(reviews)} reviews into {len(themes)} themes.")
    batch_size = 20
    all_classified = []
    
    for i in range(0, len(reviews), batch_size):
        batch = reviews[i:i + batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}/{(len(reviews)-1)//batch_size + 1}...")
        results = classify_batch(batch, themes)
        all_classified.extend(results)
        
    output_path = "output/v2c_classified_reviews.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_classified, f, indent=2, ensure_ascii=False)
        
    logger.info(f"Phase 2C complete. Results saved to {output_path}.")
    logger.info(f"Successfully classified {len(all_classified)} reviews.")

if __name__ == "__main__":
    run_phase2c()
