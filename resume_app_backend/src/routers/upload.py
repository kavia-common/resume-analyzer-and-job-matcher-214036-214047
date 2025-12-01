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


@router.post(
    "/resumes/upload",
    tags=["Resumes"],
    status_code=201,
    response_model=UploadResponse,
)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: Annotated[UploadFile, File()],
    user_id: Annotated[int, Form()],
    resume_repo: ResumeRepository = Depends(),
    orchestrator: AnalysisOrchestratorService = Depends(),
):
    """
    Upload a resume file, parse it, and create an analysis.
    The analysis is run in the background. The response contains the ID for status polling.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")

    # Validate file type to some extent
    if file.content_type not in [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
    ]:
        raise HTTPException(
            status_code=422,
            detail="Invalid file type. Please upload a PDF, DOC, DOCX, or TXT file.",
        )

    try:
        content = await file.read()
        # Basic text extraction, a real implementation would use a library like textract
        content_text = content.decode("utf-8", errors="ignore")
    except Exception as e:
        raise HTTPException(
            status_code=422, detail=f"Error reading or decoding file: {e}"
        )

    if not content_text.strip():
        raise HTTPException(
            status_code=422, detail="File appears to be empty or could not be read."
        )

    # 1. Create the resume record first
    resume_id = await resume_repo.create(
        user_id=user_id,
        source="upload",
        url=file.filename,
        content_text=content_text,
    )

    # 2. Start the analysis in the background
    analysis_id = await orchestrator.start_analysis_for_resume(
        user_id=user_id, resume_id=resume_id, background_tasks=background_tasks
    )

    # 3. Return the analysis ID for the client to poll
    return UploadResponse(analysis_id=analysis_id)
