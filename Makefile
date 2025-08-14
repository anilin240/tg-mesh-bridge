SHELL := /bin/sh

# Convenience wrapper around docker compose in infra/
define DOCKER_COMPOSE
cd infra && docker compose
endef

.PHONY: up down logs db test

up:
	$(DOCKER_COMPOSE) up -d --build

down:
	$(DOCKER_COMPOSE) down

logs:
	$(DOCKER_COMPOSE) logs -f app

db:
	$(DOCKER_COMPOSE) exec app alembic upgrade head

test:
	$(DOCKER_COMPOSE) exec app pytest -q


