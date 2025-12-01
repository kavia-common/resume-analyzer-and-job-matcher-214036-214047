from typing import List, Optional

from src.repositories.analyses import AnalysisRepository
from src.repositories.findings import FindingRepository
from src.repositories.skills import SkillRepository
from src.repositories.analysis_skills import AnalysisSkillRepository
from src.repositories.suggestions import SuggestionRepository
from src.repositories.jobs import JobRepository
from src.repositories.recommendations import RecommendationRepository
from src.repositories.user_preferences import UserPreferenceRepository
from src.services.ats_rules import evaluate_ats_basics
from src.services.skill_extraction import extract_skills_from_text
from src.services.recommendations import score_job_match, apply_user_preferences


class AnalysisOrchestratorService:
    """Coordinates analysis pipeline: ATS checks, skills extraction, suggestions, and recommendations."""

    def __init__(self) -> None:
        self.analyses = AnalysisRepository()
        self.findings = FindingRepository()
        self.skills = SkillRepository()
        self.analysis_skills = AnalysisSkillRepository()
        self.suggestions = SuggestionRepository()
        self.jobs = JobRepository()
        self.recs = RecommendationRepository()
        self.prefs = UserPreferenceRepository()

    # PUBLIC_INTERFACE
    async def analyze_text(self, user_id: int, text: Optional[str], target_role: Optional[str] = None) -> int:
        """Create an analysis record, run ATS checks and skill extraction, and store results."""
        analysis_id = await self.analyses.create(
            user_id=user_id,
            resume_id=None,
            profile_id=None,
            target_role=target_role,
            status="running",
            score_overall=None,
        )

        try:
            score, findings, missing_core = evaluate_ats_basics(text)

            # store findings
            for f in findings:
                await self.findings.create(
                    analysis_id, f.get("category", "general"), f.get("severity", "info"), f.get("message", ""), f
                )

            # suggestions based on missing sections
            for section in missing_core:
                await self.suggestions.create(
                    analysis_id,
                    title=f"Add {section.capitalize()} section",
                    message=f"Consider adding a clear {section} section to improve ATS parsing.",
                    priority="high" if section in ("experience", "education") else "medium",
                )

            # skills
            extracted = extract_skills_from_text(text)
            candidate_skill_names: List[str] = []
            for name, conf, stype in extracted:
                skill_id = await self.skills.get_or_create(name, stype)
                await self.analysis_skills.create(analysis_id, skill_id, conf)
                candidate_skill_names.append(name)

            # finalize analysis
            await self.analyses.update_status(analysis_id, status="complete", score_overall=score)

            # generate recommendations
            await self._create_recommendations(analysis_id, user_id, candidate_skill_names)

            return analysis_id
        except Exception:
            await self.analyses.update_status(analysis_id, status="failed", score_overall=None)
            raise

    async def _create_recommendations(self, analysis_id: int, user_id: int, candidate_skills: List[str]) -> None:
        """Create recommendations comparing candidate skills to recent jobs, adjusted by preferences."""
        jobs = await self.jobs.list_recent(limit=50)
        prefs = await self.prefs.get_by_user(user_id)
        pref_locations = (prefs or {}).get("locations")
        remote_ok = (prefs or {}).get("remote_ok")

        for job in jobs:
            job_skills = job.get("skills_json") or []
            base_score = score_job_match(candidate_skills, job_skills)
            final = apply_user_preferences(base_score, job.get("location"), pref_locations, remote_ok)
            if final > 0:
                await self.recs.create(analysis_id, job["id"], final)
