from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Technology


class TechnologyRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str) -> Technology:
        technology = Technology(name=name)
        self.db.add(technology)
        self.db.commit()
        self.db.refresh(technology)
        return technology

    def list_all(self) -> list[Technology]:
        return list(self.db.scalars(select(Technology).order_by(Technology.name)))

    def get_by_name(self, name: str) -> Technology | None:
        # comparação sem diferenciar maiúsculas/minúsculas ("python" == "Python")
        return self.db.scalar(
            select(Technology).where(func.lower(Technology.name) == name.lower())
        )

    def get_by_ids(self, ids: list[int]) -> list[Technology]:
        if not ids:
            return []
        return list(self.db.scalars(select(Technology).where(Technology.id.in_(ids))))
