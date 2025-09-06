# Docker Development Scripts

# Start all services
.PHONY: up
up:
	docker-compose up -d

# Start all services with logs
.PHONY: up-logs
up-logs:
	docker-compose up

# Stop all services
.PHONY: down
down:
	docker-compose down

# Stop all services and remove volumes (full reset)
.PHONY: down-volumes
down-volumes:
	docker-compose down -v

# Rebuild all services
.PHONY: build
build:
	docker-compose build

# Rebuild and start services
.PHONY: rebuild
rebuild:
	docker-compose down && docker-compose build && docker-compose up -d

# View logs
.PHONY: logs
logs:
	docker-compose logs -f

# View backend logs only
.PHONY: logs-backend
logs-backend:
	docker-compose logs -f backend

# View frontend logs only
.PHONY: logs-frontend
logs-frontend:
	docker-compose logs -f frontend

# View database logs only
.PHONY: logs-db
logs-db:
	docker-compose logs -f db

# Execute bash in backend container
.PHONY: shell-backend
shell-backend:
	docker-compose exec backend /bin/bash

# Execute bash in frontend container
.PHONY: shell-frontend
shell-frontend:
	docker-compose exec frontend /bin/sh

# Connect to PostgreSQL database
.PHONY: db-shell
db-shell:
	docker-compose exec db psql -U library_user -d library_system

# Run backend tests
.PHONY: test-backend
test-backend:
	docker-compose exec backend pytest

# Install backend dependencies
.PHONY: install-backend
install-backend:
	docker-compose exec backend pip install -r requirements.txt

# Install frontend dependencies
.PHONY: install-frontend
install-frontend:
	docker-compose exec frontend npm install

# Show status of all containers
.PHONY: status
status:
	docker-compose ps

# ===== PODMAN COMMANDS =====

# Start all services with Podman
.PHONY: up-podman
up-podman:
	podman-compose up -d

# Start all services with logs (Podman)
.PHONY: up-logs-podman
up-logs-podman:
	podman-compose up

# Stop all services (Podman)
.PHONY: down-podman
down-podman:
	podman-compose down

# Stop all services and remove volumes (Podman)
.PHONY: down-podman-volumes
down-podman-volumes:
	podman-compose down -v

# Rebuild all services (Podman)
.PHONY: build-podman
build-podman:
	podman-compose build

# Rebuild and start services (Podman)
.PHONY: rebuild-podman
rebuild-podman:
	podman-compose down && podman-compose build && podman-compose up -d

# View logs (Podman)
.PHONY: logs-podman
logs-podman:
	podman-compose logs -f

# View backend logs only (Podman)
.PHONY: logs-backend-podman
logs-backend-podman:
	podman-compose logs -f backend

# View frontend logs only (Podman)
.PHONY: logs-frontend-podman
logs-frontend-podman:
	podman-compose logs -f frontend

# View database logs only (Podman)
.PHONY: logs-db-podman
logs-db-podman:
	podman-compose logs -f db

# Execute bash in backend container (Podman)
.PHONY: shell-backend-podman
shell-backend-podman:
	podman-compose exec backend /bin/bash

# Execute bash in frontend container (Podman)
.PHONY: shell-frontend-podman
shell-frontend-podman:
	podman-compose exec frontend /bin/sh

# Connect to PostgreSQL database (Podman)
.PHONY: db-shell-podman
db-shell-podman:
	podman-compose exec db psql -U library_user -d library_system

# Run backend tests (Podman)
.PHONY: test-backend-podman
test-backend-podman:
	podman-compose exec backend pytest

# Show status of all containers (Podman)
.PHONY: status-podman
status-podman:
	podman-compose ps

# ===== HELP COMMANDS =====

# Show Docker commands
.PHONY: help
help:
	@echo "🐳 Library Management System - Docker Commands"
	@echo "=============================================="
	@echo "Development:"
	@echo "  make up              - Start all services in background"
	@echo "  make up-logs         - Start all services with logs"
	@echo "  make down            - Stop all services"
	@echo "  make down-volumes    - Stop services and remove data"
	@echo "  make rebuild         - Rebuild and restart services"
	@echo ""
	@echo "Monitoring:"
	@echo "  make logs            - View all logs"
	@echo "  make logs-backend    - View backend logs only"
	@echo "  make logs-frontend   - View frontend logs only"
	@echo "  make logs-db         - View database logs only"
	@echo "  make status          - Show container status"
	@echo ""
	@echo "Development:"
	@echo "  make shell-backend   - Open bash in backend container"
	@echo "  make shell-frontend  - Open shell in frontend container"
	@echo "  make db-shell        - Connect to PostgreSQL database"
	@echo "  make test-backend    - Run backend tests"
	@echo ""
	@echo "🐳 For Podman commands, use: make help-podman"

# Show Podman commands
.PHONY: help-podman
help-podman:
	@echo "🐳 Library Management System - Podman Commands"
	@echo "=============================================="
	@echo "Development:"
	@echo "  make up-podman           - Start all services in background"
	@echo "  make up-logs-podman      - Start all services with logs"
	@echo "  make down-podman         - Stop all services"
	@echo "  make down-podman-volumes - Stop services and remove data"
	@echo "  make rebuild-podman      - Rebuild and restart services"
	@echo ""
	@echo "Monitoring:"
	@echo "  make logs-podman            - View all logs"
	@echo "  make logs-backend-podman    - View backend logs only"
	@echo "  make logs-frontend-podman   - View frontend logs only"
	@echo "  make logs-db-podman         - View database logs only"
	@echo "  make status-podman          - Show container status"
	@echo ""
	@echo "Development:"
	@echo "  make shell-backend-podman   - Open bash in backend container"
	@echo "  make shell-frontend-podman  - Open shell in frontend container"
	@echo "  make db-shell-podman        - Connect to PostgreSQL database"
	@echo "  make test-backend-podman    - Run backend tests"
	@echo ""
	@echo "🚀 Quick start: ./setup-dev-podman.sh"
