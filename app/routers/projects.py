from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.profile_repository import ProfileRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.technology_repository import TechnologyRepository
from app.schemas.error import ErrorResponse
from app.schemas.project import ProjectCreate, ProjectPage, ProjectResponse
from app.services.project_service import ProjectService

router = APIRouter(prefix="/api/projects", tags=["Projetos"])


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastra um projeto",
    responses={
        400: {"model": ErrorResponse, "description": "Dados inválidos"},
        404: {"model": ErrorResponse, "description": "Perfil ou tecnologia inexistente"},
    },
)
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


@router.get(
    "",
    response_model=ProjectPage,
    summary="Lista os projetos com filtro por tecnologia e paginação",
    description="Sem filtro, lista todos os projetos. Página além do fim devolve `results` vazio.",
    responses={400: {"model": ErrorResponse, "description": "Parâmetro de consulta inválido"}},
)
def list_projects(
    technology: str | None = Query(
        None,
        min_length=1,
        max_length=60,
        description="Nome da tecnologia (não diferencia maiúsculas/minúsculas)",
        examples=["python"],
    ),
    page: int = Query(1, ge=1, description="Número da página, começando em 1"),
    page_size: int = Query(10, ge=1, le=50, description="Projetos por página (de 1 a 50)"),
    db: Session = Depends(get_db),
):
    return ProjectService(db).list(technology, page, page_size)


@router.put(
    "/{project_id}/upvote",
    response_model=ProjectResponse,
    summary="Dá um upvote (curtida) no projeto",
    description="Soma 1 em `likes` direto no banco (`SET likes = likes + 1`). Não precisa de corpo.",
    responses={
        400: {"model": ErrorResponse, "description": "Id inválido"},
        404: {"model": ErrorResponse, "description": "Projeto não encontrado"},
    },
)
def upvote_project(project_id: int = Path(..., gt=0), db: Session = Depends(get_db)):
    return ProjectService(db).upvote(project_id)
