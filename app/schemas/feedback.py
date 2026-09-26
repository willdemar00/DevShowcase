from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FeedbackCreate(BaseModel):
    """DTO de entrada de feedback: nota de 1 a 5 e comentário."""

    model_config = ConfigDict(str_strip_whitespace=True)

    author_name: str = Field(..., min_length=1, max_length=120, examples=["Matheus Lima Avelino Barros"])
    comment: str = Field(..., min_length=1, max_length=1000, examples=["Muito fácil de usar!"])
    rating: int = Field(..., ge=1, le=5, examples=[5])


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_name: str
    comment: str
    rating: int
    project_id: int
    created_at: datetime


class FeedbackCreatedResponse(FeedbackResponse):
    """Feedback salvo + como ficou o projeto depois dele."""

    project_avg_rating: float = Field(..., description="Nova nota média do projeto", examples=[4.0])
    project_feedback_count: int = Field(..., description="Total de feedbacks do projeto", examples=[2])
