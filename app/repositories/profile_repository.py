from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Profile


class ProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> Profile:
        profile = Profile(**data)
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def get_by_id(self, profile_id: int) -> Profile | None:
        return self.db.get(Profile, profile_id)

    def get_by_email(self, email: str) -> Profile | None:
        return self.db.scalar(select(Profile).where(Profile.email == email))
