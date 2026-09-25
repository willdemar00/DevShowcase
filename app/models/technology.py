from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Technology(Base):
    """Tecnologia usada nos projetos (ex: Python, React). Relação N:N com Project."""

    __tablename__ = "technologies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)

    projects: Mapped[list["Project"]] = relationship(
        secondary="project_technology", back_populates="technologies"
    )
