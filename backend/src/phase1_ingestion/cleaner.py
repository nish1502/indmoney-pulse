import re
import logging
from langdetect import detect, DetectorFactory
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# To ensure consistent results from langdetect
DetectorFactory.seed = 0

def _strip_emojis(text):
    """
    Remove emojis from the text using regex to help language detection and word count.
    """
    if not text:
        return ""
    # Remove characters from the emoji range
    # Basic emoji regex
    emoji_pattern = r'[^\x00-\x7F]+'
    return re.sub(emoji_pattern, '', text).strip()

def _remove_pii(text):
    """
    Remove emails and phone numbers from the review text.
    """
    if not text:
        return ""
        
    # Regex for emails
    email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    # Regex for phone numbers (generalized for common formats)
    phone_regex = r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{1,4}?[-.\s]?\(?\d{2,4}?\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b'
        
    # Replace PII with a placeholder (e.g., [REDACTED])
    text = re.sub(email_regex, '[REDACTED_EMAIL]', text)
    text = re.sub(phone_regex, '[REDACTED_PHONE]', text)
    
    return text.strip()

def _is_english(text):
    """
    Return True if the text is English using langdetect.
    """
    if not text:
        return False
        
    try:
        lang = detect(text)
        return lang == 'en'
    except Exception:
        # Fallback to True if detect fails (defaulting to assuming English for unclear short text if it passed other filters)
        # or logging the error.
        return False

def clean_reviews(reviews):
    """
    Clean and filter the fetched reviews.
    """
    logger.info(f"Starting cleaning process for {len(reviews)} reviews...")
    
    cleaned_data = []
    
    for r in reviews:
        review_text = r.get("review", "").strip()
        review_date = r.get("date", "")
        
        # 1. Skip empty reviews
        if not review_text:
            continue
            
        # 2. Basic cleaning (whitespace)
        review_text = review_text.replace('\n', ' ').strip()
        
        # 3. Filter: Non-English reviews (detect on original text)
        if not _is_english(review_text):
            continue
            
        # 4. Strip emojis/non-ASCII for word count analysis
        text_for_analysis = _strip_emojis(review_text)
        
        # 5. Filter: Word count >= 5 (based on text only, no emojis/non-ASCII)
        words = text_for_analysis.split()
        if len(words) < 5:
            continue
            
        # 6. PII Removal (Emails, Phone numbers)
        review_text = _remove_pii(review_text)
        
        # Double check after cleaning
        if not review_text:
            continue
            
        # Success: Add to cleaned data
        cleaned_data.append({
            "review": review_text,
            "date": review_date
        })
        
    logger.info(f"Cleaning complete. Kept {len(cleaned_data)} out of {len(reviews)} reviews.")
    return cleaned_data

if __name__ == "__main__":
    # Test sample
    sample = [
        {"review": "This is a great app for investing in US stocks! Highly recommend.", "date": "2026-03-20"},
        {"review": "Bad app.", "date": "2026-03-20"}, # Should be removed (< 5 words)
        {"review": "C'est une excellente application.", "date": "2026-03-20"}, # Should be removed (French)
        {"review": "Please contact me at test@example.com or 9988776655 for US stock info.", "date": "2026-03-20"} # Should be redacted
    ]
    res = clean_reviews(sample)
    for r in res:
        print(f"Cleaned review: {r['review']}")
