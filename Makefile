.PHONY: help install test run docker-build docker-up docker-down migrate clean

help:
	@echo "Payment Service - Available Commands"
	@echo "===================================="
	@echo "install      - Install dependencies"
	@echo "test         - Run tests"
	@echo "test-cov     - Run tests with coverage"
	@echo "run          - Run development server"
	@echo "docker-build - Build Docker image"
	@echo "docker-up    - Start Docker containers"
	@echo "docker-down  - Stop Docker containers"
	@echo "migrate      - Run database migrations"
	@echo "migration    - Create new migration"
	@echo "clean        - Clean cache and build files"

install:
	pip install -r requirements.txt

install-test:
	pip install -r requirements-test.txt

test:
	pytest

test-cov:
	pytest --cov=app --cov-report=html --cov-report=term

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

docker-build:
	docker build -t payment-service:latest .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f payment-service

migrate:
	alembic upgrade head

migration:
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +

format:
	black app/ tests/
	isort app/ tests/

lint:
	flake8 app/ tests/
	mypy app/

db-create:
	createdb eygar_property_listing

db-drop:
	dropdb eygar_property_listing

db-reset: db-drop db-create migrate
