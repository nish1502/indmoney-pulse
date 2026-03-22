import asyncio
from main import execute_pipeline
from src.phase4_automation.email_service import send_email
import logging

# Setup basic logging to see progression in GitHub Action logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    print(">>> 🚀 Initializing INDMoney Pulse Pipeline CLI trigger...")
    try:
        # Run the same core business logic as the API's manual trigger
        execute_pipeline()
        print(">>> ✅ Pipeline run completed. Attempting to dispatch intelligence email...")
        
        # Dispatch the email report
        send_email()
        print(">>> 📨 Email dispatch completed specifically via CLI.")
    except Exception as e:
        print(f">>> ❌ CRITICAL FAILURE: {e}")
        exit(1)
