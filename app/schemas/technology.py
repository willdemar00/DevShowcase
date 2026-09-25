from pydantic import BaseModel, ConfigDict, Field


class TechnologyCreate(BaseModel):
    """DTO de entrada para cadastro de tecnologia."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=60, examples=["Python"])


class TechnologyResponse(BaseModel):
    """DTO de saída da tecnologia."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
