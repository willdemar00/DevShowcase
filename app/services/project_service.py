import math

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Project
from app.repositories.project_repository import ProjectRepository


class ProjectService:
    """Regras da listagem paginada e do upvote."""

    def __init__(self, db: Session):
        self.db = db
        self.projects = ProjectRepository(db)

    def list(self, technology: str | None, page: int, page_size: int) -> dict:
        technology = technology.strip() if technology else None
        total_items = self.projects.count(technology)
        results = self.projects.list_page(technology, offset=(page - 1) * page_size, limit=page_size)
        return {
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": math.ceil(total_items / page_size),
            "results": results,
        }

    def upvote(self, project_id: int) -> Project:
        if not self.projects.increment_likes(project_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Projeto não encontrado.")
        self.db.commit()
        return self.projects.get_by_id(project_id)
