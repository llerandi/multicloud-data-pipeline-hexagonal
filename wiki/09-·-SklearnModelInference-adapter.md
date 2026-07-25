# 09 · SklearnModelInference adapter

Branch: `feature/sklearn-inference-adapter` · Technical write-up:
[docs/09-sklearn-inference-adapter.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/09-sklearn-inference-adapter.md)

## The concept this stage teaches

The first real adapter for `ModelInferencePort` ([08](08-·-ModelInferencePort)),
and the first time this project has to bridge its own plain-Python shapes
(`rows` as dicts, `Sequence[Any]` as output) against a library with its
own conventions (numpy arrays in, numpy arrays out). The adapter's job is
narrow on purpose: it does not train or load a model, only turns rows into
the matrix shape scikit-learn expects and turns whatever comes back into
the plain `Sequence[Any]` the port promises.

## What to notice

- `feature_names` is provided once, at construction, to fix column order -
  a model trained on `[age, income]` fed `[income, age]` produces wrong
  predictions silently, no exception. The adapter can't verify this order
  is correct; that's the caller's responsibility.
- `.tolist()` is preferred over `list()` when converting a numpy array
  back - `list()` still leaves numpy scalar types (`numpy.int64`) inside,
  `.tolist()` converts all the way down to native Python numbers, which
  matters the moment something downstream tries to serialize to JSON.
- Two separate test files: one using a bare `FakeModel` (no scikit-learn
  needed, runs everywhere), one fitting a real `LogisticRegression`
  (skipped cleanly via `pytest.importorskip` if scikit-learn isn't
  installed, rather than failing the whole suite).
- `scikit-learn` gets its own `sklearn` optional dependency extra, not
  bundled into `dev` - the first appearance of a pattern every adapter
  from here on repeats. See [Glossary](Glossary#optional-dependency-extra).

## Why it matters for the rest of the project

This is the template for "wrap a real, specific library behind a generic
port" - narrow responsibility, isolate the dependency, test both without
and with the real library. Stages [10](10-·-PostgresDatasetRepository-adapter)
through [13](13-·-BigqueryDatasetRepository-adapter) follow the same shape
against different SDKs; [14](14-·-CloudMonitoringMetricsPublisher-adapter)
is where that shape stops being enough.

Back to [Home](Home) · Previous: [08 · ModelInferencePort](08-·-ModelInferencePort) · Next: [10 · PostgresDatasetRepository adapter](10-·-PostgresDatasetRepository-adapter)
