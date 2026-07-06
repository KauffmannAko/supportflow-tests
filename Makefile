COMPOSE := docker compose
SERVICE := api-tests

.PHONY: help config build test shell clean

help:
	@echo "Available commands:"
	@echo "  make config  - Validate Docker Compose configuration"
	@echo "  make build   - Build the test image"
	@echo "  make test    - Build and run all API tests"
	@echo "  make shell   - Open a shell inside the test container"
	@echo "  make clean   - Remove Compose resources"

config:
	$(COMPOSE) config

build:
	$(COMPOSE) build $(SERVICE)

test: build
	$(COMPOSE) run --rm $(SERVICE)

shell: build
	$(COMPOSE) run --rm --entrypoint sh $(SERVICE)

clean:
	$(COMPOSE) down --remove-orphans