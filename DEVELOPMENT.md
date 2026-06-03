# Development

Setup, tests, and linting for working in this repo. User-facing CLI
usage and configuration live in [README.md](README.md). For agent-facing
internals (type system, collation/merge flows) see [AGENTS.md](AGENTS.md).

## Setup

Use a virtualenv:

```bash
virtualenv venv
source venv/bin/activate
pip install -e ".[test]"
```

## Tests

Full suite (bandit + pylint + pytest with 100% coverage gate) across
py311–py314:

```bash
tox
```

Single Python version:

```bash
tox -e py312
```

Tests only:

```bash
pytest tests/
```

Coverage report:

```bash
pytest --cov=enheduanna --cov-report=html --cov-fail-under=100 tests/
# open htmlcov/index.html
```

One file or test:

```bash
pytest tests/test_cli.py
pytest tests/test_cli.py::test_function_name
```

## Linting and security

```bash
pylint enheduanna/
bandit -r enheduanna/
```

Both run inside `tox` and must pass for a release build. Pylint config
is `.pylintrc` — several checks (line-too-long, too-many-*, etc.) are
intentionally disabled there.

## Docker build

```bash
docker build -t enheduanna .
```

Used by CI to publish images via the shared
`tnoff-projects/github-workflows` `buildkit-docker-push.yml` template.

## Releasing

`VERSION` at the repo root is the single source of truth. Bump it and
push to `main` — CI tags the commit and runs the release pipeline.
