# PR 2: Tooling

Branch: `chore/tooling`

Files added: `pyproject.toml`, `.github/workflows/ci.yaml`.

## Why `pyproject.toml` at all

`pyproject.toml` is the standard, PEP 621, way to describe a Python project:
its name, its dependencies, and how the tools that work with it (the test
runner, the linter, the build backend) should behave. It replaces the older
pattern of a `setup.py` script plus a handful of scattered config files
(`setup.cfg`, `pytest.ini`, `.flake8`). One file, one format, every tool
reads the section it cares about.

## The `src` layout, and why this project's version is unusual

A common Python project layout puts importable code under `src/` to force
tests to import the installed package rather than accidentally picking up
files from the current directory. In the typical version of this layout,
`src/` itself is not a package, the packages live directly inside it
(`src/domain/`, `src/application/`), and code imports them as
`from domain.models import ...`.

This project already has `src/__init__.py`, which makes `src` itself a
regular Python package, and the existing test files already import as
`from src.domain.models import ...`, with the `src.` prefix. That decision
was made before this PR, this PR just needs to make packaging match it, not
change it. Hence:

```toml
[tool.setuptools.packages.find]
where = ["."]
include = ["src*"]
```

`where = ["."]` tells setuptools to look for packages starting at the repo
root, not inside `src/`. `include = ["src*"]` tells it to only pick up
`src` and everything under it (`src.domain`, `src.application`, and so on),
so it does not accidentally try to package `tests/` or `docs/` as
importable code.

## Dev dependencies as an optional group

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "ruff>=0.6",
]
```

`dependencies = []` at the top level means the pipeline itself, once it has
real code, needs nothing beyond the standard library so far. `pytest` and
`ruff` are not something the pipeline needs to run in production, they are
tools needed to develop it, so they live in a separate `dev` extra. Installing
with `pip install -e ".[dev]"` (as the CI workflow does) pulls in both the
project and the dev tools in one step, installing with just
`pip install -e .` would skip them.

## Pytest configuration

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

`testpaths = ["tests"]` tells pytest where to look for tests without needing
to type `pytest tests/` every time. `pythonpath = ["."]` adds the repo root
to Python's import path explicitly.

That second line is technically redundant today: every folder from the repo
root down to each test file already has an `__init__.py`
(`tests/__init__.py`, `tests/domain/__init__.py`, and so on), and pytest's
default import mode already walks up that chain of `__init__.py` files and
adds the first directory without one (the repo root) to `sys.path`. The
explicit `pythonpath` entry is there so imports keep working even if that
chain of `__init__.py` files changes later, or if pytest is invoked in a way
that skips its usual rootdir detection (for example, from a different
working directory in some CI setups). Explicit here costs one line and
removes a way for imports to silently start failing.

## Ruff configuration

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I"]
```

Ruff is a linter (and formatter, not used as one yet here) that replaces
what used to be several separate tools. The `select` line chooses which
rule categories run: `E` is pycodestyle errors (basic style issues like
inconsistent whitespace), `F` is Pyflakes (actual bugs: unused imports,
undefined names), `I` is import sorting and grouping. This is a deliberately
small starting set, wide enough to catch real mistakes, narrow enough not to
generate noise while the project is still small.

## The CI workflow

```yaml
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  lint:
    ...
  test:
    needs: lint
    ...
```

Two triggers: every pull request targeting `main`, and every push to `main`
(covering the merge commit itself). Two jobs: `lint` runs `ruff check .`,
`test` runs `pytest`. `test` declares `needs: lint`, which makes it wait for
`lint` to succeed before starting. The reasoning: if the code does not even
pass basic lint checks, there is little point spending CI minutes running
the full test suite, fail fast on the cheaper check first.

Both jobs install the project the same way: `pip install -e ".[dev]"`. The
`-e` (editable) flag means the package is linked in place rather than
copied, which is standard practice in CI since nothing here needs a real
distributable build, just the ability to `import src...` from anywhere in
the checked-out repository.

## A note on local verification

`pytest` and `ruff` could not be installed in the assistant's sandbox to run
these checks locally (no outbound network access there), so this PR was
verified by manually re-running the equivalent logic with plain `python3`.
GitHub Actions runners do have normal network access, so the actual `lint`
and `test` jobs run for real once this PR (and any PR after it) is opened.
