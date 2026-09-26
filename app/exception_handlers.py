"""Manipulador global de erros.

Toda resposta de erro da API sai daqui, sempre no mesmo formato:
    {"status": 404, "detail": "Projeto não encontrado."}
Nos erros de validação vem também a lista "erros", com o campo e a mensagem.
Os erros de validação do FastAPI (que seriam 422) são devolvidos como 400.
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("devshowcase")

# tradução das mensagens mais comuns do Pydantic (o texto original vem em inglês)
VALIDATION_MESSAGES = {
    "missing": "campo obrigatório",
    "string_too_short": "não pode ficar vazio",
    "string_too_long": "pode ter no máximo {max_length} caracteres",
    "greater_than_equal": "deve ser maior ou igual a {ge}",
    "greater_than": "deve ser maior que {gt}",
    "less_than_equal": "deve ser no máximo {le}",
    "int_parsing": "deve ser um número inteiro",
    "int_type": "deve ser um número inteiro",
    "int_from_float": "deve ser um número inteiro",
    "string_type": "deve ser um texto",
    "list_type": "deve ser uma lista",
    "url_parsing": "não é uma URL válida",
    "url_scheme": "a URL deve começar com http:// ou https://",
    "json_invalid": "JSON malformado: confira aspas, vírgulas e chaves",
    "model_attributes_type": "o corpo deve ser um objeto JSON",
    "dict_type": "o corpo deve ser um objeto JSON",
}

# mensagens do próprio FastAPI/Starlette que chegam em inglês
HTTP_MESSAGES = {
    "Not Found": "Rota não encontrada.",
    "Method Not Allowed": "Método não permitido nesta rota.",
}


def _error(status_code: int, detail: str, erros: list | None = None, headers=None) -> JSONResponse:
    content = {"status": status_code, "detail": detail}
    if erros:
        content["erros"] = erros
    return JSONResponse(status_code=status_code, content=content, headers=headers)


def _translate(err: dict) -> str:
    if err["type"] == "value_error" and "email" in err["msg"]:
        return "e-mail inválido"
    template = VALIDATION_MESSAGES.get(err["type"])
    if not template:
        return err["msg"]
    try:
        return template.format(**err.get("ctx", {}))
    except KeyError:
        return err["msg"]


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        erros = []
        for err in exc.errors():
            loc = [str(p) for p in err["loc"] if p not in ("body", "query", "path")]
            if err["type"] == "json_invalid":
                loc = []
            erros.append({"campo": ".".join(loc) or "corpo", "mensagem": _translate(err)})
        return _error(status.HTTP_400_BAD_REQUEST, "Dados inválidos.", erros)

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException):
        detail = HTTP_MESSAGES.get(exc.detail, exc.detail)
        return _error(exc.status_code, detail, headers=getattr(exc, "headers", None))

    @app.exception_handler(IntegrityError)
    async def integrity_error(request: Request, exc: IntegrityError):
        return _error(status.HTTP_409_CONFLICT, "Registro duplicado ou ligado a um dado que não existe.")

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception):
        logger.exception("Erro inesperado em %s %s", request.method, request.url.path)
        return _error(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Erro interno no servidor. Tente novamente em instantes.",
        )
