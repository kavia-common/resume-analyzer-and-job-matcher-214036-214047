import logging
from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from asyncpg.exceptions import PostgresError

from src.domain.schemas import UploadResponse
from src.repositories.resumes import ResumeRepository
from src.repositories.users import UserRepository
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
    user_id: Annotated[UUID, Form()],
    file: Annotated[UploadFile, File()],
    resume_repo: ResumeRepository = Depends(),
    user_repo: UserRepository = Depends(),
    orchestrator: AnalysisOrchestratorService = Depends(),
) -> UploadResponse:
    """
    Upload a resume file, parse it, and create an analysis.
    The analysis is run in the background. The response contains the ID for status polling.
    """
    logger.info(f"Received resume upload request for user_id='{user_id}'")

    # Validate user existence
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=422, detail=f"User with id '{user_id}' not found.")

    if not file or not file.filename:
        raise HTTPException(status_code=422, detail="A file upload is required.")

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

    content_text: str | None = None
    try:
        content = await file.read()
        if file.content_type == "text/plain":
            try:
                content_text = content.decode("utf-8")
            except UnicodeDecodeError:
                content_text = content.decode("latin-1")
        else:
            logger.warning(
                f"Attempting basic text extraction from binary file type '{file.content_type}'. "
                "A dedicated library is needed for reliable results."
            )
            content_text = content.decode("utf-8", errors="replace").replace("\ufffd", " ")

    except Exception as e:
        logger.error(
            f"Error reading or decoding file '{file.filename}' for user {user_id}: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=422, detail=f"Error reading or processing file content: {e}"
        )

    if not content_text or not content_text.strip():
        raise HTTPException(
            status_code=422,
            detail="Could not extract text from file. It may be empty or in an unsupported format.",
        )

    try:
        # 1. Create the resume record first
        logger.info(
            f"Attempting to create resume record for user_id='{user_id}' file='{file.filename}'"
        )
        resume_id = await resume_repo.create(
            user_id=user_id,
            file_name=file.filename,
            content_type=file.content_type,
            content_text=content_text,
        )
        logger.info(
            f"Successfully created resume record with id={resume_id} for user_id='{user_id}'"
        )

        # 2. Create analysis record and schedule the background task
        logger.info(f"Attempting to start analysis for resume_id={resume_id}")
        analysis_id = await orchestrator.start_analysis_for_resume(
            user_id=user_id, resume_id=resume_id
        )
        background_tasks.add_task(
            orchestrator.run_analysis_pipeline,
            analysis_id=analysis_id,
            user_id=user_id,
            resume_id=resume_id,
        )
        logger.info(
            f"Successfully enqueued analysis with analysis_id='{analysis_id}' for resume_id={resume_id}"
        )

        # 3. Return the analysis ID for the client to poll
        return UploadResponse(analysis_id=analysis_id)
    except PostgresError as e:
        logger.critical(
            f"Database error during resume processing for user '{user_id}': {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=503, detail="Service temporarily unavailable. Please try again later."
        )
    except Exception as e:
        logger.error(
            f"Critical error during resume processing for user '{user_id}': {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="Internal server error while processing resume."
        )
