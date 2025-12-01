import logging
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        logger.error(f"Error reading or decoding file: {e}", exc_info=True)
        raise HTTPException(
            status_code=422, detail=f"Error reading or decoding file: {e}"
        )

    if not content_text.strip():
        raise HTTPException(
            status_code=422, detail="File appears to be empty or could not be read."
        )

    try:
        # 1. Create the resume record first
        logger.info(f"Creating resume record for user {user_id} and file {file.filename}")
        resume_id = await resume_repo.create(
            user_id=user_id,
            source="upload",
            url=file.filename,
            content_text=content_text,
        )
        logger.info(f"Resume record created with ID: {resume_id}")

        # 2. Start the analysis in the background
        logger.info(f"Starting analysis for resume_id {resume_id}")
        analysis_id = await orchestrator.start_analysis_for_resume(
            user_id=user_id, resume_id=resume_id, background_tasks=background_tasks
        )
        logger.info(f"Analysis started with ID: {analysis_id}")

        # 3. Return the analysis ID for the client to poll
        return UploadResponse(analysis_id=analysis_id)
    except Exception as e:
        logger.error(f"Error during resume upload and analysis start: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
