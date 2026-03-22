import json
import os
import logging
from collections import Counter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_impact_scorer(file_path="output/v2c_classified_reviews.json"):
    """
    Compute impact scores based on frequency and severity weight rules.
    """
    if not os.path.exists(file_path):
        logger.error(f"Classified reviews file not found: {file_path}")
        return {"status": "error", "message": "No data"}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reviews = json.load(f)
    
    severity_3_keywords = ["money", "charged", "loss", "negative", "fraud"]
    severity_2_keywords = ["not working", "issue", "error"]
    
    theme_scores = Counter()
    total_reviews = len(reviews)
    
    for r in reviews:
        text = r["review"].lower()
        theme = r["theme"]
        
        weight = 1
        if any(kw in text for kw in severity_3_keywords):
            weight = 3
        elif any(kw in text for kw in severity_2_keywords):
            weight = 2
        
        theme_scores[theme] += weight
        
    # Scale scores by frequency % to normalize for theme size
    # actually, user said "frequency * severity_weight", which is just sum of weights
    
    # Sort and get top 3
    most_critical = sorted(theme_scores.items(), key=lambda x: x[1], reverse=True)[:3]
    
    output_path = "output/v3_impact.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(most_critical, f, indent=2, ensure_ascii=False)
        
    logger.info(f"Impact scoring complete. Saved to {output_path}.")
    return most_critical

if __name__ == "__main__":
    run_impact_scorer()
