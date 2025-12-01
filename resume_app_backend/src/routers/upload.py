from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from src.domain.schemas import UploadResponse
from src.repositories.resumes import ResumeRepository
from src.services.analysis_orchestrator import AnalysisOrchestratorService

router = APIRouter()


@router.post("/resumes/upload", tags=["Resumes"], status_code=201, response_model=UploadResponse)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: Annotated[UploadFile, File()],
    userId: Annotated[int, Form()],
    resume_repo: ResumeRepository = Depends(),
    orchestrator: AnalysisOrchestratorService = Depends(),
):
    """
    Upload a resume file, parse it, and create an analysis.
    The analysis is run in the background. The response contains the ID for status polling.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")

    try:
        content = await file.read()
        content_text = content.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading or decoding file: {e}")

    # 1. Create the resume record first
    resume_id = await resume_repo.create(
        user_id=userId, source="upload", url=file.filename, content_text=content_text
    )

    # 2. Start the analysis in the background
    analysis_id = await orchestrator.start_analysis_for_resume(
        user_id=userId,
        resume_id=resume_id,
        text=content_text,
        background_tasks=background_tasks,
    )

    # 3. Return the analysis ID for the client to poll
    return UploadResponse(analysisId=analysis_id)
