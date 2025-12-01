from typing import Tuple

# PUBLIC_INTERFACE
def evaluate_ats_basics(text: str | None) -> Tuple[float, list[dict], list[str]]:
    """Evaluate minimal ATS compliance on text and return (score, findings, required_sections_missing).

    Heuristic implementation:
    - Checks presence of key sections.
    - Penalizes if text is too short.
    """
    if not text:
        return 0.0, [
            {"category": "content", "severity": "error", "message": "No content available"}
        ], ["summary", "experience", "education"]

    lower = text.lower()
    sections = {
        "summary": any(k in lower for k in ["summary", "about", "objective"]),
        "experience": "experience" in lower or "work history" in lower,
        "education": "education" in lower or "bachelor" in lower or "master" in lower,
        "skills": "skills" in lower,
    }

    findings: list[dict] = []
    missing = [k for k, present in sections.items() if not present]
    for m in missing:
        findings.append({
            "category": "sections",
            "severity": "warning",
            "message": f"Missing common section: {m.capitalize()}"
        })

    score = 100.0
    score -= len(missing) * 10.0
    if len(text.split()) < 150:
        findings.append({
            "category": "length",
            "severity": "info",
            "message": "Content is relatively short; add more details."
        })
        score -= 10.0

    score = max(0.0, min(100.0, score))
    return score, findings, [m for m in missing if m in ("summary", "experience", "education")]
