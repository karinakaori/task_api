# API de Gerenciamento de Tarefas

## Visão Geral

Este projeto é um gerenciador de tarefas com backend em FastAPI e frontend estático que ajuda o usuário a acompanhar metas, prazos e progresso do trabalho. A aplicação suporta criação, atualização parcial, exclusão e listagem de tarefas, além de apresentar um painel visual com urgência de prazo e progresso de meta.

## Tecnologias

- Python 3.10+
- FastAPI
- SQLAlchemy
- SQLite
- Pytest
- HTTPX
- Uvicorn

## Como executar

1. Crie o ambiente virtual:

```bash
python -m venv .venv
```

2. Ative o ambiente:

Windows:

```powershell
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Execute a aplicação:

```bash
uvicorn app.main:app --reload
```

5. Acesse a interface web:

- `http://127.0.0.1:8000`

6. Acesse a documentação automática (Swagger):

- `http://127.0.0.1:8000/docs`

## Funcionalidades

- painel visual de tarefas com colunas: `A Fazer`, `Em andamento` e `Concluídas`
- criação de tarefas com título, descrição opcional e data de conclusão
- arrastar e soltar tarefas entre colunas para atualizar status
- indicação de urgência por cor:
  - verde: prazo confortável
  - amarelo: atenção necessária
  - vermelho: tarefa urgente ou vencida
- barra de progresso de meta baseada em tarefas concluídas
- contadores dinâmicos com status geral das tarefas

## Arquitetura

O sistema segue uma separação de responsabilidades entre API, modelos, persistência e frontend.

```mermaid
flowchart LR
    Cliente --> API[FastAPI]
    API --> Validação[Validação de esquema Pydantic]
    Validação --> Repositório[TaskRepository]
    Repositório --> DB[SQLite]
    DB --> Persistência[Tarefas gravadas]
    API --> Resposta[Serialização de resposta]
    Resposta --> Cliente
```

## Fluxo de requisição

```mermaid
sequenceDiagram
    participant Cliente
    participant API as FastAPI
    participant Repo as TaskRepository
    participant DB as SQLite

    Cliente->>API: POST /tasks
    API->>API: Valida TaskCreate
    API->>Repo: create(task_create)
    Repo->>DB: INSERT task
    DB-->>Repo: tarefa persistida
    Repo-->>API: objeto TaskDB
    API->>API: Serializa TaskResponse
    API-->>Cliente: 201 Created
```

## Testes

Para executar o conjunto de testes:

```bash
pytest
```

## Endpoints disponíveis

- `POST /tasks` - cria uma nova tarefa
- `GET /tasks` - lista tarefas com filtros opcionais `skip`, `limit` e `status`
- `GET /tasks/{id}` - obtém uma tarefa pelo UUID
- `PUT /tasks/{id}` - atualiza parcialmente uma tarefa
- `DELETE /tasks/{id}` - remove uma tarefa

## Como usar

1. Abra a interface web em `http://127.0.0.1:8000`
2. Preencha título, descrição e data de conclusão
3. Arraste a tarefa para `Em andamento` ou `Concluídas`
4. Use o painel no topo para identificar rapidamente o que está em dia, em atenção ou urgente

## Observações

- O campo `due_date` aceita apenas data no formato `YYYY-MM-DD`.
- Tarefas concluídas não recebem mais indicação de urgência.
- O frontend é servido via `app/main.py` e os arquivos estáticos estão em `app/static`.
