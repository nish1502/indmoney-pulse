import os
import json
import logging
import time
from collections import Counter
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

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
    Generate a concise weekly pulse report using Gemini 2.5 Flash.
    """
    if not reviews:
        logger.error("No reviews to synthesize.")
        return ""
        
    # Pre-calculate counts and percentage distribution
    total_reviews = len(reviews)
    theme_distribution = Counter([r["theme"] for r in reviews])
    
    distribution_text = ""
    for theme, count in theme_distribution.most_common():
        percentage = (count / total_reviews) * 100
        distribution_text += f"- {theme}: {percentage:.1f}%\n"
        
    # Prepare themes and quotes for the prompt
    # List all reviews as categorized summaries if too many
    # For 80 reviews, we can list them all or samples. 
    # Let's provide a structured overview of all reviews to the LLM.
    reviews_context = ""
    for theme in theme_distribution.keys():
        theme_reviews = [r["review"] for r in reviews if r["theme"] == theme]
        reviews_context += f"\n### Theme: {theme}\n"
        # List up to 10 reviews per theme for context
        for r in theme_reviews[:10]:
            reviews_context += f"- {r}\n"

    prompt = f"""
You are a Product Manager at INDMoney. Based on the following app review data, generate a SHARP and INSIGHT-DRIVEN weekly pulse report.

### Theme Distribution (Calculated):
{distribution_text}

### Raw Categorized Reviews:
{reviews_context}

### Strict Requirements (PM Summary Rules):
1. Max 250 words, NO fluff, NO generic "mixed feedback" lines.
2. TONE: Senior Product Manager executive summary.
3. TOP THEMES: List EXACTLY 3 themes with percentages. Ensure at least one Action Item addresses the TOP theme.
4. USER VOICES: List EXACTLY 3 real quotes highlighting actual friction points (not general praise).
5. ACTION IDEAS (CRITICAL):
   - Provide EXACTLY 3 PRIORITIZED action items.
   - Include priority labels: [HIGH], [MEDIUM], [LOW].
   - RULE: The highest priority [HIGH] action must address FINANCIAL RISK or TRANSACTION FAILURE if present in reviews.
   - RULE: Every action must be specific (e.g., "Restore EPF/NPS manual tracking" instead of "Improve account flows").
   - Each action should have a Title and a sharp 1-sentence Explanation.

### Output Format:
## INDMoney Weekly Pulse

### Top Themes
- [Theme Name] ([Percentage]%)
- ...

### User Voices
- "[Quote 1]"
- ...

### Action Ideas
1. [HIGH] [Action Title]:
   [Specific Explanation/Fix]

2. [MEDIUM] [Action Title]:
   [Specific Explanation/Fix]

6. NO PII or redacted PII should appear in the final report unless it's the redacted tags like [REDACTED_EMAIL].
"""

    model_name = "models/gemini-2.5-flash-lite"
    generation_config = {
        "temperature": 0.2, # Low for factual synthesis
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 1024,
    }

    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config
    )

    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            # Log candidate info for debugging truncation
            if response.candidates:
                logger.debug(f"Finish reason: {response.candidates[0].finish_reason}")
                logger.debug(f"Safety ratings: {response.candidates[0].safety_ratings}")
            
            report = response.text
            
            if len(report.split()) > 400: # Safety cap
                logger.warning("Report too long. Retrying with stricter constraints.")
                continue
                
            return report.strip()
            
        except Exception as e:
            logger.warning(f"Report generation attempt {attempt + 1} failed: {e}")
            if "429" in str(e):
                time.sleep(10)
            elif attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                logger.error("Final report generation failed.")
                return ""

def run_phase3():
    """
    Orchestrate the report generation phase.
    """
    logger.info("Starting Phase 3: Weekly Pulse Report Generation...")
    
    reviews = load_classified_reviews()
    if not reviews:
        return
        
    report = generate_weekly_pulse(reviews)
    
    if report:
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        output_path = os.path.join(output_dir, "v3_weekly_pulse.md")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
            
        logger.info(f"Phase 3 complete. Report saved to {output_path}.")
        print("\n--- GENERATED REPORT ---\n")
        print(report)
        print("\n-------------------------\n")
    else:
        logger.error("Failed to generate the pulse report.")

if __name__ == "__main__":
    run_phase3()
