import asyncio
from main import execute_pipeline
import logging

# Setup basic logging to see progression in GitHub Action logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    print(">>> 🚀 Initializing INDMoney Pulse Pipeline CLI trigger...")
    try:
        # Run the same core business logic as the API's manual trigger
        execute_pipeline()
        print(">>> ✅ Pipeline run completed specifically via CLI.")
    except Exception as e:
        print(f">>> ❌ CRITICAL FAILURE: {e}")
        exit(1)
