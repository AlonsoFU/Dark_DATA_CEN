.PHONY: help install install-dev test lint format clean build deploy docs learn-structure analyze-patterns

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies
	pip install -r requirements/base.txt

install-dev:  ## Install development dependencies
	pip install -r requirements/dev.txt
	pre-commit install

test:  ## Run tests
	pytest tests/ -v --cov=dark_data --cov-report=html

test-quick:  ## Run quick tests (unit only)
	pytest tests/unit/ -v

lint:  ## Run linting
	flake8 dark_data tests
	mypy dark_data
	black --check dark_data tests
	isort --check-only dark_data tests

format:  ## Format code
	black dark_data tests
	isort dark_data tests

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:  ## Build package
	python -m build

docs:  ## Generate documentation
	sphinx-build -b html docs/api docs/_build/html

setup-db:  ## Setup database
	python -c "import sqlite3; conn = sqlite3.connect('data/databases/dark_data.db'); conn.executescript(open('config/schemas/database_schema.sql').read()); conn.close(); print('✅ Database created!')"

ingest-data:  ## Ingest data into database
	python scripts/ingest_data.py

run-web:  ## Run web dashboard
	python -m dark_data.web.dashboard

run-mcp:  ## Run MCP server
	python -m dark_data.mcp.servers.mcp_server

run-cli:  ## Run CLI interface
	python -m dark_data.cli.simple_viewer

learn-structure:  ## Learn document structure from data/raw/*.json
	python scripts/learn_document_structure.py --documents "data/raw/*.json" --phase auto

analyze-patterns:  ## Analyze patterns in documents without learning
	python scripts/learn_document_structure.py --analyze "data/raw/*.json"

learn-discovery:  ## Start with discovery phase (3-5 documents)
	python scripts/learn_document_structure.py --documents "data/raw/*.json" --phase discovery --batch-size 3

learn-validation:  ## Continue with validation phase  
	python scripts/learn_document_structure.py --documents "data/raw/*.json" --phase validation --batch-size 5

test-structure:  ## Test learned structure on new documents
	python scripts/learn_document_structure.py --test "data/test/*.json"