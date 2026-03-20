import os
import json
import logging
from src.phase1_ingestion.scraper import fetch_reviews
from src.phase1_ingestion.cleaner import clean_reviews

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_phase1():
    """
    Run the ingestion and cleaning phase of the pipeline.
    """
    # 1. Ensure output directory exists
    output_dir = "output"
    if not os.path.exists(output_dir):
        logger.info(f"Creating output directory: {output_dir}")
        os.makedirs(output_dir)
    
    # 2. Ingest: Fetch latest reviews
    raw_reviews = fetch_reviews(package_name="in.indwealth", count=200)
    
    if not raw_reviews:
        logger.warning("No reviews fetched. Ending pipeline.")
        return
        
    # 3. Clean: Remove PII, non-English, and short reviews
    cleaned_reviews = clean_reviews(raw_reviews)
    
    # 4. Save: Persist to JSON
    output_file = os.path.join(output_dir, "v1_raw_reviews.json")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_reviews, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Successfully saved {len(cleaned_reviews)} cleaned reviews to: {output_file}")
            
    except Exception as e:
        logger.error(f"Failed to save output to {output_file}: {e}")

if __name__ == "__main__":
    # In future phases, this orchestrator will grow to call P2, P3, etc.
    run_phase1()
