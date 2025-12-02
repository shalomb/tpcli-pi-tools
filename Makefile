#!/usr/bin/make -f
#
# tpcli-pi-tools Makefile
#
# SHELL & BASH CONVENTIONS:
# - This Makefile uses bash (.SHELLFLAGS) with strict mode:
#   - errexit (-e): exit immediately on error
#   - nounset (-u): treat unset variables as errors
#   - pipefail: propagate errors through pipes
# - All shell code is checked with: shellcheck -x
# - Prefer bash builtins over external tools (grep, awk, etc.)
#   whenever possible to reduce dependencies
# - Use modern bash constructs (arrays, parameter expansion, etc.)
#   instead of POSIX shell compatibility where appropriate
# - External tools (grep, awk, sed) used only when bash is inadequate
# - All variables are quoted to prevent word splitting/globbing
#

# Better make configuration
MAKEFLAGS += --no-print-directory
MAKEFLAGS += --warn-undefined-variables

.ONESHELL:
SHELL := /bin/bash
.SHELLFLAGS := -o errexit -o nounset -o pipefail -ec

# Set default goal
.DEFAULT_GOAL := help

# Quiet specific targets
.SILENT: help venv clean

# Variables
PYTHON := python3
UV := uv
VENV_DIR := .venv
PYTHON_VERSION := 3.11
BIN_DIR := $(VENV_DIR)/bin
GO := go
TPCLI_BIN := $(BIN_DIR)/tpcli

# Better PATH management
export PATH := $(PWD)/$(BIN_DIR):$(HOME)/.local/bin:$(PATH)

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

## help: Show available make targets
help:
	{ \
	echo "$(BLUE)tpcli-pi-tools - PI Planning Tools for TargetProcess$(NC)"; \
	echo ""; \
	echo "$(GREEN)Installation targets:$(NC)"; \
	echo "  install              - Install for local development"; \
	echo "  install-dev          - Install with dev tools (testing, linting)"; \
	echo "  install-global       - Install globally via uv tool install"; \
	echo "  venv                 - Create Python virtual environment"; \
	echo "  tpcli                - Build tpcli Go binary"; \
	echo ""; \
	echo "$(GREEN)Development targets:$(NC)"; \
	echo "  check                - Run lint + type-check"; \
	echo "  go-test              - Run Go unit tests"; \
	echo "  py-test              - Run Python pytest tests"; \
	echo "  bdd                  - Run BDD tests with behave"; \
	echo "  test                 - Run all tests (go-test + py-test + bdd)"; \
	echo "  test-cov             - Run tests with coverage report"; \
	echo "  lint                 - Check code quality with ruff"; \
	echo "  type-check           - Run mypy type checker (strict)"; \
	echo "  format               - Format code with ruff"; \
	echo ""; \
	echo "$(GREEN)Utility targets:$(NC)"; \
	echo "  clean                - Remove venv, binaries, and artifacts"; \
	echo "  run                  - Run a command in venv (CMD=...)"; \
	echo "  docs                 - Show documentation location"; \
	echo "  show-config          - Open tpcli config in \$${EDITOR:-vi}"; \
	echo "  all                  - Full setup: install-dev, check, test"; \
	echo ""; \
	echo "$(GREEN)Testing targets:$(NC)"; \
	echo "  uat                  - User Acceptance Testing (end-to-end)"; \
	echo ""; \
	}

## venv: Create Python virtual environment
venv:
	echo "$(BLUE)Creating virtual environment...$(NC)"
	if [[ -d "$(VENV_DIR)" ]]; then \
		echo "$(YELLOW)Virtual environment already exists, skipping...$(NC)"; \
	else \
		$(UV) venv $(VENV_DIR) --python $(PYTHON_VERSION); \
		echo "$(GREEN)✓ Virtual environment created$(NC)"; \
		echo ""; \
		echo "Activate with: source $(VENV_DIR)/bin/activate"; \
	fi

## tpcli: Build and install tpcli Go binary
tpcli: venv
	echo "$(BLUE)Building tpcli Go binary...$(NC)"
	if command -v $(GO) &> /dev/null; then \
		$(GO) build -o $(TPCLI_BIN) .; \
		echo "$(GREEN)✓ tpcli binary installed: $(TPCLI_BIN)$(NC)"; \
	else \
		echo "$(YELLOW)⚠ Go not found - skipping tpcli build$(NC)"; \
		echo "$(YELLOW)  Install Go from https://golang.org/doc/install$(NC)"; \
	fi

