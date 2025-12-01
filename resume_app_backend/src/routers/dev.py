from fastapi import APIRouter, Depends, HTTPException
from src.domain.schemas import User, UserCreate
from src.repositories.users import UserRepository

router = APIRouter()


@router.post("/api/v1/dev/create-user", response_model=User, tags=["Development"], include_in_schema=False)
async def create_user_for_testing(
    user_create: UserCreate, user_repo: UserRepository = Depends()
):
    """
    Creates a user for testing purposes. If the user already exists, it returns the existing user.
    This is to make the verification script idempotent.
    """
    existing_user = await user_repo.get_by_email(user_create.email)
    if existing_user:
        return existing_user

    user_id = await user_repo.create(
        email=user_create.email, full_name=user_create.full_name
    )
    created_user = await user_repo.get_by_id(user_id)
    if not created_user:
        # This should realistically not happen
        raise HTTPException(status_code=500, detail="Failed to retrieve user after creation.")
    return created_user
