import os
import json
import smtplib
import logging
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_report(file_path="output/v3_weekly_pulse.md"):
    """
    Read content from the generated pulse report.
    """
    if not os.path.exists(file_path):
        logger.error(f"Report file not found: {file_path}")
        return None
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading report: {e}")
        return None

def format_email(content):
    """
    Format content including trends and impact scores.
    """
    if not content:
        return ""
    
    # 1. Load context from Phase 3 results
    trends_content = ""
    if os.path.exists("output/v3_trends.json"):
        with open("output/v3_trends.json", 'r', encoding='utf-8') as f:
            trends_data = json.load(f)
            trends_content = "\n--- TRENDS ---\n"
            for theme, info in trends_data.items():
                trends_content += f"{theme}: {info['current_pct']}% ({info['direction']} {abs(info['change'])}%)\n"

    impact_content = ""
    if os.path.exists("output/v3_impact.json"):
        with open("output/v3_impact.json", 'r', encoding='utf-8') as f:
            impact_data = json.load(f)
            impact_content = "\n--- TOP CRITICAL ISSUES ---\n"
            for theme, score in impact_data:
                impact_content += f"- {theme} (Impact Score: {score})\n"

    # 2. Format Body
    # Remove markdown headers (#)
    cleaned = re.sub(r'#+\s*(.*)', r'\1', content)
    # Remove bold (**)
    cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned)
    
    final_body = f"{cleaned.strip()}\n\n{trends_content}\n{impact_content}"
    return final_body

def send_email(recipient: str = None):
    """
    Orchestrate the process and send via Gmail SMTP.
    If recipient is provided, use it. Otherwise, fallback to EMAIL_ID.
    """
    # 1. Load report
    content = load_report()
    if not content:
        return
    
    # 2. Format it
    formatted_body = format_email(content)
    
    # 3. SMTP Config
    email_id = os.getenv("EMAIL_ID")
    email_password = os.getenv("EMAIL_PASSWORD")
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    
    if not email_id or not email_password:
        logger.error("Email credentials (EMAIL_ID/EMAIL_PASSWORD) not found in .env.")
        return

    # 4. Prepare email message
    msg = MIMEMultipart()
    msg['From'] = email_id
    msg['To'] = recipient if recipient else email_id # Use custom recipient if provided
    msg['Subject'] = "INDMoney Weekly Product Pulse"
    
    msg.attach(MIMEText(formatted_body, 'plain'))
    
    # 5. Send using smtplib
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.set_debuglevel(0) # Set to 0 for clean production output
        server.starttls()
        server.login(email_id, email_password)
        server.send_message(msg)
        
    logger.info("Email sent successfully.")

if __name__ == "__main__":
    send_email()
