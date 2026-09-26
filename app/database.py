import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# lê o arquivo .env, se existir (no Render as variáveis vêm do painel)
load_dotenv()


def _normalize_url(url: str) -> str:
    """O Render entrega a URL como postgres://...; o SQLAlchemy com psycopg 3 espera postgresql+psycopg://..."""
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


# Em produção a URL do PostgreSQL vem da variável de ambiente DATABASE_URL.
# Sem ela, a API usa um SQLite local (devshowcase.db) para facilitar o desenvolvimento.
DATABASE_URL = _normalize_url(os.getenv("DATABASE_URL", "sqlite:///./devshowcase.db"))

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # pool_pre_ping testa a conexão antes de usar (o banco na nuvem derruba conexões paradas)
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """Abre uma sessão por requisição e fecha ao final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
