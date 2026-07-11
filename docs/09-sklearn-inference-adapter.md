# PR 9: SklearnModelInference adapter

Branch: `feature/sklearn-inference-adapter`

Files added: `src/infrastructure/inference/sklearn_model_inference.py`,
`src/infrastructure/inference/__init__.py` (updated),
`tests/infrastructure/inference/test_sklearn_model_inference.py`,
`tests/infrastructure/inference/test_sklearn_model_inference_integration.py`,
`pyproject.toml` (updated), `.github/workflows/ci.yaml` (updated).

## What this adapter does, and what it deliberately does not do

`SklearnModelInference` implements `ModelInferencePort` by calling
`.predict()` on a scikit-learn estimator. It does not train a model, load
one from disk, or know anything about how the model was built, it is
handed an already-fitted `model` object at construction and only knows
how to turn `rows` into the matrix shape scikit-learn expects, and how to
hand the result back in the shape `ModelInferencePort` promises. Training
and loading a model is a different concern from serving predictions
inside a pipeline, and keeping this adapter narrow is what makes it
possible to write the same class regardless of how the model it wraps
was produced.

## Why `feature_names` is a constructor argument, and why order matters

```python
def __init__(self, model, feature_names):
    self._model = model
    self._feature_names = feature_names

def predict(self, dataset_name, rows):
    matrix = [[row[name] for name in self._feature_names] for row in rows]
```

Rows arrive as dictionaries (`{"age": 30, "income": 50000}`), but
scikit-learn expects a 2D array of plain numbers with no column names
attached at all, a model trained on columns in the order `[age, income]`
will silently produce nonsense if handed `[income, age]` instead, no
exception, just wrong predictions. `feature_names` exists to fix that
order explicitly, provided once when the adapter is built, matching
whatever order the model was actually trained with. This adapter has no
way to verify that order is correct on its own, getting it right is the
responsibility of whoever constructs it.

## Why the numpy conversion exists, and why `tolist()` over `list()`

```python
predictions = self._model.predict(matrix)
if hasattr(predictions, "tolist"):
    return predictions.tolist()
return list(predictions)
```

A real scikit-learn model returns a numpy array, not a plain Python list.
`ModelInferencePort` promises a `Sequence[Any]`, and this line is what
keeps that promise regardless of which model is behind it, whoever calls
`predict()` should not need to know or care whether the numbers came back
wrapped in numpy or not.

`list(a_numpy_array)` and `a_numpy_array.tolist()` look interchangeable
but are not: `list()` gives back a Python list whose elements are still
numpy scalar types (`numpy.int64`, not `int`), `tolist()` converts all the
way down to native Python numbers. The difference rarely bites in a quick
script, `numpy.int64(1) == 1` is `True`, but it can surface later in
unexpected places, like a numpy type failing to serialize to JSON where a
plain `int` would not. `tolist()` is used when available, with `list()`
as a fallback for anything that returns a plain list or tuple already
(the fakes used in the unit tests, for instance).

## Two separate test files, and why

`test_sklearn_model_inference.py` uses `FakeModel`, a small class with
nothing but a `.predict(matrix)` method, not scikit-learn at all. That is
enough to test everything this adapter's own code is responsible for: the
row-to-matrix conversion in the right order, and the two return-type
paths (plain list, and a `NumpyLikeArray` stand-in with a `.tolist()`
method, to prove that branch is taken without needing real numpy).
Because none of this needs scikit-learn installed, these tests run
everywhere.

`test_sklearn_model_inference_integration.py` is the one test in the
project that fits and runs a real `LogisticRegression`, on a tiny,
trivial, perfectly separable dataset, not to demonstrate anything about
machine learning, only to prove the adapter works against the actual
library, not just against something shaped like it. It starts with
`pytest.importorskip("sklearn")`, so this one file is skipped with a
clear reason rather than failing on an environment where scikit-learn is
not installed, instead of the whole test suite refusing to run.

## Why `scikit-learn` is its own optional dependency group, not part of `dev`

```toml
[project.optional-dependencies]
dev = ["pytest>=8.0", "ruff>=0.6"]
sklearn = ["scikit-learn>=1.4"]
```

The project scope is explicitly multi-cloud: a GCS adapter, an S3
adapter, a BigQuery adapter, a Postgres adapter, and eventually a Vertex
AI adapter are all meant to exist side by side, each behind the same
ports. Bundling every adapter's dependency into one `dev` group would
mean anyone working on, say, the domain layer, ends up installing
scikit-learn, and later `google-cloud-bigquery`, `psycopg2`, and every
other cloud SDK, whether they touch that code or not. Giving `sklearn`
its own extra means `pip install -e ".[dev]"` stays light for anyone not
touching this adapter, and `pip install -e ".[dev,sklearn]"` opts in only
when needed, the same pattern this project will reuse for `gcp`, `aws`,
and so on as those adapters get built.

`.github/workflows/ci.yaml` installs with `".[dev,sklearn]"` specifically
in the `test` job, since CI has to run every test in the repository,
including the real scikit-learn integration test. The `lint` job still
installs only `".[dev]"`, `ruff check` does not import the code it
examines, so it does not need scikit-learn installed to do its job.
