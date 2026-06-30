# Leads — common developer tasks.
# Run `make help` for the list. All app commands go through docker compose.

COMPOSE := docker compose

.DEFAULT_GOAL := help
.PHONY: help up down fresh build logs ps restart \
        backend-logs frontend-logs shell migrate seed test lint health

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

up: ## Build (if needed) and start the full stack in the background
	$(COMPOSE) up --build -d
	@echo "App:  http://localhost"
	@echo "Docs: http://localhost/docs"

down: ## Stop the stack (keeps data volumes)
	$(COMPOSE) down

fresh: ## Wipe volumes and rebuild from scratch (clean DB + storage)
	$(COMPOSE) down -v
	$(COMPOSE) up --build -d

build: ## Rebuild images without starting
	$(COMPOSE) build

logs: ## Tail logs for all services
	$(COMPOSE) logs -f

backend-logs: ## Tail backend logs
	$(COMPOSE) logs -f backend

frontend-logs: ## Tail frontend logs
	$(COMPOSE) logs -f frontend

ps: ## Show service status
	$(COMPOSE) ps

restart: ## Restart the backend (after code changes)
	$(COMPOSE) up -d --build backend

shell: ## Open a shell in the backend container
	$(COMPOSE) exec backend sh

migrate: ## Apply database migrations
	$(COMPOSE) exec backend alembic upgrade head

seed: ## (Re)create the attorney account from .env
	$(COMPOSE) exec backend python -m scripts.seed

test: ## Run the backend test suite
	$(COMPOSE) exec backend pytest

lint: ## Lint the backend (ruff)
	$(COMPOSE) exec backend ruff check app

health: ## Hit the health endpoint through nginx
	@curl -fsS http://localhost/health && echo
