import os
import json
import logging
import time
from collections import Counter
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def load_classified_reviews(file_path="output/v2c_classified_reviews.json"):
    """
    Load the classified reviews from Phase 2C.
    """
    if not os.path.exists(file_path):
        logger.error(f"Input file not found: {file_path}")
        return []
        
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_weekly_pulse(reviews, max_retries=3):
    """
    Generate a concise weekly pulse report using Groq (llama-3.1-8b-instant).
    """
    if not reviews:
        logger.error("No reviews to synthesize.")
        return ""
        
    total_reviews = len(reviews)
    theme_distribution = Counter([r["theme"] for r in reviews])
    
    distribution_text = ""
    for theme, count in theme_distribution.most_common():
        percentage = (count / total_reviews) * 100
        distribution_text += f"- {theme}: {percentage:.1f}%\n"
        
    reviews_context = ""
    for theme in theme_distribution.keys():
        theme_reviews = [r["review"] for r in reviews if r["theme"] == theme]
        reviews_context += f"\n### Theme: {theme}\n"
        for r in theme_reviews[:10]:
            reviews_context += f"- {r}\n"

    prompt = f"""
You are a Senior Product Manager at INDMoney. Based on the app reviews below, generate a 200-word EXECUTIVE PULSE REPORT.

### Theme Distribution:
{distribution_text}

### Raw Categorized Reviews:
{reviews_context}

### Strict Requirements:
1. TOP THEMES: Exactly 3 themes with percentages.
2. USER VOICES: Exactly 3 sharp quotes.
3. ACTION IDEAS: Exactly 3 prioritized actions ([HIGH], [MEDIUM], [LOW]). 
4. The [HIGH] priority item must address Account Issues or High Charges if present.

### Output Style:
## INDMoney Weekly Pulse

### Top Themes
- Theme A (X%)
- ...

### User Voices
- "Quote..."
- ...

### Action Ideas
1. [HIGH] Title: Description.
2. ...
"""

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"Report generation attempt {attempt + 1} failed: {e}")
            time.sleep(10)
    return ""

def run_phase3():
    """
    Orchestrate the report generation phase using Groq.
    """
    logger.info("Starting Phase 3 (Groq 8B Engine): Pulse Report Synthesis...")
    
    reviews = load_classified_reviews()
    if not reviews:
        return
        
    report = generate_weekly_pulse(reviews)
    
    if report:
        output_path = "output/v3_weekly_pulse.md"
        with open(output_path, 'w', encoding='utf-8', errors='surrogatepass') as f:
            f.write(report)
        logger.info(f"Phase 3 complete. Report saved to {output_path}.")
    else:
        logger.error("Failed to generate the pulse report.")

if __name__ == "__main__":
    run_phase3()
