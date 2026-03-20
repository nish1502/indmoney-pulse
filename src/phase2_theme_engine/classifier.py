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
    Send a batch of reviews to Groq for classification into one of the themes.
    """
    # Prepare reviews for the prompt
    # We include an ID to ensure we can map them back easily if needed, but the prompt asks for the full object back
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
4. DO NOT create new themes.
5. NO explanations or reasoning.
6. STRICTURE ON "Trading Features":
   - Assign "Trading Features" ONLY if the review specifically mentions: trading tools, SIPs, charts, stocks, or investment functionality.
   - Do NOT assign "Trading Features" for generic app praise, payments, or cashback.
   - Use "Payments & Rewards" for generic praise, UPI, payments, or cashback instead.
7. If a review fits multiple, choose the MOST dominant one.

### Reviews:
{json.dumps(reviews_input, indent=2)}

### Output Format:
[
  {{"review": "...", "date": "...", "theme": "..."}},
  ...
]
"""

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a precise classification engine. You only output valid JSON lists of objects based on provided themes."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            
            try:
                classified = json.loads(content)
            except Exception as json_err:
                logger.error(f"Failed to parse LLM JSON response: {json_err}. Content: {content}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                else:
                    return []
            
            # Handle if LLM wrapped it in an object (ensure we have a list)
            if isinstance(classified, dict):
                 # Common keys Llama might use: "reviews", "results", etc.
                 found_list = False
                 for key in classified:
                     if isinstance(classified[key], list):
                         classified = classified[key]
                         found_list = True
                         break
                 if not found_list:
                     logger.warning(f"No list found in dictionary response: {classified}")
                     return []
            
            # Validation: Ensure the number of reviews matches and themes are valid
            valid_classified = []
            for item in classified:
                theme = item.get("theme")
                if theme in themes:
                    valid_classified.append({
                        "review": item.get("review"),
                        "date": item.get("date"),
                        "theme": theme
                    })
                else:
                    logger.warning(f"Invalid theme found: {theme}. Defaulting to closest or skipping.")
                    # In a strict scenario, we could skip or re-prompt. 
                    # Here we skip to maintain data integrity or map to the first theme as fallback if needed.
            
            return valid_classified
            
        except Exception as e:
            logger.warning(f"Classification attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                logger.error(f"Batch classification failed after {max_retries} attempts.")
                return []

def run_phase2c():
    """
    Orchestrate the review classification into final themes.
    """
    logger.info("Starting Phase 2C: Review Classification...")
    
    reviews, themes = load_data()
    if not reviews or not themes:
        return
        
    logger.info(f"Classifying {len(reviews)} reviews into {len(themes)} themes.")
    logger.info(f"Themes: {themes}")
    
    batch_size = 15 # Smaller batches for higher precision in classification
    all_classified = []
    
    for i in range(0, len(reviews), batch_size):
        batch = reviews[i:i + batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}/{(len(reviews)-1)//batch_size + 1}...")
        
        results = classify_batch(batch, themes)
        all_classified.extend(results)
        
    # Final Validation
    valid_count = len(all_classified)
    logger.info(f"Successfully classified {valid_count} out of {len(reviews)} reviews.")
    
    # Theme distribution logging
    from collections import Counter
    distribution = Counter([r["theme"] for r in all_classified])
    logger.info("Theme Distribution:")
    for theme, count in distribution.items():
        logger.info(f"- {theme}: {count}")
        
    # Save output
    output_path = "output/v2c_classified_reviews.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_classified, f, indent=2, ensure_ascii=False)
        
    logger.info(f"Phase 2C complete. Results saved to {output_path}.")

if __name__ == "__main__":
    run_phase2c()
