from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Feedback(Base):
    """Opinião deixada sobre um projeto. Cada projeto tem vários feedbacks (1:N)."""

    __tablename__ = "feedbacks"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_name: Mapped[str] = mapped_column(String(120), nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # nota de 1 a 5
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    project: Mapped["Project"] = relationship(back_populates="feedbacks")
