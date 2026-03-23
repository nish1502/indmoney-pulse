import os
import json
import logging
import groq
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Groq
client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))

def load_fee_kb(file_path="src/phase5_fee_explainer/fee_kb.json"):
    """
    Load the fee knowledge base.
    Note: When running from backend/, path starts with src/.
    """
    # Adjust for relative path if running as module
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(base_path, "phase5_fee_explainer/fee_kb.json")
    
    if not os.path.exists(full_path):
        logger.error(f"KB file not found: {full_path}")
        return None
        
    with open(full_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_fee_explanation(kb_data):
    """
    Generate a concise fee explanation using Gemini.
    """
    if not kb_data:
        return None

    model = "llama-3.1-8b-instant"
    
    prompt = f"""
    You are a Senior Product Support Analyst at INDMoney. Use the provided Facts to generate a structured explanation for the scenario: "{kb_data['scenario']}".
    
    ### Raw Facts:
    {json.dumps(kb_data['facts'], indent=2)}
    
    ### Guidelines:
    1. STRICT LIMIT: Maximum 6 bullet points.
    2. TONE: Neutral, facts-only, and extremely clear.
    3. NO RECOMMENDATIONS: Do not say things like "we recommend" or "you should".
    4. NO COMPARISONS: Do not compare with other apps.
    5. FORMAT: Use a clear bulleted list.
    6. SOURCE LINKS: Include at least 2 relevant URLs from the provided source_links.
    7. LAST CHECKED: End the explanation with "Last checked: {kb_data['last_checked']}".
    
    ### Desired Output Structure:
    ## {kb_data['scenario']} Explanation
    
    - [Bullet point 1]
    - [Bullet point 2]
    - [Bullet point 3]
    - [Bullet point 4]
    - [Bullet point 5]
    - [Bullet point 6]
    
    ### Reference Sources:
    - [Link 1]
    - [Link 2]
    
    Last checked: {kb_data['last_checked']}
    """

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Groq Fee Explanation failed: {e}")
        return None

def run_phase5():
    """
    Orchestrate the Fee Explainer phase.
    """
    logger.info("Starting Phase 5: Fee Explanation Generation...")
    
    kb_data = load_fee_kb()
    if not kb_data:
        return
        
    explanation = generate_fee_explanation(kb_data)
    
    if explanation:
        output_path = "output/v5_fee_explanation.md"
        # Ensure output dir exists (main pipe handles this usually)
        os.makedirs("output", exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(explanation)
        
        # Also save as structured JSON for API
        json_output = {
            "scenario": kb_data['scenario'],
            "last_checked": kb_data['last_checked'],
            "explanation": explanation,
            "source_links": kb_data['source_links'][:2]
        }
        with open("output/v5_fee_explanation.json", 'w', encoding='utf-8') as f:
            json.dump(json_output, f, indent=2)
            
        logger.info(f"Phase 5 complete. Fee explanation saved to {output_path}.")
        return json_output
    else:
        logger.error("Failed to generate fee explanation.")
        return None

if __name__ == "__main__":
    run_phase5()
