from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile import ProfileCreate, ProfileResponse

router = APIRouter(prefix="/api/profiles", tags=["Perfis"])


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(payload: ProfileCreate, db: Session = Depends(get_db)):
    repo = ProfileRepository(db)
    if repo.get_by_email(payload.email):
        raise HTTPException(status.HTTP_409_CONFLICT, "Já existe um perfil com este e-mail.")

    data = payload.model_dump()
    data["github_url"] = str(payload.github_url) if payload.github_url else None
    return repo.create(data)


@router.get("/{profile_id}", response_model=ProfileResponse)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = ProfileRepository(db).get_by_id(profile_id)
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Perfil não encontrado.")
    return profile
