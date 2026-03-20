import json
import os
import re

def validate_p2a():
    file_path = "output/v2a_theme_candidates.json"
    if not os.path.exists(file_path):
        print("FAIL: output/v2a_theme_candidates.json not found.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        batches = json.load(f)

    print(f"=== Phase 2A Stats ===")
    print(f"Number of batches created: {len(batches)}")
    print(f"Batch size used: 20 (as per extractor.py)")
    print("")

    vague_themes = ["general issue", "other problems", "misc feedback", "general feedback", "miscellaneous"]
    
    checks = {
        "Theme count (3-5)": True,
        "Theme length (2-3 words)": True,
        "No vague themes": True,
        "No duplicates within batch": True
    }
    
    problems = []
    all_themes = []

    for b in batches:
        b_id = b["batch_id"]
        themes = b["themes"]
        print(f"Batch {b_id}:")
        for t in themes:
            print(f"- {t}")
            all_themes.append(t)
        print("")

        # 1. Theme count
        if not (3 <= len(themes) <= 5):
            checks["Theme count (3-5)"] = False
            problems.append(f"Batch {b_id} has {len(themes)} themes (expected 3-5).")

        # 2. Theme length & vague themes
        seen_in_batch = set()
        for t in themes:
            words = t.split()
            if not (2 <= len(words) <= 3):
                checks["Theme length (2-3 words)"] = False
                problems.append(f"Batch {b_id} theme '{t}' has {len(words)} words (expected 2-3).")
            
            if t.lower() in vague_themes:
                checks["No vague themes"] = False
                problems.append(f"Batch {b_id} has vague theme: '{t}'")
            
            if t.lower() in seen_in_batch:
                checks["No duplicates within batch"] = False
                problems.append(f"Batch {b_id} has duplicate theme: '{t}'")
            seen_in_batch.add(t.lower())

    print("=== Cross-Batch Consistency Check ===")
    from collections import Counter
    counts = Counter([t.lower() for t in all_themes])
    print("All Unique Themes (Frequency):")
    for t, count in counts.most_common():
        print(f"- {t}: {count}")
    print("")

    print("=== Validation Summary ===")
    for check, passed in checks.items():
        print(f"{check}: {'PASS' if passed else 'FAIL'}")

    if problems:
        print("\n=== Problematic Themes/Batches ===")
        for p in problems:
            print(f"- {p}")

if __name__ == "__main__":
    validate_p2a()
