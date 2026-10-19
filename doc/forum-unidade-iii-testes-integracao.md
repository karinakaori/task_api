# Unidade III — Testes de integração com GenAI

## Cenário

A API de tarefas recebe chamadas REST pelo FastAPI, valida os dados com Pydantic, encaminha as operações por `TaskService` e `TaskRepository` e persiste os registros em SQLite. O cabeçalho opcional `X-User-Id` delimita as consultas e alterações por proprietário. Os testes usam `TestClient` e SQLite em memória, cobrindo a comunicação entre HTTP, validação, serviço, repositório e banco sem depender do `tasks.db` local.

## Prompts experimentados

Os prompts abaixo foram experimentados com ChatGPT (LLM) usando como contexto o código e os contratos existentes neste repositório. As sugestões foram conferidas contra a implementação antes de serem transformadas em testes.

### 1. Prompt para jornadas ponta a ponta

> Atue como engenheiro de QA especializado em testes de integração de APIs REST. Analise a API de gerenciamento de tarefas neste repositório e gere cenários que validem o fluxo completo entre endpoints, serviços, repositórios e banco de dados. Cubra criação e consulta pelo ID retornado, atualização seguida de nova consulta, filtro e paginação, exclusão seguida de consulta, e isolamento por `X-User-Id`. Para cada caso, informe objetivo, pré-condições, sequência de requisições, status HTTP e asserções sobre resposta e persistência. Inclua casos positivos e negativos. Use somente comportamentos confirmados pelo código e pelos schemas; indique dúvidas em vez de inventar regras.

O prompt orientado a jornadas favoreceu diversidade funcional e dependências entre chamadas: por exemplo, verificar se a criação pode ser seguida por consulta, se uma atualização persiste e se uma exclusão torna o recurso indisponível. Para torná-lo útil, foi importante apontar os componentes reais e pedir que a LLM não inferisse regras ausentes. Isso evitou tratar `X-User-Id` como autenticação: no projeto, ele é um mecanismo de escopo por proprietário.

### 2. Prompt para contratos e casos de erro

> Atue como especialista em testes de contrato e integração de APIs REST. Inspecione as rotas, schemas e configuração da API neste repositório. Gere casos para corpo inválido, campo obrigatório, data e status inválidos, UUID malformado, recurso inexistente e limites de paginação. Para cada caso, especifique a requisição, status esperado, estrutura relevante do erro e efeito esperado no banco. Separe comportamentos comprovados de hipóteses. Não marque como aprovado sem execução dos testes.

O prompt de contrato concentrou os casos de borda e ajudou a relacionar respostas HTTP com efeitos na persistência, como confirmar que um corpo inválido não cria tarefa. A instrução para consultar os schemas e distinguir fatos de hipóteses foi necessária para alinhar as expectativas ao código real: título com 3–100 caracteres e não vazio, três valores possíveis para status, `skip >= 0`, `1 <= limit <= 100`, data válida e UUID válido. O limite de requisições é 30 por IP em 60 segundos na configuração padrão; como já havia teste para 429 e `Retry-After`, a cobertura existente foi reutilizada em vez de duplicada.

## Casos registrados e execução

Os cenários gerados e implementados estão em `tests/test_task_integration_scenarios.py`; a fixture HTTP/SQLite isolada existente em `tests/test_tasks.py` é reutilizada. O caso de rate limit já coberto fica em `tests/test_tasks.py`.

| ID | Cenário | Resultado esperado | Situação |
| --- | --- | --- | --- |
| E2E-01 | Criar e consultar pelo ID retornado | `201`, depois `200` com a tarefa persistida | Aprovado |
| E2E-02 | Atualizar status e consultar novamente | `200`; status atualizado permanece salvo | Aprovado |
| E2E-03 | Filtrar por status e percorrer páginas | Total, filtro e subconjuntos coerentes | Aprovado |
| E2E-04 | Excluir e consultar depois | `204`, depois `404` | Aprovado |
| E2E-05 | Outro usuário consulta/atualiza a tarefa | `404`; tarefa do proprietário continua inalterada | Aprovado |
| CON-01 | Título ausente, data inválida ou status inválido | `422` padronizado; nenhuma tarefa criada | Aprovado |
| CON-02 | `skip` negativo ou `limit` acima do máximo | `422` padronizado | Aprovado |
| CON-03 | UUID malformado | `422` padronizado | Aprovado |
| CON-04 | Excluir ID inexistente | `404` padronizado | Aprovado |
| CON-05 | Exceder limite de requisições | `429` e cabeçalho `Retry-After` | Aprovado; teste existente reutilizado |

Execução após a revisão: ` .venv\Scripts\python.exe -m pytest tests/ -v` — **19 passed**. O pytest reportou apenas um aviso de permissão ao gravar o cache `.pytest_cache`; os testes foram concluídos com sucesso.

## Resposta para o fórum

**Repositório:** https://github.com/karinakaori/task_api

Considerei a integração entre os endpoints REST de tarefas, as camadas de serviço e repositório e o SQLite. Experimentei dois tipos de prompt com ChatGPT: um voltado a jornadas ponta a ponta e outro a contratos e casos de erro. Registrei os prompts e os casos em [`doc/forum-unidade-iii-testes-integracao.md`](doc/forum-unidade-iii-testes-integracao.md) e implementei os cenários em [`tests/test_task_integration_scenarios.py`](../tests/test_task_integration_scenarios.py).

O prompt de jornadas produziu casos mais diversos entre operações encadeadas, como criar e consultar, atualizar e confirmar persistência, filtrar e paginar, excluir e verificar o `404`, além do isolamento entre usuários. O prompt de contratos aprofundou entradas inválidas, limites e respostas de erro, incluindo o efeito no banco. Para melhorar os resultados, dei à LLM contexto das rotas, schemas e regras implementadas, solicitei entradas, status e asserções explícitos e pedi que hipóteses fossem separadas de comportamentos confirmados. Também conferi as sugestões no código e reutilizei a cobertura existente de rate limit.

A suíte foi executada após as alterações: **19 testes passaram**. A experiência mostrou que a GenAI ajuda a ampliar e organizar a cobertura, mas os contratos sugeridos precisam ser confrontados com a implementação e os resultados precisam ser confirmados pela execução.
