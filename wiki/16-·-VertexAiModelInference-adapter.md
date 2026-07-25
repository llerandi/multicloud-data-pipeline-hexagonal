# 16 · VertexAiModelInference adapter

Branch: `feature/vertex-ai-inference-adapter` · Technical write-up:
[docs/16-vertex-ai-inference-adapter.md](https://github.com/llerandi/multicloud-data-pipeline-hexagonal/blob/main/docs/16-vertex-ai-inference-adapter.md)

## The concept this stage teaches

This is the last adapter the project scope asked for - every port now has
every adapter it was defined for. Vertex AI's real client exposes
`.predict(endpoint, instances)`, one method, plain arguments - simple
enough to duck-type directly, no protobuf construction needed the way
[14](14-·-CloudMonitoringMetricsPublisher-adapter) required. The real
lesson of this stage isn't the mechanism though, it's the comparison this
adapter completes: `ModelInferencePort` ([08](08-·-ModelInferencePort))
was written back in PR 8 specifically to let two adapters be compared
this way, the same way [12](12-·-S3FileStorage-adapter) compared
`FileStorage`'s GCS and S3 adapters.

## What to notice

- `SklearnModelInference` builds a positional matrix (`[[row[name] for
  name in feature_names] for row in rows]`) - a plain list of lists with
  no column names attached, so `feature_names`'s *order* is what tells
  the model which value goes where. `VertexAiModelInference` builds named
  JSON objects instead (`{name: row[name] for name in feature_names}`) -
  a deployed model matches keys against its serving signature, so
  `feature_names` here selects *which* keys to keep, not what order to
  put them in.
- Same port, same constructor argument (`feature_names`), two genuinely
  different reasons it exists - one about position, one about naming.
  That's the pair of adapters making visible exactly what the port was
  designed to expose.
- `response.predictions` is an attribute on Vertex AI's response object,
  not a dict key like S3's `response["Body"]` - `FakeVertexAiResponse` is
  written to match that specific shape, the same discipline
  `FakeBucket` followed in [11](11-·-GcsFileStorage-adapter) and
  [12](12-·-S3FileStorage-adapter): a fake that gets the real API's shape
  wrong would still pass tests while testing a client that doesn't exist.

## Why it matters for the rest of the project

Every port defined back in [03](03-·-Application-ports) now has every
adapter its scope called for - see [Roadmap](Roadmap-and-status) for what
that leaves open (an actual composition root wiring these adapters
together, the shared not-found exception gap, a real Postgres integration
test, and the `out_of_range_count` schema). None of those gaps were left
unnoticed; each was written down in the PR that first ran into it.

Back to [Home](Home) · Previous: [15 · SlackNotificationPort adapter](15-·-SlackNotificationPort-adapter)
