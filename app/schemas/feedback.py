from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FeedbackCreate(BaseModel):
    """DTO de entrada de feedback (endpoint previsto para a próxima etapa)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    author_name: str = Field(..., min_length=1, max_length=120)
    comment: str = Field(..., min_length=1, max_length=1000)
    rating: int = Field(..., ge=1, le=5)


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_name: str
    comment: str
    rating: int
    project_id: int
    created_at: datetime
