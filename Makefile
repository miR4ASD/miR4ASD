# Makefile for miR4ASD Project
# Tools: python3, uv, ruff, pytest

PYTHON = python3
UV = uv
PORT = 8000

.PHONY: all data serve test lint format clean help

all: data

# Run data processing ETL pipeline
data:
	@echo "--- Processing Excel data and generating JSON feeds ---"
	$(PYTHON) process_data.py
	@echo "--- Data generation complete ---"

# Start local HTTP preview server
serve:
	@echo "--- Starting local web server at http://localhost:$(PORT) ---"
	$(PYTHON) -m http.server $(PORT)

# Run test suite
test:
	@echo "--- Running test suite with pytest ---"
	$(UV) run pytest

# Lint code with ruff
lint:
	@echo "--- Checking code with ruff ---"
	$(UV) run ruff check .

# Format code with ruff
format:
	@echo "--- Formatting code with ruff ---"
	$(UV) run ruff format .

# Clean generated feeds and cache directories
clean:
	@echo "--- Cleaning build and test artifacts ---"
	rm -rf .pytest_cache .ruff_cache __pycache__ tests/__pycache__
	@echo "--- Clean complete ---"

help:
	@echo "miR4ASD Makefile Commands:"
	@echo "  make data    - Run process_data.py to generate JSON feeds"
	@echo "  make serve   - Start local preview web server at http://localhost:8000"
	@echo "  make test    - Run automated test suite using pytest"
	@echo "  make lint    - Run ruff linter checks"
	@echo "  make format  - Format code using ruff"
	@echo "  make clean   - Remove cache directories"
