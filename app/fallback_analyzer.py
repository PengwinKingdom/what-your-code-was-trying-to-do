import re

def detect_language(code: str) -> str:
    c = code.strip()

    # Python signals
    if re.search(r'^\s*def\s+\w+\(.*\)\s*:', c, re.M):
        return "python"
    if re.search(r'^\s*(import|from)\s+\w+', c, re.M):
        return "python"
    if re.search(r'^\s*print\s*\(', c, re.M):
        return "python"

    # JavaScript signals
    if re.search(r'\bfunction\b|=>|\bconsole\.log\b|\bconst\b|\blet\b', c):
        return "javascript"

    # C++ signals
    if re.search(r'#include\s*<|\bstd::\b', c):
        return "cpp"

    # C# signals
    if re.search(r'\busing\s+System\b|\bnamespace\b', c):
        return "csharp"

    return "unknown"


def fallback_analyze(code: str, provided_language: str | None = None) -> dict:
    lang = (provided_language or "").strip().lower() or detect_language(code)

    clues = []
    if re.search(r'\bfor\b|\bwhile\b', code): clues.append("Loop detected → iterating over data")
    if re.search(r'\breturn\b', code): clues.append("Return detected → computing a result")
    if re.search(r'\bif\b', code): clues.append("Branching detected → conditional logic")
    if "TODO" in code or "FIXME" in code: clues.append("TODO/FIXME found → unfinished logic")
    if '["' in code or "['" in code: clues.append("Direct key access detected → possible missing key crash")

    if not clues:
        clues = ["Low signal code → needs context to be confident"]

    most_wanted = None
    if '["' in code or "['" in code:
        most_wanted = ("High", "Missing key / undefined field crash", "Direct indexing like item['x'] assumes the key exists")
    elif re.search(r'/\s*0', code) or " / 0" in code:
        most_wanted = ("High", "Division by zero", "Math operation risks runtime error")
    else:
        most_wanted = ("Med", "Input assumptions break silently", "No validation suggests edge cases will slip in")

    severity, problem, why = most_wanted
    
    badges = []
    confidence = 50 + min(30, 10 * (len(clues) - 1))
    
    if '["' in code or "['" in code:
        badges.append("Risk: Missing Key")
        confidence += 10
    if re.search(r'\bfor\b|\bwhile\b', code):
        badges.append("Looping Logic")
    if re.search(r'\bif\b', code):
        badges.append("Branching")
    if "TODO" in code or "FIXME" in code:
        badges.append("Incomplete")
        confidence -= 10

    confidence = max(10, min(95, confidence))
    
    future_problems = [
        {"severity": severity, "problem": f"Most Wanted Bug: {problem}", "why": why},
        {"severity": "Med", "problem": "Maintainability risk as logic grows", "why": "Logic + validation are mixed; changes get risky"},
        {"severity": "Low", "problem": "Harder to extend safely", "why": "No clear contract/tests shown; future features may break behavior"}
    ]

    hidden_assumptions = [
        {"assumption": "Inputs are well-formed and contain expected fields/types", "risk": "Unexpected values can crash or corrupt results"},
        {"assumption": "Required fields exist", "risk": "Missing fields lead to KeyError/undefined values"}
    ]
    
    return {
        "ai_used": False,
        "confidence_score": confidence,
        "badges": badges[:5],
        "language_detected": lang,
        "intended_goal": {
            "summary": "Code Detective Verdict: This code is likely transforming input data into a result",
            "signals": [
                f"Clue #1: {clues[0]}",
                f"Clue #2: {clues[1] if len(clues) > 1 else clues[0]}",
                f"Clue #3: {clues[2] if len(clues) > 2 else clues[0]}",
            ]
        },
        "hidden_assumptions": hidden_assumptions,
        "future_problems": future_problems,
        "one_high_impact_recommendation": {
            "action": "Add a small validation guard before the core logic runs",
            "why_it_matters": "Prevents the most common crashes and makes intent clearer",
            "first_step": "Check required fields/types and return a friendly error if missing"
        },
        "note": "AI quota unavailable --> returning Code Detective fallback"
    }
