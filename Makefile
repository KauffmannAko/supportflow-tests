COMPOSE := docker compose
SERVICE := api-tests

.PHONY: help config build up test shell clean

help:
	@echo "Available commands:"
	@echo "  make config  - Validate Docker Compose configuration"
	@echo "  make build   - Build the test image"
	@echo "  make up      - Build test image, start services and run migrations"
	@echo "  make test    - Run tests against the published API image"
	@echo "  make shell   - Open a shell inside the test container"
	@echo "  make clean   - Stop containers and remove test database data"

config:
	$(COMPOSE) config --quiet

build:
	$(COMPOSE) build $(SERVICE)

up:
	sh scripts/test-integration.sh up

test:
	sh scripts/test-integration.sh

shell: build
	$(COMPOSE) run --rm --entrypoint sh $(SERVICE)

clean:
	$(COMPOSE) down --volumes --remove-orphans
