from typing import Iterable, List, Tuple


DEFAULT_SKILL_LEXICON = [
    # Technical
    "python", "java", "javascript", "typescript", "sql", "postgresql", "mysql",
    "react", "node", "fastapi", "django", "flask",
    "aws", "gcp", "azure", "docker", "kubernetes", "terraform",
    "machine learning", "deep learning", "nlp", "pandas", "numpy",
    # Soft/Other
    "communication", "leadership", "teamwork", "problem solving",
]


# PUBLIC_INTERFACE
def extract_skills_from_text(text: str | None, lexicon: Iterable[str] = DEFAULT_SKILL_LEXICON) -> List[Tuple[str, float, str]]:
    """Extract skills from text using a lexicon, returning (skill_name, confidence, type).

    Currently a simple substring/word boundary check with basic confidence scoring.
    """
    if not text:
        return []

    t = " " + text.lower() + " "
    results: List[Tuple[str, float, str]] = []
    for raw in lexicon:
        skill = raw.lower()
        # naive word boundary check
        if f" {skill} " in t or skill in t:
            conf = 0.7
            stype = "technical" if any(x in skill for x in ["python", "java", "script", "sql", "react", "node", "fastapi", "django", "flask", "aws", "gcp", "azure", "docker", "kubernetes", "terraform", "ml", "learning", "nlp", "pandas", "numpy"]) else "soft"
            results.append((raw, conf, stype))
    # Deduplicate while keeping first
    seen = set()
    unique: List[Tuple[str, float, str]] = []
    for name, conf, stype in results:
        key = name.lower()
        if key not in seen:
            unique.append((name, conf, stype))
            seen.add(key)
    return unique
