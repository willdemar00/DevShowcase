from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.feedback import FeedbackCreate, FeedbackResponse


class FeedbackService:
    """Regra de negócio do feedback: salvar e recalcular a nota média do projeto."""

    def __init__(self, db: Session):
        self.db = db
        self.projects = ProjectRepository(db)
        self.feedbacks = FeedbackRepository(db)

    def create(self, project_id: int, payload: FeedbackCreate) -> dict:
        # trava o projeto: dois feedbacks ao mesmo tempo não calculam a média errada
        project = self.projects.get_by_id(project_id, lock=True)
        if not project:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Projeto não encontrado.")

        # tudo na mesma transação: ou salva o feedback e a média nova, ou não salva nada
        try:
            feedback = self.feedbacks.add(project_id, payload.model_dump())
            count, avg = self.feedbacks.rating_stats(project_id)
            project.avg_rating = round(avg, 2)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        self.db.refresh(feedback)
        return {
            **FeedbackResponse.model_validate(feedback).model_dump(),
            "project_avg_rating": round(avg, 2),
            "project_feedback_count": count,
        }
