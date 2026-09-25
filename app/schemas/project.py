from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from app.schemas.technology import TechnologyResponse


class ProjectCreate(BaseModel):
    """DTO de entrada para cadastro de projeto."""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(..., min_length=1, max_length=150, examples=["DevShowcase"])
    description: str | None = Field(None, max_length=2000)
    repository_url: HttpUrl = Field(..., examples=["https://github.com/maria/devshowcase"])
    demo_url: HttpUrl | None = None
    profile_id: int = Field(..., gt=0)
    technology_ids: list[int] = Field(default_factory=list)

    @field_validator("technology_ids")
    @classmethod
    def remove_duplicates(cls, value: list[int]) -> list[int]:
        return list(dict.fromkeys(value))


class ProfileSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class ProjectSummary(BaseModel):
    """Versão resumida usada dentro do perfil."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    repository_url: str


class ProjectResponse(BaseModel):
    """DTO de saída do projeto."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    repository_url: str
    demo_url: str | None
    created_at: datetime
    profile: ProfileSummary
    technologies: list[TechnologyResponse] = []
    feedback_count: int = 0
