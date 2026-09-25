from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.profile_repository import ProfileRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.technology_repository import TechnologyRepository
from app.schemas.project import ProjectCreate, ProjectResponse

router = APIRouter(prefix="/api/projects", tags=["Projetos"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    # o perfil dono do projeto precisa existir
    if not ProfileRepository(db).get_by_id(payload.profile_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Perfil informado não existe.")

    # todas as tecnologias informadas precisam existir
    technologies = TechnologyRepository(db).get_by_ids(payload.technology_ids)
    missing = set(payload.technology_ids) - {t.id for t in technologies}
    if missing:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Tecnologia(s) não encontrada(s): {sorted(missing)}",
        )

    data = payload.model_dump(exclude={"technology_ids"})
    data["repository_url"] = str(payload.repository_url)
    data["demo_url"] = str(payload.demo_url) if payload.demo_url else None
    return ProjectRepository(db).create(data, technologies)


@router.get("", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    return ProjectRepository(db).list_all()
