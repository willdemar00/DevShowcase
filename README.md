# DevShowcase API

API REST para uma vitrine de projetos de desenvolvedores, feita com **Python + FastAPI + SQLAlchemy**.
Em produção usa **PostgreSQL** no Render; na máquina local também roda com SQLite.

- **API no ar:** https://devshowcase-api-np2f.onrender.com
- **Documentação (Swagger):** https://devshowcase-api-np2f.onrender.com/docs

> A API está no plano gratuito do Render: depois de 15 minutos sem uso ela "dorme", e a primeira
> requisição seguinte demora cerca de 1 minuto.

## Integrantes
- Wildemar Pedro Leal
- Matheus Lima Avelino Barros
- Osanan José Leal

## Modelagem

| Entidade | Descrição |
|---|---|
| `Profile` | Perfil do desenvolvedor |
| `Project` | Projeto de um desenvolvedor, com curtidas (`likes`) e nota média (`avg_rating`) |
| `Technology` | Tecnologia usada nos projetos |
| `Feedback` | Opinião sobre um projeto, com nota de 1 a 5 |

Relacionamentos:
- **Profile 1 : N Project** (chave estrangeira `profile_id` em `projects`)
- **Project N : N Technology** (tabela associativa `project_technology`)
- **Project 1 : N Feedback** (chave estrangeira `project_id` em `feedbacks`)

## Estrutura

```
app/
├── main.py               # criação da aplicação e registro das rotas
├── database.py           # conexão com o banco (DATABASE_URL) e sessão
├── exception_handlers.py # manipulador global de erros
├── models/               # entidades (tabelas)
├── schemas/              # DTOs de entrada (validação) e de saída
├── repositories/         # camada de acesso a dados
├── services/             # regras de negócio (nota média, upvote e paginação)
└── routers/              # endpoints REST
```

## Como rodar localmente

```bash
# 1. criar e ativar o ambiente virtual
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 2. instalar as dependências
pip install -r requirements.txt

# 3. iniciar o servidor
uvicorn app.main:app --reload
```

A API sobe em `http://localhost:8000` e a raiz `/` redireciona para o Swagger em `/docs`.

O banco vem da variável de ambiente `DATABASE_URL`. Sem ela, a API usa o SQLite `devshowcase.db`,
criado automaticamente. Para usar um PostgreSQL, copie o `.env.example` para `.env` e preencha a URL
(o `.env` está no `.gitignore` e não vai para o GitHub):

```env
DATABASE_URL=postgresql://usuario:senha@localhost:5432/devshowcase
```

As tabelas são criadas na inicialização. Quem ainda tem o `devshowcase.db` da etapa 1 deve apagá-lo,
porque as colunas novas (`likes` e `avg_rating`) só aparecem num banco novo.

## Endpoints

| Método | Rota | Descrição | Sucesso |
|---|---|---|---|
| GET | `/api/projects` | Lista os projetos com filtro por tecnologia e paginação | 200 |
| POST | `/api/projects` | Cadastra um projeto | 201 |
| PUT | `/api/projects/{id}/upvote` | Dá um upvote (curtida) no projeto | 200 |
| POST | `/api/projects/{id}/feedbacks` | Envia um feedback e recalcula a nota média | 201 |
| POST | `/api/profiles` | Cadastra um perfil | 201 |
| GET | `/api/profiles/{id}` | Busca um perfil por id (com seus projetos) | 200 |
| POST | `/api/technologies` | Cadastra uma tecnologia | 201 |
| GET | `/api/technologies` | Lista todas as tecnologias | 200 |
| GET | `/status` | Mostra se a API está no ar | 200 |

### Listagem com filtro e paginação

`GET /api/projects?technology=python&page=1&page_size=10`

| Parâmetro | Padrão | Regra |
|---|---|---|
| `technology` | (sem filtro) | Nome da tecnologia; `python`, `Python` e `PYTHON` dão o mesmo resultado |
| `page` | `1` | Inteiro a partir de 1 |
| `page_size` | `10` | Inteiro de 1 a 50 |

```json
{
  "page": 1,
  "page_size": 10,
  "total_items": 2,
  "total_pages": 1,
  "results": [
    {
      "id": 1,
      "title": "Mercadinho do Bairro",
      "description": "Catálogo de produtos e pedidos para mercadinhos de bairro",
      "repository_url": "https://github.com/willdemar00/mercadinho-do-bairro",
      "demo_url": null,
      "likes": 2,
      "avg_rating": 4.0,
      "feedback_count": 2,
      "created_at": "2026-09-25T22:10:31",
      "profile": { "id": 1, "name": "Wildemar Pedro Leal" },
      "technologies": [
        { "id": 1, "name": "Python" },
        { "id": 2, "name": "FastAPI" },
        { "id": 3, "name": "PostgreSQL" }
      ]
    }
  ]
}
```

