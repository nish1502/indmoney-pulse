import json
import os
import random

def validate_p2c():
    file_path = "output/v2c_classified_reviews.json"
    if not os.path.exists(file_path):
        print("FAIL: output/v2c_classified_reviews.json not found.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_count = len(data)
    print(f"=== Execution Stats ===")
    print(f"Total reviews processed: {total_count}")
    print(f"Total classified reviews: {len(data)}")
    print("")

    # Theme distribution
    themes = ["App Performance", "UI Problems", "High Charges", "Account Issues", "Trading Features"]
    distribution = {t: 0 for t in themes}
    for r in data:
        distribution[r["theme"]] += 1

    print("=== Theme Distribution ===")
    for theme, count in distribution.items():
        print(f"- {theme}: {count}")
    print("")

    checks = {
        "Completeness (one theme, no nulls)": True,
        "Valid Themes (from approved list)": True,
        "Distribution Sanity (no 0, no >70%)": True,
        "Correctness (Spot-check heuristics)": True
    }

    problems = []

    # 1. Completeness & Validity
    for i, r in enumerate(data):
        theme = r.get("theme")
        if not theme:
            checks["Completeness (one theme, no nulls)"] = False
            problems.append(f"Review {i} has no theme: {r}")
        elif theme not in themes:
            checks["Valid Themes (from approved list)"] = False
            problems.append(f"Review {i} has invalid theme '{theme}': {r}")

    # 2. Distribution Sanity
    for theme, count in distribution.items():
        if count == 0:
            checks["Distribution Sanity (no 0, no >70%)"] = False
            problems.append(f"Theme '{theme}' has 0 reviews.")
        if count / total_count > 0.70:
            checks["Distribution Sanity (no 0, no >70%)"] = False
            problems.append(f"Theme '{theme}' exceeds 70% of total data (X%).")

    # 3. Misclassification Detection (Keyword Heuristics)
    heuristics = {
        "App Performance": ["slow", "lag", "crash", "time", "loading", "delay", "hang"],
        "UI Problems": ["ui", "layout", "color", "graphic", "design", "interface", "icon"],
        "High Charges": ["charge", "fee", "brokerage", "cost", "money", "deduct"],
        "Account Issues": ["kyc", "login", "bank", "account", "blocked", "verify", "signup"]
    }

    suspicious = []
    for r in data:
        text = r["review"].lower()
        theme = r["theme"]
        
        # Cross-validation: Check if another theme's keywords are more dominant
        for other_theme, kws in heuristics.items():
            if theme != other_theme:
                for kw in kws:
                    if f" {kw} " in f" {text} ": # simple word match or just kw in text
                        if other_theme == "App Performance" and theme == "UI Problems" and "crash" in text:
                            suspicious.append(f"Review: '{r['review'][:60]}...' -> Theme: {theme} (Expected {other_theme}? Found 'crash')")
                        if other_theme == "High Charges" and theme == "Account Issues" and "brokerage" in text:
                            suspicious.append(f"Review: '{r['review'][:60]}...' -> Theme: {theme} (Expected {other_theme}? Found 'brokerage')")

    # 4. Spot Check (Print 10 random)
    print("=== Spot Check (10 random) ===")
    sample = random.sample(data, min(10, total_count))
    for r in sample:
        print(f"Review: \"{r['review']}\"")
        print(f"Theme: \"{r['theme']}\"")
        print("-" * 20)
    print("")

    if suspicious:
        print("=== Misclassification Detection (Suspicious Mappings) ===")
        for s in suspicious:
            print(f"❌ {s}")
        if len(suspicious) > 5:
            print(f"... and {len(suspicious)-5} more.")
        checks["Correctness (Spot-check heuristics)"] = False
    else:
        print("No suspicious mappings detected by heuristics.\n")

    print("=== Validation Summary ===")
    for check, passed in checks.items():
        print(f"{check}: {'PASS' if passed else 'FAIL'}")

if __name__ == "__main__":
    validate_p2c()
