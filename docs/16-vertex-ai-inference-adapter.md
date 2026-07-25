# PR 16: VertexAiModelInference adapter

Branch: `feature/vertex-ai-inference-adapter`

Files added: `src/infrastructure/inference/vertex_ai_model_inference.py`,
`src/infrastructure/inference/__init__.py` (updated),
`tests/infrastructure/inference/test_vertex_ai_model_inference.py`,
`pyproject.toml` (updated).

This is the last adapter the project scope asked for. Every port now has
every adapter it was defined for: `FileStorage` (local, GCS, S3),
`DatasetRepository` (Postgres, BigQuery), `MetricsPublisher` (console,
Cloud Monitoring), `NotificationPort` (log stub, Slack), and now
`ModelInferencePort` (local scikit-learn, Vertex AI).

## Back to a single duck-typed method, same as Slack, unlike Cloud Monitoring

Vertex AI's real `PredictionServiceClient` exposes `.predict(endpoint, instances)`,
one method, plain arguments, returning a response with a `.predictions`
attribute. That is enough to duck-type directly, the same way
`PostgresDatasetRepository`'s connection or `GcsFileStorage`'s bucket
were, without needing to build any protobuf message by hand the way
`CloudMonitoringMetricsPublisher` had to. This module does not import
`google-cloud-aiplatform` for the same reason none of those adapters
import their SDKs.

## The real comparison in this PR: two `ModelInferencePort` adapters, two different instance shapes

```python
# SklearnModelInference
matrix = [[row[name] for name in self._feature_names] for row in rows]
predictions = self._model.predict(matrix)
```

```python
# VertexAiModelInference
instances = [{name: row[name] for name in self._feature_names} for row in rows]
response = self._client.predict(endpoint=self._endpoint, instances=instances)
```

`ModelInferencePort` was written back in PR 8 specifically to be
compared this way, the same way `FileStorage`'s GCS and S3 adapters were
compared in PR 12. scikit-learn wants a positional matrix, a plain list
of lists with no column names attached at all, `feature_names`'s order
is what tells this adapter which value goes in which position, get the
order wrong and the model silently scores the wrong column as the wrong
feature. A deployed Vertex AI model instead expects each instance as a
named JSON object, `{"age": 30, "income": 50000}`, matching whatever
keys its serving signature was built with, `feature_names` here selects
which keys to keep, not what order to put them in, a row's extra keys
(`id`, in the test) are dropped, and the ones kept can appear in any
order without changing the result.

Same port, same constructor-level `feature_names` argument even, two
meaningfully different reasons that argument exists, one about position,
one about naming. That difference is exactly what this pair of adapters
was meant to make visible, the same lesson `FileStorage`'s pair already
taught with client shapes instead of data shapes.

## `response.predictions` is an attribute, not a dict key, and the fakes reflect that

```python
class FakeVertexAiResponse:
    def __init__(self, predictions):
        self.predictions = predictions
```

`S3FileStorage`'s response is a dict (`response["Body"]`), Vertex AI's is
an object with a `.predictions` attribute. `FakeVertexAiResponse` is
written to match that specific shape rather than a dict, for the same
reason `FakeBucket` in the S3 and GCS tests was written to fail at the
same step the real client fails at: a fake that gets the real API's
shape wrong would still make the tests pass while testing a client that
does not actually exist.

## `google-cloud-aiplatform` as its own `vertexai` extra

Same pattern as every dependency before it, its own optional extra, so
`pip install -e ".[dev]"` stays light for anyone not touching this
adapter.

## Where this leaves the project

Every port defined back in the original scope now has every adapter that
scope called for. What is still open, and documented as such in earlier
PRs rather than silently missing, is wiring these adapters into an actual
running composition (a script or entry point that builds real clients
and passes them into `ValidateAndIngestDataset`), and the handful of
explicitly noted gaps: the shared not-found exception across `FileStorage`
adapters (PR 11), a real Postgres integration test (PR 10), and a schema
representation for `out_of_range_count` (PR 4). None of those were left
unnoticed, each is written down in the PR that first ran into it.
