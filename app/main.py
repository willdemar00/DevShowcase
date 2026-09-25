from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app import models  # noqa: F401  (registra as tabelas no metadata)
from app.database import Base, engine
from app.routers import profiles, projects, technologies


@asynccontextmanager
async def lifespan(app: FastAPI):
    # cria as tabelas no SQLite na primeira execução
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="DevShowcase API",
    description="API para vitrine de projetos de desenvolvedores.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Deixa os erros de validação mais legíveis: campo + mensagem."""
    errors = [
        {
            "campo": ".".join(str(loc) for loc in err["loc"] if loc != "body"),
            "mensagem": err["msg"],
        }
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={"detail": "Dados inválidos.", "erros": errors},
    )


app.include_router(profiles.router)
app.include_router(technologies.router)
app.include_router(projects.router)


@app.get("/", tags=["Status"])
def root():
    return {"api": "DevShowcase API", "status": "online", "docs": "/docs"}
