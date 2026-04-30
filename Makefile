.PHONY: install run test format help

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v --cov=.

format:
	black . && isort .

help:
	@echo "Comandos disponíveis:"
	@echo "  make install  - Instala as dependências"
	@echo "  make run      - Executa o servidor"
	@echo "  make test     - Executa os testes"
	@echo "  make format   - Formata o código"
