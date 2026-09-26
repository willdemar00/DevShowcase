from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app import models  # noqa: F401  (registra as tabelas no metadata)
from app.database import Base, engine
from app.exception_handlers import register_exception_handlers
from app.routers import feedbacks, profiles, projects, technologies


@asynccontextmanager
async def lifespan(app: FastAPI):
    # cria as tabelas que ainda não existem (SQLite local ou PostgreSQL no Render)
    Base.metadata.create_all(bind=engine)
    yield


DESCRIPTION = """
API para vitrine de projetos de desenvolvedores.

- **Etapa 1:** perfis, tecnologias e projetos.
- **Etapa 2:** feedbacks com nota média, upvote e listagem com filtro por tecnologia e paginação.

Todo erro volta no formato `{"status": 404, "detail": "Projeto não encontrado."}`;
nos erros de validação (status 400) vem também a lista `erros`, com o campo e a mensagem.
"""

app = FastAPI(
    title="DevShowcase API",
    description=DESCRIPTION,
    version="2.0.0",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "Projetos", "description": "Cadastro, listagem paginada e upvote"},
        {"name": "Feedbacks", "description": "Notas de 1 a 5 e nota média do projeto"},
        {"name": "Perfis", "description": "Desenvolvedores donos dos projetos"},
        {"name": "Tecnologias", "description": "Tecnologias usadas nos projetos"},
        {"name": "Status", "description": "Verifica se a API está no ar"},
    ],
)

register_exception_handlers(app)

app.include_router(projects.router)
app.include_router(feedbacks.router)
app.include_router(profiles.router)
app.include_router(technologies.router)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/status", tags=["Status"])
def api_status():
    return {"api": "DevShowcase API", "status": "online", "docs": "/docs"}
