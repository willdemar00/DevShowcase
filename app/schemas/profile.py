from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl

from app.schemas.project import ProjectSummary


class ProfileCreate(BaseModel):
    """DTO de entrada para cadastro de perfil."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=120, examples=["Maria Silva"])
    email: EmailStr = Field(..., examples=["maria@email.com"])
    bio: str | None = Field(None, max_length=500)
    github_url: HttpUrl | None = Field(None, examples=["https://github.com/mariasilva"])


class ProfileResponse(BaseModel):
    """DTO de saída do perfil, com a lista resumida de projetos."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    bio: str | None
    github_url: str | None
    created_at: datetime
    projects: list[ProjectSummary] = []
