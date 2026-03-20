import os
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
    Convert markdown to clean readable text for email body.
    Removes headers (#) and keeps structure.
    """
    if not content:
        return ""
    
    # Remove markdown headers (#)
    cleaned = re.sub(r'#+\s*(.*)', r'\1', content)
    # Remove bold (**)
    cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned)
    
    return cleaned.strip()

def send_email():
    """
    Orchestrate the process and send via Gmail SMTP.
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
    msg['To'] = email_id # Self-send as per requirements
    msg['Subject'] = "INDMoney Weekly Product Pulse"
    
    msg.attach(MIMEText(formatted_body, 'plain'))
    
    # 5. Send using smtplib
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.set_debuglevel(0) # Set to 0 for clean production output
            server.starttls()
            server.login(email_id, email_password)
            server.send_message(msg)
            
        logger.info("Email sent successfully.")
        
    except smtplib.SMTPAuthenticationError:
        logger.error("Authentication failed. Please check your EMAIL_ID and App Password.")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

if __name__ == "__main__":
    send_email()
