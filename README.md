# DevShowcase API

API REST para uma vitrine de projetos de desenvolvedores, feita com **Python + FastAPI + SQLAlchemy + SQLite**.

## Integrantes
- Wildemar Pedro Leal
- Matheus Lima Avelino Barros
- Osanan José Leal

## Modelagem

| Entidade | Descrição |
|---|---|
| `Profile` | Perfil do desenvolvedor |
| `Project` | Projeto de um desenvolvedor |
| `Technology` | Tecnologia usada nos projetos |
| `Feedback` | Opinião deixada sobre um projeto |

Relacionamentos:
- **Profile 1 : N Project** (chave estrangeira `profile_id` em `projects`)
- **Project N : N Technology** (tabela associativa `project_technology`)
- **Project 1 : N Feedback** (chave estrangeira `project_id` em `feedbacks`)

## Estrutura

```
app/
├── main.py            # criação da aplicação, rotas e tratamento de erros
├── database.py        # conexão com o banco e sessão
├── models/            # entidades (tabelas)
├── schemas/           # DTOs de entrada (validação) e de saída
├── repositories/      # camada de acesso a dados
└── routers/           # endpoints REST
```

## Como rodar

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

A API sobe em `http://localhost:8000`. O banco `devshowcase.db` é criado automaticamente na primeira execução.
A documentação interativa (Swagger) fica em `http://localhost:8000/docs`.

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/profiles` | Cadastra um perfil |
| GET | `/api/profiles/{id}` | Busca um perfil por id (com seus projetos) |
| POST | `/api/technologies` | Cadastra uma tecnologia |
| GET | `/api/technologies` | Lista todas as tecnologias |
| POST | `/api/projects` | Cadastra um projeto |
| GET | `/api/projects` | Lista os projetos |

### Validações
- Nome do perfil e título do projeto não podem ser vazios
- E-mail precisa ser válido e único
- `github_url`, `repository_url` e `demo_url` precisam ser URLs válidas
- Nome de tecnologia não pode ser vazio nem repetido
- Projeto só é criado se o perfil e as tecnologias informadas existirem

### Códigos de resposta
- `201` criado com sucesso
- `200` consulta com sucesso
- `404` recurso não encontrado
- `409` registro duplicado
- `422` dados inválidos

## Testes com Postman
Importe o arquivo `DevShowcase.postman_collection.json` no Postman. As requisições estão numeradas na ordem certa para a demonstração.
