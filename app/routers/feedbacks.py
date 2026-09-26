from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.error import ErrorResponse
from app.schemas.feedback import FeedbackCreate, FeedbackCreatedResponse
from app.services.feedback_service import FeedbackService

router = APIRouter(prefix="/api/projects", tags=["Feedbacks"])


@router.post(
    "/{project_id}/feedbacks",
    response_model=FeedbackCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Envia um feedback (nota de 1 a 5) e recalcula a nota média do projeto",
    responses={
        400: {"model": ErrorResponse, "description": "Nota fora de 1 a 5, comentário vazio ou id inválido"},
        404: {"model": ErrorResponse, "description": "Projeto não encontrado"},
    },
)
def create_feedback(
    payload: FeedbackCreate,
    project_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    return FeedbackService(db).create(project_id, payload)
