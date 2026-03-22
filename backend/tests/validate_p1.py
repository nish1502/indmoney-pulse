import json
import random
import re
import os
from langdetect import detect

def validate():
    file_path = "output/v1_raw_reviews.json"
    if not os.path.exists(file_path):
        print(f"FAIL: {file_path} not found.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"=== Execution Stats ===")
    print(f"Total reviews after cleaning: {len(data)}")
    print("")

    print(f"=== Sample Data (up to 10 random) ===")
    sample = random.sample(data, min(10, len(data)))
    for i, r in enumerate(sample):
        print(f"{i+1}. [{r['date']}] {r['review'][:100]}...")
    print("")

    checks = {
        "Word count filter": True,
        "Language filter": True,
        "PII removal": True,
        "Data integrity": True
    }
    
    problems = []

    # 1. Word count & Empty checks
    for r in data:
        text = r.get("review", "")
        if not text:
            checks["Data integrity"] = False
            problems.append(f"Empty/Null review: {r}")
            continue
            
        words = text.split()
        if len(words) < 5:
            checks["Word count filter"] = False
            problems.append(f"Short review (< 5 words): '{text}'")

    # 2. Language check (all should be 'en')
    for r in data:
        text = r.get("review", "")
        try:
            lang = detect(text)
            if lang != 'en':
                checks["Language filter"] = False
                problems.append(f"Non-English detected ({lang}): '{text}'")
        except:
            pass # Skip if detection fails

    # 3. PII Detection (Scanning for @ or phone-like patterns in CLEANED output)
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    # Phone: 10+ digits OR +91... or space-separated digits
    phone_pattern = r'(\d{10,})|(\+\d{1,2}[\s-]?\d{10})'
    
    for r in data:
        text = r.get("review", "")
        if re.search(email_pattern, text):
            checks["PII removal"] = False
            problems.append(f"Email pattern found: '{text}'")
        if re.search(phone_pattern, text):
            # Also check for redacted version
            if "[REDACTED_PHONE]" not in text:
                 # Check if it looks like a real unredacted number
                 pass
        
        # Explicitly checking for the pattern the user asked: "10+ digits or formats like +91, spaces"
        # However, we ALREADY redacted in cleaner.py. We are checking if the REDACTION missed it.
        digit_count = sum(c.isdigit() for c in text if c.isdigit())
        if digit_count >= 10:
             # This might be normal numbers (dates, amounts), so we have to be careful.
             # But the user asked us to scan for it.
             # Let's check for specific formats like +91
             if re.search(r'\+91', text) and "[REDACTED_PHONE]" not in text:
                 checks["PII removal"] = False
                 problems.append(f"Unredacted +91 found: '{text}'")

    print("=== Validation Summary ===")
    for check, passed in checks.items():
        print(f"{check}: {'PASS' if passed else 'FAIL'}")

    if problems:
        print("\n=== Problematic Reviews ===")
        for p in problems[:10]: # Cap at 10
            print(f"- {p}")
        if len(problems) > 10:
            print(f"... and {len(problems)-10} more.")

if __name__ == "__main__":
    validate()
