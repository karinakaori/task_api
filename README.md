# API de Gerenciamento de Tarefas

<!-- README_RENDER_VERSION: 2026-05-01-notranslate-v2 -->

> Este README ja esta em portugues. Se ele for aberto no navegador, desative a traducao automatica da pagina para preservar nomes tecnicos como `Alembic`, `Uvicorn` e `Pydantic`.

## Visao Geral

Este projeto e uma aplicacao de tarefas com backend em `FastAPI` e frontend estatico. A interface permite criar, listar, mover e excluir tarefas em um quadro com colunas de status, prazo final, urgencia e progresso.

A arquitetura foi organizada em camadas para separar rotas HTTP, regras de negocio, acesso ao banco, configuracoes e frontend.

## Funcionalidades

- Quadro com as colunas `A Fazer`, `Em andamento` e `Concluidas`.
- Cadastro de tarefa com titulo, descricao opcional e prazo final.
- Mudanca de status por botao ou por arrastar e soltar.
- Exclusao de tarefas.
- Indicador visual de urgencia:
  - verde: prazo depois de amanha ou mais distante;
  - amarelo: prazo amanha;
  - vermelho: prazo hoje ou vencido;
  - neutro: tarefa concluida ou sem prazo.
- Barra de progresso com base nas tarefas concluidas.
- Filtro por status e paginacao na API.
- Rate limit simples por IP.
- Logs estruturados em JSON.
- Respostas de erro padronizadas.
- Migracoes de banco com `Alembic`.
- Execucao local ou com `Docker`.

## Ferramentas Usadas

- `Python 3.10+`
- `FastAPI`
- `Uvicorn`
- `SQLAlchemy`
- `SQLite`
- `Alembic`
- `Pydantic`
- `pydantic-settings`
- `pytest`
- `HTTPX`
- `Docker`

## Estrutura

```txt
app/
  api/routes/        Rotas HTTP
  core/              Configuracao, logs, erros, seguranca e rate limit
  db/                Conexao e modelos do banco
  repositories/      Consultas e alteracoes no banco
  schemas/           Contratos Pydantic
  services/          Regras de negocio
  static/            Frontend estatico
alembic/             Migracoes do banco
tests/               Testes automatizados
doc/                 Documentacao complementar
```

## Como Executar Localmente

1. Crie o ambiente virtual:

```bash
python -m venv .venv
```

2. Ative o ambiente.

Windows:

```powershell
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

3. Instale as dependencias:

```bash
pip install -r requirements.txt
```

4. Opcionalmente, crie o arquivo `.env`:

```powershell
Copy-Item .env.example .env
```

5. Aplique as migracoes:

```bash
alembic upgrade head
```

6. Inicie a aplicacao:

```bash
uvicorn app.main:app --reload
```

7. Abra no navegador:

```txt
http://localhost:8000/
```

8. Documentacao interativa da API:

```txt
http://localhost:8000/docs
```

## Comandos com Makefile

```bash
make install
make migrate
make run
```

Outros comandos:

```bash
make test
make docker-run
make docker-build
```

## Executar com Docker

```bash
docker compose up --build
```

Depois acesse:

```txt
http://localhost:8000/
```

O `docker-compose.yml` aplica as migracoes antes de subir a API e guarda o banco `SQLite` em um volume Docker.

## Configuracao

As variaveis principais ficam em `.env.example`:

```txt
APP_NAME=Task API
APP_DESCRIPTION=Servico de gerenciamento de tarefas com FastAPI.
APP_VERSION=1.0.0
ENVIRONMENT=development
DATABASE_URL=sqlite:///./tasks.db
RATE_LIMIT_MAX_REQUESTS=30
RATE_LIMIT_WINDOW_SECONDS=60
```

## Rotas da API

- `POST /tasks`: cria uma tarefa.
- `GET /tasks`: lista tarefas com paginacao e filtro por status.
- `GET /tasks/{id}`: busca uma tarefa pelo UUID.
- `PUT /tasks/{id}`: atualiza parcialmente uma tarefa.
- `DELETE /tasks/{id}`: remove uma tarefa.

Parametros de `GET /tasks`:

- `skip`: quantidade de registros ignorados. Padrao: `0`.
- `limit`: quantidade maxima de registros. Padrao: `50`. Maximo: `100`.
- `status`: filtro opcional. Valores: `todo`, `in_progress` ou `done`.

Resposta de exemplo:

```json
{
  "items": [
    {
      "id": "7d879d2c-78b8-48af-9e0d-7f0b60d9ce0f",
      "title": "Escrever testes",
      "description": "Cobrir fluxo principal",
      "status": "todo",
      "owner_id": null,
      "created_at": "2026-05-01T12:00:00",
      "due_date": "2026-05-03"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 50
}
```

As rotas aceitam o cabecalho opcional `X-User-Id`. Ele prepara o projeto para autenticacao futura e permite separar tarefas por usuario quando informado.

## Resposta de Erro

Formato padrao:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": []
  }
}
```

## Arquitetura

Fluxo principal:

```txt
Cliente -> FastAPI Router -> TaskService -> TaskRepository -> SQLite
```

| Camada | Responsabilidade |
| --- | --- |
| Cliente | Interface web ou cliente HTTP. |
| Router | Recebe requisicoes e define respostas HTTP. |
| Schemas | Valida entradas e saidas com `Pydantic`. |
| Service | Centraliza regras de negocio. |
| Repository | Acessa e altera dados no banco. |
| SQLite | Armazena as tarefas. |

## Fluxo de Criacao

1. Cliente envia `POST /tasks`.
2. Router valida o corpo com `TaskCreate`.
3. Router chama `TaskService.create`.
4. Service chama `TaskRepository.create`.
5. Repository grava a tarefa no banco.
6. API retorna `201 Created` com `TaskResponse`.

## Testes

```bash
pytest tests/ -v
```

Ou:

```bash
make test
```

Os testes usam `SQLite` em memoria, sem alterar o arquivo local `tasks.db`.

## Migracoes

Aplicar migracoes:

```bash
alembic upgrade head
```

Criar uma nova migracao depois de alterar modelos `SQLAlchemy`:

```bash
alembic revision --autogenerate -m "descricao da alteracao"
```

Pelo Makefile:

```bash
make revision message="descricao da alteracao"
```

## Uso da Interface

1. Abra `http://localhost:8000/`.
2. Preencha titulo, descricao e prazo final.
3. Clique em `Adicionar tarefa`.
4. Mova a tarefa entre colunas pelo botao ou por arrastar e soltar.
5. Acompanhe urgencia e progresso nos indicadores do topo.

## Boas Praticas

- Nao versionar `.env`, bancos locais ou credenciais.
- Usar variaveis de ambiente para configuracao.
- Manter migracoes versionadas com `Alembic`.
- Manter testes isolados do banco local.
- Usar logs estruturados para facilitar diagnostico.
- Usar respostas de erro consistentes para integracao com frontend e clientes externos.

## Observacoes

- O campo `due_date` aceita valores no formato `YYYY-MM-DD`.
- Prazos sao tratados como datas locais no frontend para evitar deslocamento por fuso horario.
- Tarefas concluidas nao recebem indicador ativo de urgencia.
- O frontend e servido por `app/main.py`.
- Os arquivos estaticos ficam em `app/static`.
