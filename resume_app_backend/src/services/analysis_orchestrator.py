from typing import List, Optional
from uuid import UUID

from fastapi import BackgroundTasks, Depends

from src.repositories.analyses import AnalysisRepository
from src.repositories.findings import FindingRepository
from src.repositories.skills import SkillRepository
from src.repositories.analysis_skills import AnalysisSkillRepository
from src.repositories.suggestions import SuggestionRepository
from src.repositories.jobs import JobRepository
from src.repositories.recommendations import RecommendationRepository
from src.repositories.user_preferences import UserPreferenceRepository
from src.repositories.resumes import ResumeRepository
from src.services.ats_rules import evaluate_ats_basics
from src.services.skill_extraction import extract_skills_from_text
from src.services.recommendations import score_job_match, apply_user_preferences


class AnalysisOrchestratorService:
    """Coordinates analysis pipeline: ATS checks, skills extraction, suggestions, and recommendations."""

    def __init__(
        self,
        analyses: AnalysisRepository = Depends(),
        findings: FindingRepository = Depends(),
        skills: SkillRepository = Depends(),
        analysis_skills: AnalysisSkillRepository = Depends(),
        suggestions: SuggestionRepository = Depends(),
        jobs: JobRepository = Depends(),
        recs: RecommendationRepository = Depends(),
        prefs: UserPreferenceRepository = Depends(),
        resumes: ResumeRepository = Depends(),
    ) -> None:
        self.analyses = analyses
        self.findings = findings
        self.skills = skills
        self.analysis_skills = analysis_skills
        self.suggestions = suggestions
        self.jobs = jobs
        self.recs = recs
        self.prefs = prefs
        self.resumes = resumes

    async def _run_analysis_pipeline(
        self, analysis_id: UUID, user_id: UUID, text: Optional[str] = None, resume_id: Optional[int] = None
    ) -> None:
        """The core analysis pipeline. To be run as a background task or synchronously."""
        try:
            # Set status to running at the beginning of execution
            await self.analyses.update_status(analysis_id, status="running")

            analysis_text = text
            if resume_id and not analysis_text:
                resume_record = await self.resumes.get(resume_id)
                if resume_record:
                    analysis_text = resume_record.get("content_text")

            score, findings, missing_core = evaluate_ats_basics(analysis_text)

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
            extracted = extract_skills_from_text(analysis_text)
            candidate_skill_names: List[str] = []
            for name, conf, stype in extracted:
                skill_id = await self.skills.get_or_create(name, stype)
                await self.analysis_skills.create(analysis_id, skill_id, conf)
                candidate_skill_names.append(name)

            # finalize analysis
            await self.analyses.update_status(analysis_id, status="complete", score_overall=score)

            # generate recommendations
            await self._create_recommendations(analysis_id, user_id, candidate_skill_names)

        except Exception:
            await self.analyses.update_status(analysis_id, status="failed", score_overall=None)
            # In a real app, you'd have more robust error logging here.
            raise

    # PUBLIC_INTERFACE
    async def start_analysis_for_resume(
        self, user_id: UUID, resume_id: int, background_tasks: BackgroundTasks
    ) -> UUID:
        """Creates an analysis record and schedules the pipeline to run in the background."""
        analysis_id = await self.analyses.create(
            user_id=user_id,
            resume_id=resume_id,
            profile_id=None,
            target_role=None,
            status="queued",
        )

        background_tasks.add_task(self._run_analysis_pipeline, analysis_id=analysis_id, user_id=user_id, resume_id=resume_id)

        return analysis_id

    # PUBLIC_INTERFACE
    async def analyze_text(self, user_id: UUID, text: Optional[str], target_role: Optional[str] = None) -> UUID:
        """Create an analysis record, run ATS checks and skill extraction synchronously, and store results."""
        analysis_id = await self.analyses.create(
            user_id=user_id,
            resume_id=None,
            profile_id=None,
            target_role=target_role,
            status="running",  # Start as running since it's sync
            score_overall=None,
        )

        await self._run_analysis_pipeline(analysis_id, user_id, text)
        return analysis_id

    async def _create_recommendations(self, analysis_id: UUID, user_id: UUID, candidate_skills: List[str]) -> None:
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