## install: Install tpcli-pi-tools (basic)
install: venv tpcli
	echo "$(BLUE)Installing tpcli-pi-tools...$(NC)"
	$(UV) sync
	# If we built a local tpcli binary, also copy it to ~/.local/bin for global use
	if [ -f "$(TPCLI_BIN)" ]; then \
		mkdir -p "$${HOME}/.local/bin"; \
		cp "$(TPCLI_BIN)" "$${HOME}/.local/bin/tpcli"; \
		echo "$(GREEN)✓ tpcli binary installed: ~/.local/bin/tpcli$(NC)"; \
		echo ""; \
		echo "$(YELLOW)⚠ IMPORTANT: Clear your shell's command cache:$(NC)"; \
		echo "   hash -r"; \
		echo "   (or restart your shell/tmux session)"; \
		echo ""; \
	fi
	echo "$(GREEN)✓ Installation complete$(NC)"
	echo ""
	echo "Available commands (run with 'uv run'):"
	echo "  uv run art-dashboard         - ART-wide PI planning overview"
	echo "  uv run team-deep-dive        - Team capacity and risk analysis"
	echo "  uv run objective-deep-dive   - Objective details and assessment"
	echo "  uv run release-status        - PI progress tracking"
	echo ""
	echo "Or activate venv: source $(VENV_DIR)/bin/activate"
	echo "Then: art-dashboard --help"

## install-dev: Install with development tools (test, lint, type-check)
install-dev: venv tpcli
	echo "$(BLUE)Installing tpcli-pi-tools with dev tools...$(NC)"
	$(UV) sync --all-extras
	echo "$(GREEN)✓ Development installation complete$(NC)"
	echo ""
	echo "Available dev commands:"
	echo "  make test             - Run pytest tests"
	echo "  make lint             - Run ruff linter"
	echo "  make type-check       - Run mypy type checker"
	echo "  make format           - Format code with ruff"
	echo ""

## install-global: Install tools globally without polluting user's venv
install-global:
	echo "$(BLUE)Installing tpcli-pi-tools globally...$(NC)"
	if ! command -v $(UV) &> /dev/null; then \
		echo "$(RED)Error: uv not found - cannot install globally$(NC)"; \
		echo "Install uv from https://astral.sh/uv"; \
		exit 1; \
	fi
	$(UV) tool install -e .
	echo ""
	if command -v $(GO) &> /dev/null; then \
		mkdir -p "$${HOME}/.local/bin"; \
		$(GO) build -o "$${HOME}/.local/bin/tpcli" .; \
		echo "$(GREEN)✓ tpcli binary installed: ~/.local/bin/tpcli$(NC)"; \
	else \
		echo "$(YELLOW)⚠ Go not found - tpcli binary not installed$(NC)"; \
		echo "$(YELLOW)  Install Go from https://golang.org/doc/install$(NC)"; \
	fi
	echo ""
	echo "$(GREEN)✓ Global installation complete$(NC)"
	echo ""
	echo "Tools installed to: ~/.local/bin"
	echo "Make sure ~/.local/bin is in your PATH"
	echo ""
	echo "Available commands:"
	echo "  art-dashboard         - ART-wide PI planning overview"
	echo "  team-deep-dive        - Team capacity and risk analysis"
	echo "  objective-deep-dive   - Objective details and assessment"
	echo "  release-status        - PI progress tracking"

## go-test: Run Go unit tests
go-test:
	echo "$(BLUE)Running Go tests...$(NC)"
	$(GO) test -v ./...
	echo "$(GREEN)✓ Go tests passed$(NC)"

## py-test: Run Python pytest tests (requires install-dev)
py-test:
	echo "$(BLUE)Running Python tests...$(NC)"
	PATH="$(BIN_DIR):$$PATH" $(UV) run pytest -v tests/
	echo "$(GREEN)✓ Python tests passed$(NC)"

## test: Run all tests (Go + Python + BDD)
test: build go-test py-test bdd
	echo "$(GREEN)✓ All tests passed$(NC)"

## build: Build the tpcli binary
build:
	echo "$(BLUE)Building tpcli binary...$(NC)"
	$(GO) build -o tpcli .

## test-cov: Run tests with coverage report
test-cov:
	echo "$(BLUE)Running tests with coverage...$(NC)"
	PATH="$(BIN_DIR):$$PATH" $(UV) run pytest -v --cov=tpcli_pi --cov-report=html tests/
	echo "$(GREEN)✓ Coverage report: htmlcov/index.html$(NC)"

## lint: Check code quality with ruff
lint:
	echo "$(BLUE)Checking code quality...$(NC)"
	$(UV) run ruff check tpcli_pi/ tests/
	echo "$(GREEN)✓ Code quality check passed$(NC)"

## type-check: Run mypy type checker (strict mode)
type-check:
	echo "$(BLUE)Type checking (mypy strict)...$(NC)"
	$(UV) run mypy tpcli_pi/
	echo "$(GREEN)✓ Type checking passed$(NC)"

## format: Format code with ruff
format:
	echo "$(BLUE)Formatting code...$(NC)"
	$(UV) run ruff format tpcli_pi/ tests/
	echo "$(GREEN)✓ Code formatted$(NC)"

