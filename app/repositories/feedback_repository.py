from sqlalchemy.orm import Session

from app.models import Feedback


class FeedbackRepository:
    """Repositório de feedbacks (usado a partir da próxima etapa)."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, project_id: int, data: dict) -> Feedback:
        feedback = Feedback(project_id=project_id, **data)
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback
