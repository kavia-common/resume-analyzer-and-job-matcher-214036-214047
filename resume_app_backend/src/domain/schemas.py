from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr


# PUBLIC_INTERFACE
class UserBase(BaseModel):
    """Base schema for a user record."""
    email: EmailStr = Field(..., description="Unique email address of the user")
    full_name: Optional[str] = Field(None, description="Full name of the user")


class UserCreate(UserBase):
    """Schema for creating a user."""
    pass


class User(UserBase):
    """Schema representing a persisted user."""
    id: int = Field(..., description="Primary key")
    created_at: datetime = Field(..., description="Creation timestamp")


# PUBLIC_INTERFACE
class ResumeBase(BaseModel):
    """Base schema for a resume record."""
    user_id: int = Field(..., description="Owner user id (FK users.id)")
    source: str = Field(..., description="Source type: upload, linkedin, naukri, etc.")
    url: Optional[str] = Field(None, description="Source URL when available")
    content_text: Optional[str] = Field(None, description="Extracted plain text content")


class ResumeCreate(ResumeBase):
    """Schema for creating a resume."""
    pass


class Resume(ResumeBase):
    """Schema representing a persisted resume."""
    id: int = Field(..., description="Primary key")
    created_at: datetime = Field(..., description="Creation timestamp")


# PUBLIC_INTERFACE
class ProfileBase(BaseModel):
    """Base schema for a user profile snapshot."""
    user_id: int = Field(..., description="Owner user id")
    platform: str = Field(..., description="Profile platform (linkedin, naukri, etc.)")
    url: str = Field(..., description="Profile URL")
    headline: Optional[str] = Field(None, description="Profile headline or title")
    summary: Optional[str] = Field(None, description="Profile summary/about")
    data_json: Optional[dict] = Field(None, description="Raw parsed profile data as JSON")


class ProfileCreate(ProfileBase):
    """Schema for creating a profile snapshot."""
    pass


class Profile(ProfileBase):
    """Schema representing a persisted profile snapshot."""
    id: int = Field(..., description="Primary key")
    created_at: datetime = Field(..., description="Creation timestamp")


# PUBLIC_INTERFACE
class AnalysisBase(BaseModel):
    """Base schema for an analysis run over a resume or profile."""
    user_id: int = Field(..., description="Owner user id")
    resume_id: Optional[int] = Field(None, description="Analyzed resume id")
    profile_id: Optional[int] = Field(None, description="Analyzed profile id")
    target_role: Optional[str] = Field(None, description="Target role used for analysis")
    status: str = Field(..., description="Status of analysis (queued, running, complete, failed)")
    score_overall: Optional[float] = Field(None, description="Overall ATS score [0-100]")


class AnalysisCreate(AnalysisBase):
    """Schema for creating an analysis run."""
    pass


class Analysis(AnalysisBase):
    """Schema representing a persisted analysis run."""
    id: int = Field(..., description="Primary key")
    created_at: datetime = Field(..., description="Creation timestamp")


# PUBLIC_INTERFACE
class FindingBase(BaseModel):
    """Base schema for an ATS finding result."""
    analysis_id: int = Field(..., description="FK to analyses.id")
    category: str = Field(..., description="Category (formatting, sections, keywords, etc.)")
    severity: str = Field(..., description="Severity (info, warning, error)")
    message: str = Field(..., description="Human-readable message")
    detail_json: Optional[dict] = Field(None, description="Optional structured details")


class FindingCreate(FindingBase):
    """Schema for creating a finding."""
    pass


class Finding(FindingBase):
    """Schema representing a persisted finding."""
    id: int = Field(..., description="Primary key")
    created_at: datetime = Field(..., description="Creation timestamp")


# PUBLIC_INTERFACE
class SkillBase(BaseModel):
    """Base schema for a known skill."""
    name: str = Field(..., description="Canonical skill name")
    type: Optional[str] = Field(None, description="Skill type (technical, soft, tool, etc.)")


class SkillCreate(SkillBase):
    """Schema for creating a skill."""
    pass