Uma página depois da última devolve `results` vazio. `page=0`, `page_size=100` ou `page=abc` respondem `400`.

### Upvote

`PUT /api/projects/1/upvote` (sem corpo) devolve `200` com o projeto e o novo valor de `likes`.
A soma é feita pelo próprio banco (`UPDATE projects SET likes = likes + 1`), então dois upvotes ao
mesmo tempo não se perdem. Projeto inexistente responde `404`.

### Feedbacks

`POST /api/projects/1/feedbacks`

```json
{ "author_name": "Visitante", "comment": "Faltou a opção de entrega em casa.", "rating": 3 }
```

- `author_name` e `comment`: obrigatórios, não podem ser vazios
- `rating`: inteiro de 1 a 5

A regra fica na camada de serviço (`app/services/feedback_service.py`): o projeto é travado com
`SELECT ... FOR UPDATE`, o feedback é salvo, a média das notas é recalculada e gravada em
`avg_rating`, tudo **na mesma transação**. Resposta `201`:

```json
{
  "id": 2,
  "author_name": "Visitante",
  "comment": "Faltou a opção de entrega em casa.",
  "rating": 3,
  "project_id": 1,
  "created_at": "2026-09-25T22:12:05",
  "project_avg_rating": 4.0,
  "project_feedback_count": 2
}
```

Projeto inexistente responde `404`.

### Validações da etapa 1
- Nome do perfil e título do projeto não podem ser vazios
- E-mail precisa ser válido e único
- `github_url`, `repository_url` e `demo_url` precisam ser URLs válidas
- Nome de tecnologia não pode ser vazio nem repetido
- Projeto só é criado se o perfil e as tecnologias informadas existirem

## Erros

Todos os erros passam pelo manipulador global em `app/exception_handlers.py` e voltam no mesmo formato:

```json
{ "status": 404, "detail": "Projeto não encontrado." }
```

Nos erros de validação vem também a lista `erros`, com o campo e a mensagem em português. O FastAPI
devolveria `422` nesses casos; a API converte para `400`:

```json
{
  "status": 400,
  "detail": "Dados inválidos.",
  "erros": [
    { "campo": "comment", "mensagem": "não pode ficar vazio" },
    { "campo": "rating", "mensagem": "deve ser no máximo 5" }
  ]
}
```

| Status | Quando |
|---|---|
| `400` | Corpo inválido, JSON malformado, id que não é número, `page`/`page_size` fora da regra |
| `404` | Projeto, perfil, tecnologia ou rota inexistente |
| `409` | E-mail de perfil ou tecnologia já cadastrados |
| `500` | Erro inesperado (o detalhe fica só no log do servidor) |

## Deploy no Render

1. **Banco:** New → Postgres, nome `devshowcase-postgres`, região **Ohio**, plano **Free**.
   Quando ficar disponível, copiar a **Internal Database URL**.
2. **API:** New → Web Service ligado a este repositório, branch `main`, região **Ohio** (a mesma do banco):
   - Runtime: Python (a versão vem do arquivo `.python-version`: 3.12)
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Plano: Free
3. **Environment:** variável `DATABASE_URL` com a Internal Database URL. A senha do banco fica só no
   painel do Render, nunca no código. A API converte `postgres://` para o formato do SQLAlchemy e usa
   `pool_pre_ping` para descartar conexões que o banco derrubou.
4. **Auto-Deploy:** On Commit. Cada commit na `main` gera um deploy novo.

O PostgreSQL gratuito do Render expira 30 dias depois de criado.

## Testes com Postman

Importe o arquivo `DevShowcase.postman_collection.json`. A variável `baseUrl` vem com
`http://localhost:8000`; para testar em produção, troque para `https://devshowcase-api-np2f.onrender.com`.

| Pasta | O que faz |
|---|---|
| 0. Preparação | Cadastra tecnologias, os perfis do grupo e três projetos, guardando os ids (rodar uma vez antes das outras) |
| 1. Listagem com filtro e paginação | Filtro por tecnologia (minúsculas e maiúsculas), páginas e filtro sem resultado |
| 2. Upvote | Duas curtidas seguidas no mesmo projeto |
| 3. Feedbacks e nota média | Nota 5, nota 3 e a média conferida na listagem |
| 4. Erros 400 e 404 | Validações, JSON malformado, id inválido, projeto e rota inexistentes |
| 5. Etapa 1 | Perfis, tecnologias e projetos da etapa 1 |

Todas as requisições têm testes; a coleção inteira roda pelo Runner do Postman.