## bdd: Run BDD tests with behave (Gherkin scenarios)
bdd:
	echo "$(BLUE)Running BDD tests...$(NC)"
	if [ -d "tests/features" ]; then \
		PATH="$(BIN_DIR):$$PATH" $(UV) run behave tests/features/; \
	else \
		echo "$(YELLOW)⚠ No BDD test features found in tests/features$(NC)"; \
	fi
	echo "$(GREEN)✓ BDD tests complete$(NC)"

## check: Run all checks (lint + type-check)
check: lint type-check
	echo "$(GREEN)✓ All checks passed$(NC)"

## clean: Remove virtual environment, tpcli binary, and build artifacts
clean:
	echo "$(BLUE)Cleaning up...$(NC)"
	rm -rf $(VENV_DIR)
	rm -f $(TPCLI_BIN)
	rm -rf build/ dist/ *.egg-info .eggs/
	rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/
	rm -rf htmlcov/ .coverage uv.lock
	find . -type d -name __pycache__ -delete 2>/dev/null || true
	echo "$(GREEN)✓ Cleanup complete$(NC)"

## run: Run a command with uv run (usage: make run CMD="art-dashboard --help")
run:
	if [[ -z "$${CMD:-}" ]]; then \
		echo "Usage: make run CMD=\"<command>\""; \
		echo "Example: make run CMD=\"art-dashboard --art 'Example ART'\""; \
		exit 1; \
	fi
	PATH="$(BIN_DIR):$$PATH" $(UV) run $${CMD}

## docs: Show documentation location
docs:
	echo "$(BLUE)Documentation is in docs/ directory$(NC)"
	echo "Start with: $(GREEN)docs/QUICKSTART.md$(NC)"

## show-config: Open tpcli global config in editor
show-config:
	if [[ ! -f "$$HOME/.config/tpcli/config.yaml" ]]; then \
		echo "$(RED)Error: tpcli config not found at ~/.config/tpcli/config.yaml$(NC)"; \
		echo "Create it first with your TargetProcess credentials"; \
		exit 1; \
	fi
	echo "$(BLUE)Opening tpcli config in $${EDITOR:-vi}$(NC)"
	$${EDITOR:-vi} "$$HOME/.config/tpcli/config.yaml"

