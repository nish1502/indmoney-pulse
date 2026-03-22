import json
import os
import logging
from collections import Counter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_trend_analyzer(current_path="output/v2c_classified_reviews.json", previous_path="output/v2c_previous.json"):
    """
    Compare current vs previous theme frequencies.
    """
    if not os.path.exists(current_path):
        logger.error("Current classification file not found.")
        return {"status": "error", "message": "No current data"}

    with open(current_path, 'r', encoding='utf-8') as f:
        current_data = json.load(f)
    
    current_counts = Counter([r["theme"] for r in current_data])
    total_current = len(current_data)
    
    if not os.path.exists(previous_path):
        logger.warning("Previous classification file not found. Skipping trend analysis.")
        return {"status": "no_previous", "message": "No previous data"}

    with open(previous_path, 'r', encoding='utf-8') as f:
        previous_data = json.load(f)
    
    previous_counts = Counter([r["theme"] for r in previous_data])
    total_previous = len(previous_data)
    
    trends = {}
    all_themes = set(list(current_counts.keys()) + list(previous_counts.keys()))
    
    for theme in all_themes:
        curr_p = (current_counts[theme] / total_current) * 100 if total_current > 0 else 0
        prev_p = (previous_counts[theme] / total_previous) * 100 if total_previous > 0 else 0
        diff = curr_p - prev_p
        
        trends[theme] = {
            "current_pct": round(curr_p, 1),
            "previous_pct": round(prev_p, 1),
            "change": round(diff, 1),
            "direction": "↑" if diff > 0 else "↓" if diff < 0 else "→"
        }
        
    output_path = "output/v3_trends.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(trends, f, indent=2, ensure_ascii=False)
        
    logger.info(f"Trend analysis complete. Saved to {output_path}.")
    return trends

if __name__ == "__main__":
    run_trend_analyzer()
