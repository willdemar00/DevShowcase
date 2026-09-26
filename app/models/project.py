from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Table, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Tabela associativa da relação N:N entre Project e Technology
project_technology = Table(
    "project_technology",
    Base.metadata,
    Column("project_id", ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
    Column("technology_id", ForeignKey("technologies.id", ondelete="CASCADE"), primary_key=True),
)


class Project(Base):
    """Projeto do desenvolvedor.
    - N:1 com Profile (cada projeto pertence a um perfil)
    - N:N com Technology
    - 1:N com Feedback
    """

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    repository_url: Mapped[str] = mapped_column(String(255), nullable=False)
    demo_url: Mapped[str | None] = mapped_column(String(255))
    likes: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    avg_rating: Mapped[float | None] = mapped_column(Float)  # nota média; fica null até o 1º feedback
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False
    )
    profile: Mapped["Profile"] = relationship(back_populates="projects")

    technologies: Mapped[list["Technology"]] = relationship(
        secondary=project_technology, back_populates="projects"
    )
    feedbacks: Mapped[list["Feedback"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )

    @property
    def feedback_count(self) -> int:
        return len(self.feedbacks)
