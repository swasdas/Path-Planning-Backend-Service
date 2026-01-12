.PHONY: help build up down logs test clean seed restart

help:
	@echo "Available commands:"
	@echo "  make build    - Build all Docker images"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make logs     - View logs"
	@echo "  make test     - Run tests"
	@echo "  make seed     - Seed database with sample data"
	@echo "  make clean    - Remove all containers and volumes"
	@echo "  make restart  - Restart all services"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services starting..."
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "Frontend: http://localhost:3000"

down:
	docker-compose down

logs:
	docker-compose logs -f

test:
	docker-compose exec backend pytest -v

seed:
	docker-compose exec backend python -m scripts.seed_data

clean:
	docker-compose down -v --remove-orphans
	docker system prune -f

restart: down up
