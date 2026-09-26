from sqlalchemy import func, select, update
from sqlalchemy.orm import Session, selectinload

from app.models import Project, Technology


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict, technologies: list[Technology]) -> Project:
        project = Project(**data)
        project.technologies = technologies
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def get_by_id(self, project_id: int, lock: bool = False) -> Project | None:
        stmt = select(Project).where(Project.id == project_id)
        if lock:
            # SELECT ... FOR UPDATE: trava a linha do projeto até o fim da transação
            stmt = stmt.with_for_update()
        return self.db.scalar(stmt)

    @staticmethod
    def _filter(stmt, technology: str | None):
        if technology:
            # filtro pelo nome da tecnologia sem diferenciar maiúsculas/minúsculas
            stmt = stmt.where(
                Project.technologies.any(func.lower(Technology.name) == technology.lower())
            )
        return stmt

    def count(self, technology: str | None = None) -> int:
        stmt = self._filter(select(func.count(Project.id)), technology)
        return self.db.scalar(stmt)

    def list_page(self, technology: str | None, offset: int, limit: int) -> list[Project]:
        stmt = (
            select(Project)
            .options(
                selectinload(Project.profile),
                selectinload(Project.technologies),
                selectinload(Project.feedbacks),
            )
            .order_by(Project.id)
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(self._filter(stmt, technology)))

    def increment_likes(self, project_id: int) -> bool:
        """UPDATE projects SET likes = likes + 1: o próprio banco soma, então nenhum upvote se perde."""
        result = self.db.execute(
            update(Project).where(Project.id == project_id).values(likes=Project.likes + 1)
        )
        return result.rowcount > 0
