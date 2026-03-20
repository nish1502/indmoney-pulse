import os
import json
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Phase 1: Ingestion & Cleaning
from src.phase1_ingestion.scraper import fetch_reviews
from src.phase1_ingestion.cleaner import clean_reviews

# Phase 2: Theme Engine
from src.phase2_theme_engine.extractor import run_phase2a
from src.phase2_theme_engine.consolidator import run_phase2b
from src.phase2_theme_engine.classifier import run_phase2c

# Phase 3: Pulse Report Generation
from src.phase3_pulse_generator.report_generator import run_phase3

# Phase 4: Email Automation
from src.phase4_automation.email_service import send_email

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_phase1():
    """
    Ingest latest reviews, clean them, and save to v1_raw_reviews.json.
    """
    logger.info(">>> Starting Phase 1: Ingestion & Cleaning...")
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    raw_reviews = fetch_reviews(package_name="in.indwealth", count=200)
    if not raw_reviews:
        raise Exception("No reviews fetched during Phase 1.")
        
    cleaned_reviews = clean_reviews(raw_reviews)
    output_path = "output/v1_raw_reviews.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_reviews, f, indent=2, ensure_ascii=False)
        
    logger.info(f"Phase 1 completed: {len(cleaned_reviews)} reviews saved.")

def main():
    """
    Orchestrate the full Weekly Pulse pipeline.
    """
    print("\n🚀 STARTING INDMONEY WEEKLY PULSE PIPELINE\n")
    
    try:
        # Phase 1: Scraping and Cleaning
        run_phase1()
        
        # Phase 2A: Theme Extraction (Groq)
        logger.info(">>> Starting Phase 2A: Batch Theme Extraction...")
        run_phase2a()
        logger.info("Phase 2A completed.")
        
        # Phase 2B: Theme Consolidation (Gemini)
        logger.info(">>> Starting Phase 2B: Theme Consolidation...")
        run_phase2b()
        logger.info("Phase 2B completed.")
        
        # Phase 2C: Review Classification (Groq)
        logger.info(">>> Starting Phase 2C: Review Classification...")
        run_phase2c()
        logger.info("Phase 2C completed.")
        
        # Phase 3: Report Synthesis (Gemini)
        logger.info(">>> Starting Phase 3: Pulse Report Synthesis...")
        run_phase3()
        logger.info("Phase 3 completed.")
        
        # Phase 4: Email Delivery (SMTP)
        logger.info(">>> Starting Phase 4: Email Delivery...")
        send_email()
        logger.info("Phase 4 completed: Email sent successfully.")
        
        print("\n✅ PIPELINE COMPLETED SUCCESSFULLY!\n")
        
    except Exception as e:
        logger.error(f"❌ PIPELINE STOPPED at phase failure: {e}")
        exit(1)

if __name__ == "__main__":
    main()
