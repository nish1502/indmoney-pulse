import os
import json
import logging
import shutil
import asyncio
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Imports from src
from src.phase1_ingestion.scraper import fetch_reviews
from src.phase1_ingestion.cleaner import clean_reviews
from src.phase2_theme_engine.extractor import run_phase2a
from src.phase2_theme_engine.consolidator import run_phase2b
from src.phase2_theme_engine.classifier import run_phase2c
from src.phase3_pulse_generator.report_generator import run_phase3
from src.phase3_pulse_generator.trend_analyzer import run_trend_analyzer
from src.phase3_pulse_generator.impact_scorer import run_impact_scorer
from src.phase4_automation.email_service import send_email

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# FastAPI Instance
app = FastAPI(title="INDMoney Pulse API")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class EmailRequest(BaseModel):
    recipient: Optional[str] = None

# In-Memory State Manager
class PipelineStatus:
    def __init__(self):
        self.state = "idle" 
        self.last_run_timestamp = None
        self.last_run_status = None
        self.error_message = None

status_manager = PipelineStatus()

def run_phase1():
    """Ingest latest reviews, clean them, and save."""
    logger.info(">>> Starting Phase 1: Ingestion & Cleaning...")
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    raw_reviews = fetch_reviews(package_name="in.indwealth", weeks=1) # Limit for now
    if not raw_reviews:
        raise Exception("No reviews fetched during Phase 1.")
        
    cleaned_reviews = clean_reviews(raw_reviews)
    output_path = "output/v1_raw_reviews.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_reviews, f, indent=2, ensure_ascii=False)
    logger.info(f"Phase 1 completed: {len(cleaned_reviews)} reviews saved.")

def execute_pipeline():
    """Background task for the full Weekly Pulse pipeline."""
    global status_manager
    status_manager.state = "running"
    status_manager.last_run_timestamp = datetime.now().isoformat()
    status_manager.error_message = None
    
    try:
        run_phase1()
        run_phase2a()
        run_phase2b()
        
        # Rotate previous classification file
        p2c_output = "output/v2c_classified_reviews.json"
        p2c_prev = "output/v2c_previous.json"
        if os.path.exists(p2c_output):
            shutil.copy(p2c_output, p2c_prev)

        run_phase2c()
        run_phase3()
        run_trend_analyzer()
        run_impact_scorer()
        
        # Optionally send email to default on completion if desired
        # For now, UI handles manual trigger
        
        status_manager.state = "idle"
        status_manager.last_run_status = "success"
        logger.info("Pipeline completed successfully.")
        
    except Exception as e:
        status_manager.state = "failed"
        status_manager.last_run_status = "error"
        status_manager.error_message = str(e)
        logger.error(f"PIPELINE FAILED: {e}")

# API ENDPOINTS

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/status")
def get_status():
    return {
        "state": status_manager.state,
        "last_run_timestamp": status_manager.last_run_timestamp,
        "last_run_status": status_manager.last_run_status,
        "error": status_manager.error_message
    }

@app.post("/run", status_code=202)
def trigger_run(background_tasks: BackgroundTasks):
    if status_manager.state == "running":
        raise HTTPException(status_code=409, detail="Running.")
    background_tasks.add_task(execute_pipeline)
    return {"message": "Started."}

@app.get("/report")
def get_report():
    report_path = "output/v3_weekly_pulse.md"
    trends_path = "output/v3_trends.json"
    impact_path = "output/v3_impact.json"
    
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="No report found.")
    
    with open(report_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    trends = {}
    if os.path.exists(trends_path):
        with open(trends_path, 'r', encoding='utf-8') as f:
            trends = json.load(f)
            
    impact = []
    if os.path.exists(impact_path):
        with open(impact_path, 'r', encoding='utf-8') as f:
            impact = json.load(f)

    return {
        "markdown": md_content,
        "trends": trends,
        "impact": impact,
        "generated_at": status_manager.last_run_timestamp
    }

@app.post("/send-email")
def trigger_email(req: EmailRequest):
    """Manually trigger delivery to a specific recipient."""
    try:
        send_email(recipient=req.recipient)
        return {"message": f"Email sent successfully to {req.recipient or 'default recipient'}."}
    except Exception as e:
        logger.error(f"Manual email trigger failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
