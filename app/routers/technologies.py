from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.technology_repository import TechnologyRepository
from app.schemas.technology import TechnologyCreate, TechnologyResponse

router = APIRouter(prefix="/api/technologies", tags=["Tecnologias"])


@router.post("", response_model=TechnologyResponse, status_code=status.HTTP_201_CREATED)
def create_technology(payload: TechnologyCreate, db: Session = Depends(get_db)):
    repo = TechnologyRepository(db)
    if repo.get_by_name(payload.name):
        raise HTTPException(status.HTTP_409_CONFLICT, "Esta tecnologia já está cadastrada.")
    return repo.create(payload.name)


@router.get("", response_model=list[TechnologyResponse])
def list_technologies(db: Session = Depends(get_db)):
    return TechnologyRepository(db).list_all()
