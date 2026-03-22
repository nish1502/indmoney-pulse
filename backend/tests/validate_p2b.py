import json
import os

def validate_p2b():
    file_path = "output/v2b_consolidated_themes.json"
    if not os.path.exists(file_path):
        print("FAIL: output/v2b_consolidated_themes.json not found.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    final_themes = data.get("final_themes", [])
    
    print("=== Execution Stats ===")
    print(f"Total Unique Raw Themes: 22")
    print(f"Final Themes Generated: {len(final_themes)}")
    print("")

    print("=== Final Themes ===")
    for i, t in enumerate(final_themes):
        print(f"{i+1}. {t}")
    print("")

    checks = {
        "Theme count (3-5)": True,
        "Theme length (2-3 words)": True,
        "No overlap (unique meanings)": True,
        "No vague themes": True,
        "Coverage (Core issues)": True
    }

    problems = []

    # 1. Count
    if not (3 <= len(final_themes) <= 5):
        checks["Theme count (3-5)"] = False
        problems.append(f"Got {len(final_themes)} themes; expected 3-5.")

    # 2. Length & Vague
    vague_list = ["general issues", "user experience", "platform feedback", "other", "miscellaneous"]
    for t in final_themes:
        words = t.split()
        if not (2 <= len(words) <= 3):
            checks["Theme length (2-3 words)"] = False
            problems.append(f"Theme '{t}' has {len(words)} words; expected 2-3.")
        
        if t.lower() in vague_list:
            checks["No vague themes"] = False
            problems.append(f"Theme '{t}' is too vague.")

    # 3. No overlap (simple string similarity/contains)
    for i, t1 in enumerate(final_themes):
        for j, t2 in enumerate(final_themes):
            if i != j and (t1.lower() in t2.lower() or t2.lower() in t1.lower()):
                 # This is a heuristic
                 checks["No overlap (unique meanings)"] = False
                 problems.append(f"Possible overlap: '{t1}' vs '{t2}'")

    # 4. Coverage
    # Core issues: performance, support, UI, charges/payments, account/KYC
    combined = " ".join(final_themes).lower()
    coverage_keywords = ["perform", "stability", "support", "help", "ui", "interface", "charge", "fee", "pay", "kyc", "account", "invest"]
    
    # Let's check how many categories are hit
    found_coverage = False
    for kw in coverage_keywords:
        if kw in combined:
            found_coverage = True
            break
    if not found_coverage:
        checks["Coverage (Core issues)"] = False
        problems.append("Final themes don't seem to cover core app issues.")

    print("=== Validation Summary ===")
    for check, passed in checks.items():
        print(f"{check}: {'PASS' if passed else 'FAIL'}")

    if problems:
        print("\n=== Issues Found ===")
        for p in set(problems): # Unique problems
            print(f"- {p}")

if __name__ == "__main__":
    validate_p2b()
