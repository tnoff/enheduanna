# AGENTS.md

This file provides guidance to AI coding agents when working with code in this repository.

## Project Overview

Enheduanna is a CLI tool for creating and managing entries in Markdown. It organizes entries into weekly/monthly sub-directories and provides "collate" functionality to combine multiple entries into summaries and documentation files.

Named after Enheduanna, sometimes considered the first known author in history.

## Development Commands

### Running Tests
```bash
# Run tests with coverage (requires 95% coverage)
pytest --cov=enheduanna --cov-fail-under=95 tests/

# Run tests for a specific file
pytest tests/test_cli.py

# Run tests for a specific test function
pytest tests/test_cli.py::test_function_name

# Run with tox (tests against multiple Python versions)
tox

# Run with specific Python version
tox -e py311
tox -e py312
tox -e py313
```

### Linting
```bash
# Run pylint
pylint enheduanna/
```

### Installation
```bash
# Install in development mode
pip install -e .

# Install with requirements
pip install -r requirements.txt
```

## Architecture

### Core Type System

The codebase uses Pydantic dataclasses for type safety and validation:

- **MarkdownFile** (`enheduanna/types/markdown/markdown_file.py`): Represents a markdown file with a path and root section. Provides parsing functionality to convert raw markdown text into a tree of MarkdownSection objects.

- **MarkdownSection** (`enheduanna/types/markdown/markdown_section.py`): Represents a section in a markdown file with title, contents, level (heading depth), and optional subsections. Forms a tree structure for nested sections.

- **CollateSection** (`enheduanna/types/markdown/collate_section.py`): Extends MarkdownSection with regex pattern matching and groupBy capabilities for combining similar content during collation (e.g., grouping by Jira ticket numbers).

- **Config** (`enheduanna/types/config/`): Configuration loaded from YAML files using pyaml-env. Includes FileConfig for file paths and sections, and CollationType for weekly vs monthly collation.

### Key Utilities

- **Collation** (`enheduanna/utils/collation/`): Creates parent folders for notes based on weekly or monthly grouping. Uses `days.py` utilities to calculate week/month start and end dates.

- **File Utils** (`enheduanna/utils/files.py`): Functions for listing markdown files, finding the most recent file, and normalizing file names.

- **Markdown Utils** (`enheduanna/utils/markdown.py`): Core collation and merge logic. `generate_markdown_collation()` combines specific sections with regex grouping and document extraction. `generate_markdown_merge()` provides simpler merging of all sections without filtering.

### CLI Flow

The CLI (`enheduanna/cli.py`) has three main commands:

1. **new-entry**: Creates today's entry
   - Finds last markdown file for carryover sections
   - Creates parent folder (week or month based on config)
   - Generates new file with entry sections
   - If carryover sections exist, removes them from old file and adds to new file

2. **collate**: Combines entries into summaries
   - Reads all markdown files in a directory
   - Combines configured collate sections (e.g., "Work Done")
   - Groups content by regex patterns (e.g., Jira tickets)
   - Extracts non-standard sections as separate documentation files
   - Removes empty sections from source files after collation

3. **merge**: Merges markdown files into a single file
   - Primarily used to combine documentation files extracted by collate
   - Reads all markdown files in a directory (not just entries)
   - Combines ALL sections from all files (ignores collate configuration)
   - Merges sections with the same name by simply combining content
   - Does not apply regex grouping or extract documentation files
   - Common workflow: collate extracts docs → merge combines related docs into runbooks

### Configuration System

Config loading happens in `enheduanna/types/config/__init__.py` with defaults in `enheduanna/defaults.py`:

- Default note directory: `~/Notes`
- Default document directory: `~/Documents`
- Default date format: `%Y-%m-%d`
- Config file location: `~/.enheduanna.yml` (overridable with `-c` flag)
- Supports environment variable interpolation via pyaml-env

The config system uses Pydantic validators to apply defaults when sections aren't specified in the YAML config.

### Test Structure

Tests mirror the source structure under `tests/`:
- `tests/types/` - Tests for type classes
- `tests/utils/` - Tests for utility functions
- `tests/test_cli.py` - CLI integration tests
- `tests/data/` - Test fixtures and sample data

Tests use pytest with freezegun for date mocking and pytest-cov for coverage reporting.

## Code Style

- Pylint is configured with many checks disabled (see `.pylintrc`)
- Disabled checks include: line-too-long, too-many-arguments, too-many-branches, invalid-name, etc.
- Coverage threshold: 95%
