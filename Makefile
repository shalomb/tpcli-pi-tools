.PHONY: help install install-dev venv clean test lint type-check format run

# Variables
PYTHON := python3
UV := uv
VENV_DIR := .venv
PYTHON_VERSION := 3.11

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

## help: Show this help message
help:
	@echo "$(BLUE)tpcli-pi-tools - PI Planning Tools for TargetProcess$(NC)"
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@sed -n 's/^## //p' ${MAKEFILE_LIST} | column -t -s ':' | sed -e 's/^/  /'
	@echo ""
	@echo "$(GREEN)Examples:$(NC)"
	@echo "  make install              # Install tools for use"
	@echo "  make install-dev          # Install with dev tools (testing, linting)"
	@echo "  make test                 # Run all tests"
	@echo "  make lint                 # Check code quality"
	@echo ""

## venv: Create Python virtual environment
venv:
	@echo "$(BLUE)Creating virtual environment...$(NC)"
	@if [ -d "$(VENV_DIR)" ]; then \
		echo "$(YELLOW)Virtual environment already exists, skipping...$(NC)"; \
	else \
		$(UV) venv $(VENV_DIR) --python $(PYTHON_VERSION); \
		echo "$(GREEN)✓ Virtual environment created$(NC)"; \
		echo ""; \
		echo "Activate with: source $(VENV_DIR)/bin/activate"; \
	fi

## install: Install tpcli-pi-tools (basic)
install: venv
	@echo "$(BLUE)Installing tpcli-pi-tools...$(NC)"
	@. $(VENV_DIR)/bin/activate && $(UV) pip install -e .
	@echo "$(GREEN)✓ Installation complete$(NC)"
	@echo ""
	@echo "Available commands:"
	@echo "  art-dashboard         - ART-wide PI planning overview"
	@echo "  team-deep-dive        - Team capacity and risk analysis"
	@echo "  objective-deep-dive   - Objective details and assessment"
	@echo "  release-status        - PI progress tracking"
	@echo ""
	@echo "Try: art-dashboard --help"

## install-dev: Install with development tools (test, lint, type-check)
install-dev: venv
	@echo "$(BLUE)Installing tpcli-pi-tools with dev tools...$(NC)"
	@. $(VENV_DIR)/bin/activate && $(UV) pip install -e ".[dev]"
	@echo "$(GREEN)✓ Development installation complete$(NC)"
	@echo ""
	@echo "Available dev commands:"
	@echo "  make test             - Run pytest tests"
	@echo "  make lint             - Run ruff linter"
	@echo "  make type-check       - Run mypy type checker"
	@echo "  make format           - Format code with ruff"
	@echo ""

## test: Run pytest tests (requires install-dev)
test:
	@echo "$(BLUE)Running tests...$(NC)"
	@. $(VENV_DIR)/bin/activate && pytest -v tests/
	@echo "$(GREEN)✓ Tests complete$(NC)"

## test-cov: Run tests with coverage report
test-cov:
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	@. $(VENV_DIR)/bin/activate && pytest -v --cov=tpcli_pi --cov-report=html tests/
	@echo "$(GREEN)✓ Coverage report: htmlcov/index.html$(NC)"

## lint: Check code quality with ruff
lint:
	@echo "$(BLUE)Checking code quality...$(NC)"
	@. $(VENV_DIR)/bin/activate && ruff check tpcli_pi/ tests/
	@echo "$(GREEN)✓ Code quality check passed$(NC)"

## type-check: Run mypy type checker (strict mode)
type-check:
	@echo "$(BLUE)Type checking (mypy strict)...$(NC)"
	@. $(VENV_DIR)/bin/activate && mypy tpcli_pi/
	@echo "$(GREEN)✓ Type checking passed$(NC)"

## format: Format code with ruff
format:
	@echo "$(BLUE)Formatting code...$(NC)"
	@. $(VENV_DIR)/bin/activate && ruff format tpcli_pi/ tests/
	@echo "$(GREEN)✓ Code formatted$(NC)"

## bdd: Run BDD tests (behave/pytest-bdd)
bdd:
	@echo "$(BLUE)Running BDD tests...$(NC)"
	@. $(VENV_DIR)/bin/activate && behave scripts/specs/
	@echo "$(GREEN)✓ BDD tests complete$(NC)"

## check: Run all checks (lint + type-check)
check: lint type-check
	@echo "$(GREEN)✓ All checks passed$(NC)"

## clean: Remove virtual environment and build artifacts
clean:
	@echo "$(BLUE)Cleaning up...$(NC)"
	@rm -rf $(VENV_DIR)
	@rm -rf build/ dist/ *.egg-info .eggs/
	@rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/
	@rm -rf htmlcov/ .coverage
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

## run: Run a command in the virtual environment (usage: make run CMD="art-dashboard --help")
run:
	@if [ -z "$(CMD)" ]; then \
		echo "Usage: make run CMD=\"<command>\""; \
		echo "Example: make run CMD=\"art-dashboard --art 'Example ART'\""; \
	else \
		. $(VENV_DIR)/bin/activate && $(CMD); \
	fi

## docs: Generate documentation (if applicable)
docs:
	@echo "$(BLUE)Documentation is in docs/ directory$(NC)"
	@echo "Start with: $(GREEN)docs/QUICKSTART.md$(NC)"

## all: Install dev tools and run all checks
all: install-dev check test
	@echo "$(GREEN)✓ All done! Everything looks good$(NC)"

.PHONY: venv install install-dev test test-cov lint type-check format bdd check clean run docs all help
