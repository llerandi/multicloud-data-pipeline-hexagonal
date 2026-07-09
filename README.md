# Multicloud Data Pipeline Hexagonal

This is a learning project. It exists to practice hexagonal architecture (also called ports and adapters) applied to a data engineering problem, so the code favors clarity over brevity. Comments and docstrings are more detailed than you would normally write in a production codebase, on purpose, because the goal here is to explain the reasoning, not just the result. If you land on this repository from GitHub, that is why.

## Scope

The project implements a small pipeline that ingests a dataset (CSV or JSON), checks it against a set of data quality rules, computes quality metrics (null ratio, duplicates, out of range values) and, if the dataset passes, persists it and optionally runs a model inference step.

The problem it is meant to solve is not the pipeline itself, plenty of tools already do CSV validation. The point is a specific pain in data engineering: switching cloud provider (GCS to S3, BigQuery to Postgres, Cloud Monitoring to something else) without rewriting the business rules that decide whether a dataset is good enough to use. Hexagonal architecture is the tool used to keep that boundary explicit: the rules live in one place, the cloud-specific code lives in another, and the two only talk through interfaces.

Business rule implemented so far: a dataset is rejected if more than 5% of its rows contain a null value.

## Architecture

The code is split into three layers, each with a single direction of dependency: infrastructure depends on application, application depends on domain, domain depends on nothing.

```
src/
├── domain/            business entities, value objects and rules
├── application/        use cases and the ports they rely on
│   ├── ports/           interfaces the application needs from the outside world
│   ├── use_cases/       one module per use case
│   └── services/        orchestration across multiple use cases or steps
└── infrastructure/      concrete adapters implementing the ports
    ├── storage/          FileStorage: GCS, S3, local filesystem
    ├── repository/        DatasetRepository: BigQuery, Postgres
    ├── metrics/           MetricsPublisher: Cloud Monitoring, console
    ├── notifications/     NotificationPort: Slack/email, log stub
    └── inference/         ModelInferencePort: local scikit-learn, Vertex AI
```

**domain** holds `DataQualityReport` and the business rule that decides if a dataset is acceptable. It does not import anything from `application` or `infrastructure`, and it does not know that GCS or BigQuery exist. This is what makes the rule testable with plain unit tests and no mocks.

**application** defines what the pipeline needs from the outside world as ports (Python interfaces, in practice abstract base classes), and implements the use case that coordinates them: read the file, validate it, persist it, notify on failure, run inference if it passed. This layer knows the steps of the pipeline but not which cloud runs them.

**infrastructure** implements each port for a specific provider. A GCS adapter and an S3 adapter both implement `FileStorage`, so the application layer can use either one without changes. This is where the actual cloud SDK calls live.

## Current status

- [x] Domain layer: `DataQualityReport`, `QualityThresholds`, `DatasetRejectedError`, and the null-ratio rule, with unit tests.
- [x] Application layer: ports and the `ValidateAndIngestDataset` use case.
- [ ] Infrastructure adapters: storage, repository, metrics, notifications.
- [ ] `ModelInferencePort` with a scikit-learn adapter and a Vertex AI adapter.
- [x] Tooling: `pyproject.toml` and GitHub Actions CI (lint and tests on every pull request).

## Commands

All commands below assume a Python virtual environment is active. Without
one, `pytest` and `ruff` are installed into some Python installation on the
machine, not necessarily the one PowerShell resolves when you type their
name, which is why the terminal says it does not recognize them.

Create and activate a virtual environment, once, from the repository root
in PowerShell:

```
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell refuses to run that script (an execution policy error), allow
it for the current window only, then activate again:

```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.venv\Scripts\Activate.ps1
```

Once active, the prompt shows `(.venv)` at the start of the line. That is
the sign `pytest`, `ruff` and anything else installed below will be found.
Every new PowerShell window needs `.venv\Scripts\Activate.ps1` run again,
activation does not persist between terminal sessions. To leave the
environment: `deactivate`. `.venv` is already listed in `.gitignore`, it
never gets committed.

Setup, once after creating the environment, and again after pulling changes
to `pyproject.toml`:

```
pip install -e ".[dev]"
```

Run the tests:

```
pytest
```

Run only one layer's tests, for example the domain layer:

```
pytest tests/domain
```

Lint:

```
ruff check .
```

Format:

```
ruff format .
```

Running the pipeline itself has no command yet. Only the domain and
application layers exist so far, with no real adapter wired in, so there
is nothing runnable end to end until the first infrastructure PR lands.

## Documentation

Each pull request has a companion write-up in [docs/](docs/README.md) explaining not just what changed, but why, at a level of detail this README does not go into.

## Development workflow

Work happens in small pull requests, one per layer or per adapter, rather than one large branch for the whole project.

Branch naming:
- `feature/...` for new functionality (for example, `feature/domain-model`)
- `chore/...` for tooling and configuration (for example, `chore/tooling`)
- `fix/...` for bug fixes

A typical cycle: create a branch from `main` for one small piece of work, open a pull request once it is done and passing CI, merge it, then branch again from the updated `main` for the next piece.
