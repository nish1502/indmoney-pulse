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
    Load cleaned reviews from Phase 1 output.
    """
    if not os.path.exists(file_path):
        logger.error(f"Input file not found: {file_path}")
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_batches(reviews, batch_size=20):
    """
    Split the list of reviews into chunks of specified batch_size.
    """
    for i in range(0, len(reviews), batch_size):
        yield reviews[i:i + batch_size]

def extract_themes_batch(batch_id, batch_reviews, max_retries=3):
    """
    Call Groq to extract themes from a batch of reviews.
    """
    # Prepare the review text for the prompt
    review_texts = "\n".join([f"- {r['review']}" for r in batch_reviews])
    
    prompt = f"""
Extract 3-5 core product themes from the following app reviews.

### Reviews:
{review_texts}

### Strict Rules:
1. Return ONLY 3-5 themes as a JSON list of strings.
2. Each theme must be exactly 2-3 words (e.g., "Slow App Performance").
3. NO vague names like "general", "other", "miscellaneous", or "feedback".
4. NO duplicate or overlapping themes within a batch.
5. Themes must reflect actual issues, features, or user sentiment mentioned.

### Output Format:
["Theme One", "Theme Two", "Theme Three"]
"""

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert product analyst specializing in app review categorization. Return JSON lists only."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            # Extract content and parse as list
            # Note: Llama3-70b on Groq works well with JSON mode
            content = response.choices[0].message.content
            themes = json.loads(content)
            
            # Handle if LLM wrapped it in an object (e.g. {"themes": [...]})
            if isinstance(themes, dict):
                themes = themes.get("themes", list(themes.values())[0])
            
            # Final validation: 3-5 themes, 2-3 words each
            # (Though LLM should do this, we log it)
            logger.info(f"Batch {batch_id} complete. Themes: {themes}")
            return {
                "batch_id": batch_id,
                "themes": themes[:5] # Respect the max limit
            }
            
        except Exception as e:
            logger.warning(f"Batch {batch_id} attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt) # Exponential backoff
            else:
                logger.error(f"Batch {batch_id} failed after {max_retries} attempts.")
                return None

def run_phase2a():
    """
    Orchestrate the batch theme extraction.
    """
    logger.info("Starting Phase 2A: Batch Theme Extraction...")
    
    # Check for API key
    if not os.getenv("GROQ_API_KEY"):
        logger.error("GROQ_API_KEY not found in environment. Please add it to your .env file.")
        return

    reviews = load_reviews()
    if not reviews:
        logger.warning("No reviews to process.")
        return
        
    batches = list(create_batches(reviews, batch_size=20))
    logger.info(f"Total reviews: {len(reviews)}. Created {len(batches)} batches.")
    
    all_batch_results = []
    
    for idx, batch in enumerate(batches):
        batch_id = idx + 1
        result = extract_themes_batch(batch_id, batch)
        if result:
            all_batch_results.append(result)
            
    # Save the output
    output_path = "output/v2a_theme_candidates.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_batch_results, f, indent=2, ensure_ascii=False)
        
    logger.info(f"Phase 2A complete. Saved {len(all_batch_results)} batch results back to {output_path}.")

if __name__ == "__main__":
    run_phase2a()