class Skill(SkillBase):
    """Schema representing a persisted skill."""
    id: int = Field(..., description="Primary key")
    created_at: datetime = Field(..., description="Creation timestamp")


# PUBLIC_INTERFACE
class AnalysisSkillBase(BaseModel):
    """Base schema for the relation of analysis and extracted skill."""
    analysis_id: int = Field(..., description="FK analyses.id")
    skill_id: int = Field(..., description="FK skills.id")
    confidence: Optional[float] = Field(None, description="Confidence in extraction [0-1]")


class AnalysisSkillCreate(AnalysisSkillBase):
    """Schema for creating analysis-skill relation."""
    pass


class AnalysisSkill(AnalysisSkillBase):
    """Schema representing a persisted analysis-skill record."""
    id: int = Field(..., description="Primary key")
    created_at: datetime = Field(..., description="Creation timestamp")


# PUBLIC_INTERFACE
class SuggestionBase(BaseModel):
    """Base schema for a suggestion produced by analysis."""
    analysis_id: int = Field(..., description="FK analyses.id")
    title: str = Field(..., description="Suggestion short title")
    message: str = Field(..., description="Detailed guidance")
    priority: str = Field(..., description="Priority (low, medium, high)")


class SuggestionCreate(SuggestionBase):
    """Schema for creating a suggestion."""
    pass


class Suggestion(SuggestionBase):
    """Schema representing a persisted suggestion."""
    id: int = Field(..., description="Primary key")
    created_at: datetime = Field(..., description="Creation timestamp")


# PUBLIC_INTERFACE
class JobBase(BaseModel):
    """Base schema for a job opening ingested from sources."""
    external_id: str = Field(..., description="Unique id from external source")
    source: str = Field(..., description="Source identifier")
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: Optional[str] = Field(None, description="Location text")
    description: Optional[str] = Field(None, description="Job description text")
    url: Optional[str] = Field(None, description="Apply or job page URL")
    skills_json: Optional[List[str]] = Field(None, description="List of required/preferred skills")


class JobCreate(JobBase):
    """Schema for creating a job record."""
    pass


class Job(JobBase):
    """Schema representing a persisted job record."""
    id: int = Field(..., description="Primary key")
    created_at: datetime = Field(..., description="Creation timestamp")


# PUBLIC_INTERFACE
class RecommendationBase(BaseModel):
    """Base schema for a recommendation linking analysis and job."""
    analysis_id: int = Field(..., description="FK analyses.id")
    job_id: int = Field(..., description="FK jobs.id")
    score: float = Field(..., description="Match score [0-100]")


class RecommendationCreate(RecommendationBase):
    """Schema for creating recommendation."""
    pass


class Recommendation(RecommendationBase):
    """Schema representing a persisted recommendation."""
    id: int = Field(..., description="Primary key")
    created_at: datetime = Field(..., description="Creation timestamp")


# PUBLIC_INTERFACE
class UserPreferenceBase(BaseModel):
    """Base schema for a user's preference regarding job recommendations."""
    user_id: int = Field(..., description="FK users.id")
    locations: Optional[List[str]] = Field(None, description="Preferred locations")
    roles: Optional[List[str]] = Field(None, description="Preferred roles")
    remote_ok: Optional[bool] = Field(None, description="Whether remote jobs are acceptable")
    salary_min: Optional[int] = Field(None, description="Minimum desired salary (annual)")
    data_json: Optional[dict] = Field(None, description="Other preferences as JSON")


class UserPreferenceCreate(UserPreferenceBase):
    """Schema for creating user preferences."""
    pass


class UserPreference(UserPreferenceBase):
    """Schema representing persisted user preferences."""
    id: int = Field(..., description="Primary key")
    created_at: datetime = Field(..., description="Creation timestamp")


class UploadResponse(BaseModel):
    """Response model for successful upload."""

    analysis_id: int = Field(..., description="Created analysis ID for polling.")


class AnalysisStatus(BaseModel):
    """Response model for analysis status requests."""

    status: str = Field(..., description="Current status of the analysis")
    score_overall: Optional[float] = Field(None, description="Overall score if completed")
