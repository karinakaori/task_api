.PHONY: install run test migrate revision docker-build docker-run format help

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v --cov=.

migrate:
	alembic upgrade head

revision:
	alembic revision --autogenerate -m "$(message)"

docker-build:
	docker build -t task-api .

docker-run:
	docker compose up --build

format:
	black . && isort .

help:
	@echo "Comandos disponiveis:"
	@echo "  make install    - Instala as dependencias"
	@echo "  make run        - Executa o servidor"
	@echo "  make test       - Executa os testes"
	@echo "  make migrate    - Aplica as migracoes do banco"
	@echo "  make revision   - Cria uma nova migracao com message=..."
	@echo "  make docker-run - Executa com Docker Compose"
	@echo "  make format     - Formata o codigo"