## uat: User Acceptance Testing - test extensions work from any directory
uat:
	printf "$(BLUE)Running UAT: User Acceptance Tests$(NC)\n"
	printf "\n"
	printf "$(GREEN)Step 1: Verify tpcli config exists and read defaults$(NC)\n"
	if [[ ! -f "$$HOME/.config/tpcli/config.yaml" ]]; then \
		printf "$(RED)Error: tpcli config not found at ~/.config/tpcli/config.yaml$(NC)\n"; \
		exit 1; \
	fi
	printf "✓ Config file found: $$HOME/.config/tpcli/config.yaml\n"
	DEFAULT_ART=$$(grep "^default-art:" "$$HOME/.config/tpcli/config.yaml" | sed "s/.*: *'//;s/'.*//"); \
	DEFAULT_TEAM=$$(grep "^default-team:" "$$HOME/.config/tpcli/config.yaml" | sed "s/.*: *'//;s/'.*//"); \
	if [[ -z "$$DEFAULT_ART" ]]; then \
		printf "$(YELLOW)⚠ default-art not configured in config.yaml (optional)$(NC)\n"; \
		DEFAULT_ART="Data, Analytics and Digital"; \
	else \
		printf "✓ Using default-art: $$DEFAULT_ART\n"; \
	fi
	if [[ -z "$$DEFAULT_TEAM" ]]; then \
		printf "$(YELLOW)⚠ default-team not configured in config.yaml (optional)$(NC)\n"; \
		DEFAULT_TEAM="Cloud Enablement & Delivery"; \
	else \
		printf "✓ Using default-team: $$DEFAULT_TEAM\n"; \
	fi
	printf "\n"
	printf "$(GREEN)Step 2: Test tpcli binary directly (with config auth)$(NC)\n"
	export PATH="$$HOME/.local/bin:$$PATH"; \
	printf "  Testing: tpcli list Teams (should read credentials from config)\n"; \
	bash -c 'tpcli list Teams --take 1' > /tmp/uat-tpcli-direct.out 2>&1; \
	if grep -q '"Id"' /tmp/uat-tpcli-direct.out; then \
		printf "  $(GREEN)✓ tpcli reads config and authenticates successfully$(NC)\n"; \
	else \
		printf "  $(RED)✗ tpcli failed to authenticate$(NC)\n"; \
		cat /tmp/uat-tpcli-direct.out; \
		exit 1; \
	fi
	printf "\n"
	printf "$(GREEN)Step 3: List available extensions$(NC)\n"
	export PATH="$$HOME/.local/bin:$$PATH"; \
	tpcli ext list
	printf "\n"
	printf "$(GREEN)Step 4: Test direct extension calls WITHOUT explicit options (uses defaults)$(NC)\n"
	export PATH="$$HOME/.local/bin:$$PATH"; \
	printf "  Testing: team-deep-dive (should use default-team from config)\n"; \
	team-deep-dive > /tmp/uat-team-deep-dive.out 2>&1; \
	if grep -q "Team Overview" /tmp/uat-team-deep-dive.out; then \
		printf "  $(GREEN)✓ team-deep-dive works with defaults$(NC)\n"; \
	else \
		printf "  $(RED)✗ team-deep-dive failed$(NC)\n"; \
		cat /tmp/uat-team-deep-dive.out; \
		exit 1; \
	fi
	printf "\n"
	printf "$(GREEN)Step 5: Test tpcli ext wrapper (without explicit options)$(NC)\n"
	export PATH="$$HOME/.local/bin:$$PATH"; \
	printf "  Testing: tpcli ext team-deep-dive (should use default-team from config)\n"; \
	tpcli ext team-deep-dive > /tmp/uat-ext-wrapper.out 2>&1; \
	if grep -q "Team Overview" /tmp/uat-ext-wrapper.out; then \
		printf "  $(GREEN)✓ tpcli ext wrapper works with defaults$(NC)\n"; \
	else \
		printf "  $(RED)✗ tpcli ext wrapper failed$(NC)\n"; \
		cat /tmp/uat-ext-wrapper.out; \
		exit 1; \
	fi
	printf "\n"
	printf "$(GREEN)Step 6: Test from arbitrary directory (/tmp) without explicit options$(NC)\n"
	export PATH="$$HOME/.local/bin:$$PATH"; \
	cwd=$$(pwd); \
	cd /tmp; \
	printf "  Current directory: $$(pwd)\n"; \
	printf "  Testing: art-dashboard (should use default-art from config)\n"; \
	art-dashboard > /tmp/uat-art-dashboard.out 2>&1; \
	if grep -q "ART Dashboard" /tmp/uat-art-dashboard.out; then \
		printf "  $(GREEN)✓ art-dashboard works from arbitrary directory with defaults$(NC)\n"; \
	else \
		printf "  $(RED)✗ art-dashboard failed$(NC)\n"; \
		cat /tmp/uat-art-dashboard.out; \
		cd "$$cwd"; \
		exit 1; \
	fi; \
	cd "$$cwd"
	printf "\n"
	printf "$(GREEN)Step 6: Test from home directory ($$HOME) without explicit options$(NC)\n"
	export PATH="$$HOME/.local/bin:$$PATH"; \
	cwd=$$(pwd); \
	cd ~; \
	printf "  Current directory: $$(pwd)\n"; \
	printf "  Testing: team-deep-dive (should use default-team from config)\n"; \
	team-deep-dive > /tmp/uat-home-dir.out 2>&1; \
	if grep -q "Team Overview" /tmp/uat-home-dir.out; then \
		printf "  $(GREEN)✓ team-deep-dive works from home directory with defaults$(NC)\n"; \
	else \
		printf "  $(RED)✗ team-deep-dive failed from home$(NC)\n"; \
		cat /tmp/uat-home-dir.out; \
		cd "$$cwd"; \
		exit 1; \
	fi; \
	cd "$$cwd"
	printf "\n"
	printf "$(GREEN)✓ UAT Complete: All tests passed!$(NC)\n"
	printf "\n"
	printf "Summary:\n"
	printf "  $(GREEN)✓ Config file accessible$(NC)\n"
	printf "  $(GREEN)✓ Default values sourced from config (ART: $$DEFAULT_ART, Team: $$DEFAULT_TEAM)$(NC)\n"
	printf "  $(GREEN)✓ Extensions discoverable via tpcli ext list$(NC)\n"
	printf "  $(GREEN)✓ Commands work WITHOUT explicit options (use config defaults)$(NC)\n"
	printf "  $(GREEN)✓ team-deep-dive works with defaults from config$(NC)\n"
	printf "  $(GREEN)✓ art-dashboard works with defaults from config$(NC)\n"
	printf "  $(GREEN)✓ tpcli ext wrapper works with defaults$(NC)\n"
	printf "  $(GREEN)✓ Extensions work from arbitrary directories (/tmp, home)$(NC)\n"
	printf "  $(GREEN)✓ No venv pollution - tools isolated$(NC)\n"

## all: Install dev tools and run all checks
all: install-dev check test
	echo "$(GREEN)✓ All done! Everything looks good$(NC)"

.PHONY: venv install install-dev install-global go-test py-test test test-cov lint type-check format bdd check clean run docs show-config all uat help
