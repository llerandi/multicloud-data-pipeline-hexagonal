# 02 · Tooling

Branch: `chore/tooling` · Technical write-up:
[docs/02-tooling.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/02-tooling.md)

## The concept this stage teaches

Not every PR in a hexagonal-architecture project is about the architecture
itself. This one is scaffolding: `pyproject.toml` and a CI workflow. It's
included as its own stage because a learning project benefits from seeing
*when* tooling gets introduced (right after the domain layer exists,
before any real infrastructure code) and *why* (so every PR from here on
is linted and tested automatically, catching regressions in the boundary
between layers before they get merged).

## What to notice

- The `src/` layout here is slightly non-standard: `src/__init__.py`
  exists, making `src` itself a package, so imports are
  `from src.domain.models import ...` rather than the more common
  `from domain.models import ...`. `pyproject.toml` had to match that
  existing decision, not the other way around.
- `dev` dependencies (`pytest`, `ruff`) are a separate optional group -
  the pipeline itself needs nothing beyond the standard library so far,
  so tools needed only to *develop* it stay out of the production
  dependency list.
- CI runs `lint` before `test` (`needs: lint`) - fail fast on the cheaper
  check first.

## Why it matters for the rest of the project

This is the safety net every subsequent adapter PR runs through. Once real
cloud adapters start landing (GCS, S3, BigQuery...), CI is what catches an
adapter accidentally importing something it shouldn't, or breaking an
existing test for a layer it wasn't supposed to touch.

Back to [Home](Home) · Previous: [01 · Domain model](01-Domain-Model) · Next: [03 · Application ports](03-Application-Ports)
