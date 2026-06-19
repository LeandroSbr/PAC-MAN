.PHONY: run build clean-build install env debug clean lint lint-strict

UV = uv run

RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[38;2;253;253;100m
RESET := \033[0m

PYTHON	= .venv/bin/python3
FLAKE8	= .venv/bin/flake8
MYPY	= .venv/bin/mypy
DOCSTYLE = .venv/bin/pydocstyle
PYINSTALLER = .venv/bin/pyinstaller
INPUT = config/config.json
PACKAGE_NAME = pacman-release
BUILD_DIR = build

all: install run clean

run: install
	$(UV) $(PYTHON) -m src $(INPUT)

build: install
	rm -rf $(BUILD_DIR)
	mkdir -p $(BUILD_DIR)

	# Genera l'eseguibile
	$(PYINSTALLER) --onefile --name pacman src/__main__.py

	# Copia tutto ciò che serve
	cp dist/pacman dist/Pac-Man
	cp  dist/Pac-Man $(BUILD_DIR)/
	cp -r config $(BUILD_DIR)/
	cp -r resources $(BUILD_DIR)/
	cp README.md $(BUILD_DIR)/

	# Crea lo zip finale
	cd $(BUILD_DIR) && zip -r ../$(PACKAGE_NAME).zip .
	rm -f pacman.spec
	rm -rf dist

install: env
	@echo "$(YELLOW)→ Installing dependencies...$(RESET)"
	uv sync
	@echo "$(GREEN)✓ Dependencies installed.$(RESET)"

env:
	@echo "$(YELLOW)→ Setup of the venv...$(RESET)"
	test -d .venv || python3 -m venv .venv
	@echo "$(GREEN)✓ Venv created.$(RESET)"

debug: install
	$(UV) $(PYTHON) -m pdb -m src $(INPUT)

clean:
	@find . -type d -name "__pycache__" -not -path "./.venv/*" | xargs rm -rf
	@find . -type d -name ".mypy_cache" -not -path "./.venv/*" | xargs rm -rf
	@find . -type d -name "*.egg-info"  -not -path "./.venv/*" | xargs rm -rf
	@find . -type d -name ".cache"  -not -path "./.venv/*" | xargs rm -rf

clean-build:
	rm -rf build dist *.spec __pycache__

lint: install
	@echo "$(YELLOW)→ Running flake8...$(RESET)"
	$(UV) $(FLAKE8) src/
	@echo "$(YELLOW)→ Running mypy...$(RESET)"
	$(UV) $(MYPY) src/ --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
	@echo "$(GREEN)✓ Lint passed.$(RESET)"

lint-strict: install
	@echo "$(YELLOW)→ Running flake8...$(RESET)"
	$(UV) $(FLAKE8) src/
	@echo "$(YELLOW)→ Running mypy --strict...$(RESET)"
	$(UV) $(MYPY) src/ --strict
	@echo "$(YELLOW)→ Running pydocstyle --strict...$(RESET)"
	$(UV) $(DOCSTYLE) src/
	@echo "$(GREEN)✓ Strict lint passed.$(RESET)"