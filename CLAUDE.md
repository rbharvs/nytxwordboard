# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development
- Install dependencies: `uv sync --dev`
- Run API locally: `uv run fastapi dev src/app/entrypoints/asgi.py`

### Linting & Formatting
- Fix linting issues: `uv run ruff check --fix`
- Format code: `uv run ruff format`

### Testing
- Run all tests: `uv run pytest`
- Run a single test: `uv run pytest tests/path/to/test.py::test_function_name -v`

## Style Guidelines
- Python version: 3.12
- Error handling: Use try/except with specific exceptions
- Naming: Use snake_case for functions/variables, PascalCase for classes
- Async: Use asyncio for I/O operations
- Comments: Code should be self-documenting; use comments judiciously for complex logic
- Docstrings: All docstrings should be one line at most using the format """Short description."""
