# Explicação do MVP

## Objetivo

O MVP (Produto Mínimo Viável) deste projeto é criar um gerenciador de tarefas simples e intuitivo que permite ao usuário acompanhar metas, prazos e urgência com clareza.

## Escopo do MVP

- Criação de tarefas com título, descrição e data de conclusão.
- Exibição de tarefas em três colunas: `A Fazer`, `Em andamento` e `Concluídas`.
- Atualização de status por drag and drop ou botão de ação.
- Exibição visual de urgência de prazo com cores e rótulos.
- Painel de controle com contagem de tarefas e progresso da meta.
- Interface em português e navegação simples.

## Por que este MVP é útil?

- Permite que o usuário veja rapidamente se está no caminho certo.
- Ajuda a priorizar tarefas com prazos próximos ou vencidos.
- Mostra a evolução da meta por meio de métricas visuais.
- Mantém a experiência leve usando front-end estático e backend simples.

## Critérios de aceitação

- A interface deve carregar em `http://127.0.0.1:8000`.
- É possível criar uma tarefa com data de entrega.
- A tarefa aparece na coluna correta e pode ser movida entre colunas.
- O painel de urgência atualiza automaticamente conforme os prazos.
- O backend deve responder aos endpoints REST de tarefas.
