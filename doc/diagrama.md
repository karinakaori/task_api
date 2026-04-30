# Diagrama do MVP

```mermaid
flowchart LR
  A[Usuário] --> B[Navegador / Interface Web]
  B --> C[Frontend HTML/CSS/JS]
  C --> D[API FastAPI]
  D --> E[Validação de dados (Pydantic)]
  D --> F[Repositório de tarefas]
  F --> G[SQLite]
  D --> H[Resposta JSON]
  H --> C
  C --> B
  B --> A
```

- O usuário interage com a interface web estática.
- O frontend consome a API REST para criar, listar, atualizar e excluir tarefas.
- A API valida os dados, persiste as tarefas e devolve respostas em JSON.
- A base SQLite guarda o estado das tarefas entre as sessões.
