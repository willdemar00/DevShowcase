from sqlalchemy import select
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

    def list_all(self) -> list[Project]:
        stmt = (
            select(Project)
            .options(
                selectinload(Project.profile),
                selectinload(Project.technologies),
                selectinload(Project.feedbacks),
            )
            .order_by(Project.id)
        )
        return list(self.db.scalars(stmt))
