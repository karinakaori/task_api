# Regras de Negócio do MVP

## Entidades principais

- **Tarefa**: representa uma ação que precisa ser feita para alcançar uma meta.
- **Status da tarefa**: `todo`, `in_progress`, `done`.
- **Prazo**: data de conclusão desejada.

## Regras

1. A tarefa deve ter um título válido e não pode ser vazia.
2. A descrição é opcional, mas aceita até 500 caracteres.
3. A data de conclusão é opcional, mas se fornecida deve ser armazenada e exibida no formato `YYYY-MM-DD`.
4. O status inicial de uma tarefa criada deve ser `todo`.
5. As tarefas podem ser movidas entre `A Fazer`, `Em andamento` e `Concluídas`.
6. Quando uma tarefa estiver `done`, ela não deve mais receber cor de urgência ativa.
7. A urgência é calculada com base no prazo:
   - Verde: prazo confortável
   - Amarelo: prazo se aproxima (até 24 horas)
   - Vermelho: prazo curto ou vencido (até 4 horas ou vencido)
8. O painel de progresso deve mostrar a porcentagem de tarefas concluídas em relação ao total.
9. A exclusão deve remover a tarefa permanentemente do banco de dados.
10. O frontend deve ser intuitivo e permitir ver, em um relance, que tarefas precisam de atenção.
