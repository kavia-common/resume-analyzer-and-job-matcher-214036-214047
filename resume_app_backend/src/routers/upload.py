from fastapi import APIRouter, File, UploadFile, Form
from typing import Annotated

from src.services.analysis_orchestrator import AnalysisOrchestratorService
from src.repositories.resumes import ResumeRepository

router = APIRouter()

@router.post("/resumes/upload", tags=["Resumes"], status_code=201)
async def upload_resume(
    file: Annotated[UploadFile, File()],
    user_id: Annotated[int, Form()],
):
    """
    Upload a resume file, parse it, and create an analysis.
    """
    content = await file.read()
    content_text = content.decode("utf-8")  # simple decode, might need more robust parsing

    # Not awaiting the result intentionally, fire-and-forget
    orchestrator = AnalysisOrchestratorService()
    analysis_id = await orchestrator.analyze_text(user_id=user_id, text=content_text)

    resume_repo = ResumeRepository()
    resume_id = await resume_repo.create(
        user_id=user_id,
        source="upload",
        url=None,
        content_text=content_text
    )

    return {"resume_id": resume_id, "analysis_id": analysis_id}
