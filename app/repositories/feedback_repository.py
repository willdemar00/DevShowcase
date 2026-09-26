from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Feedback


class FeedbackRepository:
    """Repositório de feedbacks. Não faz commit: quem fecha a transação é o service."""

    def __init__(self, db: Session):
        self.db = db

    def add(self, project_id: int, data: dict) -> Feedback:
        feedback = Feedback(project_id=project_id, **data)
        self.db.add(feedback)
        self.db.flush()  # envia o INSERT sem encerrar a transação
        return feedback

    def rating_stats(self, project_id: int) -> tuple[int, float]:
        """Quantidade de feedbacks e média das notas do projeto."""
        count, avg = self.db.execute(
            select(func.count(Feedback.id), func.avg(Feedback.rating)).where(
                Feedback.project_id == project_id
            )
        ).one()
        return count, float(avg)
