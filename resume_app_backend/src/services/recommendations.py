from typing import List, Optional


# PUBLIC_INTERFACE
def score_job_match(candidate_skills: List[str], job_skills: Optional[List[str]]) -> float:
    """Score a job match based on skill overlap percentage [0-100]."""
    if not candidate_skills or not job_skills:
        return 0.0
    cset = {s.lower() for s in candidate_skills}
    jset = {s.lower() for s in job_skills}
    if not jset:
        return 0.0
    overlap = len(cset & jset)
    score = (overlap / len(jset)) * 100.0
    return round(max(0.0, min(100.0, score)), 2)


# PUBLIC_INTERFACE
def apply_user_preferences(score: float, location: Optional[str], pref_locations: Optional[List[str]], remote_ok: Optional[bool]) -> float:
    """Adjust score for user preferences (simple heuristic)."""
    if score <= 0:
        return 0.0
    adjusted = score
    if pref_locations:
        loc_match = any((location or "").lower().find(pl.lower()) >= 0 for pl in pref_locations)
        if not loc_match and not remote_ok:
            adjusted *= 0.8  # small penalty
    return round(adjusted, 2)
