import os

def validate_p3():
    file_path = "output/v3_weekly_pulse.md"
    if not os.path.exists(file_path):
        print("FAIL: output/v3_weekly_pulse.md not found.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    word_count = len(content.split())
    print("=== Pulse Report Content ===")
    print(content)
    print(f"Word Count: {word_count}")
    print("")

    checks = {
        "Format (Themes, Voices, Actions)": True,
        "Word limit (<=250 words)": True,
        "Top Themes (Percentages)": True,
        "User Quotes (Real language)": True,
        "Action Ideas (Specific)": True,
        "No Fluff (Clean language)": True
    }

    problems = []

    # 1. Format
    for sec in ["### Top Themes", "### User Voices", "### Action Ideas"]:
        if sec not in content:
            checks["Format (Themes, Voices, Actions)"] = False
            problems.append(f"Missing section: {sec}")

    # 2. Word Limit
    if word_count > 250:
        checks["Word limit (<=250 words)"] = False
        problems.append(f"Report is {word_count} words; limit is 250.")

    # 3. Percentages
    import re
    if not re.search(r"\(\d+\.\d+%\)", content):
        checks["Top Themes (Percentages)"] = False
        problems.append("Top Themes missing percentage distribution.")

    # 4. Action Ideas Specificity
    generic_actions = ["Improve UI", "Enhance performance", "Fix bugs", "Improve experience", "User satisfaction"]
    for action in generic_actions:
        if action.lower() in content.lower():
            # Only flag if it's the WHOLE action or too generic
            if any(line.strip().startswith(f"- {action}") for line in content.split("\n")):
                 checks["Action Ideas (Specific)"] = False
                 problems.append(f"Generic action idea found: '{action}'")

    # 5. Fluff Detection
    fluff_phrases = ["Users have mixed feedback", "Overall experience is good", "Some users reported issues"]
    for fluff in fluff_phrases:
        if fluff.lower() in content.lower():
            checks["No Fluff (Clean language)"] = False
            problems.append(f"Fluff phrase found: '{fluff}'")

    print("=== Validation Summary ===")
    overall_pass = True
    for check, passed in checks.items():
        print(f"{check}: {'PASS' if passed else 'FAIL'}")
        if not passed:
            overall_pass = False

    if problems:
        print("\n=== Issues Found ===")
        for p in problems:
            print(f"- {p}")

    print(f"\nFINAL VERDICT: {'PASS (insightful, actionable)' if overall_pass else 'FAIL (generic, vague, or fluffy)'}")

if __name__ == "__main__":
    validate_p3()
