from pydantic import BaseModel, Field


class ErrorItem(BaseModel):
    campo: str = Field(..., examples=["rating"])
    mensagem: str = Field(..., examples=["deve ser no máximo 5"])


class ErrorResponse(BaseModel):
    """Formato de todas as respostas de erro da API (usado na documentação do Swagger)."""

    status: int = Field(..., examples=[400])
    detail: str = Field(..., examples=["Dados inválidos."])
    erros: list[ErrorItem] | None = Field(None, description="Só aparece nos erros de validação")
